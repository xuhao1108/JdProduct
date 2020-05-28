# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html


# class JdSpiderSpiderMiddleware(object):
#     # Not all methods need to be defined. If a method is not defined,
#     # scrapy acts as if the spider middleware does not modify the
#     # passed objects.
#
#     @classmethod
#     def from_crawler(cls, crawler):
#         # This method is used by Scrapy to create your spiders.
#         s = cls()
#         crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
#         return s
#
#     def process_spider_input(self, response, spider):
#         # Called for each response that goes through the spider
#         # middleware and into the spider.
#
#         # Should return None or raise an exception.
#         return None
#
#     def process_spider_output(self, response, result, spider):
#         # Called with the results returned from the Spider, after
#         # it has processed the response.
#
#         # Must return an iterable of Request, dict or Item objects.
#         for i in result:
#             yield i
#
#     def process_spider_exception(self, response, exception, spider):
#         # Called when a spider or process_spider_input() method
#         # (from other spider middleware) raises an exception.
#
#         # Should return either None or an iterable of Request, dict
#         # or Item objects.
#         pass
#
#     def process_start_requests(self, start_requests, spider):
#         # Called with the start requests of the spider, and works
#         # similarly to the process_spider_output() method, except
#         # that it doesn’t have a response associated.
#
#         # Must return only requests (not items).
#         for r in start_requests:
#             yield r
#
#     def spider_opened(self, spider):
#         spider.logger.info('Spider opened: %s' % spider.name)
#
#
# class JdSpiderDownloaderMiddleware(object):
#     # Not all methods need to be defined. If a method is not defined,
#     # scrapy acts as if the downloader middleware does not modify the
#     # passed objects.
#
#     @classmethod
#     def from_crawler(cls, crawler):
#         # This method is used by Scrapy to create your spiders.
#         s = cls()
#         crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
#         return s
#
#     def process_request(self, request, spider):
#         # Called for each request that goes through the downloader
#         # middleware.
#
#         # Must either:
#         # - return None: continue processing this request
#         # - or return a Response object
#         # - or return a Request object
#         # - or raise IgnoreRequest: process_exception() methods of
#         #   installed downloader middleware will be called
#         return None
#
#     def process_response(self, request, response, spider):
#         # Called with the response returned from the downloader.
#
#         # Must either;
#         # - return a Response object
#         # - return a Request object
#         # - or raise IgnoreRequest
#         return response
#
#     def process_exception(self, request, exception, spider):
#         # Called when a download handler or a process_request()
#         # (from other downloader middleware) raises an exception.
#
#         # Must either:
#         # - return None: continue processing this exception
#         # - return a Response object: stops process_exception() chain
#         # - return a Request object: stops process_exception() chain
#         pass
#
#     def spider_opened(self, spider):
#         spider.logger.info('Spider opened: %s' % spider.name)


import requests
import random
import re
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from JdProduct.settings import PROXY_URL
from JdProduct.settings import USER_AGENTS_LIST


class JdSpiderHeadersMiddleware(object):
    def process_request(self, request, spider):
        # 判断是否为手机抓包的请求
        if request.url.startswith('https://cdnware.m.jd.com'):
            # 设置为手机请求头
            request.headers['User-Agent'] = 'JD4iPhone/164880 (iPhone; iOS 12.1.2; Scale/2.00)'
        else:
            # 随机获取一个请求头
            request.headers['User-Agent'] = random.choice(USER_AGENTS_LIST)
        return None


class JdSpiderProxyMiddleware(object):
    def process_request(self, request, spider):
        # 随机获取一个代理ip
        proxy = self.get_random_proxy()
        if proxy:
            # 设置代理ip
            request.meta['proxy'] = proxy
        return None

    def process_response(self, request, response, spider):
        if response.status != 200:
            # 随机获取一个代理ip
            proxy = self.get_random_proxy()
            if proxy:
                # 设置代理ip
                request.meta['proxy'] = proxy
            return request
        return response

    def process_exception(self, request, exception, spider):
        # 判断当前异常
        if isinstance(exception, RetryMiddleware.EXCEPTIONS_TO_RETRY):
            # 获取异常的代理ip的url
            proxy = request.meta['proxy']
            # 获取代理ip位置
            # 截取代理ip
            ip = re.findall('://(.+):', proxy)[0] if re.findall('://(.+):', proxy) else ''
            # 设置此代理ip的不可用域名
            url = '{}/disable_domain'.format(PROXY_URL)
            # 参数
            params = {
                'ip': ip,
                'domain': 'jd.com'
            }
            # 更新此代理ip的不可用域名
            requests.get(url, params=params)
            return request

    def get_random_proxy(self):
        # 获取代理ip的url
        url = '{}/random'.format(PROXY_URL)
        # 参数
        params = {
            'protocol': 'https',
            'domain': 'jd.com'
        }
        # 发送请求，获取代理ip
        response = requests.get(url, params=params)
        return response.text
