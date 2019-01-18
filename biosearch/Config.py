import os

config = {}

config['es_mappings'] = os.getenv('ES_MAPPINGS', '/conf/es_mappings.yml')
config['conf_dir'] = os.getenv('CONF_DIR', '/conf')
config['host_name'] = os.getenv('HOST_NAME', '')
config['db_fn'] = os.getenv('DB_FN', '/db/biosearch.sqlite')
