# Notes


## Plan/wishlist/features

1. Pubmed file collection
1. Processing Pubmed files into ES load format
1. Mapping file for Pubmed ES
1. Load documents (remembering to delete docs as well)
1. Create docker-compose to run traefik, ES and pubmedprocessor.py
1. Create Cloudformation
1. configuration file
1. Alias indexes == pubmed <- pubmed19  or pubmed18
1. Capture history of files that have been processed to handle re-baselining - in sqlite
1. Figure out how to handle potential updates to baselining before loading new baseline - use baseline-2019-sample/pubmedsample.xml
1. Send note on 12/5 that new baseline is about to show up and check sample - even create a test to run against sample
1. Add config parameter for initiating new baseline (auto, false, true)

1. Dev/Test config - create local sample of files and use those for dev/test
1. Stats -> load these ES
1. Kibana Dashboard?

## Dev notes
1. Create a Makefile to build/run tests/publish docker container
1. Create a bumpversion config
1. Docs?
1. Logging?
1. Configuration
1. .env file?

https://pipenv.readthedocs.io/en/latest/


## Current Status

* script that reads update files from Pubmed and loads into ES
* baseline loading manually initiated
* tests?
* mapping file for ES?
