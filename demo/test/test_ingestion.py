import sys, json
sys.path.append('./demo/')
from docbot.ingestion import *

def test_read_files_from_data():
  result = read_files_from_data()

  #test result has values
  assert(len(result) > 0)

  #test the result is a list
  assert(isinstance(result, list))

  #test result is a list of serializable json
  for string in result:
    assert(isinstance(json.dumps(string), str))
