import sys
from opensearchpy import OpenSearch

sys.path.append('./demo/')

from docbot.language_pipeline import generate_response
from docbot.util import opensearch_connection_builder, MLClient


class Controller():
  def __init__(self, client: MLClient):
    """
    Args:
        Client: OpenSearch
    Returns:
        returns None if connector was created or is exists else raises Exception
    """

    self.conversations = {"name": []}
    self.client = client

  def handle_message(self, message_object):
    # get conversation id form _conversation handler
    id = self.conversation_handler(message_object.channel.name)
    # with conversation id call docbot.generate_response(conversation_id, message) and return response
    return generate_response(id, message_object)

  def conversation_handler(self, conversation_name):
    # check if conversation in state
    id = None
    client = opensearch_connection_builder()
    if conversation_name in self.conversations['name']:
      # check if conversation exists. If it exists track conversation id in self.conversations by name: id
      id = self.conversations[conversation_name]
    else:
      # Check if it exists in OpenSearch
      search_query = {"query": {"match": {"name": conversation_name}}}
      try:
        result = self.client._client.search(index='cohere', body=search_query)
        data = result.json()
        hits = data.get('hits', {}).get('hits', [])
        id = hits[0]['id']
      except Exception as e:
        id = client.put_conversation({"name": conversation_name})

    #Then return the relevant ID
    if id == None:
      raise Exception("ID was not generated correctly")
    return id
