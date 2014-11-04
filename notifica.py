#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import getpass
import json
import requests
import smtplib
import time
import traceback

from email.mime.text import MIMEText

FLIGHTS = [
]

RECIPIENT_LIST = (
)

SENDER_GMAIL = 

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

def get_lowest_prices():
    prices = []
    for flight in FLIGHTS:
        req = requests.get(flight['url'], headers=flight['headers'])
        resp = json.loads(req.text)
        lowest_price = int(resp['result']['data']['lowestFare'][0]['raw']['amount']);
        if not flight['last_price'] or lowest_price < flight['last_price']:
            prices.append(u'%s: R$%d' % (flight['name'], lowest_price))
        flight['last_price'] = lowest_price
    if not prices:
        return None
    return u'\r\n'.join(prices)

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
