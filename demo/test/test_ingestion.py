import sys, pytest, random

sys.path.append('./demo/')

from docbot.ingestion import *
from docbot.util import opensearch_connection_builder


def test_read_files_from_data():
  #Test normal data
  data_list = read_files_from_data()

  assert (isinstance(data_list, list))
  assert (len(data_list) > 0)
  assert (isinstance(data_list[0], dict))

  #Test a non-valid directory
  with pytest.raises(NotADirectoryError):
    read_files_from_data("!>!>!>")

  #test an empty directory
  fake_folder = os.path.join(os.getcwd(), "TESTINGBLANKFOLDER")
  os.mkdir(fake_folder)
  with pytest.raises(FileNotFoundError):
    read_files_from_data(fake_folder)
  os.rmdir(fake_folder)


def test_ingest_to_opensearch():
  client = opensearch_connection_builder()

  ##test correct ingestion
  test_documents = []
  for i in range(random.randint(1, 100)):
    test_documents.append({"id": i, "content": f"Document {i}"})
  ingest_to_opensearch(client, test_documents)
  for doc in test_documents:
    assert (client._client.exists(index="docbot", id=doc["id"]))
    assert (client._client.get(index="docbot",
                               id=doc["id"])["_source"]['content'] == doc["content"])

  ##test incorrect ingestion
  with pytest.raises(ValueError):
    ingest_to_opensearch(client, [])
