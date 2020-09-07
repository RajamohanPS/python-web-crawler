import requests
import dns
from concurrent import futures
import time
from bs4 import BeautifulSoup
import pymongo
from datetime import datetime
import urllib
from cfg import config
from datab import save_html
from utils import rand_string
from utils import crawl_html

client = pymongo.MongoClient(config["mongo_srv"])
db = client.CrawlFileData
db.links.drop()
db.create_collection("links")
collection = db.links

root = config['root']
r = requests.get(root)
#f_name = ('Crawl/'+rand_string()+'.html')
f_name = (rand_string()+'.html')
f = open(f_name,"w")
f.write(r.text)
f.close()
soup = BeautifulSoup(r.text,'html.parser')

response = requests.get(root,stream = True)
c_type = response.headers["Content-Type"]
size = len(response.content)
status = response.status_code

collection.insert_one({ 
  "file": f_name,
  "link": root,
  "source_link": root,
  "content_type": c_type,
  "response_status": status,
  "size": size,
  "created_at": datetime.utcnow(),
  "last_crawl_date": datetime.utcnow(),
  "is_crawled": True
}) 

while True:

  #f = open('links.txt', "a")
  for link in soup.find_all('a'):
    links = link.get('href')
    links = urllib.parse.urljoin(root,links)
    link_parse = urllib.parse.urlparse(links)
    if link_parse.netloc and link_parse.scheme and (not link_parse.fragment):
      if collection.find_one({"link": links})  == None:
        save_html(links,root)
        #f.write(links + '\n')
  
   
  #f.close()


  while True:
    with futures.ThreadPoolExecutor(max_workers=5) as tpl:
      tpl.submit(crawl_html)
      tpl.submit(crawl_html)
      tpl.submit(crawl_html)
      tpl.submit(crawl_html)
      tpl.submit(crawl_html)
    if db.links.count_documents({})>=5000:
      print("Max limit reached")
      break
    
  print("Cycle done")
  time.sleep(5)


#add 5 sec rest