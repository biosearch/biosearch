# coding: utf-8
"""
Content collection module.

"""

import ftputil
import gzip
import os
import sys
from io import BytesIO
import urllib.request


class Downloader:
    """
    """

    # Location of PubMed files
    repo = {"baseline": "/pubmed/baseline/", "updates": "/pubmed/updatefiles/"}

    def __init__(self, repository=None):
        """
        Args:
            repository (str) - [optional] type of PubMed XML files to process:
                'baseline' or 'updates'
        """
        if repository and repository in self.repo.keys():
            self.sources = [repository]
        else:
            self.sources = list(self.repo.keys())
        print(self.sources)
        # connect to FTP server
        self.file_list = list()
        with ftputil.FTPHost("ftp.ncbi.nlm.nih.gov", "anonymous", "") as ftp_host:
            ftp_host.use_list_a_option = False
            # get list of files in repository
            for src in self.sources:
                ftp_host.chdir(self.repo[src])
                for fn in ftp_host.listdir(ftp_host.curdir):
                    if fn.endswith("xml.gz"):
                        self.file_list.append(src + "/" + fn)

    def xml_file_generator(self, filter=None):
        """
        Args:
            filter (list) - optional file number range [start, stop];
                e.g., [0, 100] or [1, 100] - use first 100 files,
                      [10, 99] - use file number 10 to 99,
                      [100, 0] - use file number >= 100;
                if None, all files used
        """
        filter[0] = max(1, filter[0])

        for fpath in self.file_list:

            # file number
            fname = os.path.basename(fpath)
            # print(">>>", fpath, "::", fname)
            this_file_number = int(fname[9:13])
            if filter and not filter[0] <= this_file_number <= filter[1]:
                continue

            url = "ftp://ftp.ncbi.nlm.nih.gov/pubmed/%s" % (fpath)
            # print(url)
            mysock = urllib.request.urlopen(url)
            memfile = BytesIO(mysock.read())
            yield gzip.GzipFile(fileobj=memfile).read().decode("utf-8")


if __name__ == "__main__":
    # Run some tests
    D = Downloader()
    filter = [970, 1001]
    for fpath in D.file_list:
        fname = os.path.basename(fpath)
        this_file_number = int(fname[9:13])
        # print(this_file_number)
        if filter and not filter[0] <= this_file_number <= filter[1]:
            continue

        print(fpath)

    for xml_file in D.xml_file_generator([972, 972]):
        print(xml_file[:1000])
