import scrapy
from scrapy_selenium import SeleniumRequest
from scrapy.selector import Selector
import time 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

opts = Options()
opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36")
driver = webdriver.Chrome(chrome_options=opts)

class RoboticsSpider(scrapy.Spider):
    name = 'robotics'
    job_title = ""
    final_url = ""

    def start_requests(self):
        yield SeleniumRequest(url="https://www.naukri.com/robotics-jobs-in-india-remote?k=robotics&l=india%20remote&ctcFilter=101&ctcFilter=10to15&ctcFilter=15to25&ctcFilter=25to50&ctcFilter=50to75&ctcFilter=75to100",
                                wait_time=3, 
                                screenshot=True,
                                callback=self.parse
                                    )     

    def parse(self, response):
        
        driver = response.meta['driver']
        for jobs in response.xpath('//article'):
            tech_stack_list = []
            job_title = jobs.xpath('.//div[1]/div/a/text()').get()
            self.job_title = job_title
            job_link = jobs.xpath('.//div[1]/div/a/@href').get()
            experience_required = jobs.xpath('.//div[1]/div/ul/li[1]/span/text()').get()
            ctc = jobs.xpath('.//div[1]/div/ul/li[2]/span/text()').get()
            location = jobs.xpath('.//div[1]/div/ul/li[3]/span/text()').get()
            #responsibility = jobs.xpath('.//div[@class="job-description fs12 grey-text"]/text()[2]').get()
            tech_stack = jobs.xpath('.//ul/li')
            days = jobs.xpath('.//div[3]/div[2]/span/text()').get()
            for t in tech_stack:
                tech_stack_list.append(t.xpath('.//text()').get())

            yield{
                    'job_title': job_title,
                    'job_link': job_link,
                    'experience_required': experience_required,
                    'ctc': ctc,
                    'location': location,
                    #'responsibility': responsibility,
                    'tech_stack': tech_stack_list[3:],
                    'days': days
                }
            

        
        next_page = response.xpath('//div[@class="pagination mt-64 mb-60"]/a[2]/@href').get()

        name = re.sub("-|\/", "_", str(next_page))
        with open(f"{name}.png", 'wb') as image_file:
            image_file.write(response.meta['screenshot'])

        if next_page:
            absolute_url = f"https://www.naukri.com{next_page}?ctcFilter=101&ctcFilter=10to15&ctcFilter=15to25&ctcFilter=25to50&ctcFilter=50to75&ctcFilter=75to100"
            self.final_url = absolute_url
            yield SeleniumRequest(url=absolute_url,
                            wait_time = 20,
                            wait_until=EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div[3]/div[2]/section[2]/div[3]/a[2]')),
                            screenshot=True,
                            callback=self.parse
                 )
            

