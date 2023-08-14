from fastapi import FastAPI, Request, Depends, HTTPException
from functools import wraps, lru_cache
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import InsertOne
import openai
import uvicorn
from dotenv import load_dotenv
import urllib.robotparser as urp
from fastapi.middleware.cors import CORSMiddleware
import config
from .api_utils import *
import requests as req
from datetime import datetime as dt

#Load environment variables
load_dotenv()

#Load OpenAI key
openai.api_key = config.OPENAI_KEY

#Load app
app = FastAPI()

#CORS setup (cross-origin thingies)
origins = [
    "http://localhost:8000",
    "*",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Cache the MongoDB client connection
@lru_cache()
def get_db_client():
  #Connect to mongodb client
  return MongoClient(config.MONGO_URI)

@lru_cache()
def get_req_session():
  return req.Session()

@lru_cache()
def get_url_parser():
  return urp.RobotFileParser()

#Need an auth wrapper!
def auth_required_async(func):
  @wraps(func)
  async def wrapper(*args, **kwargs):
    #TODO: do stuff here (ie. check header for auth, but we should do this wayyyy later...)

    #We need our generated token string as the auth :)
    #Optimally we have some assert statement here...
    print(kwargs['request'].headers)

    return await func(*args, **kwargs)
  return wrapper

def auth_required_sync(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    #TODO: do stuff here (ie. check header for auth, but we should do this wayyyy later...)

    #We need our generated token string as the auth :)
    #Optimally we have some assert statement here...
    print(kwargs['request'].headers)

    return func(*args, **kwargs)
  return wrapper

#Dummy HTTP request sample
@app.get('/')
@auth_required_async
async def root(request: Request):
  #return {'example': 'This is an example', 'data': config.FRONTEND_PW}
  return {'example': 'This is an example', 'data': 'fooled you'}

#
#DB requests start here :)
#

#Check MongoDB connection
@app.get('/checkdb')
@auth_required_async
async def check_db(request: Request, client: MongoClient = Depends(get_db_client)):
  retVal = client.admin.command('ping')
  print("Pinged your deployment. You successfully connected to MongoDB!")
  return retVal

#Dummy function for scheduled RSS master collection reset
#TODO: Turn this into a DAG, deploy a Docker container
@app.get('/data_scheduled')
@auth_required_sync
def dummy_scheduled_job(request: Request, client: MongoClient = Depends(get_db_client), req_session = Depends(get_req_session)):
  #If we finish, we can return True
  #Else, we can return False

  #Collect and parse all RSS feeds, put in master collection for posts

  #Grab the master RSS post collection, put into each individual collection
  bulk_list=[]
  #TODO: Check OpenAI API status
  #We need minimal downtime, and if down we wait

  try:
    user_coll = client['data']['rss_feeds']
    posts_coll = client['data']['posts']
    all_feeds = user_coll.find({})
    #Get all feeds
    for f in all_feeds:
      feed_url=f['_id']
      articles = get_articles(feed_url, req_session)
      #Get all articles in 1 feed
      for a in articles:
        title = a.find('title').text
        link = a.find('link').text
        published = a.find('pubDate').text
        description = a.find('description').text
        #TODO: Get fulltext of each article
        fulltext = get_fulltext(link, req_session)
        embedding=None
        #Try to get embedding
        try:
          embedding = openai.Embedding.create(input=fulltext, model="text-embedding-ada-002")['data'][0]['embedding']
        except:
          pass

        #TODO: Bulk add articles to MongoDB
        bulk_list.append(InsertOne({
          '_id': title,
          'link': link,
          'published': published,
          'description': description,
          'fulltext': fulltext,
          'embedding': embedding
        }))
      #It's a good idea to place a breakpoint here for debugging
  except BaseException as inst:
    print("Oh no, /data_scheduled JOB FAILED.")
  return True

#TODO: Embed Missing Embeddings
@app.get('/label_scheduled')
@auth_required_sync
def embedding_labels(request: Request, client: MongoClient = Depends(get_db_client)):
  #Label each post in DB
  posts_coll = client['data']['posts']


  return