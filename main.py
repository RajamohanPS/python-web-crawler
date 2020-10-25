import requests
import dns
from concurrent import futures
import time
from bs4 import BeautifulSoup
import pymongo
from datetime import datetime
from datetime import timedelta
from cfg import config
from datab import rand_string
from utils import crawl_html
from utils import extract

client = pymongo.MongoClient(config["mongo_srv"])
db = client.CrawlFileData
db.links.drop()
db.create_collection("links")
collection = db.links

root = config['root']
r = requests.get(root)
f_name = ('Crawl/'+rand_string()+'.html')
#f_name = (rand_string()+'.html')
f = open(f_name,"w")
f.write(r.text)
f.close()
#soup = BeautifulSoup(r.text,'html.parser')

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
  "is_crawled": True,
  "cycle_no": 0
}) 

while True:
  days = timedelta(1)
  to_date = datetime.utcnow() - days 
  c_no = 0 #cycle number
  
  extract(root,c_no)

  while True:
    c_no+=1
    with futures.ThreadPoolExecutor(max_workers=5) as tpl:
      tpl.submit(crawl_html(c_no))
      tpl.submit(crawl_html(c_no))
      tpl.submit(crawl_html(c_no))
      tpl.submit(crawl_html(c_no))
      tpl.submit(crawl_html(c_no))
      
    if collection.find_one({"is_crawled": False, "cycle_no": c_no-1}) == None and collection.find_one({"last_crawl_date": {"$lt": to_date}}) == None:
      print("All crawled")
      break
    if db.links.count_documents({})>=5000:
      print("Max limit reached")
      break
    
  print("Cycle done")
  time.sleep(5)


#add 5 sec rest