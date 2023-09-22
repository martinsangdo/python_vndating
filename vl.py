from lxml import html
from pymongo import MongoClient
import requests

#######################
PREVIOUS_RANGE_NUM = 2  #scrape X latest items
NEXT_RANGE_NUM = 0     #scrape X next items
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
    latest_record = db_collection.find({}).sort("index").limit(1)
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
    if index < 10:
        str_index = '0000' + str(int_index)
    elif index < 100:
        str_index = '000' + str(int_index)
    elif index < 1000:
        str_index = '00' + str(int_index)
    else:
        str_index = '0' + str(int_index)

    return str_index
####################### main flow
client = MongoClient('localhost:27017')
db_client = client['martin_projects']   #database
db_collection = db_client['vietlott_655']

int_index = find_latest_record(db_collection)
for index in range(int_index - PREVIOUS_RANGE_NUM, int_index + NEXT_RANGE_NUM):
    str_current_index = convert_int_to_drawId(index);
    RetExtraParam1 = request_vietlott(str_current_index)
    if len(RetExtraParam1) > 0:
        #had data, parse it
        parse_and_save(db_collection, index, str_current_index, RetExtraParam1)
        print('finish parsing index: ' + str_current_index)
# print(latest_index)
# ####################### test
#
# org_str = "<div class=\"porlet border CssLength2\">                      <div class=\"header\">                          <div class=\"header-title text-center border-bottom padding_top_30 padding_bottom_20\">                              <div class=\"chitietketqua_title\">                                  <img  src=\"https://media.vietlott.vn//main/06.2018/cms/game/Power655.png\" alt=\"Power 6/55\">                                  <h4>Kết quả quay số mở thưởng POWER 6/55</h4>  \t\t                          <h5>Kỳ quay thưởng <b>#00001</b> ngày <b>01/08/2017</b></h5>                              </div><!-- /chitietketqua_title -->                          </div>                          <!-- /.header-title -->                          <div class=\"header-tool\">                          </div>                          <!-- /.header-tool -->                      </div>                      <!-- /.header -->                      <div class=\"content\">                          <div class=\"day_so_ket_qua border-bottom\">                            <div class=\"day_so_ket_qua_v2\">  \t\t\t                    <span class=\"bong_tron small\">05</span><span class=\"bong_tron small\">10</span><span class=\"bong_tron small\">14</span><span class=\"bong_tron small\">23</span><span class=\"bong_tron small\">24</span><span class=\"bong_tron small\">38</span><i>|</i><span class=\"bong_tron small no-margin-right active\">35</span>                            </div>                           <div class=\"btn_chuyendulieu\">    <a class=\"btn_chuyendulieu_left tat-nutchuyen\" title=\"Đang là kỳ đầu tiên không có kết quả kỳ trước.\"><i class=\"fas fa-angle-left\"></i></a>    <a class=\"btn_chuyendulieu_right\" href=\"javascript:ClientDrawResult('00002');\" title=\"\"><i class=\"fas fa-angle-right\"></i></a>     </div><!-- /btn_chuyendulieu -->                          </div><!-- /day_so_ket_qua -->                      </div>                      <!-- /.content -->                      <div class=\"footer\">                          <div class=\"box_kqtt_nd_chinh text-center\">                              <p class=\"box_kqtt_nd_note color_red\">\"Các con số dự thưởng phải trùng với số kết quả nhưng không cần theo đúng thứ  tự\"</p>                              <p>Truyền Hình Trực Tiếp Trên Kênh VTC3</p>                              <h5>Từ 18h00 – 18h30 Thứ 3 - Thứ 5 - Thứ 7</h5>                          </div><!-- /box_kqtt_nd_chinh -->                      </div>                      <!-- /.footer -->                  </div>                  <!-- /.porlet -->"
#
# tree = html.fromstring(org_str)
#
# rows = tree.xpath('//span[@class="bong_tron small"]')
#
# print(rows)
# numb = len(rows)
#
# for row in rows:
#     print(row.text)