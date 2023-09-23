from lxml import html
from pymongo import MongoClient
import requests

#######################
PREVIOUS_RANGE_NUM = 5  #scrape X latest items
NEXT_RANGE_NUM = 5     #scrape X next items
#######################
def request_vietlott(DrawId):
    post_url = 'https://vietlott.vn/ajaxpro/Vietlott.PlugIn.WebParts.Game655ResultDetailWebPart,Vietlott.PlugIn.WebParts.ashx'
    json_data = {
        "ORenderInfo": {
            "SiteId": "main.frontend.vi",
            "SiteAlias": "main.vi",
            "UserSessionId": "",
            "SiteLang": "vi",
            "IsPageDesign": False,
            "ExtraParam1": "",
            "ExtraParam2": "",
            "ExtraParam3": "",
            "SiteURL": "",
            "SiteName": "Vietlott",
            "System": 1
        },
        "Key": "58e07371",
        "DrawId": DrawId
    }
    r = requests.post(post_url, headers={'Content-Type': 'application/json', 'X-Ajaxpro-Method':'ServerSideDrawResult'},
                      json=json_data)
    RetExtraParam1 = r.json()['value']['RetExtraParam1']
    return RetExtraParam1
#######################
def find_latest_record(db_collection):
    latest_record = db_collection.find({}).sort("index", -1).limit(1)
    if latest_record is not None:
        return latest_record.next()['index']
    return 0
#######################
def parse_and_save(db_collection, int_index, str_latest_index, text):
    tree = html.fromstring(text)
    tags = tree.xpath('//span[@class="bong_tron small"]')
    #
    nums = []
    for tag in tags:
        nums.append(int(tag.text))
    #last number
    last_num = tree.xpath('//span[@class="bong_tron small no-margin-right active"]')
    nums.append(int(last_num[0].text))
    #date
    _date = ''
    h5tags = tree.xpath('//h5')
    for h5 in h5tags:
        b_tags = h5.xpath('.//b')
        for b in b_tags:
            if b.text.find('/') > 0:
                _date = b.text
    #
    #search if index is saved in db or not
    record = db_collection.find_one({'index': int_index})
    if record is None:
        #insert new document
        doc = {
            "id": str_latest_index,
            "index": int_index,
            "date": _date,
            "nums": nums
        }
        # print(doc)
        db_collection.insert_one(doc)
#######################
def convert_int_to_drawId(int_index):
    str_index = str(int_index)
    if int_index < 10:
        str_index = '0000' + str(int_index)
    elif int_index < 100:
        str_index = '000' + str(int_index)
    elif int_index < 1000:
        str_index = '00' + str(int_index)
    else:
        str_index = '0' + str(int_index)

    return str_index
#######################
def parse_data(db_collection):
    int_index = find_latest_record(db_collection)
    for index in range(int_index - PREVIOUS_RANGE_NUM, int_index + NEXT_RANGE_NUM):
        str_current_index = convert_int_to_drawId(index);
        RetExtraParam1 = request_vietlott(str_current_index)
        if len(RetExtraParam1) > 0:
            #had data, parse it
            parse_and_save(db_collection, index, str_current_index, RetExtraParam1)
        print('finish parsing index: ' + str_current_index)
####################### calculate frequency of numbers
def sum_up_statistic(db_collection):
    records = db_collection.find({})    #find all
    number_set = {}
    for record in records:
        nums = record['nums']
        for num in nums:
            if num not in number_set:
                number_set[num] = 1
            else:
                number_set[num] += 1
    print('statistic ---------- ')
    for num in number_set:
        print(str(num) + ',' + str(number_set[num]))
####################### calculate frequency of numbers at the column index
def sum_up_statistic_posit(db_collection, column_index):
    records = db_collection.find({})    #find all
    number_set = {}
    for record in records:
        num = record['nums'][column_index]
        if num not in number_set:
            number_set[num] = 1
        else:
            number_set[num] += 1
    print('statistic ---------- ')
    for num in number_set:
        print(num)
    print('---------- ')
    for num in number_set:
        print(number_set[num])
####################### calculate correlation of appearance between of numbers
# pair(x, y) = Z means: Z times x & y appear together in 1 day
#
def calculate_correlation(db_collection):
    records = db_collection.find({})    #find all
    pairs = []
    date_pairs = []
    #init 2-dimensional array
    for x in range(0, 55):  #from 1 to 55
        pairs.append([])
        date_pairs.append([])
        for y in range(0, 55):
            pairs[x].append(0)
            date_pairs[x].append('')
    #
    for record in records:
        nums = record['nums']
        for x in range(0, 6):
            for y in range(x+1, 7):
                pairs[nums[x]-1][nums[y]-1] += 1
                if pairs[nums[x]-1][nums[y]-1] == 1:
                    date_pairs[nums[x]-1][nums[y]-1] = record['index']
                else:
                    date_pairs[nums[x]-1][nums[y]-1] = ''
    # print_pairs_matrix(pairs)
    # print(date_pairs[53][0])
    # print_pairs_csv(pairs)
#######################
def print_pairs_csv(pairs):
    for row in range(0, 55):
        for col in range(0, 55):
            if (pairs[row][col] > 0):
                print("("+str(row+1)+"-"+str(col+1)+")" + "," + str(pairs[row][col]))
#######################
def print_pairs_matrix(pairs):
    str_col = ""
    for col in range(0, 55):
        if col < 10:
            str_col += "  " + str(col+1)
        else:
            str_col += " " + str(col+1)
    print("    " + str_col)
    print("-------")
    for row in range(0, 55):
        str_col = ""
        for col in range(0, 55):
            if pairs[row][col] < 10:
                str_col += "  " + str(pairs[row][col])
            else:
                str_col += " " + str(pairs[row][col])
        if (row < 9):
            print(str(row+1) + ":  " + str_col)
        else:
            print(str(row+1) + ": " + str_col)
####################### main flow
client = MongoClient('localhost:27017')
db_client = client['martin_projects']   #database
db_collection = db_client['vietlott_655']

# parse_data(db_collection)
# sum_up_statistic(db_collection)
# sum_up_statistic_posit(db_collection, 1)
calculate_correlation(db_collection)