import dotenv
from os import getenv
from opensearchpy import OpenSearch
from opensearch_py_ml.ml_commons import MLCommonClient


dotenv.load_dotenv()
ADMIN_PW = getenv('ADMIN_PW')
ADMIN_UN = getenv('ADMIN_UN')
HOSTS = getenv('HOSTS')
DEVELOPMENT= getenv('DEVELOPMENT')


##### Monkey patching 🤪 #####

from opensearch_py_ml.ml_commons.ml_common_utils import (
    ML_BASE_URI,
    MODEL_FORMAT_FIELD,
    MODEL_GROUP_ID,
    MODEL_NAME_FIELD,
    MODEL_VERSION_FIELD,
    TIMEOUT,
)
from typing import Union, Any
from datetime import time

class MLClient(MLCommonClient):
  def register_model_group(self, model_group_meta_json: dict):
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

  def create_connector(self, connector_meta_json: dict):
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

  def register_connector_model(self, model_meta_json: dict):
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


  def delete_model_group(self, model_group_id: dict):
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

  def delete_connector(self, connector_id: str) -> object:
      """
      This method deletes a model from opensearch cluster (using ml commons api)

      :param model_id: unique id of the model
      :type model_id: string
      :return: returns a json object, with detailed information about the deleted model
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
