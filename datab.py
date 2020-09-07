import requests
import pymongo
from datetime import datetime 
from cfg import config
from utils import rand_string

client = pymongo.MongoClient(config["mongo_srv"])
db = client.CrawlFileData
collection = db.links

def save_html(link,source):
  try:
    l = requests.get(link)
  except:
    return

  response = requests.get(link,stream = True)
  c_type = response.headers["Content-Type"]
  size = len(response.content)
  status = response.status_code


  #f_name = ('Crawl/'+ rand_string() + '.html')
  if int(status) == 200:
    f_name = (rand_string() + '.html')
    f = open(f_name,"w")
    f.write(l.text)
    f.close()


  data = {
    "file": f_name,
    "link": link,
    "source_link": source,
    "content_type": c_type,
    "response_status": status,
    "size": size,
    "created_at": datetime.utcnow(),
    "last_crawl_date": 0,
    "is_crawled": False
  }
  
  if collection.find_one({"link": link}) == None:
    collection.insert_one(data)
    print(db.links.count_documents({}),link)