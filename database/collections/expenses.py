from bson.objectid import ObjectId
from database.collections.users import add_expense_for_user
from database.constants.db_constants import expenses_collection, users_collection
from database.constants.status_enums import Status
from database.constants.access_enums import Access
from database.constants.split_type_enums import Split
from database.helpers.parse_json import parse_json
from datetime import datetime
from uuid import uuid4
from flask import abort, Response

def create_new_expense(name: str, description: str, date: datetime, split_by: Split, creator_id: str):
  new_expense = {
    'name': name,
    'description': description,
    'date': date,
    'split_by': split_by,
    'owed_party': [],
    'indebted_party': [],
    'status': Status.ACTIVE,
    'history': [],
  }
  expenses_collection.insert_one(new_expense)
  parsed_new_expense = parse_json(new_expense)
  new_expense_id = parsed_new_expense['_id']['$oid']
  add_expense_for_user(creator_id, new_expense_id, Access.CREATOR, Status.ACTIVE)
  add_expense_history(new_expense_id, 'Expense created.')
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

  if 'name' in values_to_update:
    add_expense_history(id, f'Expense name changed from {parsed_expense[0]['name']} to {values_to_update['name']}.')
  if 'description' in values_to_update:
    add_expense_history(id, f'Expense description changed from {parsed_expense[0]['description']} to {values_to_update['description']}.')
  if 'date' in values_to_update:
    old_datetime = datetime.strptime(parsed_expense[0]['date'], '%Y-%d-%mT%H:%M:%S.%fZ')
    new_datetime = datetime.strptime(values_to_update['date'], '%Y-%d-%mT%H:%M:%S.%fZ')
    old_date_string = old_datetime.strftime('%b %d, %Y')
    new_date_string = new_datetime.strftime('%b %d, %Y')
    add_expense_history(id, f'Expense date changed from {old_date_string} to {new_date_string}.')

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

def update_expense_split(id: str, split_by: Split):
  expense_query = {'_id': ObjectId(id)}
  expense = expenses_collection.find(expense_query)
  parsed_expense = parse_json(expense)
  if len(parsed_expense) == 0:
   return abort(Response('Expense with that id does not exist.', 404))
  
  expenses_collection.update_one(expense_query, {'$set': {'split_by': split_by}})

  add_expense_history(id, f'Expense splitting changed to Divvy by {split_by}.')
  
  updated_expense = parse_json(expenses_collection.find(expense_query))
  return updated_expense[0]

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

  add_expense_history(id, 'Expense paid up and closed.')

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

  add_expense_history(id, 'Expense reopened.')

  updated_expense = parse_json(expenses_collection.find(expense_query))
  return updated_expense[0]

def add_owed_party(id: str, first_name: str, last_name: str, amount_owed: float):
  expense_query = {'_id': ObjectId(id)}
  expense = expenses_collection.find(expense_query)
  parsed_expense = parse_json(expense)
  if len(parsed_expense) == 0:
   return abort(Response('Expense with that id does not exist.', 404))
  
  duplicate_member_in_owed_party = parse_json(expenses_collection.find({'_id': ObjectId(id), 'owed_party.first_name': first_name, 'owed_party.last_name': last_name}))
  if len(duplicate_member_in_owed_party) != 0:
    return abort(Response('An "Owed" member of that name already exists in this expense.', 400))
  
  duplicate_member_in_indebted_party = parse_json(expenses_collection.find({'_id': ObjectId(id), 'indebted_party.first_name': first_name, 'indebted_party.last_name': last_name}))
  if len(duplicate_member_in_indebted_party) != 0:
    return abort(Response('A member of that name is already marked as "Indebted" in this expense.', 400))
  
  new_owed_party = {
    'uuid': str(uuid4()),
    'first_name': first_name,
    'last_name': last_name,
    'amount_owed': float(amount_owed),
    'amount_received': 0.00
  }
  expenses_collection.update_one(expense_query, {'$push': {'owed_party': new_owed_party}})

  add_expense_history(id, f'{first_name} {last_name} added to expense - owed ${amount_owed}.')

  updated_expense = parse_json(expenses_collection.find(expense_query))
  return updated_expense[0]

def update_owed_party(expense_id: str, uuid: str, values_to_update: dict):
  expense_query = {'_id': ObjectId(expense_id), 'owed_party.uuid': uuid}
  expense = expenses_collection.find(expense_query)
  parsed_expense = parse_json(expense)
  if len(parsed_expense) == 0:
   return abort(Response('Owed member with that uuid does not exist.', 404))
  
  updated_values = {}

  if 'first_name' in values_to_update:
    updated_values['owed_party.$.first_name'] = values_to_update['first_name']
  if 'last_name' in values_to_update:
    updated_values['owed_party.$.last_name'] = values_to_update['last_name']
  if 'amount_owed' in values_to_update:
    updated_values['owed_party.$.amount_owed'] = float(values_to_update['amount_owed'])
  if 'amount_received' in values_to_update:
    updated_values['owed_party.$.amount_received'] = float(values_to_update['amount_received'])

  expenses_collection.update_one(expense_query, {'$set': updated_values })

  owed_party = parsed_expense[0]['owed_party']
  for member in owed_party:
    if member['uuid'] == uuid:
      if 'first_name' in values_to_update or 'last_name' in values_to_update:
        first_name_string = values_to_update['first_name'] if 'first_name' in values_to_update else member['first_name']
        last_name_string = values_to_update['last_name'] if 'last_name' in values_to_update else member['last_name']
        add_expense_history(expense_id, f'Changed member name in Owed list from {member['first_name']} {member['last_name']} to {first_name_string} {last_name_string}.')
      if 'amount_owed' in values_to_update:
        add_expense_history(expense_id, f'Changed amount owed for {member['first_name']} {member['last_name']} to ${values_to_update['amount_owed']}.')
      if 'amount_received' in values_to_update:
        add_expense_history(expense_id, f'Updated amount received for {member['first_name']} {member['last_name']} to ${values_to_update['amount_received']}.')

  updated_expense = parse_json(expenses_collection.find(expense_query))
  return updated_expense[0]

def delete_owed_party(expense_id: str, uuid: str):
  expense_query = {'_id': ObjectId(expense_id)}
  expense = expenses_collection.find(expense_query)
  parsed_expense = parse_json(expense)
  if len(parsed_expense) == 0:
   return abort(Response('Expense with that id does not exist.', 404))
  
  expense_member_query = {'_id': ObjectId(expense_id), 'owed_party.uuid': uuid}
  expense_member = expenses_collection.find(expense_member_query)
  parsed_expense_member = parse_json(expense_member)
  if len(parsed_expense_member) == 0:
   return abort(Response('Owed member with that uuid does not exist within expense.', 404))
  
  expenses_collection.update_one({'_id': ObjectId(expense_id), 'owed_party.uuid': uuid}, {'$pull': {'owed_party': {'uuid': uuid}}})
  owed_party = parsed_expense[0]['owed_party']
  for member in owed_party:
    if member['uuid'] == uuid:
      add_expense_history(expense_id, f'{member['first_name']} {member['last_name']} deleted from list of Owed members.')
  updated_expense = parse_json(expenses_collection.find(expense_query))
  return updated_expense[0]

def add_indebted_party(id: str, first_name: str, last_name: str, amount_owes: float):
  expense_query = {'_id': ObjectId(id)}
  expense = expenses_collection.find(expense_query)
  parsed_expense = parse_json(expense)
  if len(parsed_expense) == 0:
   return abort(Response('Expense with that id does not exist.', 404))
  
  duplicate_member_in_indebted_party = parse_json(expenses_collection.find({'_id': ObjectId(id), 'indebted_party.first_name': first_name, 'indebted_party.last_name': last_name}))
  if len(duplicate_member_in_indebted_party) != 0:
    return abort(Response('An "Indebted" member of that name already exists in this expense.', 400))
  
  duplicate_member_in_owed_party = parse_json(expenses_collection.find({'_id': ObjectId(id), 'owed_party.first_name': first_name, 'owed_party.last_name': last_name}))
  if len(duplicate_member_in_owed_party) != 0:
    return abort(Response('A member of that name is already marked as "Owed" in this expense.', 400))
  
  new_indebted_party = {
    'uuid': str(uuid4()),
    'first_name': first_name,
    'last_name': last_name,
    'amount_owes': float(amount_owes),
    'amount_paid': 0.00
  }
  expenses_collection.update_one(expense_query, {'$push': {'indebted_party': new_indebted_party}})

  add_expense_history(id, f'{first_name} {last_name} added to expense - owes ${amount_owes}.')

  updated_expense = parse_json(expenses_collection.find(expense_query))
  return updated_expense[0]

def update_indebted_party(expense_id: str, uuid: str, values_to_update: dict):
  expense_query = {'_id': ObjectId(expense_id), 'indebted_party.uuid': uuid}
  expense = expenses_collection.find(expense_query)
  parsed_expense = parse_json(expense)
  if len(parsed_expense) == 0:
   return abort(Response('Indebted member with that uuid does not exist within expense.', 404))
  
  updated_values = {}

  if 'first_name' in values_to_update:
    updated_values['indebted_party.$.first_name'] = values_to_update['first_name']
  if 'last_name' in values_to_update:
    updated_values['indebted_party.$.last_name'] = values_to_update['last_name']
  if 'amount_owes' in values_to_update:
    updated_values['indebted_party.$.amount_owes'] = float(values_to_update['amount_owes'])
  if 'amount_paid' in values_to_update:
    updated_values['indebted_party.$.amount_paid'] = float(values_to_update['amount_paid'])

  expenses_collection.update_one(expense_query, {'$set': updated_values })

  indebted_party = parsed_expense[0]['indebted_party']
  for member in indebted_party:
    if member['uuid'] == uuid:
      if 'first_name' in values_to_update or 'last_name' in values_to_update:
        final_first_name = values_to_update['first_name'] if 'first_name' in values_to_update else member['first_name']
        final_last_name = values_to_update['last_name'] if 'last_name' in values_to_update else member['last_name']
        add_expense_history(expense_id, f'Changed member name in Owing list from {member['first_name']} {member['last_name']} to {final_first_name} {final_last_name}.')
      if 'amount_owes' in values_to_update:
        add_expense_history(expense_id, f'Changed amount {member['first_name']} {member['last_name']} owes to ${values_to_update['amount_owes']}.')
      if 'amount_paid' in values_to_update:
        add_expense_history(expense_id, f'Updated amount paid for {member['first_name']} {member['last_name']} to ${values_to_update['amount_paid']}.')

  updated_expense = parse_json(expenses_collection.find(expense_query))
  return updated_expense[0]

def delete_indebted_party(expense_id: str, uuid: str):
  expense_query = {'_id': ObjectId(expense_id)}
  expense = expenses_collection.find(expense_query)
  parsed_expense = parse_json(expense)
  if len(parsed_expense) == 0:
   return abort(Response('Expense with that id does not exist.', 404))
  
  expense_member_query = {'_id': ObjectId(expense_id), 'indebted_party.uuid': uuid}
  expense_member = expenses_collection.find(expense_member_query)
  parsed_expense_member = parse_json(expense_member)
  if len(parsed_expense_member) == 0:
   return abort(Response('Indebted member with that uuid does not exist within expense.', 404))
  
  expenses_collection.update_one({'_id': ObjectId(expense_id), 'indebted_party.uuid': uuid}, {'$pull': {'indebted_party': {'uuid': uuid}}})
  indebted_party = parsed_expense[0]['indebted_party']
  for member in indebted_party:
    if member['uuid'] == uuid:
      add_expense_history(expense_id, f'{member['first_name']} {member['last_name']} deleted from list of Owing members.')
  updated_expense = parse_json(expenses_collection.find(expense_query))
  return updated_expense[0]

def add_expense_history(id: str, text: str):
  expense_query = {'_id': ObjectId(id)}
  expense = expenses_collection.find(expense_query)
  parsed_expense = parse_json(expense)
  if len(parsed_expense) == 0:
   return abort(Response('Expense with that id does not exist.', 404))
  
  history_object = {
    'text': text,
    'datetime': str(datetime.now())
  }
  expenses_collection.update_one(expense_query, {'$push': {'history': history_object}})
  updated_expense = parse_json(expenses_collection.find(expense_query))
  return updated_expense[0]