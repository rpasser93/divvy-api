from dotenv import load_dotenv, find_dotenv
import os
import pprint
import certifi
from pymongo import MongoClient
from bson.json_util import dumps
from json import loads
from bson.objectid import ObjectId

def parse_json(data):
 return loads(dumps(data, default=str))

printer = pprint.PrettyPrinter()

load_dotenv(find_dotenv())
password = os.environ.get('MONGODB_PWD')
connection_string = f'mongodb+srv://rpasser93:{password}@divvy-cluster.zffibkx.mongodb.net/?retryWrites=true&w=majority'

client = MongoClient(connection_string, tlsCAFile=certifi.where())
divvy_db = client.divvy_db
users_collection = divvy_db.users
expenses_collection = divvy_db.expenses

def create_new_user(login: str, password: str):
  new_user = {
    'login': login,
    'password': password,
    'first_name': None,
    'last_name': None,
  }
  users_collection.insert_one(new_user)
  return parse_json(new_user)

def get_all_users():
  users = users_collection.find({})
  all_users_dict = {
    'users': parse_json(users)
  }
  return all_users_dict

def get_user_by_id(id: str):
  user = users_collection.find({'_id': ObjectId(id)})
  return parse_json(user)

def get_user_by_login(login: str):
  user = users_collection.find({'login': login})
  return parse_json(user)

def update_user(id: str, values_to_update: dict):
  new_values = {
    '$set': values_to_update
  }
  user_query = {'_id': ObjectId(id)}
  users_collection.update_one(user_query, new_values)
  user = users_collection.find(user_query)
  return parse_json(user)

def delete_user(id: str):
  user = users_collection.find({'_id': ObjectId(id)})
  user_json = parse_json(user)
  users_collection.delete_one({'_id': ObjectId(id)})
  return user_json