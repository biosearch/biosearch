# coding: utf-8
"""
Content collection module.

"""
import argparse
import ftputil
import gzip
from io import BytesIO
import urllib.request

class Downloader:
    """
    """

    # Location of PubMed files
    repo = {
        'baseline': '/pubmed/baseline/',
        'updates': '/pubmed/updatefiles/'
    }

    def __init__(self, repository):
        """
        Args:
            repository (str) - type of PubMed XML files to process:
                'baseline' or 'updates'
        """
        self.src = self.repo[repository]
        # connect to FTP server
        with ftputil.FTPHost('ftp.ncbi.nlm.nih.gov', 'anonymous', '') as ftp_host:
            # get list of files in repository
            ftp_host.use_list_a_option = False
            ftp_host.chdir(self.src)
            self.file_list = [fn for fn in ftp_host.listdir(ftp_host.curdir)
                if fn.endswith('xml.gz')]


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

        for fname in self.file_list:

            # file number
            this_file_number = int(fname[9:13])
            if filter and not filter[0] <= this_file_number <= filter[1]:
                continue

            url = 'ftp://ftp.ncbi.nlm.nih.gov/%s/%s' % (self.src, fname)
            mysock = urllib.request.urlopen(url)
            memfile = BytesIO(mysock.read())
            yield gzip.GzipFile(fileobj=memfile).read().decode('utf-8')



##----------------------------------------------------------------------------##

if __name__ == "__main__":
    # Run some tests
    D = Downloader('baseline')
    filter = [960,970]
    for fname in D.file_list:
        this_file_number = int(fname[9:13])
        #print(this_file_number)
        if filter and not filter[0] <= this_file_number <= filter[1]:
            continue

        print(fname)

    for xml_file in D.xml_file_generator([972,972]):
        print(xml_file[:1000])

##----------------------------------------------------------------------------##
