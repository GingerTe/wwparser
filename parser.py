# coding: utf-8
import datetime
import json
import os
import re
import yaml

from sqlalchemy.orm import sessionmaker

from engine import engine
from model import Data
import lxml.html as html
import logging.config

DATE_FORMAT = '%d.%m.%Y %H:%M:%S'

with open('logging.yaml', 'rt') as f:
    config = yaml.safe_load(f.read())
    f.close()
logging.config.dictConfig(config)
logger = logging.getLogger(__name__)
logger.info("Contest is starting")


class Parser:
    SKIP_LINE_ANCHORS = 'Найдено', 'Ты ранен', 'Потеряно', 'Проебано', 'Ты потерял', 'будет проводиться 👊Рейд', \
                        '/help', 'Ты можешь продолжить путь в Темной зоне', 'Найден дрон', 'Ты заработал', \
                        'Ты покидаешь Темную зону', 'Тебе удалось избежать схватки, используя такое модное ' \
                                                    'молодежное направление, как "бег"'

    SKIP_BLOCK_ANCHORS = 'Ты тоже хлам собираешь', 'Твой путь преградил', 'Проводник', 'Старьёвщик', \
                         'Хламосборщик', 'Таинственный незнакомец', 'Во время вылазки на тебя напал', \
                         'Ты проиграл в этой схватке', \
                         'Безумный старик', 'Они все мертвы', 'Тебя буквально размазали', \
                         'Недалеко от себя ты заметил какого-то человека', 'Недалеко ты заметил какого-то человека', \
                         'Белое гетто', 'Выбери одну из фракций'

    PARAMS_REGEXP = re.compile(r'.*\d+/\d+ 🍗\d+% 🔋\d+/\d+ 👣(\d+)+км(.*)')

    def __init__(self, log_dir='data'):
        self.log_dir = log_dir
        self.current_line = ''
        self.doc = None

        session = sessionmaker()
        session.configure(bind=engine)
        self.session = session()

    def _fix_br(self):
        for br in self.doc.xpath("*//br"):
            br.tail = "\n" + br.tail if br.tail else "\n"

    def check_skipped(self, type_='line'):
        if type_ == 'all':
            skip_list = self.SKIP_BLOCK_ANCHORS
        else:
            skip_list = self.SKIP_LINE_ANCHORS

        for si in skip_list:
            if si in self.current_line:
                return True
        return False

    def parse_all(self):
        self.session.query(Data).delete()
        self.session.commit()
        for user in os.listdir(self.log_dir):
            logger.info(user)
            # print(user)
            user_dir = os.path.join(self.log_dir, user)
            for name in os.listdir(user_dir):
                if not name.endswith('.html'):
                    continue
                self.parse(os.path.join(user_dir, name), user)

    def parse(self, file_name, user):
        with open(file_name, encoding='utf8') as f:
            data = f.read()
        self.doc = html.document_fromstring(data)
        self._fix_br()
        body = self.doc.find_class('body')

        for block in body:
            msg_date = self._get_date(block)

            msg = self._get_msg(block)

            if not (msg_date and msg):
                continue
            data = Data(user=user, date=msg_date)

            content = msg.text_content().strip().split('\n')

            data.txt = []
            data.received = []
            data.bonus = []
            f_skip_block = False

            for index, self.current_line in enumerate(content):
                self.current_line = self.current_line.strip()
                if not self.current_line:
                    continue
                # Первая строка - локация
                elif not data.location:
                    data.location = self.current_line
                # Если строка параметров
                elif self.PARAMS_REGEXP.match(self.current_line):
                    km = self.PARAMS_REGEXP.match(self.current_line).group(1)
                    if not km:
                        break
                    data.km = int(km)
                # Если получили локацию, дальше должен идти км
                # Дополнительно проверяем, не является ли блок пропускаемым
                elif data.location and not data.km or self.check_skipped('all'):
                    f_skip_block = True
                    break
                # Проверка, не нужно ли пропустить строку
                elif self.check_skipped('line'):
                    continue
                # Обработка полученного хлама
                elif self.current_line.startswith('Получено'):
                    s = self.current_line.split(':')
                    data.received.append(s[1].strip())
                    # if len(s) > 1:
                    #     num = ''.join(i for i in line if i.isdigit())
                    #     get[-1]['num'] = int(num) if num else 1
                # Обработка полученных бонусов
                elif self.current_line.startswith('Бонус'):
                    self.current_line = self.current_line[7:]
                    if '❤' in self.current_line:
                        continue
                    else:
                        data.bonus.append(self.current_line)

                else:
                    data.txt.append(self.current_line)
            # Если получили флаг пропустить блок, или не получили км, или не получили текстовку
            if f_skip_block or not (data.km and data.txt):
                continue
            data.txt = ' '.join(data.txt)

            # Убираем владельца локации
            if '(' in data.location:
                data.location = data.location[:data.location.index('(')]
            # Определяем зону
            data.zone = 'safe'
            if data.location.startswith('🚷'):
                data.zone = 'dark'
                data.location = data.location[2:]

            self.session.add(data)
        self.session.commit()

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


if __name__ == '__main__':
    Parser().parse_all()
