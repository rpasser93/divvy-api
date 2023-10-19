from bson.objectid import ObjectId
from database.constants.db_constants import users_collection, expenses_collection
from database.constants.status_enums import Status
from database.constants.access_enums import Access
from database.helpers.parse_json import parse_json
from flask import abort, Response

def login(login: str, password: str):
  registered_user = users_collection.find({'login': login, 'password': password})
  parsed_registered_user = parse_json(registered_user)
  if len(parsed_registered_user) == 0:
    return abort(Response('Invalid login name or password.', 400))
  
  return f'User {login} logged in.'
  

def create_new_user(login: str, password: str):

  login_already_exists = len(get_user_by_login(login)) != 0
  if login_already_exists:
    return abort(Response('That login name already exists.', 400))
  
  new_user = {
    'login': login,
    'password': password,
    'first_name': None,
    'last_name': None,
    'expenses': []
  }
  users_collection.insert_one(new_user)
  parsed_user = parse_json(new_user)
  del parsed_user['password']
  return parsed_user

def get_all_users():
  users = users_collection.find({})
  all_users_dict = {
    'users': parse_json(users)
  }
  for user in all_users_dict['users']:
    print(user)
    if 'password' in user:
      del user['password']

  return all_users_dict

def get_user_by_id(id: str):
  user = users_collection.find({'_id': ObjectId(id)})
  parsed_user = parse_json(user)
  if len(parsed_user) == 0:
    return abort(Response('User with that id does not exist.', 404))
  del parsed_user[0]['password']
  return parsed_user[0]

def get_user_by_login(login: str):
  user = users_collection.find({'login': login})
  parsed_user = parse_json(user)
  return parsed_user

def update_user(id: str, values_to_update: dict):
  new_values = {
    '$set': values_to_update
  }
  user_query = {'_id': ObjectId(id)}
  user = users_collection.find(user_query)
  parsed_user = parse_json(user)

  if len(parsed_user) == 0:
    return abort(Response('User with that id does not exist.', 404))
  
  users_collection.update_one(user_query, new_values)
  updated_user = parse_json(users_collection.find(user_query))
  del updated_user[0]['password']
  return updated_user[0]

def delete_user(id: str):
  user = users_collection.find({'_id': ObjectId(id)})
  parsed_user = parse_json(user)

  if len(parsed_user) == 0:
    return abort(Response('User with that id does not exist.', 404))
  
  users_collection.delete_one({'_id': ObjectId(id)})
  del parsed_user[0]['password']
  return parsed_user[0]

def add_expense_for_user(user_id: str, expense_id: str, access_level: Access, status: Status):
  user_query = {'_id': ObjectId(user_id)}
  expense_query = {'_id': ObjectId(expense_id)}

  user = users_collection.find(user_query)
  expense = expenses_collection.find(expense_query)

  parsed_user = parse_json(user)
  parsed_expense = parse_json(expense)

  if len(parsed_user) == 0:
    return abort(Response('User with that id does not exist.', 404))
  
  if len(parsed_expense) == 0:
    return abort(Response('Expense with that id does not exist.', 404))
  
  duplicate_expenses = parse_json(users_collection.find({'_id': ObjectId(user_id), 'expenses.id': expense_id}))
  if len(duplicate_expenses) != 0:
    return abort(Response('Expense has already been added for that user.', 400))
  
  new_expense = {
    'id': expense_id,
    'access_level': access_level,
    'status': status
  }
  users_collection.update_one(user_query, {'$push': {'expenses': new_expense}})
  updated_user = users_collection.find(user_query)
  parsed_updated_user = parse_json(updated_user)
  del parsed_updated_user[0]['password']
  return parsed_updated_user[0]

def update_expense_access_for_user(user_id: str, expense_id: str, access_level: Access):
  user_query = {'_id': ObjectId(user_id)}
  expense_query = {'_id': ObjectId(expense_id)}

  user = users_collection.find(user_query)
  expense = expenses_collection.find(expense_query)

  parsed_user = parse_json(user)
  parsed_expense = parse_json(expense)

  if len(parsed_user) == 0:
    return abort(Response('User with that id does not exist.', 404))
  
  if len(parsed_expense) == 0:
    return abort(Response('Expense with that id does not exist.', 404))
  
  users_collection.update_one({'_id': ObjectId(user_id), 'expenses.id': expense_id}, {'$set': {'expenses.$.access_level': access_level}})
  updated_user = parse_json(users_collection.find(user_query))
  parsed_updated_user = parse_json(updated_user)
  del parsed_updated_user[0]['password']
  return parsed_updated_user[0]

def delete_expense_for_user(user_id: str, expense_id: str):
  user_query = {'_id': ObjectId(user_id)}
  expense_query = {'_id': ObjectId(expense_id)}

  user = users_collection.find(user_query)
  expense = expenses_collection.find(expense_query)

  parsed_user = parse_json(user)
  parsed_expense = parse_json(expense)

  if len(parsed_user) == 0:
    return abort(Response('User with that id does not exist.', 404))
  
  if len(parsed_expense) == 0:
    return abort(Response('Expense with that id does not exist.', 404))
  
  users_collection.update_one({'_id': ObjectId(user_id), 'expenses.id': expense_id}, {'$pull': {'expenses': {'id': expense_id}}})
  updated_user = parse_json(users_collection.find(user_query))
  parsed_updated_user = parse_json(updated_user)
  del parsed_updated_user[0]['password']
  return parsed_updated_user[0]