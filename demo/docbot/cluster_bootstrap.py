# Place where we will validate the clusters
# configuration and settings on import
from opensearchpy import OpenSearch

# Check and apply cluster settings
def initialize_cluster_settings():
  # PUT /_cluster/settings
  # {
  #     "persistent": {
  #         "plugins.ml_commons.allow_registering_model_via_url": true,
  #         "plugins.ml_commons.only_run_on_ml_node": false,
  #         "plugins.ml_commons.connector_access_control_enabled": true,
  #         "plugins.ml_commons.model_access_control_enabled": true,
  #         "plugins.ml_commons.trusted_connector_endpoints_regex": [
  #           "^https://runtime\\.sagemaker\\..*[a-z0-9-]\\.amazonaws\\.com/.*$",
  #           "^https://api\\.openai\\.com/.*$",
  #           "^https://api\\.cohere\\.ai/.*$"
  #         ]
  #     }
  # }

  pass

def init_index_template(client: OpenSearch):
  """
  Args:
    Client: OpenSearch
  Returns:
    returns if template was created or is exists
  """

  if not client.indices.exists_index_template("nlp-template"):
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

    response = client.indices.put_index_template("nlp-template", body=template)
    if not response["acknowledged"]:
      raise Exception("Unable to create index template.")


def initialize_model_group():
  # POST /_plugins/_ml/model_groups/_register
  # {
  #     "name": "Cohere_Group",
  #     "description": "Public Cohere Model Group",
  #     "access_mode": "public"
  # }
  pass


def initialize_connector():
  #   POST /_plugins/_ml/connectors/_create
  # {
  #    "name": "Cohere Connector",
  #    "description": "External connector for connections into Cohere",
  #    "version": "1.0",
  #    "protocol": "http",
  #    "credential": {
  #            "cohere_key": "<COHERE KEY HERE>"
  #        },
  #     "parameters": {
  #       "model": "embed-english-v2.0",
  #       "truncate": "END"
  #     },
  #    "actions": [{
  #        "action_type": "predict",
  #        "method": "POST",
  #        "url": "https://api.cohere.ai/v1/embed",
  #        "headers": {
  #                "Authorization": "Bearer ${credential.cohere_key}"
  #            },
  # 			"request_body": "{ \"texts\": ${parameters.prompt}, \"truncate\": \"${parameters.truncate}\", \"model\": \"${parameters.model}\" }",
  # 			"pre_process_function": "connector.pre_process.cohere.embedding",
  # 			 "post_process_function": "connector.post_process.cohere.embedding"
  #        }]
  # }
  pass


def initialize_model():
  #   POST /_plugins/_ml/models/_register?deploy=true
  # {
  #     "name": "embed-english-v2.0",
  #     "function_name": "remote",
  #     "description": "test model",
  #     "model_group_id": "<MODEL_GROUP_ID>",
  #     "connector_id": "<CONNECTOR_ID>"
  # }
  pass


def initialize_ingestion_pipeline():
  #   PUT _ingest/pipeline/cohere-ingest-pipeline
  # {
  #   "description": "Cohere Neural Search Pipeline",
  #   "processors" : [
  #     {
  #       "text_embedding": {
  #         "model_id": "<MODEL_ID>",
  #         "field_map": {
  #           "content": "content_embedding"
  #         }
  #       }
  #     }
  #   ]
  # }

  pass


def initialize_index():
  # PUT /cohere-index
  # {
  # 	"settings": {
  # 		"index.knn": true,
  # 		"default_pipeline": "cohere-ingest-pipeline"
  # 	},
  # 	"mappings": {
  # 		"properties": {
  # 			"content_embedding": {
  # 				"type": "knn_vector",
  # 				"dimension": 4096,
  # 				"method": {
  # 					"name": "hnsw",
  # 					"space_type": "cosinesimil",
  # 					"engine": "nmslib"
  # 				}
  # 			},
  # 			"content": {
  # 				"type": "text"
  # 			}
  # 		}
  # 	}
  # }

  pass


def main():
  initialize_cluster_settings()
  initialize_model_group()
  initialize_connector()
  initialize_model()
  initialize_ingestion_pipeline()
  initialize_index()

main()
