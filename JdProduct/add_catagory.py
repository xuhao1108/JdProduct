# -*- coding: utf-8 -*-
import pickle
from pymongo import MongoClient
from redis import StrictRedis
from JdProduct.settings import MONGO_URL, REDIS_URL, JD_PRODUCT_REDIS_KEY


def add_catagory():
    # 连接MongoDB
    mongo_client = MongoClient(MONGO_URL)
    # 连接Redis
    redis_cliten = StrictRedis.from_url(REDIS_URL)
    # 清空redis之前的记录
    redis_cliten.delete(JD_PRODUCT_REDIS_KEY)
    # 获取catagory集合
    collection = mongo_client['jd']['catagory']
    # 查询所有数据
    cursor = collection.find()
    # 将每条catagory插入到Redis中
    for catagory in cursor:
        # 将数据序列化
        data = pickle.dumps(catagory)
        # 将数据存入指定key的list中
        redis_cliten.lpush(JD_PRODUCT_REDIS_KEY, data)
    # 关闭MongoDB
    mongo_client.close()


if __name__ == '__main__':
    add_catagory()
