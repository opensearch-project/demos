import sys
from tkinter.filedialog import Open
from token import OP
from unittest import result
from opensearchpy import OpenSearch
sys.path.append('./demo/')

from docbot.language_pipeline import generate_response
from opensearchpy import OpenSearch

class DocBot():
  def __init__ (self, open_search:OpenSearch):
      self.conversations = {}
      self.OpenSearch = open_search

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
      result = self.OpenSearch.search(index='cohere', body=search_query)
      if result['hits']['total']['value'] > 0:
        data = result.json()
        hits = data.get('hits', {}).get('hits', [])
        id = hits[0]['id']
      else:
        id = len(self.conversations) + 1
        self.conversations[conversation_name] = id

    #Then return the relevant ID
    if id == None:
      raise Exception("ID was not generated correctly")
    return id
