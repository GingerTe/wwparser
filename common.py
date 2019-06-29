# coding: utf-8
import datetime
import os
import re
import lxml.html as html

import params

DATE_FORMAT = '%d.%m.%Y %H:%M:%S'


class Parser:
    PARAMS_REGEXP = re.compile(r'.*\d+/\d+ 🍗\d+% 🔋\d+/\d+ 👣(\d+)+км(.*)')

    def __init__(self, user, dir_):
        self.doc = None

        self.user = user
        self.dir = dir_

        self.current_line = ''

    def _fix_br(self):
        for br in self.doc.xpath("*//br"):
            br.tail = "\n" + br.tail if br.tail else "\n"

    def parse(self, ):
        for name in self._get_html_files():
            self._parse_document(os.path.join(self.dir, name))

    def _get_html_files(self):
        res = []
        for file_name in os.listdir(self.dir):
            if file_name.endswith('.html'):
                res.append(file_name)

        res.sort(key=lambda x: int(''.join([y for y in x if y.isdigit()]) if ''.join([y for y in x if y.isdigit()]) else '0'))
        return res

    def _parse_document(self, file_name):
        with open(file_name, encoding='utf8') as file_doc:
            self.doc = html.document_fromstring(file_doc.read())
        body = self.doc.find_class('body')

        self._fix_br()

        for block in body:
            try:
                self._parse_block(block)
            except:
                break

    def _parse_block(self, block):
        raise NotImplementedError

    def _format_km(self, data):
        km = self.PARAMS_REGEXP.match(self.current_line).group(1)
        data.km = int(km)

    def _format_location_and_zone(self, data):
        data.location = self.current_line
        # Убираем владельца локации
        if '(' in data.location:
            data.location = data.location[:data.location.index('(')]
        # Определяем зону
        if data.location.startswith('🚷'):
            data.zone = 'dark'
            data.location = data.location[2:].strip()
        data.location = params.EVENT_LOCATION_REL.get(data.location, data.location).strip()

    @staticmethod
    def _get_msg(block):
        msg = block.find_class('text')
        if msg:
            msg = msg[0]
            return msg.text_content().strip()

    @staticmethod
    def _get_date(block):
        msg_date = None
        date_element = block.find_class('date')
        if date_element:
            date_string = date_element[0].attrib['title']
            msg_date = datetime.datetime.strptime(date_string, DATE_FORMAT)
        return msg_date
