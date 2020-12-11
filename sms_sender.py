# -*- coding: utf-8 -*-
import sys
import requests
import json
from datetime import datetime
import xml.etree.cElementTree as ET

try:
    from bs4 import BeautifulSoup
except:
    pass


class SMS():
    def __init__(self):
        self.message = ''
        self.send_to = []


class SendSMS():
    def __init__(self, operator):
        self.URL = self.proxy(operator)['web']
        self.default_page = self.URL + 'html/index.html'
        self.sms_sender_URL = self.URL + 'html/smsinbox.html'
        self.sms_send_url = self.URL + 'api/sms/send-sms'
        self.csrf_token_pattern = '<meta name="csrf_token" content="'
        self.csrf_token_name = "csrf_token"
        self.sms_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.session = requests.Session()
        self.token = ''

    def send(self, sms, operator):
        self.create_session(operator)
        self.get_token(operator)
        data = self.merge_template(sms)
        proxy = self.proxy(operator)['ip']
        headers = {}
        headers['__RequestVerificationToken'] = self.token
        headers['X-Requested-With'] = 'XMLHttpRequest'
        headers['Content-Type'] = 'text/xml'
        proxies = {
            "http": proxy,
            "https": proxy
        }
        response = self.session.post(self.sms_send_url, data=data, headers=headers, proxies=proxies)

    def proxy(self, operator):
        proxy_dict = {
            'Beeline': {
                'web': 'http://192.168.12.10/',
                'ip': '192.168.1.101:8123'
            },
            'Megafon': {
                'web': 'http://192.168.142.10/',
                'ip': '192.168.1.103:8123'
            },
            'Yota': {
                'web': 'http://192.168.95.95/',
                'ip': '192.168.1.104:8123'
            },
            'Tele2': {
                'web': 'http://192.168.8.1/',
                'ip': '192.168.1.112:8123'
            }
        }
        return proxy_dict[operator]

    def create_session(self, operator):
        proxy = self.proxy(operator)['ip']
        proxies = {
            "http": proxy,
            "https": proxy
        }
        response = self.session.get(self.default_page, proxies=proxies)

    def get_token(self, operator):
        proxy = self.proxy(operator)['ip']
        proxies = {
            "http": proxy,
            "https": proxy
        }
        response = self.session.get(self.sms_sender_URL, proxies=proxies)
        if 'bs4' not in sys.modules:
            token_start = response.text.find(self.csrf_token_pattern)
            if token_start != -1:
                token_start += len(self.csrf_token_pattern)
                token_end = token_start + response.text[token_start:].find('"')
                self.token = response.text[token_start:token_end]

        else:
            soup = BeautifulSoup(response.text, "html.parser")
            for token in soup.findAll('meta', attrs={'name': self.csrf_token_name}):
                self.token = token['content']
                break

    def merge_template(self, sms):
        request = ET.Element("request")
        pageindex = ET.SubElement(request, "Index")
        pageindex.text = "-1"

        phones = ET.SubElement(request, "Phones")
        sca = ET.SubElement(request, "Sca")
        content = ET.SubElement(request, "Content")
        length = ET.SubElement(request, "Length")
        reserved = ET.SubElement(request, "Reserved")
        reserved.text = "1"
        date = ET.SubElement(request, "Date")

        for number in sms.send_to:
            phone = ET.SubElement(phones, "Phone")
            phone.text = number

        content.text = sms.message
        length.text = str(len(sms.message))
        date.text = self.sms_time
        return (ET.tostring(request, 'utf-8', method="xml"))
