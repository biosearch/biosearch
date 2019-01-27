import os
import yaml
import sys


conf_dir = os.getenv("CONF_DIR", "/conf")

with open(f"{conf_dir}/biosearch.yml", "r") as f:
    config = yaml.load(f)

if not config:
    sys.exit(f"Could not load configuration file: {conf_dir}/biosearch.yml")
