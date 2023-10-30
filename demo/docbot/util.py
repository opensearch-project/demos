import dotenv
from os import getenv
from opensearchpy import OpenSearch
from opensearch_py_ml.ml_commons import MLCommonClient
from copy import deepcopy


dotenv.load_dotenv()
ADMIN_PW = getenv('ADMIN_PW')
ADMIN_UN = getenv('ADMIN_UN')
HOSTS = getenv('HOSTS')
DEVELOPMENT= getenv('DEVELOPMENT')


##### Monkey patching 🤪 #####

from opensearch_py_ml.ml_commons.ml_common_utils import (
    ML_BASE_URI,
    TIMEOUT,
)
from typing import Union, Any
from datetime import time


class MLClient(MLCommonClient):
  def register_model_group(self, model_group_meta_json: dict) -> str:
    """
    This method registers a model group with ML Commons' register api

    :param model_group_meta_json: a dictionary object with model group configurations
    :type model_group_meta_json: dict
    :return: returns a unique id of the model group
    :rtype: string
    """

    output: dict = self._client.transport.perform_request(
        method="POST",
        url=f"{ML_BASE_URI}/model_groups/_register",
        body=model_group_meta_json,
    )
    if not output["status"] == "CREATED":
       raise Exception("Failed to create model group")

    return output["model_group_id"]


  def get_model_group_id(self, model_group_name: str=None) -> str | None:
    """
    This gets a model group id by doing a search on the model name

    :param model_group_name: the model group name
    :type model_group_name: str
    :return: returns a unique id of the model group or none if it doesnt exist
    :rtype: string | None
    """
    query = {
       "query": {
        "match": {}
      }
    }

    if model_group_name is not None:
       query["query"]["match"].update({"name": model_group_name})
    else: raise Exception("Model group name and id cannot both be empty")

    output = self._client.transport.perform_request(
        method="POST",
        url=f"{ML_BASE_URI}/model_groups/_search",
        body=query,
    )

    if not output["hits"]["total"]["value"] > 0:
       return None

    return output["hits"]["hits"][0]["_id"]


  def create_connector(self, connector_meta_json: dict) -> str:
    """
    This method creates a ML Connector using ML Commons' create api

    :param connector_meta_json: a dictionary object with model configurations
    :type connector_meta_json: dict
    :return: returns a unique id of the connector
    :rtype: string
    """
    output: dict =  self._client.transport.perform_request(
        method="POST",
        url=f"{ML_BASE_URI}/connectors/_create",
        body=connector_meta_json,
    )
    if not output["status"] == "CREATED":
       raise Exception("Failed to create connector")

    return output["connector_id"]


  def get_connector_id(self, connector_name: str = None) -> str | None:
    """
    This gets a connector id by doing a search on the connector name

    :param connector_name: the connector name
    :type connector_name: string
    :return: returns a unique id of the connector or none if it doesnt exist
    :rtype: string | None
    """
    query = {
       "query": {
        "match": {}
      }
    }

    if connector_name is not None:
       query["query"]["match"].update({"name": connector_id})
    else: raise Exception("Model group name and id cannot both be empty")

    output = self._client.transport.perform_request(
        method="POST",
        url=f"{ML_BASE_URI}/connectors/_search",
        body=query,
    )

    if not output["hits"]["total"]["value"] > 0:
       return None

    return output["hits"]["hits"][0]["_id"]

  def register_connector_model(self, model_meta_json: dict) -> str:
        """
        This method creates a model using an already existing connector

        :param model_meta_json: a dictionary object with model configurations
        :type model_meta_json: dict
        :return: returns a unique id of the model
        :rtype: string
        """
        output: Union[bool, Any] = self._client.transport.perform_request(
            method="POST",
            url=f"{ML_BASE_URI}/models/_register?deploy=true",
            body=model_meta_json,
        )
        end = time.time() + TIMEOUT  # timeout seconds
        task_flag = False
        while not task_flag and time.time() < end:
            time.sleep(1)
            status = self._get_task_info(output["task_id"])
            if status["state"] != "CREATED":
                task_flag = True
        # TODO: need to add the test case later for this line
        if not task_flag:
            raise TimeoutError("Model registration timed out")
        if status["state"] == "FAILED":
            raise Exception(status["error"])
        print("Model was registered successfully. Model Id: ", status["model_id"])
        return status["model_id"]


  def delete_model_group(self, model_group_id: dict) -> dict:
    """
    This method sends the pretrained model info to ML Commons' register api

    :param model_meta_json: a dictionary object with model configurations
    :type model_meta_json: dict
    :return: returns a unique id of the model
    :rtype: string
    """
    return self._client.transport.perform_request(
        method="DELETE",
        url=f"{ML_BASE_URI}/model_groups/{model_group_id}",
    )

  def delete_connector(self, connector_id: str) -> dict:
      """
      This method deletes a connector from opensearch cluster (using ml commons api)

      :param connector_id: unique id of the connector
      :type connector_id: string
      :return: returns a json object, with detailed information about the deleted connector
      :rtype: object
      """

      API_URL = f"{ML_BASE_URI}/connectors/{connector_id}"

      return self._client.transport.perform_request(
          method="DELETE",
          url=API_URL,
      )

##### END MONKEYPATCH #####

def opensearch_connection_builder(ml_client=False) -> MLCommonClient | OpenSearch:
  config = {
    "hosts": HOSTS,
    "http_auth": (ADMIN_UN, ADMIN_PW),
    "use_ssl": True,
    "verify_certs": True
  }

  if DEVELOPMENT:
    config['verify_certs'] = False

  if ml_client:
    client = MLClient(
      OpenSearch(**config)
    )
  else:
    client = OpenSearch(**config)

  return client

def shorten_json_file_same_index(json_file, num_words=150, overlap=0.3) -> list:
  """
  Args:
    json_file: a json index with OpenSearch document to be ingested
    num_words: content length of each sub-document
    overlap: The percentage amount of overlap in breaking the documents
  Returns:
    A list of dict with same metadata but content is a chunk of sub-document if successful, raise exception if failed
  """
  if not isinstance(json_file, dict) or 'content' not in json_file:
    raise ValueError("Inappropriate Argument json_file must be a valid dict of OpenSearch json index")

  if num_words <= 0:
    raise ValueError("Inappropriate Argument: num_words must be positive")

  if overlap <= 0 or overlap >= 1:
    raise ValueError("Inappropriate Argument: overlap must be within 0 and 1")

  sentence_to_split = json_file['content'].split()
  temp = None
  result = []

  while len(sentence_to_split) > (num_words):
    overlapped_bound = int(num_words-(num_words*overlap))
    temp = deepcopy(json_file)
    temp['content'] = " ".join(sentence_to_split[:num_words])
    result.append(temp)
    sentence_to_split = sentence_to_split[overlapped_bound:]

  temp = deepcopy(json_file)
  temp['content'] = " ".join(sentence_to_split)
  result.append(temp)

  return result
