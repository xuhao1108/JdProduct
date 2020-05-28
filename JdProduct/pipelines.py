# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# class JdSpiderPipeline(object):
#     def process_item(self, item, spider):
#         return item
from pymongo import MongoClient
from JdProduct.spiders.jd_catagory import JdCatagorySpider
from JdProduct.spiders.jd_product import JdProductSpider
from JdProduct.settings import MONGO_URL


class JdCatagoryPipeline(object):
    """
    商品分类管道，用于将分类信息存储到MongoDB中
    需要在setting中开启ITEM_PIPELINES
    """

    def open_spider(self, spider):
        """
        爬虫开启时
        :param spider: 爬虫对象
        :return:
        """
        # 判断当前爬虫是否是商品分类爬虫
        if isinstance(spider, JdCatagorySpider):
            # 连接MongoDB客户端
            self.client = MongoClient(MONGO_URL)
            # 获取集合对象
            self.collection = self.client['jd']['catagory']

    def process_item(self, item, spider):
        """
        爬虫进行时
        :param item:
        :param spider: 爬虫对象
        :return:
        """
        # 判断当前爬虫是否是商品分类爬虫
        if isinstance(spider, JdCatagorySpider):
            # 将商品分类信息插入到MongoDB中
            self.collection.insert_one(dict(item))
        return item

    def close_spider(self, spider):
        """
        爬虫结束时
        :param spider: 爬虫对象
        :return:
        """
        # 判断当前爬虫是否是商品分类爬虫
        if isinstance(spider, JdCatagorySpider):
            # 关闭MongoDB客户端连接
            self.client.close()


class JdProductPipeline(object):
    """
    商品详细信息管道，用于将商品信息存储到MongoDB中
    需要在setting中开启ITEM_PIPELINES
    """

    def open_spider(self, spider):
        """
        爬虫开启时
        :param spider: 爬虫对象
        :return:
        """
        # 判断当前爬虫是否是商品详细信息爬虫
        if isinstance(spider, JdProductSpider):
            # 连接MongoDB客户端
            self.client = MongoClient(MONGO_URL)
            # 获取集合对象
            self.collection = self.client['jd']['product']

    def process_item(self, item, spider):
        """
        爬虫进行时
        :param item:
        :param spider: 爬虫对象
        :return:
        """
        # 判断当前爬虫是否是商品详细信息爬虫
        if isinstance(spider, JdProductSpider):
            # 将商品详细信息插入到MongoDB中
            self.collection.insert_one(dict(item))
        return item

    def close_spider(self, spider):
        """
        爬虫结束时
        :param spider: 爬虫对象
        :return:
        """
        # 判断当前爬虫是否是商品详细信息爬虫
        if isinstance(spider, JdProductSpider):
            # 关闭MongoDB客户端连接
            self.client.close()
