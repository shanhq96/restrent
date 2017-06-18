from flask import *
import connectdb
import baserestrent
from pymongo import *
import re
import math
from bson.objectid import ObjectId

userinfo = Blueprint("userinfo", __name__)


def __getblueprint__():
    return userinfo


@userinfo.route('/register', methods=['POST', ])
def register():
    # 区域，租赁方式类别，房型，面积，租金，排序，页数   (全都有全部)
    form = request.form
    info = {}
    info['username'] = form.get('username')
    info['password'] = form.get('password') # TODO 待加密
    info['status'] = None   # 保留字段
    info['interests'] = []    # 兴趣初始为空
    connection = connectdb.ConnectMongoDB()
    userinfoCollection = connection.getCollection('userinfo')
    connection.insertList(userinfoCollection, info)
    print("新创建用户,用户名:%s,密码:%s" % (info['username'], info['password']))
    response = baserestrent.get_return_response(jsonify({"status": "success", "data": info['username']}))
    return response


@userinfo.route('/validUsername', methods=['POST', ])
def validUsername():
    # 区域，租赁方式类别，房型，面积，租金，排序，页数   (全都有全部)
    form = request.form
    username = form.get('username')
    connection = connectdb.ConnectMongoDB()
    userinfoCollection = connection.getCollection('userinfo')
    count = connection.findData(userinfoCollection, {"username": username}).count()
    print("验证用户名是否重复,用户名:%s,找到匹配用户个数%s" % (username,count))
    response = baserestrent.get_return_response(jsonify({"status": "success", "data": count}))
    return response

@userinfo.route('/signIn', methods=['POST', ])
def signIn():
    form = request.form
    info = {}
    info['username'] = form.get('username')
    info['password'] = form.get('password') # TODO 待加密
    connection = connectdb.ConnectMongoDB()
    userinfoCollection = connection.getCollection('userinfo')
    count = connection.findData(userinfoCollection, {"$and":[{"username": info['username']},{"password":info['password']}]}).count()
    print("验证登录,用户名:%s,找到匹配用户个数%s" % (info['username'],count))
    response = baserestrent.get_return_response(jsonify({"status": "success", "data": {"username":info['username'], "count":count}}))
    return response

@userinfo.route('/likeTheRoom', methods=['POST', ])
def likeTheRoom():
    form = request.form
    username = form.get('username')
    roomId = ObjectId(form.get('roomId'))
    connection = connectdb.ConnectMongoDB()
    userinfoCollection = connection.getCollection('userinfo')
    userinfoTemp = userinfoCollection.find_one({"username":username})
    theInterests = userinfoTemp['interests']
    if(roomId not in theInterests):
        theInterests.append(roomId)
    userinfoCollection.update_one({"username": username}, {"$set":{"interests": theInterests}})
    print("用户%s选择喜欢该房源:%s,所有房源:%s"%(username,roomId,theInterests))
    response = baserestrent.get_return_response(jsonify({"status": "success"}))
    return response

@userinfo.route('/dislikeTheRoom', methods=['POST', ])
def dislikeTheRoom():
    form = request.form
    username = form.get('username')
    roomId = ObjectId(form.get('roomId'))
    connection = connectdb.ConnectMongoDB()
    userinfoCollection = connection.getCollection('userinfo')
    userinfoTemp = userinfoCollection.find_one({"username":username})
    theInterests = userinfoTemp['interests']
    if(roomId in theInterests):
        theInterests.remove(roomId)
    userinfoCollection.update_one({"username": username}, {"$set":{"interests": theInterests}})
    print("用户%s选择取消喜欢该房源:%s,所有房源:%s"%(username,roomId,theInterests))
    response = baserestrent.get_return_response(jsonify({"status": "success"}))
    return response


@userinfo.route('/getTheInterests', methods=['POST', ])
def getTheInterests():
    form = request.form
    username = form.get('username')
    pages = int(form.get('pages'))
    connection = connectdb.ConnectMongoDB()
    userinfoCollection = connection.getCollection('userinfo')
    userinfoTemp = userinfoCollection.find_one({"username":username})
    theInterests = userinfoTemp['interests']    # 用户喜欢的房源列表

    pagesize = 20
    pos = pages * pagesize
    rentDataCollection = connection.getCollection('rentdata')
    resultTemp = connection.findData(rentDataCollection,{"_id":{"$in":theInterests}})
    pageTotal = math.ceil(resultTemp.count()/pagesize)
    result = resultTemp.skip(pos).limit(pagesize)
    itemarray = []
    for item in result:
        item['_id'] = str(item['_id'])
        itemarray.append(item)
    print("第%s页,用户%s查看所有喜欢房源:%s"%(pages,username,theInterests))
    response = baserestrent.get_return_response(jsonify({"status": "success", "data":itemarray, "pageTotal":pageTotal}))
    return response