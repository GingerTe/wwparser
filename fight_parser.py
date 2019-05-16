# coding: utf-8
import datetime
import os

import lxml.html as html

DATE_FORMAT = '%d.%m.%Y %H:%M:%S'


class Parser:

    def __init__(self):
        super(Parser, self).__init__()
        self.doc = None

        self.pvp = 0
        self.first_kick = 0
        self.win = 0
        self.user = 'Wolчара ВХ'
        self.dir = 'data/me'
        # self.user = 'Кусяка ВХ'
        # self.dir = 'data/kusyaka'

    def parse(self, ):
        for name in os.listdir(self.dir):
            self._parse_document(os.path.join(self.dir, name))
        print(f'за {self.pvp} боев сделано {self.first_kick} первых ударов')
        print(f'{self.win} побед')

    def _parse_document(self, file_name):
        if not file_name.endswith('.html'):
            return

        with open(file_name, encoding='utf8') as file_doc:
            self.doc = html.document_fromstring(file_doc.read())
        body = self.doc.find_class('text')

        for block in body:
            self._parse_block(block)

    def _parse_block(self, block):

        msg = self._get_msg(block)
        if not msg:
            return

        content = msg.text_content()

        if 'FIGHT!' in content:
            self.get_fight(content)

    def get_fight(self, msg: str):
        self.pvp += 1
        # print(msg)
        msg = msg.split('FIGHT!')[1]
        if 'Найдено' in msg or '/tdtop' in msg or 'Получено' in msg:
            self.win += 1

        # print(msg.split('❤'))
        msg_split = msg.split('❤')
        if len(msg_split) == 1:
            print(msg)
            return
        if self.user in msg_split[1]:
            self.first_kick += 1

    @staticmethod
    def _get_msg(block):
        msg = block.find_class('text')
        if msg:
            msg = msg[0]
            return msg


if __name__ == '__main__':
    Parser().parse()
