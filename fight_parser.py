# coding: utf-8

from common import Parser


class FightParser(Parser):

    def __init__(self, user, dir_):
        super(FightParser, self).__init__(user, dir_)
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

        content = self._get_msg(block)
        if not content:
            return

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
    FightParser('Wolчара ВХ', 'data/me').parse()
