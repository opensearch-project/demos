import sys
from opensearchpy import OpenSearch
sys.path.append('./demo/')

from docbot.language_pipeline import generate_response

class DocBot():
  def __init__ (self):
      self.conversations = {}

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
      # if conversation doesn't exists create and then track using the above method
      id = len(self.conversations) + 1
      self.conversations[conversation_name] = id

    #Then return the relevant ID
    if id == None:
      raise Exception("ID was not generated correctly")
    return id
