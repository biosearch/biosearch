# coding: utf-8
"""
Test conversion on real PubMed xml file

"""

import os
import sys
from collections import defaultdict
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
    bad_recs = list()
    idx_file += 1
    idx_record = 0
    pubyears = defaultdict(int)
    pubmonths = defaultdict(int)
    n_pmc = 0
    n_refs = 0
    for record in convert.xml_to_json(xml_file):
        idx_record += 1

        if len(record["pmc"]) > 0:
            n_pmc += 1
        if len(record["references"]) > 0:
            n_refs += 1
        pubyears[record["journal_pubyear"]] += 1
        pubmonths[record["journal_pubmonth"]] += 1
        if record["journal_pubyear"] == "YYYY":
            bad_recs.append(record["pmid"])
        print("%d.%d. PMID %s: %s" % (idx_file, idx_record, record["pmid"], record["title"]))

    print("")
    print("... docs:", idx_record)
    print("... PMC:", n_pmc)
    print("... refs:", n_refs)
    print("... pubyears:", pubyears)
    print("... pubmonths:", pubmonths)
    print("... bad records:", ", ".join(bad_recs))
#
