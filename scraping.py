import requests
from pymongo import MongoClient
import calendar
import time
import sys

def getCurrentTimestamp():
    return int(calendar.timegm(time.gmtime()))

def upsert_detail(collection, user):
    #find if user is existed
    record = collection.find_one({'Id': user['Id']})
    if record is None:
        #not existed
        user.pop('IsBan', None)
        user.pop('IsBadEmail', None)
        user.pop('IsConfirm', None)
        user.pop('UpdatedDate', None)
        user.pop('IsSound', None)
        user.pop('YahooNick', None)
        user.pop('Active', None)
        user.pop('ShortDescription', None)
        user.pop('Click', None)
        user.pop('IsDirty', None)
        user.pop('IsVip', None)
        user.pop('CreatedDate', None)
        user.pop('LastLoginDate', None)
        user.pop('EncryptedPassword', None)
        user.pop('DeleteReason', None)

        user['created_time'] = getCurrentTimestamp()
        user['updated_time'] = getCurrentTimestamp()
        collection.insert_one(user)
        # print('=====insert', user)
    else:
        record['Picture'] = user['Picture']
        record['LookingFor'] = user['LookingFor']
        record['Profile'] = user['Profile']
        record['updated_time'] = getCurrentTimestamp()

        collection.update_one({'Id': user['Id']}, {'$set':record})
        # print('=====update', record)

    return

#======
# client = MongoClient('localhost:27017')
client = MongoClient('mongodb+srv://vndating_aws_user:mqwb69jbcCaA6osI@cluster0.juido.mongodb.net')

db_client = client['vndating_aws']
collection = db_client['user']

HOST_URI = 'https://henho.top/Home/'

get_url = HOST_URI + sys.argv[1] + '?gender=' + sys.argv[2]
r = requests.get(get_url, headers={})

response_json = r.json()

if 'Persons' in response_json:
    #having data
    raw_users = response_json['Persons']
    for user in raw_users:
        upsert_detail(collection, user)



