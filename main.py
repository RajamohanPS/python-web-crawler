import requests
import dns
import random 
import string
import threading
import time
from bs4 import BeautifulSoup
import pymongo
from datetime import datetime
from datetime import timedelta
import urllib
from validator_collection import checkers
from cfg import config

client = pymongo.MongoClient(config["mongo_srv"])
db = client.CrawlFileData
db.links.drop()
db.create_collection("links")
collection = db.links

#function to generate random string
def rand_string(length = 10):
  #change length as required or input
  letters = string.ascii_lowercase
  result_str = ''.join(random.choice(letters) for i in range(length))
  
  return (result_str)

#function to save .html file
def save_html(link,source):
  try:
    l = requests.get(link)
  except:
    return
  #soup = BeautifulSoup(l.text,'html.parser')
  #open file with rand string 
  #f_name = ('Crawl/'+ rand_string() + '.html')
  f_name = (rand_string() + '.html')
  f = open(f_name,"w")
  f.write(l.text)
  f.close()

  response = requests.get(link,stream = True)
  c_type = response.headers["Content-Type"]
  size = len(response.content)
  status = response.status_code


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

  collection.find_one({"link": link})
  if collection.find_one({"link": link}) == None:
    collection.insert_one(data)
    print(db.links.count_documents({}),link)
  

#function to crawl links and call save_html()
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
  
  c_file = to_crawl["file"]
  crawl_link = to_crawl["link"]
  s_l = to_crawl["source_link"]
  c_type = to_crawl["content_type"]
  c_stat = to_crawl["response_status"]
  c_size = to_crawl["size"]
  c_date = to_crawl["created_at"]

  collection.replace_one({"link": crawl_link},{
  "file": c_file,
  "link": crawl_link,
  "source_link": s_l,
  "content_type": c_type,
  "response_status": c_stat,
  "size": c_size,
  "created_at": c_date,
  "last_crawl_date": datetime.utcnow(),
  "is_crawled": True
  })

  r = requests.get(crawl_link)
  soup = BeautifulSoup(r.text,'html.parser')
  for link in soup.find_all('a'):
    links = link.get('href')
    links = urllib.parse.urljoin(root,links)
    if links[:-1]!="https://flinkhub.com/#faq-list-":
      if checkers.is_url(links):
        if collection.find_one({"link": links}) == None:
          save_html(links,crawl_link)


#threading
class myThread (threading.Thread):
   def __init__(self, threadID, name):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
   def run(self):  
      #threading.lock.acquire()
      print("Running" + self.name)
      crawl_html()
      #threading.lock.release()


#initial manual add of root link

root = config['root']
r = requests.get(root)
f_name = ('Crawl/'+rand_string()+'.html')
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

  f = open('Crawl/links.txt', "a")
  for link in soup.find_all('a'):
    links = link.get('href')
    links = urllib.parse.urljoin(root,links)
    if links[:-1]!="https://flinkhub.com/#faq-list-":
      if checkers.is_url(links):
          if collection.find_one({"link": links})  == None:
            save_html(links,root)
            f.write(links + '\n')
  
  
  f.close()
  thread1 = myThread(1, "Thread-1")
  thread2 = myThread(2, "Thread-2")
  thread3 = myThread(3, "Thread-3")
  thread4 = myThread(4, "Thread-4")
  thread5 = myThread(5, "Thread-5")

  thread1.start()
  thread2.start()
  thread3.start()
  thread4.start()
  thread5.start()

  while True:
    thread1.run()
    thread2.run()
    thread3.run()
    thread4.run()
    thread5.run()
    

    threads = []
    threads.append(thread1)
    threads.append(thread2)
    threads.append(thread3)
    threads.append(thread4)
    threads.append(thread5)
    for t in threads:
      t.join()
    print("Exiting Main Thread")
    if db.links.count_documents({})>=5000:
      print("Max limit reached")
      break
    
  print("Cycle done")
  time.sleep(5)


#add 5 sec rest