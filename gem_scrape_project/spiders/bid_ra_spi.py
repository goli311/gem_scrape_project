import requests
import scrapy
from datetime import date, timedelta
from gem_scrape_project.config import *
import scrapy.selector
import os
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]

def user_agent_get():
    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
    user_agent = user_agent_rotator.get_random_user_agent()
    return user_agent

class MainScrape(scrapy.Spider):
    name = 'spi1'

    def start_requests(self):
            try:
                ck=None
                for j in range(5):
                    ck=get_cookie()
                    print("cookie",ck)
                    if ck:
                        break
                if ck:
                    for i in ck:
                        key_name_get = i.get('name')
                        if key_name_get == "ci_session":
                            session_value = i.get('value')
                            print("session id:", session_value)

                        if key_name_get == "csrf_gem_cookie":
                            csrf_value = i.get('value')
                            print("csrf", csrf_value)
            except Exception as E:
                print("error in selenium request",E)

            url = "https://bidplus.gem.gov.in/bidresultlists"
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Cookie': 'csrf_gem_cookie=7927906ba102ebbd530f64321e4a877c; ci_session=9f764284c9b31b0f82b470fa8fa77d1714c97f4d;',
                # 'Cookie': f'csrf_gem_cookie={csrf_value}; ci_session={session_value};',
                'Referer': 'https://bidplus.gem.gov.in/bidlists',
                "user-agent": user_agent_get(),
            }

            yield scrapy.FormRequest(url=url, callback=self.parse, headers=headers,
                                     meta={'url': url ,'headers':headers})

    def parse(self, response):
        try:
            print("current url:",response.url)
            h1 = response.meta.get('headers')
            print("response",response)
            if response.status==200:
                with open('main_response.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                for i in response.xpath('//div[@class="border block"]'):
                    if i.xpath('.//input[@value="View BID Results"]/parent::a/@href'):

                        # items=i.xpath('.//p//strong[contains(text(),"Items:")]/following-sibling::span//text()').get()
                        bid_result_link = i.xpath('.//input[@value="View BID Results"]/parent::a/@href').get()
                        final_bid_result_link = f"https://bidplus.gem.gov.in{bid_result_link}"

                        bid_response_get = requests.get(url=final_bid_result_link, headers=h1)
                        print("BId Response", bid_response_get)
                        if bid_response_get.status_code == 200:
                            with open('bid_response.html', 'w', encoding='utf-8') as f:
                                f.write(bid_response_get.text)
                            bid_response_txt = bid_response_get.text
                            bid_response = scrapy.Selector(text=bid_response_txt)

                            try:
                                bid_rano_text_get = bid_response.xpath(
                                    './/div[@class="block_bid_no"]//a[contains(text(),"Bid Number")]//following-sibling::span//text()').get()
                                print("bid no:", bid_rano_text_get)
                                ministry = bid_response.xpath(
                                    './/p//strong[contains(text(),"Ministry:")]//following-sibling::span//text()').get()
                                organization = bid_response.xpath(
                                    './/p//strong[contains(text(),"Organisation:")]//following-sibling::span//text()').get()
                                state = bid_response.xpath(
                                    './/p//strong[contains(text(),"Address:")]//following-sibling::span//text()').get()


                                """seller datas"""
                                tbody_get = bid_response.xpath(
                                    '//a[contains(text(),"TECHNICAL EVALUATION")]//parent::h4//parent::div//following-sibling::div//table/tbody/tr')
                                if tbody_get:
                                    for j in tbody_get:
                                        print('---------------------------------')
                                        seller_name_get = j.xpath('.//td[2]//text()')
                                        seller_name = seller_name_get.get().strip() if seller_name_get else ""
                                        print(seller_name)

                                        offered_item_get = [i.strip() for i in j.xpath('.//td[3]/p//text()').getall() if
                                                            i.strip()]
                                        # print('offered_item_get:',offered_item_get)
                                        make_get = ''
                                        model_get = ''
                                        for l in offered_item_get:
                                            if 'Make  :' in l or 'Make' in l:
                                                make_get = l.replace('Make  :', '').strip()
                                            elif 'Model  :' in l or 'Model' in l:
                                                model_get = l.replace('Model  :', '').strip()
                                        print('make_get:', make_get, '\nmodel_get:', model_get)

                                        participate_on_get = j.xpath('.//td[4]//text()')
                                        participate_on = participate_on_get.get().strip() if participate_on_get else ""
                                        print('participate_on:', participate_on)

                                        status_get = j.xpath('.//td[6]/span//text()')
                                        status = status_get.get().strip() if status_get else ""
                                        print('status:', status)

                            except Exception as E:
                                print("error in bid xpath", E)

            """pagination"""
            if response.xpath('//ul[@class="pagination"]//a[@rel="next"]/@href'):
                next_page_link=response.xpath('//ul[@class="pagination"]//a[@rel="next"]/@href').get()
                final_next_page_link=f"https://bidplus.gem.gov.in{next_page_link}"
                print("next page..",final_next_page_link)
                yield scrapy.FormRequest(url=final_next_page_link, callback=self.parse, headers=h1,
                                         meta={'url': final_next_page_link, 'headers': h1})


        except Exception as E:
            print("error in parse",E)


from scrapy.cmdline import execute
execute('scrapy crawl spi1'.split())