import sys
sys.path.append('./demo/')

from docbot.util import opensearch_connection_builder

def test_opensearch_connection():
  connection = opensearch_connection_builder()
  health = connection.cat.health()
  assert isinstance(health, str)
