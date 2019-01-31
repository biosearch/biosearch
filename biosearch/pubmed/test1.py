# coding: utf-8
"""
Test conversion on real PubMed xml file

"""

import os
import sys

from collect import Downloader
import convert


D = Downloader()
filter = [970, 1001]
for fpath in D.file_list:
    fname = os.path.basename(fpath)
    this_file_number = int(fname[9:13])
    # print(this_file_number)
    if filter and not filter[0] <= this_file_number <= filter[1]:
        continue

    print(fpath)

print("-" * 40)
idx_file = 0
for xml_file in D.xml_file_generator([974, 974]):
    # print(xml_file[:1000])
    idx_file += 1
    idx_record = 0
    for record in convert.xml_to_json(xml_file):
        idx_record += 1

        print("%d.%d. PMID %s: %s" % (idx_file, idx_record, record["pmid"], record["title"]))

#
