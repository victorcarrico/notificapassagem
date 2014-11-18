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
            lowest_prices[airline] = min([int(price.text.replace('.', '')) for price in prices])
        return {'name': name, 'lowest_price': min(lowest_prices.values())}
    finally:
        browser.quit()

def get_lowest_prices():
    prices = []
    for flight in FLIGHTS:
        info = get_and_parse(flight['url'])
        if not flight['last_price'] or info['lowest_price'] < flight['last_price']:
            prices.append(u'%s\r\nMenor preço: R$%d' % (info['name'], info['lowest_price']))
        flight['last_price'] = info['lowest_price']
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
