from util import opensearch_connection_builder
import os, json

# Using a connection from the OpenSearch connection builder
# to see an example of using the opensearch connection builder
# check out tests/test_util.py

# We need to ingest documents into OpenSearch from our project website.
# check out the _bulk python client helper.

# Documents should be ingested from the /data/ dir
DEMOS_PATH = os.path.abspath(os.path.join(__file__,  "..", "..",".."))
DOCUMENTATION_INDEX_PATH = "data/documentation-index.json"
WEBSITE_INDEX_PATH = "data/website-index.json"

def read_files_from_data() -> (list, list):
  documentation_index = os.path.join(DEMOS_PATH, DOCUMENTATION_INDEX_PATH)
  website_index = os.path.join(DEMOS_PATH, WEBSITE_INDEX_PATH)
  with open(documentation_index) as f:
    documentation_index_data = json.load(f)
  with open(website_index) as f:
    website_index_data = json.load(f)

  return documentation_index_data, website_index_data

if __name__=="__main__":
  # do ingestion
  documentation_index_data, website_index_data = read_files_from_data()
