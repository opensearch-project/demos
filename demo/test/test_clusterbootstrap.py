import sys

sys.path.append('./demo/')

from docbot.util import opensearch_connection_builder
from docbot.cluster_bootstrap import ClusterBootstrap
import pytest


def test_init_index_template():
  client = opensearch_connection_builder()
  bootstrap = ClusterBootstrap()
  try:
    bootstrap._init_index_template(template_name="testing-template")
    template = client._client.indices.get_template(name="testing-template")
    assert template != None
  except Exception as e:
    pytest.fail(str(e))
