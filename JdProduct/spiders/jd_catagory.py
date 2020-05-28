# -*- coding: utf-8 -*-
import scrapy
import json
from JdProduct.items import JdCatagoryItem


class JdCatagorySpider(scrapy.Spider):
    name = 'jd_catagory'
    allowed_domains = ['3.cn']
    start_urls = ['https://dc.3.cn/category/get']

    def parse(self, response):
        # 获取数据
        ruslt = response.body.decode('utf-8', 'ignore')
        # 转为json格式
        json_data = json.loads(ruslt)
        # 解析数据，获取分类列表
        big_datas = json_data['data']
        # 遍历大分类列表
        for data in big_datas:
            # 创建商品分类item
            catagory = JdCatagoryItem()
            # 获取大分类信息
            big_data = data['s'][0]
            # 获取大分类url和名称
            big_catagory_url, big_catagory_name = self.get_url_and_name(big_data['n'])
            catagory['big_catagory_url'] = big_catagory_url
            catagory['big_catagory_name'] = big_catagory_name

            # 获取中分类列表
            middle_datas = big_data['s']
            # 遍历中分类列表
            for middle_data in middle_datas:
                # 获取中分类url和名称
                middle_catagory_url, middle_catagory_name = self.get_url_and_name(middle_data['n'])
                catagory['middle_catagory_url'] = middle_catagory_url
                catagory['middle_catagory_name'] = middle_catagory_name

                # 获取小分类列表
                small_datas = middle_data['s']
                # 遍历小分类列表
                for small_data in small_datas:
                    # 获取小分类url和名称
                    small_catagory_url, small_catagory_name = self.get_url_and_name(small_data['n'])
                    catagory['small_catagory_url'] = small_catagory_url
                    catagory['small_catagory_name'] = small_catagory_name
                    # 将item交给引擎
                    yield catagory

    @staticmethod
    def get_url_and_name(info):
        """
        从类别信息中提取url和名称
        :param info: 分类的信息
        :return:
        """
        # 将信息分割
        result = info.split('|')
        # 判断数据是否异常
        if result and len(result) > 1:
            # 获取url和名称
            catagory_url = result[0]
            catagory_name = result[1]
            # 判断url类型
            # url分为3种类型：
            # 1. list.jd.com/list.html?cat=737,794,798 => https://list.jd.com/list.html?cat=737,794,798
            # 2. 6144-6174                             => https://channel.jd.com/6144-6174.html
            # 3. 15901-15904-15933                     => https://list.jd.com/list.html?cat=15901,15904,15933
            if catagory_url.count('jd.com') == 1:
                catagory_url = 'https://' + catagory_url
            elif catagory_url.count('-') == 1:
                catagory_url = 'https://channel.jd.com/{}.html'.format(catagory_url)
            else:
                catagory_url = catagory_url.replace('-', ',')
                catagory_url = 'https://list.jd.com/list.html?cat={}'.format(catagory_url)

            return catagory_url, catagory_name
