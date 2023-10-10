from bson.json_util import dumps
from json import loads


def parse_json(data):
 return loads(dumps(data, default=str))