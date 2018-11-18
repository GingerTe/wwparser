# encoding: utf8
import json

from sqlalchemy.orm import sessionmaker

import log_parser
from engine import engine
from model import DungeonDrop, Type

with open('data/dungeons.json', encoding='utf8') as f:
    dungs = json.load(f)

drop_dict = {
    '🔩': '',
    '💾': '',
    '💡': '',
    '🔗': '',
    '🔹': '',
    '🕳': 'Крышки',
    '+': ' ',
    'x': ' ',
    ':': '',
    '📦': 'Маты ',
    '🔥': '',
    '🍸': '',
    '×': ''
}

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()
session.query(DungeonDrop).delete()
session.commit()

forward_num = 1
for location, data in dungs.items():
    for forward in data['forwards']:
        for loot in forward['loot'].split(','):
            loot = loot.replace('💪Сила +40  ❤️Живучесть +30', '')
            loot = loot.replace('🗣Харизма +40', '')
            loot = loot.replace('🤸🏽‍♂️Ловкость +30', '')
            loot = loot.replace(' 💣Судный день', '')
            if 'Скума' in loot:
                loot = loot[:loot.index('Скума')]
            loot = loot.strip()
            if not loot:
                continue
            for key in drop_dict:
                loot = loot.replace(key, drop_dict[key])

            drop = DungeonDrop()
            drop.km = int(data['distance'][:-2])
            drop.txt = loot
            drop.location_name = data['name']
            drop.forward_id = forward_num
            dropped = loot.split()
            drop_txt = []
            for d in dropped:
                if d[0].isdigit():
                    drop.num = int(d)
                else:
                    drop_txt.append(d)
            drop.txt = ' '.join(drop_txt)

            if drop.txt in log_parser.food_list:
                drop.type = Type.FOOD
            elif drop.txt in log_parser.metals:
                drop.type = Type.METAL
            elif drop.txt == 'Маты':
                drop.type = Type.MATS
            elif drop.txt in log_parser.other:
                drop.type = Type.OTHER
            else:
                drop.type = Type.TRUNK
            session.add(drop)
        forward_num += 1

session.commit()
