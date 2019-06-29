# coding: utf-8
import datetime
import os

import lxml.html as html

from common import Parser

DATE_FORMAT = '%d.%m.%Y %H:%M:%S'


class FightParser(Parser):

    def __init__(self):
        super(FightParser, self).__init__('Wolчара ВХ', 'data/me')
        self.doc = None

        self.pvp = 0
        self.first_kick = 0
        self.win = 0
        self.your_miss = 0
        self.enemy_miss = 0

    def parse(self, ):
        super(FightParser, self).parse()
        print(f'за {self.pvp} боев сделано {self.first_kick} первых ударов')
        print(f'{self.win} побед')

    def _parse_block(self, block):

        msg = self._get_msg(block)
        if not msg:
            return

        content = msg.text_content()

        if 'FIGHT!' in content:
            self.get_fight(content)

    def get_fight(self, msg: str):
        self.pvp += 1
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


if __name__ == '__main__':
    FightParser().parse()
