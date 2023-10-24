import dotenv
from os import getenv
from opensearchpy import OpenSearch
from opensearch_py_ml.ml_commons import MLCommonClient
from copy import deepcopy

dotenv.load_dotenv()
ADMIN_PW = getenv('ADMIN_PW')
ADMIN_UN = getenv('ADMIN_UN')
HOSTS = getenv('HOSTS')
DEVELOPMENT= getenv('DEVELOPMENT')

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
    client = MLCommonClient(
      OpenSearch(**config)
    )
  else:
    client = OpenSearch(**config)

  return client

def shorten_json_file_same_index(json_file, num_words=150, overlap=0.3) -> list:
  """
  Args:
    json_file: a json index with OpenSearch document to be ingested
    num_words: content length of each sub-document
    overlap: The percentage amount of overlap in breaking the documents
  Returns:
    A list of dict with same metadata but content is a chunk of sub-document if successful, raise exception if failed
  """
  if not isinstance(json_file, dict) or 'content' not in json_file:
    raise ValueError("Inappropriate Argument json_file must be a valid dict of OpenSearch json index")

  if num_words <= 0:
    raise ValueError("Inappropriate Argument: num_words must be positive")

  if overlap <= 0 or overlap >= 1:
    raise ValueError("Inappropriate Argument: overlap must be within 0 and 1")

  # We assume the average word is 5 characters long, this is surprisingly accurate from my testing on the data!
  char_per_word = 5
  sentence_to_split = json_file['content']
  temp = None
  result = []

  while len(sentence_to_split) > (num_words * char_per_word):
    overlapped_bound = int(num_words-(num_words*overlap))
    temp = deepcopy(json_file)
    temp['content'] = sentence_to_split[:num_words*char_per_word]
    result.append(temp)
    sentence_to_split = sentence_to_split[overlapped_bound*char_per_word:]

  temp = deepcopy(json_file)
  temp['content'] = sentence_to_split
  result.append(temp)

  return result
