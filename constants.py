from dotenv import load_dotenv, find_dotenv
import os
import certifi
from pymongo import MongoClient

load_dotenv(find_dotenv())
username = os.environ.get('MONGODB_USERNAME')
password = os.environ.get('MONGODB_PASSWORD')
connection_string = f'mongodb+srv://{username}:{password}@divvy-cluster.zffibkx.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(connection_string, tlsCAFile=certifi.where())

divvy_db = client.divvy_db
users_collection = divvy_db.users
expenses_collection = divvy_db.expenses