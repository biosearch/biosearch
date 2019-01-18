from biosearch.Config import config


def test_config_no_envs():
    """No environments set for config"""

    assert config['host_name'] == 'biosearch.test'
    assert config['db_fn'] == '/db/biosearch.sqlite'
