import dotenv
from os import getenv
from opensearchpy import OpenSearch
from opensearch_py_ml.ml_commons import MLCommonClient

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
