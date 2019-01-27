#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Usage:  main.py

    Main program to orchestrate collecting, converting and loading
    content into Elasticsearch

"""
import time
import schedule

import biosearch.pubmed.load
from biosearch.Config import config


def main():

    schedule.every().day.at("22:45").do(biosearch.pubmed.load.start())

    while True:
        schedule.run_pending()


if __name__ == "__main__":
    main()
