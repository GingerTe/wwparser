# coding: utf-8

from common import Parser


class BrokeParser(Parser):

    def __init__(self, user, dir_):
        super(BrokeParser, self).__init__(user, dir_)
        self.doc = None
        self.is_des = False
        self.kick = 0
        self.fights = 0
        self.pvp = 0
        self.mobs = 0
        self.weapon = 'Дезинтегратор'

    def _parse_block(self, block):
        msg_date = self._get_date(block)

        content = self._get_msg(block)

        if not (msg_date and content):
            return

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

    def __del__(self):
        print(f'за {self.fights} боев {self.weapon}ом сделано {self.kick} ударов')
        print(f'{self.pvp} пвп {self.mobs} мобов')


if __name__ == '__main__':
    BrokeParser('Wolчара ВХ', 'data/me').parse()
