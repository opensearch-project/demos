from os import getenv
import dotenv
from opensearchpy import OpenSearch
from docbot.util import opensearch_connection_builder, opensearch_compare_dictionaries, MLClient
import requests
import os
import json
import sys
sys.path.append('./demo/')

dotenv.load_dotenv()

class ClusterBootstrap:
    def __init__(self, use_ssl=True):
        self.Cohere_key = getenv('COHERE_KEY')
        self.model_group_id = ""
        self.connector_id = ""
        self.embedding_model = ""
        self.language_model = ""
        self.client = opensearch_connection_builder(
            ml_client=True, use_ssl=use_ssl)

        self.initialize_cluster_settings()
        self.initialize_model_group()
        self.initialize_connector()
        self.initialize_model("embed-english-v2.0", "Embedding Model")
        self.initialize_model("command-nightly", "Cohere Command Model")
        self.initialize_ingestion_pipeline()
        self.initialize_index()

    def initialize_cluster_settings(self):
        current_settings = self.client._client.cluster.get_settings()

        data = {
            "plugins.ml_commons.allow_registering_model_via_url": True,
            "plugins.ml_commons.only_run_on_ml_node": False,
            "plugins.ml_commons.connector_access_control_enabled": True,
            "plugins.ml_commons.model_access_control_enabled": True,
            "plugins.ml_commons.memory_feature_enabled": True,
            "plugins.ml_commons.rag_pipeline_feature_enabled": True,
            "plugins.ml_commons.trusted_connector_endpoints_regex": [
                "^https://runtime\\.sagemaker\\..*[a-z0-9-]\\.amazonaws\\.com/.*$",
                "^https://api\\.openai\\.com/.*$",
                "^https://api\\.cohere\\.ai/.*$"
            ]
        }

        if 'persistent' in current_settings and opensearch_compare_dictionaries(data, current_settings['persistent']):
            print("Cluster settings are already initialized!")
            return

        response = self.client.cluster.put_settings(body={"persistent": data})
        if response and 'acknowledged' in response and response['acknowledged']:
            print("Cluster settings initialized successfully!")
        else:
            raise Exception("Failed to initialize cluster settings.")

    def init_index_template(self, template_name="nlp-template"):
        if not self.client._client.indices.exists_template(name=template_name):
            template = {
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

            response = self.client._client.indices.put_template(
                name=template_name, body=template)
            if not response["acknowledged"]:
                raise Exception("Unable to create index template.")

    def initialize_model_group(self):
        model_group_name = "Cohere_Group"
        response = self.client.get_model_group_id(
            model_group_name=model_group_name)
        if response is None:
            data = {
                "name": model_group_name,
                "description": "Public Cohere Model Group",
                "access_mode": "public"
            }
            response = self.client.register_model_group(body=data)
            if isinstance(response, str):
                print("Model group initialized successfully!")
                self.model_group_id = response
            else:
                raise Exception(
                    f"Failed to initialize model group. Response: {response}")
        else:
            print(f"Model group '{model_group_name}' already exists.")

    def initialize_connector(self):
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

        connector_id = self.client.get_connector_id(
            connector_name="Cohere Connector")
        if connector_id is None:
            response = self.client.create_connector(connector_data)
            connector_id = self.client.get_connector_id(
                connector_name="Cohere Connector")
            if connector_id:
                print("Connector 'Cohere Connector' initialized successfully!")
                self.connector_id = connector_id
            else:
                raise Exception("Failed to initialize connector.")
        else:
            self.connector_id = connector_id
            print("Connector 'Cohere Connector' already exists. Skipping initialization.")

    def initialize_model(self, model_name: str, model_descp: str):
        model_meta = {
            "name": model_name,
            "function_name": "remote",
            "description": model_descp,
            "model_group_id": self.model_group_id,
            "connector_id": self.connector_id
        }

        if self.model_exists(model_name):
            print("Model " + model_name +
                  " already exists. Skipping initialization.")
            return

        response = self.client.register_connector_model(
            model_meta_json=model_meta)
        if isinstance(response, str):
            if model_name == "command-nightly":
                self.language_model = response
            else:
                self.embedding_model = response
            print("Model " + model_name + " initialized successfully!")
        else:
            raise Exception("Failed to initialize model.")

    def model_exists(self, model_name: str) -> bool:
        existing_models = self.client.search_model({
            "query": {
                "match": {
                    "name": model_name
                }
            }
        })
        if existing_models["hits"]["total"]["value"] > 0:
            self.connector_id = existing_models["hits"]["hits"][0]["_id"]
            return True
        return False

    def initialize_ingestion_pipeline(self):
        pipeline_data = {
            "description": "Cohere Neural Search Pipeline",
            "processors": [
                {
                    "text_embedding": {
                        "embedding_model": MODEL_STATE["embedding_model"],
                        "field_map": {
                            "content": "content_embedding"
                        }
                    }
                }
            ]
        }

        try:
            self.client._client.ingest.get_pipeline(
                id="cohere-ingest-pipeline")
            print(
                "Pipeline 'cohere-ingest-pipeline' already exists. Skipping initialization.")
            return
        except:
            response = self.client._client.ingest.put_pipeline(
                id="cohere-ingest-pipeline", body=pipeline_data)
            if response and 'acknowledged' in response and response['acknowledged']:
                print("Pipeline 'cohere-ingest-pipeline' initialized successfully!")
            else:
                raise Exception("Failed to initialize pipeline.")

    def initialize_index(self):
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

        index_exists = self.client._client.indices.exists(index="cohere-index")
        if not index_exists:
            response = self.client._client.indices.create(
                index="cohere-index", body=index_data)
            if response and 'acknowledged' in response and response['acknowledged']:
                print("Index 'cohere-index' created successfully!")
            else:
                raise Exception("Failed to create index.")
        else:
            print("Index 'cohere-index' already exists. Skipping initialization.")

    def ml_cleanup(self):
        try:
            if self.embedding_model:
                undeploy_model_response = self.client.undeploy_model(
                    self.embedding_model)
                stats = dict(list(undeploy_model_response.values())[0])
                if stats[self.embedding_model] == 'undeployed':
                    print('\nUndeploying model:')
                    print(undeploy_model_response)
                else:
                    raise Exception("Failed to undeploy model.")

                delete_model_response = self.client.delete_model(self.embedding_model)
                if delete_model_response and delete_model_response['result'] == 'deleted':
                    print('\nDeleting model:')
                    print(delete_model_response)
                else:
                    raise Exception("Failed to delete model.")

            if self.connector_id:
                delete_connector_response = self.client.delete_connector(
                    self.connector_id)
                if delete_connector_response and delete_connector_response['result'] == 'deleted':
                    print('\nDeleting connector:')
                    print(delete_connector_response)
                else:
                    raise Exception("Failed to delete connector.")

            delete_pipeline_response = self.client._client.ingest.delete_pipeline(
                id='cohere-ingest-pipeline')
            if delete_pipeline_response and 'acknowledged' in delete_pipeline_response and delete_pipeline_response['acknowledged']:
                print('\nDeleting pipeline:')
                print(delete_pipeline_response)
            else:
                raise Exception("Failed to delete ingest pipeline.")

            delete_index_response = self.client._client.indices.delete(
                index='cohere-index')
            if delete_index_response and 'acknowledged' in delete_index_response and delete_index_response['acknowledged']:
                print('\nDeleting index:')
                print(delete_index_response)
            else:
                raise Exception("Failed to delete index.")

        except Exception as e:
            print(f"An error occurred during cleanup: {e}")

        finally:
            # Clear MODEL_STATE
            self.model_group_id = None
            self.connector_id = None
            self.embedding_model = None
            self.language_model = None
            # Ensure that any additional cleanup is also handled here

if __name__ == "__main__":
    try:
        cluster_bootstrap = ClusterBootstrap(
            use_ssl="--no-ssl" not in sys.argv)
    except Exception as e:
        print(f"An error occurred while initializing cluster bootstrap: {e}")
