from flask import Flask, request
from bson.json_util import dumps
from json import loads

import sys
sys.path.append('.')
from database.collections.users import create_new_user, get_all_users, get_user_by_id, get_user_by_login, delete_user, update_user, add_expense_for_user, update_expense_access_for_user, delete_expense_for_user
from database.collections.expenses import create_new_expense, get_all_expenses, get_expense_by_id, update_expense, delete_expense, complete_expense, reopen_expense, add_owed_party, update_owed_party, delete_owed_party, add_indebted_party, update_indebted_party, delete_indebted_party, add_expense_history

app = Flask (__name__)

def parse_json(data):
 return loads(dumps(data, default=str))

@app.route('/')
def home():
  return 'Connected to Divvy API.'

##Endpoints for Users
@app.route('/users', methods=['GET', 'POST'])
def users():
  _json = request.json
  
  if request.method == 'POST':
   _login = _json['login']
   _password = _json['password']
   return create_new_user(_login, _password)
  
  if request.method == 'GET':
   return get_all_users()

@app.route('/users/<user_id>', methods=['GET', 'PUT', 'DELETE'])
def single_user(user_id):
  _json = request.json

  if request.method == 'GET':
   return get_user_by_id(user_id)
  
  if request.method == 'PUT':
   values_to_update = {}
   if 'password' in _json:
    values_to_update['password'] = _json['password']
   if 'first_name' in _json:
    values_to_update['first_name'] = _json['first_name']
   if 'last_name' in _json:
    values_to_update['last_name'] = _json['last_name']
   return update_user(user_id, values_to_update)
  
  if request.method == 'DELETE':
   return delete_user(user_id)

@app.route('/users/<user_id>/expense/<expense_id>', methods=['POST', 'PUT', 'DELETE'])
def user_expense(user_id, expense_id):
  _json = request.json
  
  if request.method == 'POST':
    _access_level = _json['access_level']
    _status = _json['status']
    return add_expense_for_user(user_id, expense_id, _access_level, _status)
 
  if request.method == 'PUT':
    _access_level = _json['access_level']
    return update_expense_access_for_user(user_id, expense_id, _access_level)
 
  if request.method == 'DELETE':
    return delete_expense_for_user(user_id, expense_id)

##Endpoints for Expenses
@app.route('/expenses', methods=['GET', 'POST'])
def expenses():
 _json = request.json

 if request.method == 'POST':
  _name = _json['name']
  _description = _json['description']
  _date_of_expense = _json['date_of_expense']
  _creator_id = _json['creator_id']
  return create_new_expense(_name, _description, _date_of_expense, _creator_id)
 
 if request.method == 'GET':
  return get_all_expenses()
 
@app.route('/expenses/<expense_id>', methods=['GET', 'PUT', 'DELETE'])
def single_expense(expense_id):
 _json = request.json

 if request.method == 'GET':
  return get_expense_by_id(expense_id)
 
 if request.method == 'PUT':
  values_to_update = {}
  if 'name' in _json:
    values_to_update['name'] = _json['name']
  if 'description' in _json:
    values_to_update['description'] = _json['description']
  if 'date' in _json:
    values_to_update['date'] = _json['date']
  return update_expense(expense_id, values_to_update)
 
 if request.method == 'DELETE':
  return delete_expense(expense_id)

@app.route('/expenses/<expense_id>/owed', methods=['POST', 'PUT', 'DELETE'])
def expense_owed_party(expense_id):
 
 if request.method == 'POST':
  return add_owed_party(expense_id)
 
 if request.method == 'PUT':
  return update_owed_party(expense_id)
 
 if request.method == 'DELETE':
  return delete_owed_party(expense_id)

@app.route('/expenses/<expense_id>/indebted', methods=['POST', 'PUT', 'DELETE'])
def expense_indebted_party(expense_id):
  
  if request.method == 'POST':
   return add_indebted_party(expense_id)
 
  if request.method == 'PUT':
   return update_indebted_party(expense_id)
  
  if request.method == 'DELETE':
   return delete_indebted_party(expense_id)
  
@app.route('/expenses/<expense_id>/complete', methods=['POST'])
def expense_completed(expense_id):
  return complete_expense(expense_id)

@app.route('/expenses/<expense_id>/reopen', methods=['POST'])
def expense_reopened(expense_id):
  return reopen_expense(expense_id)

@app.route('/expenses/<expense_id>/history', methods=['POST'])
def expense_history_add(expense_id):
 _json = request.json

 text = _json['text']
 return add_expense_history(expense_id, text)

if __name__ == '__main__':
  app.run(debug=True)