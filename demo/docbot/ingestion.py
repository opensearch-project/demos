import os, json, sys
# import cluster_bootstrap

sys.path.append('./demo/')

from docbot.util import opensearch_connection_builder, shorten_json_file_same_index

# Using a connection from the OpenSearch connection builder
# to see an example of using the opensearch connection builder
# check out tests/test_util.py

# We need to ingest documents into OpenSearch from our project website.
# check out the _bulk python client helper.

# Documents should be ingested from the /data/ dir
DATA_PATH = os.path.abspath(os.path.join(__file__, "..", "..", "..", "data"))


def read_files_from_data(PATH=DATA_PATH) -> list:
  """
  Args:
    PATH: a string of file path to the data folder
  Returns:
    list: a single list of all json file data extracted from the data folder.
  """
  result = []

  try:
    all_json = [f for f in os.listdir(PATH) if f.endswith('.json')]
  except:
    raise NotADirectoryError("Failed to load directory: " + PATH)

  if not all_json:
    raise FileNotFoundError("Failed to find JSON files in /demos/data")

  for file in all_json:
    path = os.path.join(PATH, file)
    with open(path) as f:
      for json_file in json.load(f):
        shortened_json_files = shorten_json_file_same_index(json_file)
        result.extend(shortened_json_files)

  return result


def ingest_to_opensearch(client, data) -> int:
  """
  Args:
    data: a list of json documents to be ingested
  Returns:
    None if successful, raise exception if failed
  """
  docs = []
  for point in range(len(data)):
    docs.append({"index": {"_index": "docbot", "_id": point}})
    docs.append(json.dumps(data[point]))

  response = client._client.bulk(docs)
  if response["errors"]:
    raise ValueError("Failed to insert data into client.")
  else:
    print(f"Bulk-inserted {len(response['items'])} items.")


if __name__ == "__main__":
  # do ingestions
  try:
    client = opensearch_connection_builder()
    data_list = read_files_from_data()
    ingest_to_opensearch(client, data_list)
  except Exception as e:
    print(f"An exception occured without finishing ingestion: {e}")
