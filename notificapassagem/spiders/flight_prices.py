import scrapy
from selenium import webdriver
from notificapassagem.items import FlightItem

class FlightPricesSpider(scrapy.Spider):
    name = "flight_prices"
    allowed_domains = ["decolar.com"]
    start_urls = [
        "http://www.decolar.com/shop/flights/results/roundtrip/REC/RIO/2015-01-09/2015-01-12/1/0/0",
        "http://www.decolar.com/shop/flights/results/roundtrip/REC/BHZ/2015-02-13/2015-02-19/1/0/0"
    ]

    def parse(self, response):
        browser = webdriver.Firefox()
        browser.implicitly_wait(10)
        try:
            browser.get(response.url)
            price_table = browser.find_element_by_class_name('matrix-container')
            airlines = price_table.find_elements_by_class_name('matrix-airline')
            for airline in airlines:
                flight = FlightItem()
                prices = airline_elem.find_elements_by_css_selector('.amount')
                flight['airline'] = airline_elem.find_element_by_css_selector('.airline-name').text
                flight['lowest_price'] = min([int(price.text.replace('.', '')) for price in prices])
                yield airline
        finally:
            browser.quit()
