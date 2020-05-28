# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


# class JdSpiderItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     pass
class JdCatagoryItem(scrapy.Item):
    """
    京东商品分类项
    """
    # 大分类url
    big_catagory_url = scrapy.Field()
    # 大分类名称
    big_catagory_name = scrapy.Field()
    # 中分类url
    middle_catagory_url = scrapy.Field()
    # 中分类名称
    middle_catagory_name = scrapy.Field()
    # 小分类url
    small_catagory_url = scrapy.Field()
    # 小分类名称
    small_catagory_name = scrapy.Field()


class JdProductItem(scrapy.Item):
    """
    京东商品详细信息项
    """
    # 商品类别
    catagory = scrapy.Field()
    # 商品类别id
    catagory_id = scrapy.Field()
    # 商品ID
    sku_id = scrapy.Field()
    # 商品店铺id
    venderid = scrapy.Field()
    # 商品名称
    name = scrapy.Field()
    # 商品图片url
    img_url = scrapy.Field()
    # 商品选项
    options = scrapy.Field()
    # 商品店铺
    shop = scrapy.Field()
    # 商品评论数量
    comments = scrapy.Field()
    # 商品促销
    ad = scrapy.Field()
    # 商品价格
    price = scrapy.Field()
