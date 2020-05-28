# -*- coding: utf-8 -*-
import scrapy
import json
import pickle
import re
from jsonpath import jsonpath
from scrapy_redis.spiders import RedisSpider
from JdProduct.items import JdProductItem
from JdProduct.settings import JD_PRODUCT_REDIS_KEY


class JdProductSpider(RedisSpider):
    name = 'jd_product'
    allowed_domains = ['jd.com', '3.cn']
    redis_key = JD_PRODUCT_REDIS_KEY

    # 使用redis分布式，需将start_requests方法改为make_request_from_data方法
    # def start_requests(self):
    #     catagory = {
    #         "big_catagory_url": "https://jiadian.jd.com",
    #         "big_catagory_name": "家用电器", "middle_catagory_url": "https://list.jd.com/list.html?cat=737,794,798",
    #         "middle_catagory_name": "电视",
    #         "small_catagory_url": "https://list.jd.com/list.html?cat=737,794,798",
    #         "small_catagory_name": "超薄电视"
    #     }
    #     yield scrapy.Request(url=catagory['small_catagory_url'], callback=self.parse, meta={'catagory': catagory})

    # 重写make_request_from_data方法
    def make_request_from_data(self, data):
        # 从redis数据库中取出catagory并反序列化
        catagory = pickle.loads(data)
        return scrapy.Request(url=catagory['small_catagory_url'], callback=self.parse, meta={'catagory': catagory})

    def parse(self, response):
        # 获取商品类别
        catagory = response.meta['catagory']
        # 获取商品sku列表
        products = response.xpath("//div[@class='gl-i-wrap j-sku-item']")
        for product_info in products:
            # 创建商品详细信息item
            product = JdProductItem()
            # 获取商品类别id
            catagory_id = re.findall('cat=(.+)', catagory['small_catagory_url'])
            if catagory_id:
                catagory_id = catagory_id[0]
                if catagory_id.count('.') > 0:
                    catagory_id = catagory_id.replace('.', ',')
            else:
                catagory_id = ''
            # 获取商品id
            sku_id = product_info.xpath('./@data-sku').extract_first()
            # 获取商品店铺id
            venderid = product_info.xpath('./@venderid').extract_first()
            product['catagory'] = catagory
            product['catagory_id'] = catagory_id
            product['sku_id'] = sku_id if sku_id else ''
            product['venderid'] = venderid if venderid else ''
            # 商品name，img_url，options信息的url
            product_url = 'https://cdnware.m.jd.com/c1/skuDetail/apple/7.3.0/{}.json'.format(product['sku_id'])
            yield scrapy.Request(url=product_url, callback=self.parse_options, meta={'product': product})

        # 获取下一页url
        next_url = response.xpath("//a[@class='pn-next']/@href").extract_first()
        # 判断是否有下一页
        if next_url:
            # 补全url
            next_url = response.urljoin(next_url)
            # 请求下一页数据
            yield scrapy.Request(url=next_url, callback=self.parse, meta={'catagory': catagory})

    def parse_options(self, response):
        # 获取商品item
        product = response.meta['product']
        # 获取数据
        ruslt = response.body.decode('utf-8', 'ignore')
        # 转为json格式
        json_data = json.loads(ruslt)
        # 获取商品name,img_url,options
        name = jsonpath(json_data, '$..wareInfo.basicInfo.name')
        img_url = jsonpath(json_data, '$..wareInfo.basicInfo.chatUrl')
        options = jsonpath(json_data, '$..colorSizeInfo..colorSize')
        product['name'] = name if name else ''
        # https://m.360buyimg.com/n3/jfs/t1/85010/16/15514/325066/5e6f7495Ea89197ec/40a5449b7770747c.jpg.webp =>
        # https://m.360buyimg.com/n1/jfs/t1/85010/16/15514/325066/5e6f7495Ea89197ec/40a5449b7770747c.jpg
        # 判断是否有图片信息
        if img_url:
            img_url = img_url[0].replace('.com/n3/', '.com/n1/').replace('.jpg.webp', '.jpg')
            product['img_url'] = img_url
        else:
            product['img_url'] = ''
        # 判断是否有分类信息
        if options:
            # 将分类信息存储在dict中
            option_dict = {}
            # 依次遍历各个分类信息
            for option in options[0]:
                # 获取选项类别
                key = jsonpath(option, '$..title')[0] if jsonpath(option, '$..title') else ' '
                # 获取选项值
                value = jsonpath(option, '$..text')
                option_dict[key] = value
            product['options'] = option_dict
        else:
            product['options'] = {}
        # 商品店铺信息的url
        product_url = 'https://c0.3.cn/stock?skuId={}&area=7_446_452_37445&venderId={}&cat={}' \
            .format(product['sku_id'], product['venderid'], product['catagory_id'])
        yield scrapy.Request(url=product_url, callback=self.parse_price_shop, meta={'product': product})

    def parse_price_shop(self, response):
        # 获取商品item
        product = response.meta['product']
        # 获取数据
        ruslt = response.body.decode('utf-8', 'ignore')
        # 转为json格式
        json_data = json.loads(ruslt)
        # 获取商品shop，price
        price = jsonpath(json_data, '$..jdPrice.p')
        shop = jsonpath(json_data, '$..deliver')
        product['price'] = price[0] if price else ''
        product['shop'] = shop[0] if shop else '京东自营'
        # 商品评价信息的url
        product_url = 'https://club.jd.com/comment/productCommentSummaries.action?referenceIds={}' \
            .format(product['sku_id'])
        yield scrapy.Request(url=product_url, callback=self.parse_comments, meta={'product': product})

    def parse_comments(self, response):
        # 获取商品item
        product = response.meta['product']
        # 获取数据
        ruslt = response.body.decode('utf-8', 'ignore')
        # 转为json格式
        json_data = json.loads(ruslt)
        # 获取商品店铺
        comments = jsonpath(json_data, '$..CommentsCount')
        # jsonpath返回类型是列表,comments
        product['comments'] = comments[0][0] if comments else ''
        # 商品促销信息的url
        product_url = 'https://cd.jd.com/promotion/v2?skuId={}&area=7_446_452_37445&cat={}' \
            .format(product['sku_id'], product['catagory_id'])
        yield scrapy.Request(url=product_url, callback=self.parse_ad, meta={'product': product})

    def parse_ad(self, response):
        # 获取商品item
        product = response.meta['product']
        # 获取数据
        ruslt = response.body.decode('utf-8', 'ignore')
        # 转为json格式
        json_data = json.loads(ruslt)
        # 获取商品店铺
        ad = jsonpath(json_data, '$..ads..ad')
        # jsonpath返回类型是列表
        product['ad'] = ad[0] if ad else ''
        # 将数据交给引擎
        yield product
