import os, json, sys
sys.path.append('./demo/')

from docbot.util import opensearch_connection_builder

# Using a connection from the OpenSearch connection builder
# to see an example of using the opensearch connection builder
# check out tests/test_util.py

# We need to ingest documents into OpenSearch from our project website.
# check out the _bulk python client helper.

# Documents should be ingested from the /data/ dir
DATA_PATH = os.path.abspath(os.path.join(__file__,  "..", "..","..","data"))

def read_files_from_data() -> list:
  """
  Args:
    None
  Returns:
    list: a single list of all json file data extracted from the data folder.
  """
  result = []
  all_json = [f for f in os.listdir(DATA_PATH) if f.endswith('.json')]

  if not all_json:
    raise FileNotFoundError("Cannot find JSON files in /demos/data")

  for file in all_json:
      path = os.path.join(DATA_PATH, file)
      with open(path) as f:
        if result:
          result.extend(json.load(f))
        else:
          result = json.load(f)

  return result

if __name__=="__main__":
  # do ingestions
  data_list = read_files_from_data()
