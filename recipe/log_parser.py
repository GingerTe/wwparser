# coding: utf-8
import datetime
import os
import re
import yaml

from sqlalchemy.orm import sessionmaker

from engine import engine
from model import Data, Drop, DropType, Type, Txt
import lxml.html as html
import logging.config

import params
from params import TXT_DICT_RELATION, TXT_DICT_TO_INSERT

DATE_FORMAT = '%d.%m.%Y %H:%M:%S'

with open('logging.yaml', 'rt') as f:
    config = yaml.safe_load(f.read())
    f.close()
logging.config.dictConfig(config)
logger = logging.getLogger(__name__)
logger.info("Contest is starting")


class DropFormatter:
    def __init__(self):
        self.current_line = ''

    def get_drop(self):
        for key in params.DROP_NAMES:
            self.current_line = self.current_line.replace(key, params.DROP_NAMES[key])
        self.current_line = self.current_line.strip()
        self.current_line = re.sub(' +', ' ', self.current_line)

        dropped = self.current_line.split()
        drop = Drop()
        drop_txt = []
        for d in dropped:
            if d[0].isdigit():
                drop.num = int(d)
            else:
                drop_txt.append(d)
        drop.txt = ' '.join(drop_txt)

        if drop.txt in params.FOOD_LIST:
            drop.type = Type.FOOD
        elif drop.txt in params.METAL_LIST:
            drop.type = Type.METAL
        elif drop.txt == 'Маты':
            drop.type = Type.MATS
        elif drop.txt in params.OTHER_LIST:
            drop.type = Type.OTHER
        else:
            drop.type = Type.TRUNK

        return drop


class Parser(DropFormatter):
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
        super(Parser, self).__init__()
        self.log_dir = log_dir
        self.doc = None

        session = sessionmaker()
        session.configure(bind=engine)
        self.session = session()
        self._txt_creation()

    def _txt_creation(self):
        logger.info('fill txt table')
        if not self.session.query(Txt).count():
            for el in TXT_DICT_TO_INSERT:
                self.session.add(Txt(id=TXT_DICT_TO_INSERT[el], txt=el))
        self.session.commit()

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
            self.parse_user(user)

    def parse_user(self, user):
        user_dir = os.path.join(self.log_dir, user)
        if os.path.isdir(user_dir):
            logger.info(user)
            for name in os.listdir(user_dir):
                self._parse_document(user, os.path.join(user_dir, name))

    def _parse_document(self, user, file_name):
        if not file_name.endswith('.html'):
            return

        with open(file_name, encoding='utf8') as file_doc:
            self.doc = html.document_fromstring(file_doc.read())
        self._fix_br()
        body = self.doc.find_class('body')

        for block in body:
            self._parse_block(user, block)
        self.session.commit()

    def _parse_block(self, user, block):
        msg_date = self._get_date(block)

        msg = self._get_msg(block)

        if not (msg_date and msg):
            return
        data = Data(user=user, date=msg_date, zone='safe')
        txt = []

        content = msg.text_content().strip().split('\n')

        for index, self.current_line in enumerate(content):
            self.current_line = self.current_line.strip()
            if not self.current_line:
                continue
            # Первая строка - локация
            elif not data.location:
                self._format_location_and_zone(data)
            # Если строка параметров
            elif self.PARAMS_REGEXP.match(self.current_line):
                self._format_km(data)
            # Если получили локацию, дальше должен идти км
            # Дополнительно проверяем, не является ли блок пропускаемым
            elif (data.location and not data.km) or self.check_skipped('all'):
                return
            # Проверка, не нужно ли пропустить строку
            elif self.check_skipped('line'):
                continue
            # Обработка полученного хлама
            elif self.current_line.startswith('Получено'):
                self._format_received(data)
            # Обработка полученных бонусов
            elif self.current_line.startswith('Бонус'):
                self._format_bonus(data)
            else:
                txt.append(self.current_line)
        # Если получили флаг пропустить блок, или не получили км, или не получили текстовку
        if not (data.km and txt):
            return
        txt = ' '.join(txt)
        data.txt_id = TXT_DICT_RELATION[txt]

        self.session.add(data)

    def _format_km(self, data):
        km = self.PARAMS_REGEXP.match(self.current_line).group(1)
        data.km = int(km)

    def _format_received(self, data):
        self.current_line = self.current_line[len('Получено'):]
        drop = self.get_drop()
        drop.drop_type = DropType.RECEIVED
        data.drop.append(drop)

    def _format_bonus(self, data):
        self.current_line = self.current_line[len('Бонус'):]
        if '❤' in self.current_line:
            return

        drop = self.get_drop()
        drop.drop_type = DropType.BONUS
        data.drop.append(drop)

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
        self.session.close()


logger.info("finish")

if __name__ == '__main__':
    Parser().parse_all()
