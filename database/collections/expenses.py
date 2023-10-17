from bson.objectid import ObjectId
from database.collections.users import add_expense_for_user
from database.constants.db_constants import expenses_collection, users_collection
from database.constants.status_enums import Status
from database.constants.access_enums import Access
from database.helpers.parse_json import parse_json
from datetime import datetime
from flask import abort, Response

def create_new_expense(name: str, description: str, date_of_expense: datetime, creator_id: str):
  new_expense = {
    'name': name,
    'description': description,
    'date_of_expense': date_of_expense,
    'owed_party': [],
    'indebted_party': [],
    'status': Status.ACTIVE,
    'history': [],
  }
  expenses_collection.insert_one(new_expense)
  parsed_new_expense = parse_json(new_expense)
  new_expense_id = parsed_new_expense['_id']['$oid']
  add_expense_for_user(creator_id, new_expense_id, Access.CREATOR, Status.ACTIVE)
  return parsed_new_expense

def get_all_expenses():
  expenses = expenses_collection.find({})
  all_expenses_dict = {
    'expenses': parse_json(expenses)
  }
  return all_expenses_dict

def get_expense_by_id(id: str):
  expense = expenses_collection.find({'_id': ObjectId(id)})
  parsed_expense = parse_json(expense)
  if len(parsed_expense) == 0:
   return abort(Response('Expense with that id does not exist.', 404))
  return parsed_expense[0]

def update_expense(id: str, values_to_update: dict):
  new_values = {
    '$set': values_to_update
  }
  expense_query = {'_id': ObjectId(id)}
  expense = expenses_collection.find(expense_query)
  parsed_expense = parse_json(expense)
  if len(parsed_expense) == 0:
   return abort(Response('Expense with that id does not exist.', 404))
  
  expenses_collection.update_one(expense_query, new_values)
  updated_expense = parse_json(expenses_collection.find(expense_query))
  return updated_expense[0]

def delete_expense(id: str):
  expense = expenses_collection.find({'_id': ObjectId(id)})
  parsed_expense = parse_json(expense)
  if len(parsed_expense) == 0:
   return abort(Response('Expense with that id does not exist.', 404))
  
  expenses_collection.delete_one({'_id': ObjectId(id)})
  users_collection.update_many({'expenses.id': id}, {'$pull': {'expenses': {'id': id}}})
  return parsed_expense[0]

def complete_expense(id: str):
  expense_query = {'_id': ObjectId(id)}
  new_status = {
    '$set': {
      'status': Status.PAID_UP
    }
  }
  expense = expenses_collection.find(expense_query)
  parsed_expense = parse_json(expense)
  if len(parsed_expense) == 0:
   return abort(Response('Expense with that id does not exist.', 404))
  
  expenses_collection.update_one(expense_query, new_status)
  users_collection.update_many({'expenses.id': id},  {'$set': {'expenses.$.status': Status.PAID_UP}})
  
  updated_expense = parse_json(expenses_collection.find(expense_query))
  return updated_expense[0]

def reopen_expense(id: str):
  new_status = {
    '$set': {
      'status': Status.ACTIVE
    }
  }
  expense_query = {'_id': ObjectId(id)}
  expense = expenses_collection.find(expense_query)
  parsed_expense = parse_json(expense)
  if len(parsed_expense) == 0:
   return abort(Response('Expense with that id does not exist.', 404))
  
  expenses_collection.update_one(expense_query, new_status)
  users_collection.update_many({'expenses.id': id},  {'$set': {'expenses.$.status': Status.ACTIVE}})

  updated_expense = parse_json(expenses_collection.find(expense_query))
  return updated_expense[0]

def add_expense_history(id: str, text: str):
  return f'Updating history for expense: {id} with text: "{text}"'

##owed and indebted
def add_owed_party(expense_id: str):
  return f'Adding owed party to expense: {expense_id}'

def update_owed_party(expense_id: str):
  return f'Updating owed party in expense: {expense_id}'

def delete_owed_party(expense_id: str):
  return f'Deleting owed party in expense: {expense_id}'

def add_indebted_party(expense_id: str):
  return f'Adding indebted party to expense in expense: {expense_id}'

def update_indebted_party(expense_id: str):
  return f'Updating indebted party in expense: {expense_id}'

def delete_indebted_party(expense_id: str):
  return f'Deleting indebted party in expense: {expense_id}'