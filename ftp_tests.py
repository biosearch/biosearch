
import gzip

from ftplib import FTP
from io import StringIO

ftp = FTP('ftp.ncbi.nlm.nih.gov')
ftp.login()
r = StringIO()
ftp.retrbinary('RETR /pub/README_ABOUT_BZ2_FILES', r.write)

print r.getvalue()



#ftp://ftp.ncbi.nlm.nih.gov/pubmed/id_list.txt.gz


import ftputil
host = ftputil.FTPHost('ftp.ncbi.nlm.nih.gov', 'anonymous', '')
host.chdir('/pubmed/sample-2019-01-01/')
file_list = host.listdir(host.curdir)
#['example.xml', 'reflist.example.xml']

def read_file(fname):
    with host.open(fname) as input_file:
        for line in input_file:
            yield line

for line in read_file("example.xml"):
    print(line)

def read_gz_file(fname):
    with host.open(fname, mode="rb") as input_file:
        return gzip.GzipFile(fileobj=input_file)

host.chdir('/pubmed/')
i = 0
compressed_xml = read_gz_file("id_list.txt.gz")

for line in gzip.decompress(compressed_xml):
    i += 1
    print(i, line)
    if i > 10:
        break

print(i)

##----------------------------------------------------------------------------##

from ftplib import FTP
import gzip
from io import StringIO

ftp = FTP('ftp.ncbi.nlm.nih.gov')
ftp.login() # Username: anonymous password: anonymous@

sio = StringIO()
def handle_binary(more_data):
    sio.write(more_data)

resp = ftp.retrbinary("RETR pub/pmc/PMC-ids.csv.gz", callback=handle_binary)
sio.seek(0) # Go back to the start
zippy = gzip.GzipFile(fileobj=sio)

uncompressed = zippy.read()
print(uncompressed[:1000])


import urllib
from io import BytesIO
import urllib.request

url = 'ftp://ftp.ncbi.nlm.nih.gov/pubmed/id_list.txt.gz'

resp = urllib.request.urlopen(url)
memfile = BytesIO(resp.read())

with gzip.GzipFile(memfile, 'r') as myzip:
    f = myzip.open('eggs.txt')
    content = f.read()  // or other file-like commands





zippy = gzip.GzipFile(fileobj=memfile)
uncompressed = zippy.read()


respData = resp.read()

#### !!!!
mysock = urllib.request.urlopen(url)
memfile = BytesIO(mysock.read())
f = gzip.GzipFile(fileobj=memfile)
r = f.read()
t = r.decode('utf-8')

###

import gzip
from io import BytesIO
import shutil
from ftplib import FTP

ftp = FTP('ftp.ncbi.nlm.nih.gov')
ftp.login('anonymous', '')

flo = BytesIO()

ftp.retrbinary('RETR /pubmed/id_list.txt.gz', flo.write)

flo.seek(0)

with open('archive.tar', 'wb') as fout, gzip.GzipFile(fileobj = flo) as gzip:
    shutil.copyfileobj(gzip, fout)

with gzip.GzipFile(fileobj = flo) as gzip:
    x = gzip.read()

gzipfile = gzip.GzipFile(mode='rb', fileobj=flo).read()
text = gzipfile.read()

buf = BytesIO(response.read())
f = gzip.GzipFile(fileobj=buf)
r = f.read()

###



import urllib
import io
from zipfile import ZipFile



mysock = urllib.urlopen('ftp://ftp.yourhost.com/spam.zip')  # check urllib for parameters
memfile = io.BytesIO(mysock.read())
with ZipFile(memfile, 'r') as myzip:
    f = myzip.open('eggs.txt')
    content = f.read()  // or other file-like commands
