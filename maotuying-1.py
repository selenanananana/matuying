# #爬取tripadvisor纽约市酒店超值排名
#
# #引入requests 获取html文件，才能从html获取信息
# import requests
# #利用BeautifulSoup解析文件，获取想要的到的数据
# from bs4 import BeautifulSoup
# #这段代码只用在获取等待，避免频繁访问ip被封禁
# import time
#
# #url = 'https://www.tripadvisor.cn/Hotels-g60763-oa30-New_York_City_New_York-Hotels.html'
# #获取全部的url。每一页的url不同
# urls = ['https://www.tripadvisor.cn/Hotels-g294245-Philippines-Hotels.html'.format(str(i)) for i in range(0,720,30)]
# #利用headers假装是浏览器，可以在网页检查，NetWork里面找
# header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
#
# #定义函数找到所需要的信息
# def get_hotel(url):
# #每次调用等待两秒
#     time.sleep(10)
#     #利用requests请求的到html
#     resp = requests.get(url)
#     #利用BeautifulSoup解析，利用率lxml解析库
#     soup = BeautifulSoup(resp.text,'lxml')
#
# #css选选择器选择所需要的信息，包括标题，价格，和排名
# #imgs = soup.select('div.aspect.is-hidden-tablet > div.inner')
#     titles = soup.select('div.listing_title > a[target="_blank"]')
#     paimings = soup.select('div.popindex')
#     prices = soup.select('div.xwrap')
#
# #存储在一个字典里面
#     for title,paiming,price in zip(titles,paimings,prices):
#         data = {
#             'title':title.get_text(),
#             'paiming':paiming.get_text(),
#             'price':price.get_text(),
#         }
#         print(data)
#
# #对每一个页面都爬取，
# for url in urls:
#     get_hotel(url)
#
#
# # # 定义输出文件路径
# # output_file = 'result.txt'
# #
# # # 创建并打开文件以进行写入操作
# # with open(output_file, 'w', encoding='utf-8') as file:
# #     # 对每一个页面都爬取
# #     for url in urls:
# #         get_hotel(url, file)
# #
# #
# # # 在 get_hotel 函数中传入文件参数
# # def get_hotel(url, file):
# #     time.sleep(2)
# #     resp = requests.get(url)
# #     soup = BeautifulSoup(resp.text, 'lxml')
# #
# #     # ... 之前的代码保持不变
# #
# #     # 将结果写入文件而不是打印出来
# #         for title, paiming, price in zip(titles, paimings, prices):
# #             data = {
# #                 'title': title.get_text(),
# #                 'paiming': paiming.get_text(),
# #                 'price': price.get_text(),
# #         }
# #         file.write(str(data) + '\n')


import requests
from bs4 import BeautifulSoup
import time

output_file = 'result.txt'
urls = ['https://www.tripadvisor.cn/Hotels-g294245-Philippines-Hotels.html?page={}'.format(i) for i in range(0, 720, 30)]

# urls = ['https://www.tripadvisor.cn/Hotels-g294245-Philippines-Hotels.html'.format(str(i)) for i in range(0, 720, 30)]
header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}

def get_hotel(url, file):
    time.sleep(10)
    resp = requests.get(url, headers=header)
    soup = BeautifulSoup(resp.text, 'lxml')

    titles = soup.select('div.listing_title > a[target="_blank"]')
    paimings = soup.select('div.popindex')
    prices = soup.select('div.xwrap')

    for title, paiming, price in zip(titles, paimings, prices):
        data = {
            'title': title.get_text(),
            'paiming': paiming.get_text(),
            'price': price.get_text(),
        }
        file.write(str(data) + '\n')

with open(output_file, 'a', encoding='utf-8') as file:
    for url in urls:
        get_hotel(url, file)
#这个代码爬取不出来东西




#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2018-09-06 11:16:59
# Project: trip_hotel

from pyspider.libs.base_handler import *
import datetime
import re
import json
import copy

from pymongo import MongoClient

# 连接线下数据库
DB_IP = ''
DB_PORT =

#DB_IP = '127.0.0.1'
#DB_PORT = 27017

client = MongoClient(host=DB_IP, port=DB_PORT)

# admin 数据库有帐号，连接-认证-切换
db_auth = client.admin
db_auth.authenticate("", "")

DB_NAME = 'research'
db = client[DB_NAME]



def get_today():
    return datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%d'), '%Y-%m-%d')

class Handler(BaseHandler):
    crawl_config = {
        'headers': {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
                   'cookie':'SetCurrency=USD'},
        'proxy': 'http://10.15.100.94:6666',
        'retries': 5
    }

    url = 'https://www.tripadvisor.com/'
    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl(self.url, callback=self.index_page)

    @config(age=60)
    def index_page(self, response):
        page = response.etree

        city_list = page.xpath("//div[@class='customSelection']/div[@class='boxhp collapsibleLists']/div[@class='section']/div[@class='ui_columns' or @class='ui_columns no-collapse']/ul[@class='lst ui_column is-4']/li[@class='item']")

        print(len(city_list))
        base_url = 'https://www.tripadvisor.com'
        for each in city_list:
            city_name = each.xpath("./a/text()")[0]
            city_link = base_url + each.xpath("./a/@href")[0]

            print(city_name, '---', city_link)

            save = {"city": city_name}
            self.crawl(city_link, callback=self.parse_city, save=save)

    @config(age=60)
    def parse_city(self, response):
        page = response.etree
        base_url = 'https://www.tripadvisor.com'
        ## 国家
        country = page.xpath("//div[@id='taplc_trip_planner_breadcrumbs_0']/ul[@class='breadcrumbs']/li[1]/a/span/text()")[0]
        print(country)

        ## 第一需求表
        ## 翻页
        #page_list = [response.url]
        #page_list.extend([base_url+i for i in page.xpath("//div[@class='pageNumbers']/a/@href")])
        #print(len(page_list))
        save = {"country": country, "city": response.save["city"]}
        #for each in page_list:
        #    self.crawl(each, callback=self.parse_page, save=save)


        tail_url = page.xpath("//div[@class='pageNumbers']/a[last()]/@href")[0]
        total_num = re.findall('oa(\d+)-',tail_url)[0]
        page_url = base_url + tail_url.replace(total_num,'{}')
        print(page_url)
        total_page = int(total_num)//30
        for i in range(total_page+1):
            if i == 0:
                self.crawl(response.url, callback=self.parse_page, save=save)
            else:
                self.crawl(page_url.format(30*i), callback=self.parse_page, save=save)

        ## 第三个需求表
        new_url = response.url.replace('Hotels','Tourism').replace('Hotels', 'Vacations')
        print(new_url)
        self.crawl(new_url, callback=self.parse_detail, save=save)


    def parse_detail(self, response):
        page = response.etree

        hotel_num = page.xpath("//div[@class='navLinks']/ul/li[@class='hotels twoLines']//span[@class='typeQty']/text()")
        hotel_num = hotel_num[0] if hotel_num else ''
        print(hotel_num)
        hotel_reviews = page.xpath("//div[@class='navLinks']/ul/li[@class='hotels twoLines']//span[@class='contentCount']/text()")
        hotel_reviews = hotel_reviews[0] if hotel_reviews else ''
        print(hotel_reviews)

        rentals_num = page.xpath("//div[@class='navLinks']/ul/li[@class='vacationRentals twoLines']//span[@class='typeQty']/text()")
        rentals_num = rentals_num[0] if rentals_num else ''
        print(rentals_num)
        rentals_reviews = page.xpath("//div[@class='navLinks']/ul/li[@class='vacationRentals twoLines']//span[@class='contentCount']/text()")
        rentals_reviews = rentals_reviews[0] if rentals_reviews else ''
        print(rentals_reviews)

        thingstodo_num = page.xpath("//div[@class='navLinks']/ul/li[@class='attractions twoLines']//span[@class='typeQty']/text()")
        thingstodo_num = thingstodo_num[0] if thingstodo_num else ''
        print(thingstodo_num)
        thingstodo_reviews = page.xpath("//div[@class='navLinks']/ul/li[@class='attractions twoLines']//span[@class='contentCount']/text()")
        thingstodo_reviews = thingstodo_reviews[0] if thingstodo_reviews else ''
        print(thingstodo_reviews)

        restaurant_num = page.xpath("//div[@class='navLinks']/ul/li[@class='restaurants twoLines']//span[@class='typeQty']/text()")
        restaurant_num = restaurant_num[0] if restaurant_num else ''
        print(restaurant_num)
        restaurant_reviews = page.xpath("//div[@class='navLinks']/ul/li[@class='restaurants twoLines']//span[@class='contentCount']/text()")
        restaurant_reviews = restaurant_reviews[0] if restaurant_reviews else ''
        print(restaurant_reviews)

        forum_post = page.xpath("//div[@class='navLinks']/ul/li[@class='forum twoLines']//span[@class='contentCount']/text()")
        forum_post = forum_post[0] if forum_post else ''
        print(forum_post)


        result = {"country": response.save["country"],
                  "city": response.save["city"],
                  "hotel_num": hotel_num,
                  "hotel_reviews": hotel_reviews,
                  "rentals_num": rentals_num,
                  "rentals_reviews": rentals_reviews,
                  "thingstodo_num": thingstodo_num,
                  "thingstodo_reviews": thingstodo_reviews,
                  "restaurant_num": restaurant_num,
                  "restaurant_reviews": restaurant_reviews,
                  "forum_post": forum_post,
                  "date": get_today(),
                  "collection": 'trip_total_daily_data'
                 }

        yield result


    @config(age=60)
    def parse_page(self, response):
        page = response.etree
        ## 酒店列表
        #content_list = page.xpath("//div[@id='taplc_hsx_hotel_list_lite_dusty_hotels_combined_sponsored_0']/div[@class='prw_rup prw_meta_hsx_responsive_listing ui_section listItem  ']")
        content_list = page.xpath("//div[@id='taplc_hsx_hotel_list_lite_dusty_hotels_combined_sponsored_0']/div/div[@class!='prw_rup prw_common_ad_resp ui_section is-ad  ']")
        print(len(content_list))

        for each in content_list:
            price_1 = each.xpath(".//div[@class='priceBlock ui_column is-12-tablet']//div[@class='price autoResize']/text()")
            price_1 = (price_1[0] if price_1 else '')
            price_origin = each.xpath(".//div[@class='priceBlock ui_column is-12-tablet']//div[@class='xthrough autoResize']/div/text()")
            if price_origin:
                price_origin = price_origin[0]
            else:
                price_origin = ''

            hotel_name = each.xpath(".//div[@data-prwidget-name='meta_hsx_listing_name']//a/text()")[0]
            hotel_id = each.xpath(".//div[@data-prwidget-name='meta_hsx_listing_name']//a/@id")[0]
            print(hotel_name, hotel_id)
            print(price_1, price_origin)

            reviews = each.xpath(".//a[@class='review_count']/text()")[0]
            print(reviews)

            web_1 = each.xpath(".//div[@class='priceBlock ui_column is-12-tablet']//div[@class='provider autoResize']/text()")[0]
            print(web_1)

            web_2 = each.xpath(".//div[@class='text-links is-shown-at-tablet has_commerce']/div[1]/div[@class='vendor']/span/text()")
            web_2 = (web_2[0] if web_2 else '')

            price_2 = each.xpath(".//div[@class='text-links is-shown-at-tablet has_commerce']/div[1]/div[@class='price autoResize']/text()")
            price_2 = (price_2[0] if price_2 else '')
            print(web_2, price_2)

            web_3 = each.xpath(".//div[@class='text-links is-shown-at-tablet has_commerce']/div[2]/div[@class='vendor']/span/text()")
            web_3 = (web_3[0] if web_3 else '')
            price_3 = each.xpath(".//div[@class='text-links is-shown-at-tablet has_commerce']/div[2]/div[@class='price autoResize']/text()")
            price_3 = (price_3[0] if price_3 else '')
            print(web_3, price_3)

            web_4 = each.xpath(".//div[@class='text-links is-shown-at-tablet has_commerce']/div[3]/div[@class='vendor']/span/text()")
            web_4 = (web_4[0] if web_4 else '')
            price_4 = each.xpath(".//div[@class='text-links is-shown-at-tablet has_commerce']/div[3]/div[@class='price autoResize']/text()")
            price_4 = (price_4[0] if price_4 else '')
            print(web_4, price_4)

            result = {"date": get_today(),
                      "country": response.save["country"],
                      "city": response.save["city"],
                      "hotel_name": hotel_name,
                      "hotel_id": hotel_id,
                      "reviews": reviews,
                      "price_origin": price_origin,
                      "1_web": web_1,
                      "1_price": price_1,
                      "2_web": web_2,
                      "2_price": price_2,
                      "3_web": web_3,
                      "3_price": price_3,
                      "4_web": web_4,
                      "4_price": price_4,
                      "update_time": datetime.datetime.now(),
                      "collection": "trip_hotel_daily_data"
                     }

            yield result



    def on_result(self, result):
        super(Handler, self).on_result(result)
        if not result:
            return
        col_name = result.pop("collection")
        col = db[col_name]

        if col_name == 'trip_hotel_daily_data':
            update_key = {
                'date': result["date"],
                'hotel_id': result["hotel_id"]

            }
        elif col_name == 'trip_total_daily_data':
            update_key = {
                'date': result["date"],
                'city': result["city"]

            }


        col.update(update_key, {'$set': result}, upsert=True)
