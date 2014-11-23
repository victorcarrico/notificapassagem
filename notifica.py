#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import getpass
import json
import requests
import smtplib
import time
import traceback

from selenium import webdriver
from email.mime.text import MIMEText

from notifica_settings import *


FLIGHTS = [{'url': flight, 'last_price': None} for flight in FLIGHT_URLS]

def _get_number(element):
    return int(element.text.replace('.', ''))

def start_smtp_session(password):
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.ehlo()
    session.starttls()
    session.login(SENDER_GMAIL, password)
    return session

def send_email(msg_text, password):
    msg = MIMEText(msg_text.encode('utf-8'))
    msg['Subject'] = u'Menores preços de passagens às %s' % (
        datetime.datetime.now().strftime('%H:%M %d/%m/%y'))
    msg['From'] = SENDER_GMAIL
    msg['To'] = ','.join(RECIPIENT_LIST)
    session = start_smtp_session(password)
    session.sendmail(msg['From'], RECIPIENT_LIST, msg.as_string())

def get_and_parse(url):
    browser = webdriver.Firefox()
    browser.implicitly_wait(10)
    try:
        browser.get(url)
        lowest_prices = {}
        items = browser.find_element_by_class_name('cluster').find_elements_by_class_name('data')
        name = '; '.join([item.text.replace('\n', ' ').replace('\r', '') for item in items])

        price_table = browser.find_element_by_class_name('matrix-container')
        airlines = price_table.find_elements_by_class_name('matrix-airline')
        for airline_elem in airlines:
            prices = airline_elem.find_elements_by_css_selector('.amount')
            airline = airline_elem.find_element_by_css_selector('.airline-name').text
            lowest_prices[airline] = min([_get_number(price) for price in prices])

        browser.find_element_by_class_name('flights-tab-priceSuggestionMatrix').click()
        prices_on_3_day_range = browser.find_elements_by_css_selector(
            '#price-suggestion-matrix .price-suggestion-matrix-content .price-amount')
        lowest_price_on_3_day_range = min([_get_number(price) for price in prices_on_3_day_range])

        return {
            'name': name,
            'lowest_price': min(lowest_prices.values()),
            'lowest_price_on_3_day_range': lowest_price_on_3_day_range
        }
    finally:
        browser.quit()

def get_lowest_prices():
    prices = []
    for flight in FLIGHTS:
        info = get_and_parse(flight['url'])

        lower_price = 'last_price' not in flight or info['lowest_price'] < flight['last_price']
        lower_price_on_3_day_range = ('last_price_on_3_day_range' not in flight or
            info['lowest_price_on_3_day_range'] < flight['last_price_on_3_day_range'])
        if lower_price or lower_price_on_3_day_range:
            text = ((u'%s\r\n'
                    u'Menor preço: R$%d\r\n'
                    u'Menor preço de outros trechos em uma variação de até 3 dias: R$%d') %
                    (info['name'], info['lowest_price'], info['lowest_price_on_3_day_range']))
            prices.append(text)

        flight['last_price'] = info['lowest_price']
        flight['last_price_on_3_day_range'] = info['lowest_price_on_3_day_range']
    if not prices:
        return None
    return u'\r\n\r\n'.join(prices)

if __name__ == '__main__':
    print 'Digite a senha do email abaixo'
    password = getpass.getpass()
    session = start_smtp_session(password)
    while True:
        try:
            prices = get_lowest_prices()
            if prices:
                print '--- Conteúdo do email a ser enviado ---'
                print prices
                print ''
                send_email(prices, password)
            else:
                print '--- Nenhum preço de passagem caiu ---'
                print ''
        except:
            print u'[%s] Erro:' % datetime.datetime.now().strftime('%H:%M:%S %d/%m/%y')
            traceback.print_exc()
            print ''
        time.sleep(1800)
