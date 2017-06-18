"""获取租房数据,暴露数据接口"""
from flask import *
import connectdb
import baserestrent
from pymongo import *
from bson.objectid import ObjectId
import re
import math

rentdata = Blueprint("rentdata", __name__)


@rentdata.route('/getall')
def rentdata_get_all():
    connection = connectdb.ConnectMongoDB()
    rentDataCollection = connection.getCollection('rentdata')
    paramarray = []
    itemarray = []
    for item in connection.findData(rentDataCollection, {"$and": [{"houseType": ""}]}):
        item['_id'] = str(item['_id'])
        itemarray.append(item)
    return jsonify(itemarray)


@rentdata.route('/getdata', methods=['POST', ])
def get_rent_data():
    # 区域，租赁方式类别，房型，面积，租金，排序，页数   (全都有全部)
    form = request.form
    cityShortName = form.get('cityShortName')  # 城市缩写
    urbanDistrict = form.get('urbanDistrict')  # 区域
    leasingMethod = form.get('leasingMethod')  # 租赁方式 整组/合租/全部
    bedroomNum = int(form.get('bedroomNum'))  # 房型 0,1,2,3,4,5 数字(5代表4室以上)
    square = int(form.get('square'))  # 面积  0:[0,+无穷) 1:[0,30)  2:[30,50)  3:[50,70)  4:[70,90)   5:[90,120)  6:[120,无穷)
    rent = int(form.get('rent'))  # 租金 0:[0,+无穷) 1:[0,1500)  2:[1500,2500)  3:[2500,3500)  4:[3500,5000)   5:[5000,无穷)
    sorters = form.get('sorters')  # normal:默认 new:最新 price:租金从低到高
    pages = int(form.get('pages'))  # 页数
    title = form.get('title')  # 标题

    param = {}
    param['cityName'] = cityShortName
    if (title != None and title != "all"):
        param['title'] = re.compile(".*" + title + ".*")
    if (urbanDistrict != "全部"):
        param['urbanDistrict'] = re.compile(".*" + urbanDistrict + ".*")
    if (leasingMethod != "全部"):
        param['leasingMethod'] = leasingMethod
    if (bedroomNum != 0):
        if (bedroomNum < 5):
            param['bedroomNum'] = str(bedroomNum)
        elif (bedroomNum == 5):
            param['bedroomNum'] = re.compile("^(([5-9])|([1-9]\d+))$")

    if (square != 0):
        if (square == 1):
            param['square'] = re.compile("^((\d)|([1-2]\d))$")
        elif (square == 2):
            param['square'] = re.compile("^([3-4]\d)$")
        elif (square == 3):
            param['square'] = re.compile("^([5-6]\d)$")
        elif (square == 4):
            param['square'] = re.compile("^([7-8]\d)$")
        elif (square == 5):
            param['square'] = re.compile("^((9\d)|1[0-1]\d)$")
        elif (square == 6):
            param['square'] = re.compile("^((1[2-9]\d)|([2-9]\d{2})|(\d{4,}))$")

    if (rent != 0):
        if (rent == 1):
            param['rentStr'] = re.compile("^((\d{3})|(1[0-4]\d{2}))$")
        elif (rent == 2):
            param['rentStr'] = re.compile("^((1[5-9]\d{2})|(2[0-4]\d{2}))$")
        elif (rent == 3):
            param['rentStr'] = re.compile("^((2[5-9]\d{2})|(3[0-4]\d{2}))$")
        elif (rent == 4):
            param['rentStr'] = re.compile("^((3[5-9]\d{2})|(4\d{3}))$")
        elif (rent == 5):
            param['rentStr'] = re.compile("^((5\d{3})|(\d{5,}))$")

    connection = connectdb.ConnectMongoDB()
    rentDataCollection = connection.getCollection('rentdata')

    pagesize = 20
    pos = pages * pagesize
    itemarray = []
    resultTemp = connection.findData(rentDataCollection, {"$and": [param]})

    pageTotal = math.ceil(resultTemp.count() / pagesize)
    if (sorters == "normal"):
        result = resultTemp.skip(pos).limit(pagesize)
    elif (sorters == "new"):
        result = resultTemp.skip(pos).limit(pagesize).sort("createTime", DESCENDING)
    elif (sorters == "price"):
        result = resultTemp.skip(pos).limit(pagesize).sort("rent", ASCENDING)

    for item in result:
        item['_id'] = str(item['_id'])
        itemarray.append(item)

    # 总页数返还
    response = baserestrent.get_return_response(
        jsonify({"status": "success", "data": itemarray, "pageTotal": pageTotal}))
    return response


@rentdata.route('/getonedata', methods=['POST', ])
def get_one_rent_data():
    # 带着喜欢与否
    form = request.form
    _id = form.get("_id")
    username = form.get("username")
    connection = connectdb.ConnectMongoDB()
    rentDataCollection = connection.getCollection('rentdata')
    _result = connection.findOneData(rentDataCollection, _id)
    _result['_id'] = str(_result['_id'])
    likeOrNot = 0  # 0代表没喜欢 1代表喜欢
    if (username != None and username != ""):
        userinfoCollection = connection.getCollection('userinfo')
        userinfoTemp = userinfoCollection.find_one({"username": username})
        theInterests = userinfoTemp['interests']
        if ((ObjectId(_result['_id'])) in theInterests):
            likeOrNot = 1
    print("用户%s,访问详情页,是否喜欢该房源:%s,数据:%s," % (username, likeOrNot, _result))
    response = baserestrent.get_return_response(
        jsonify({"status": "success", "data": {"username": username, "roomInfo": _result, "likeOrNot": likeOrNot}}))
    return response


def __getblueprint__():
    return rentdata
