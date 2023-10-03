from flask import Blueprint, request, jsonify

views = Blueprint(__name__, 'views')

@views.route('/')
def home():
  return 'this is home'

@views.route('/profile/<username>')
def profile(username):
  return 'this is the profile of {}, pulled from url parameters'.format(username)

@views.route('/group')
def group():
  args = request.args
  name = args.get('name')
  return 'this is the group named {}, pulled from query parameters'.format(name)

@views.route('/json')
def get_json():
  return jsonify({'data_1': 'example string', 'data_2': 2, 'data_3': ['x', 3, 'y', 5]})
