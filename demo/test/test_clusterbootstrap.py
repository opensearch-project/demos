import sys
sys.path.append('./demo/')

from docbot.util import opensearch_connection_builder
from docbot.cluster_bootstrap import init_index_template
import pytest

def test_init_index_template():
    client = opensearch_connection_builder()
    try:
        init_index_template(client= client, template_name="testing-template")
        template = client.indices.get_template(name="testing-template")
        assert template != None
    except Exception as e:
        pytest.fail(str(e))
