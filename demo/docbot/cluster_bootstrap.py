import sys
from util import opensearch_connection_builder
sys.path.append('./demo/')
from docbot.util import opensearch_connection_builder, MLClient
from opensearchpy import OpenSearch

import dotenv
from os import getenv

dotenv.load_dotenv()
COHERE_KEY = getenv('COHERE_KEY')
MODEL_STATE = {
    "model_group_id": "",
    "connector_id": "",
    "model_id": ""
}



def initialize_cluster_settings(client: OpenSearch, cluster_setting=None) -> None:
    """
    Args:
        Client: OpenSearch
    Returns:
        returns None if cluster settings was created or is exists else raise Exception
    """
    current_settings = client._client.cluster.get_settings()
    if cluster_setting is None:
        cluster_setting = {
            "plugins.ml_commons.allow_registering_model_via_url": True,
            "plugins.ml_commons.only_run_on_ml_node": False,
            "plugins.ml_commons.connector_access_control_enabled": True,
            "plugins.ml_commons.model_access_control_enabled": True,
            "plugins.ml_commons.trusted_connector_endpoints_regex": [
                "^https://runtime\\.sagemaker\\..*[a-z0-9-]\\.amazonaws\\.com/.*$",
                "^https://api\\.openai\\.com/.*$",
                "^https://api\\.cohere\\.ai/.*$"
            ]
        }

    if 'persistent' in current_settings and current_settings['persistent'] == cluster_setting:
        print("Cluster settings are already initialized!")
        return

    response = client.cluster.put_settings(body={"persistent": cluster_setting})

    # Check if request was successful
    if response and 'acknowledged' in response and response['acknowledged']:
        print("Cluster settings initialized successfully!")
    else:
        raise Exception("Failed to initialize cluster settings.")


def init_index_template(client: MLClient, template_name = "nlp-template", template_data=None) -> None:

  """
  Args:
    Client: OpenSearch
  Returns:
    returns None if template was created or is exists else raises Exception
  """
  if not client._client.indices.exists_template(name=template_name):
    if template_data is None:
        template_data = {
        "index_patterns": [
        "cohere*"
        ],
        "template": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 2,
            "codec": "zstd_no_dict"
            },
        "mappings": {
            "properties": {
            "data": {
                "index": False
                },
            "ancestors": {
                "index": False
                }
            }
            }
        }
        }

    response = client._client.indices.put_template(name=template_name, body=template_data)
    if not response["acknowledged"]:
      raise Exception("Unable to create index template.")


def initialize_model_group(client: MLClient, model_group_name="Cohere_Group", data=None) -> None:
    """
    Args:
        Client: OpenSearch
    Returns:
        returns None if model group was created or is exists else raises Exception
    """
    # Later on we can edit this to allow more models. For now, we will stick to Cohere.

    response = client.get_model_group_id(model_group_name=model_group_name)

    # Check if the Cohere model group already exists
    if response is not None:
        if data is None:
            data = {
                "name": model_group_name,
                "description": "Public Cohere Model Group",
                "access_mode": "public"
            }

        response = client.register_model_group(body=data)  # Adjust based on the actual method name and structure

        if isinstance(response, str):
            print("Model group initialized successfully!")
            MODEL_STATE["model_group_id"] = response
        else:
            raise Exception(f"Failed to initialize model group. Response: {response}")
    else: print(f"Model group '{model_group_name}' already exists.")



def initialize_connector(client: MLClient, connector_name="Cohere Connector", connector_data=None) -> None:
    """
    Args:
        Client: OpenSearch
    Returns:
        returns None if connector was created or is exists else raises Exception
    """
    # Once again, only allowing for the Cohere Connector. We can change this later on.
    if connector_data is None:
        connector_data = {
            "name": "Cohere Connector",
            "description": "External connector for connections into Cohere",
            "version": "1.0",
            "protocol": "http",
            "credential": {
                "cohere_key": COHERE_KEY
            },
            "parameters": {
                "model": "embed-english-v2.0",
                "truncate": "END"
            },
            "actions": [{
                "action_type": "predict",
                "method": "POST",
                "url": "https://api.cohere.ai/v1/embed",
                "headers": {
                    "Authorization": "Bearer ${credential.cohere_key}"
                },
                "request_body": "{ \"texts\": ${parameters.prompt}, \"truncate\": \"${parameters.truncate}\", \"model\": \"${parameters.model}\" }",
                "pre_process_function": "connector.pre_process.cohere.embedding",
                "post_process_function": "connector.post_process.cohere.embedding"
            }]
        }

    connector_id = client.get_connector_id(connector_name)
    if connector_id is not None:
        response = client.create_connector(connector_data) #this needs to be fixed

        if isinstance(response, str):
            print("Connector 'Cohere Connector' initialized successfully!")
            MODEL_STATE["connector_id"] = response
        else:
            raise Exception("Failed to initialize connector.")
    else:
        print("Connector 'Cohere Connector' already exists. Skipping initialization.")


def initialize_model(client: MLClient, model_data=None) -> None:
    """
    Args:
        Client: OpenSearch
    Returns:
        returns None if model was created or is exists else raises Exception
    """
    # Define the model data. For now, placeholders are used for model_group_id and connector_id.
    if model_data is None:
        model_data = {
            "name": "embed-english-v2.0",
            "function_name": "remote",
            "description": "test model",
            "model_group_id": MODEL_STATE["model_group_id"],
            "connector_id": MODEL_STATE["connector_id"]
        }

    # Check if the model already exists
    existing_models = client.search_model({
        "query": {
            "match": {
                "name": "embed-english-v2.0"
            }
        }
    })

    if existing_models["hits"]["total"]["value"] > 0:
        print("Model 'embed-english-v2.0' already exists. Skipping initialization.")
        MODEL_STATE["connector_id"] = existing_models["hits"]["hits"][0]["_id"]
    else:
        # Register (and deploy) the model
        response = client.register_connector_model(model_meta_json=model_data)

        if isinstance(response, str):
            print("Model 'embed-english-v2.0' initialized successfully!")
        else:
           raise Exception("Failed to initialize model.")



def initialize_ingestion_pipeline(client: MLClient, pipeline="cohere-ingest-pipeline", pipeline_data=None):
    """
    Args:
        Client: OpenSearch
    Returns:
        returns None if ingestion pipeline was created or is exists else raises Exception
    """
    # Fetch the model ID somehow based on how we created the model ID earlier ^
    if pipeline_data is None:
        pipeline_data = {
            "description": "Cohere Neural Search Pipeline",
            "processors": [
                {
                    "text_embedding": {
                        "model_id": MODEL_STATE["model_id"],
                        "field_map": {
                            "content": "content_embedding"
                        }
                    }
                }
            ]
        }

    # Check if the pipeline already exists
    try:
        existing_pipeline = client._client.ingest.get_pipeline(pipeline)
        if existing_pipeline:
            print("Pipeline 'cohere-ingest-pipeline' already exists. Skipping initialization.")
            return
    except Exception as e:
        print(f"An error occurred while checking for any existing pipeline: {e}")

    response = client._client.ingest.put_pipeline(pipeline, body=pipeline_data)

    if response and 'acknowledged' in response and response['acknowledged']:
        print("Pipeline 'cohere-ingest-pipeline' initialized successfully!")
    else:
        raise Exception("Failed to initialize pipeline.")



def initialize_index(client: MLClient, index="cohere-index", index_data=None) -> None:
    """
    Args:
        Client: OpenSearch
    Returns:
        returns None if index was created or is exists else raises Exception
    """
    # Define the index settings and mappings
    if index_data is None:
        index_data = {
            "settings": {
                "index.knn": True,
                "default_pipeline": "cohere-ingest-pipeline"
            },
            "mappings": {
                "properties": {
                    "content_embedding": {
                        "type": "knn_vector",
                        "dimension": 4096,
                        "method": {
                            "name": "hnsw",
                            "space_type": "cosinesimil",
                            "engine": "nmslib"
                        }
                    },
                    "content": {
                        "type": "text"
                    }
                }
            }
        }

    # Check if the index already exists
    try:
        index_exists = client._client.indices.exists(index)
        if index_exists:
            print("Index 'cohere-index' already exists. Skipping initialization.")
            return
    except Exception as e:
        print(f"An error occurred while checking for the index: {e}")

    # Create the index
    response = client._client.indices.create(index, body=index_data)

    # Check if the request was successful
    if response and 'acknowledged' in response and response['acknowledged']:
        print("Index 'cohere-index' created successfully!")
    else:
        raise Exception("Failed to create index.")


def main():
    try:
        client = opensearch_connection_builder(ml_client=True)
        initialize_cluster_settings(client)
        initialize_model_group(client)
        initialize_connector(client)
        initialize_model(client)
        initialize_ingestion_pipeline(client)
        initialize_index(client)
    except Exception as e:
        print(f"An error occurred while initializing cluster bootstrap: {e}")

main()
