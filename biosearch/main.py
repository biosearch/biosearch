#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Usage:  main.py

    Main program to orchestrate collecting, converting and loading
    content into Elasticsearch

"""
from biosearch.Config import config
import biosearch.pubmed.load


def main():
    biosearch.pubmed.load.start()


if __name__ == "__main__":
    main()
