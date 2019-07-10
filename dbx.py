url = "https://www.dropbox.com/sh/jag9uw5tkg3sj0e/AACsQzr3bcXLORygsvQuX-QLa?dl=0"  # dl=1 is important
url2="https://s3.amazonaws.com/ais-django/Events/Admin+Project/DSC_0198.jpg"
import urllib2
import shutil
import requests
from pprint import pprint
response = urllib2.urlopen(url)
from bs4 import BeautifulSoup
data = response.read()
soup=BeautifulSoup(data,'lxml')
print (soup.find('a'))

# for link in soup.find_all('class="sl-grid-cell"'):
#     print(link.get('href'))

# print (soup.prettify())
#
# # Write data to file
# filename = "test.jpg"
# file_ = open(filename, 'w')
# file_.write(data)
# file_.close()

# url = 'http://example.com/img.png'
# response = requests.get(url2, stream=True)
# with open('img.png', 'wb') as out_file:
#     shutil.copyfileobj(response.raw, out_file)
# del response