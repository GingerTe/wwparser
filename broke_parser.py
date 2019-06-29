# coding: utf-8
import datetime
import os

import lxml.html as html

DATE_FORMAT = '%d.%m.%Y %H:%M:%S'


class Parser:

    def __init__(self):
        super(Parser, self).__init__()
        self.doc = None
        self.is_des = False
        self.kick = 0
        self.fights = 0
        self.pvp = 0
        self.mobs = 0
        self.weapon = 'Дезинтегратор'
        self.user = 'ник в игре'
        self.dir = 'me'

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
        if not file_name.endswith('.html'):
            return

        with open(file_name, encoding='utf8') as file_doc:
            self.doc = html.document_fromstring(file_doc.read())
        body = self.doc.find_class('body')

        for block in body:
            try:
                self._parse_block(block)
            except:
                break

    def _parse_block(self, block):
        msg_date = self._get_date(block)

        msg = self._get_msg(block)

        if not (msg_date and msg):
            return

        content = msg.text_content()
        if 'Получено' in content and self.weapon in content:
            print(f'{self.weapon} скрафчен {msg_date}')
        if 'Экипировано' in content:
            if self.weapon in content:
                self.is_des = True
                print(f'{self.weapon} экипирован {msg_date}')
            elif self.is_des:
                self.is_des = False
                print(f'{self.weapon} снят {msg_date}')

        if 'Сломано' in content and self.weapon in content:
            print(f"\n{self.weapon} сломан {msg_date}\n")
            raise Exception()

        if self.is_des:
            self.find_fight(content)

    def find_fight(self, msg: str):
        self.fights += 1
        if 'FIGHT' in msg:
            self.pvp += 1
            self.kick += msg.count(self.user) - 1
        elif 'Сражение с' in msg:
            self.mobs += 1
            self.kick += msg.count('💥')
        else:
            self.fights -= 1

    @staticmethod
    def _get_msg(block):
        msg = block.find_class('text')
        if msg:
            msg = msg[0]
            return msg

    @staticmethod
    def _get_date(block):
        msg_date = None
        date_element = block.find_class('date')
        if date_element:
            date_string = date_element[0].attrib['title']
            msg_date = datetime.datetime.strptime(date_string, DATE_FORMAT)
        return msg_date

    def __del__(self):
        print(f'за {self.fights} боев {self.weapon}ом сделано {self.kick} ударов')
        print(f'{self.pvp} пвп {self.mobs} мобов')


if __name__ == '__main__':
    Parser().parse()
