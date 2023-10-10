from flask import Flask, request, jsonify
from bson.json_util import dumps
from json import loads
from database.collections.users import create_new_user, get_all_users, get_user_by_id, get_user_by_login, delete_user, update_user

app = Flask (__name__)

def parse_json(data):
 return loads(dumps(data, default=str))

@app.route('/')
def home():
  return 'Connected to Divvy API.'

@app.route('/users', methods=['GET', 'POST'])
def users():
  _json = request.json
  
  if request.method == 'POST':
   _login = _json['login']
   _password = _json['password']
   
   login_already_exists = len(get_user_by_login(_login)) != 0
   if login_already_exists:
    return 'Login already exists.' 
   return create_new_user(login=_login, password=_password)
  
  if request.method == 'GET':
   return get_all_users()

@app.route('/users/<user_id>', methods=['GET', 'PUT', 'DELETE'])
def single_user(user_id):
  _json = request.json_json = request.json

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

   updated_user = update_user(id=user_id, values_to_update=values_to_update)
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

if __name__ == '__main__':
  app.run(debug=True)