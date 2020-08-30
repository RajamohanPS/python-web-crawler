import requests
import pymongo
from datetime import datetime
from datetime import timedelta
from bs4 import BeautifulSoup
import urllib
from cfg import config
from utils import save_html



client = pymongo.MongoClient(config["mongo_srv"])
db = client.CrawlFileData
collection = db.links
root = config["root"]



def crawl_html():
  days = timedelta(1)
  to_date = datetime.utcnow() - days 
  if collection.find_one({"is_crawled": False}) == None:
    if collection.find_one({"last_crawl_date": {"$lt": to_date}}) == None:
      print("All links crawled")
    else:
      to_crawl = collection.find_one({"last_crawl_date": {"$lt": to_date}})
  else:
    to_crawl = collection.find_one({"is_crawled": False})
  
  if int(to_crawl["response_status"]) == 200:
    crawl_link = to_crawl["link"]
    to_crawl["last_crawl_date"] = datetime.utcnow()
    to_crawl["is_crawled"] = True

    collection.replace_one({"link": crawl_link},to_crawl)

    r = requests.get(crawl_link)
    soup = BeautifulSoup(r.text,'html.parser')
    for link in soup.find_all('a'):
      links = link.get('href')
      links = urllib.parse.urljoin(root,links)
      link_parse = urllib.parse.urlparse(links)
      if link_parse.netloc and link_parse.scheme and (not link_parse.fragment):
        if collection.find_one({"link": links}) == None:
          save_html(links,crawl_link)
