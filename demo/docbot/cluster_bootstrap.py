from os import getenv
import dotenv
from opensearchpy import OpenSearch
import sys
sys.path.append('./demo/')
from docbot.util import opensearch_connection_builder, opensearch_compare_dictionaries, MLClient, model_exists


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

        self._initialize_cluster_settings()
        self._initialize_model_group()
        self._initialize_connector()
        self._initialize_model("embed-english-v2.0", "Embedding Model")
        self._initialize_model("command-nightly", "Cohere Command Model")
        self._initialize_ingestion_pipeline()
        self._initialize_index()

    def initialize_cluster_settings(self):
        """
        Args:
            Self
        Returns:
            returns None if cluster settings was created or is exists else raise Exception
        """
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
        """
        Args:
            Self
        Returns:
            returns None if template was created or is exists else raises Exception
        """
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
        """
        Args:
            Self
        Returns:
            returns None if model group was created or is exists else raises Exception
        """

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
        """
        Args:
            Self
        Returns:
            returns None if connector was created or is exists else raises Exception
        """
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
        """
        Initialize a model in OpenSearch.
        (In the model_meta json, the parameters field is only needed when using a model
        other than text-embed-2 since it defaults to text-embedding-ada-002)

        Args:
            Self
            model_name (str): The name of the model to initialize.
            model_descp (str): The description of the model.

        Returns:
            None if model is initialized successfully or already initialized else raises Exception

        """
        model_meta = {
            "name": model_name,
            "function_name": "remote",
            "description": model_descp,
            "model_group_id": self.model_group_id,
            "connector_id": self.connector_id
        }

        model_id = model_exists(client=self.client, model_name=model_name)
        if model_id:
            self.connector_id = model_id
            print("Model " + model_name + " already exists. Skipping initialization.")
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

    def initialize_ingestion_pipeline(self):
        pipeline_data = {
            "description": "Cohere Neural Search Pipeline",
            "processors": [
                {
                    "text_embedding": {
                        "embedding_model": self.embedding_model,
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

    def initialize_rag_search_pipeline(self, id: str = "rag-search-pipeline") -> None:
        """
        Args:
            Client: MLClient
        Returns:
            returns None if pipeline was created or it exists else raises Exception
        """
        body = {
        "response_processors": [
            {
            "retrieval_augmented_generation": {
                "description": "RAG search pipeline to be used with Cohere index",
                "model_id": self.language_model,
                "context_field_list": ["content"]
            }
            }
        ]
        }
        # Check if pipeline exists, else create it
        try:
            pipeline = self.client.get_search_pipeline(id=id)
            print(f"Pipeline {id} already exisits. Skipping initialization")
            return
        except:
            response = self.client.put_search_pipeline(id=id, body=body)
            if response and "acknowledged" in response and response["acknowledged"]:
                print(f"Pipeline {id} initialized succesfully.")
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
                    },
                }
            }
        }
        # Check if the index already exists
        index_exists = self.client._client.indices.exists(index="cohere-index")
        if index_exists is not None:
            print("Index 'cohere-index' already exists. Skipping initialization.")
            return

        # Create the index
        response = self.client._client.indices.create(index="cohere-index", body=index_data)

        # Check if the request was successful
        if response and 'acknowledged' in response and response['acknowledged']:
            print("Index 'cohere-index' created successfully!")
        else:
            raise Exception("Failed to create index.")

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

                delete_model_response = self.client.delete_model(
                    self.embedding_model)
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

            delete_index_response = self.client._client.indices.delete(
                index='cohere-index')
            if delete_index_response and 'acknowledged' in delete_index_response and delete_index_response['acknowledged']:
                print('\nDeleting index:')
                print(delete_index_response)
            else:
                raise Exception("Failed to delete index.")

            delete_pipeline_response = self.client._client.ingest.delete_pipeline(
                id='cohere-ingest-pipeline')
            if delete_pipeline_response and 'acknowledged' in delete_pipeline_response and delete_pipeline_response['acknowledged']:
                print('\nDeleting pipeline:')
                print(delete_pipeline_response)
            else:
                raise Exception("Failed to delete ingest pipeline.")

              # Delete search pipeline
            delete_search_pipeline_response = client.delete_search_pipeline(id=search_pipeline)
            if delete_search_pipeline_response and 'acknowledged' in delete_search_pipeline_response and delete_search_pipeline_response['acknowledged']:
                print('\nDeleting pipeline:')
                print(delete_search_pipeline_response)
            else:
                raise Exception("Failed to delete search pipeline.")
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
