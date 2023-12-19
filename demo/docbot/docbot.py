import sys
from opensearchpy import OpenSearch
sys.path.append('./demo/')

from docbot.language_pipeline import generate_response
from docbot.util import MLClient, put_conversation
from cluster_bootstrap import ClusterBootstrap
from docbot.ingestion import read_files_from_data, ingest_to_opensearch

class DocBot():
  def __init__ (self):
    """
    Args:
        Client: OpenSearch
    Returns:
        returns None if connector was created or is exists else raises Exception
    """

    self.conversations = {}
    self.cluster_bootstrap = ClusterBootstrap(use_ssl=True)
    self.client = self.cluster_bootstrap.client

    # Ingest documents into OpenSearch
    try:
        data_list = read_files_from_data()
        ingest_to_opensearch(data_list)
    except Exception as e:
        print(f"An exception occurred during document ingestion: {e}")

  def handle_message(self, message_object):
    # get conversation id form _conversation handler
    id = self.conversation_handler(message_object.name)
    # with conversation id call docbot.generate_response(conversation_id, message) and return response
    return generate_response(id, message_object)

  def conversation_handler(self, conversation_name):
    # check if conversation in state
    id = None
    if conversation_name in self.conversations['name']:
      # check if conversation exists. If it exists track conversation id in self.conversations by name: id
      id = self.conversations[conversation_name]
    else:
      # Check if it exists in OpenSearch
      search_query = {
        "query": {
            "match": {
                "name": conversation_name
                }
              }
            }
      result = self.client._client.search(index='cohere', body=search_query)
      if result['hits']['total']['value'] > 0:
        data = result.json()
        hits = data.get('hits', {}).get('hits', [])
        id = hits[0]['id']
      else:
        id = put_conversation([name:conversation_name])

    #Then return the relevant ID
    if id == None:
      raise Exception("ID was not generated correctly")
    return id
