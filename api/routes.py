from flask import Flask, request
from bson.json_util import dumps
from json import loads

import sys
sys.path.append('.')
from database.collections.users import create_new_user, get_all_users, get_user_by_id, get_user_by_login, delete_user, update_user, add_expense_for_user, update_expense_for_user, delete_expense_for_user
from database.collections.expenses import create_new_expense, get_all_expenses, get_expense_by_id, update_expense, delete_expense, complete_expense, add_owed_party, update_owed_party, delete_owed_party, add_indebted_party, update_indebted_party, delete_indebted_party

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
   
   login_already_exists = len(get_user_by_login(_login)) != 0
   if login_already_exists:
    return 'Login already exists.' 
   return create_new_user(_login, _password)
  
  if request.method == 'GET':
   return get_all_users()

@app.route('/users/<user_id>', methods=['GET', 'PUT', 'DELETE'])
def single_user(user_id):
  _json = request.json

  if request.method == 'GET':
   user_with_id = get_user_by_id(user_id)
   user_does_not_exist = len(user_with_id) == 0
   if user_does_not_exist:
    return 'User with that id does not exist.'
   return user_with_id[0]
  
  if request.method == 'PUT':
   values_to_update = {}

   if 'password' in _json:
    values_to_update['password'] = _json['password']
   if 'first_name' in _json:
    values_to_update['first_name'] = _json['first_name']
   if 'last_name' in _json:
    values_to_update['last_name'] = _json['last_name']

   updated_user = update_user(user_id, values_to_update)
   user_does_not_exist = len(updated_user) == 0
   if user_does_not_exist:
    return 'User with that id does not exist.'
   return updated_user[0]
  
  if request.method == 'DELETE':
   deleted_user = delete_user(user_id)
   user_does_not_exist = len(deleted_user) == 0
   if user_does_not_exist:
    return 'User with that id does not exist.'
   return deleted_user[0]


@app.route('/users/<user_id>/expense/<expense_id>', methods=['POST', 'PUT', 'DELETE'])
def user_expense(user_id, expense_id):
  if request.method == 'POST':
    return add_expense_for_user(user_id, expense_id)
 
  if request.method == 'PUT':
    return update_expense_for_user(user_id, expense_id)
 
  if request.method == 'DELETE':
    return delete_expense_for_user(user_id, expense_id)

##Endpoints for Expenses
@app.route('/expenses', methods=['GET', 'POST'])
def expenses():
 _json = request.json

 if request.method == 'POST':
  _name = _json['name']
  _description = _json['description']
  _date_start = _json['date_start']
  _date_end = _json['date_end']
  return create_new_expense(_name, _description, _date_start, _date_end)
 
 if request.method == 'GET':
  return get_all_expenses()
 
@app.route('/expenses/<expense_id>', methods=['GET', 'PUT', 'DELETE'])
def single_expense(expense_id):
 if request.method == 'GET':
  return get_expense_by_id(expense_id)
 
 if request.method == 'PUT':
  return update_expense(expense_id)
 
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
def expense_paid_up(expense_id):
 return complete_expense(expense_id)

if __name__ == '__main__':
  app.run(debug=True)