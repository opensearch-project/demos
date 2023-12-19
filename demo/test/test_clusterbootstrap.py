import sys
sys.path.append('./demo/')

from docbot.util import opensearch_connection_builder
from docbot.cluster_bootstrap import ClusterBootstrap
import pytest

def test_inititialize_index():
    return
    client = opensearch_connection_builder()
    try:
        _initialize_index(client= client, template_name="testing-template")
        template = client.indices.get_template(name="testing-template")
        assert template != None
    except Exception as e:
        pytest.fail(str(e))
