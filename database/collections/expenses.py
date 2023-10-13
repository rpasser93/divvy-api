from bson.objectid import ObjectId
from database.constants.db_constants import expenses_collection
from database.constants.status_enums import Status
from database.helpers.parse_json import parse_json
import pprint
from datetime import datetime

printer = pprint.PrettyPrinter()

def create_new_expense(name: str, description: str, date_start: datetime, date_end: datetime):
  new_expense = {
    'name': name,
    'description': description,
    'date_start': date_start,
    'date_end': date_end,
    'total_amount': None,
    'owed_party': [],
    'indebted_party': [],
    'status': Status.ACTIVE,
    'date_created': datetime.now()
  }
  expenses_collection.insert_one(new_expense)
  return parse_json(new_expense)

def get_all_expenses():
  expenses = expenses_collection.find({})
  all_expenses_dict = {
    'expenses': parse_json(expenses)
  }
  return all_expenses_dict

def get_expense_by_id(expense_id: str):
  expense = expenses_collection.find({'_id': ObjectId(id)})
  return parse_json(expense)

def update_expense(expense_id: str):
  return f'Updating expense: {expense_id}.'

def delete_expense(expense_id: str):
  return f'Deleting expense: {expense_id}'

def complete_expense(expense_id: str):
  return f'Closing expense: {expense_id}'

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