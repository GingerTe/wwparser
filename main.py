# coding: utf-8
import json
import os
import re
from copy import copy

import lxml.html as html

# Путь к папке с логами телеги
DIRECTORY_WITH_LOGS = r'data'
# Название файла с результатом
RESULT_FILE_NAME = 'all.json'

res = {}
params_regexp = re.compile(r'.*\d+/\d+ 🍗\d+% 🔋\d+/\d+ 👣(\d+)+км(.*)')

skip_line_anchors = 'Найдено', 'Ты ранен', 'Потеряно', 'Проебано', 'Ты потерял', 'будет проводиться 👊Рейд', \
                    '/help', 'Ты можешь продолжить путь в Темной зоне', 'Найден дрон'

skip_block_anchors = 'Ты тоже хлам собираешь', 'Твой путь преградил', 'Проводник', 'Старьёвщик', \
                     'Хламосборщик', 'Таинственный незнакомец', 'Во время вылазки на тебя напал', \
                     'Ты проиграл в этой схватке', \
                     'Безумный старик', 'Они все мертвы', 'Тебя буквально размазали', \
                     'Недалеко от себя ты заметил какого-то человека', 'Недалеко ты заметил какого-то человека', \
                     'Белое гетто', 'Выбери одну из фракций'


def check_skipped(l, type_='line'):
    if type_ == 'all':
        skip_list = skip_block_anchors
    else:
        skip_list = skip_line_anchors
    for si in skip_list:
        if si in l:
            return True
    return False


for user in os.listdir(DIRECTORY_WITH_LOGS):
    print(user)
    user_dir = os.path.join(DIRECTORY_WITH_LOGS, user)
    for name in os.listdir(user_dir):
        if not name.endswith('.html'):
            continue

        with open(os.path.join(user_dir, name), encoding='utf8') as f:
            data = f.read()

        doc = html.document_fromstring(data)
        for br in doc.xpath("*//br"):
            br.tail = "\n" + br.tail if br.tail else "\n"
        msgs = doc.find_class('text')

        for msg in msgs:

            content = msg.text_content().strip().split('\n')

            location = None
            km = None
            txt = []
            received = []
            bonus = []
            f_skip_line = False
            f_skip_block = False

            for index, line in enumerate(content):
                line = line.strip()
                if not line:
                    continue
                # Первая строка - локация
                elif not location:
                    location = line
                # Если строка параметров
                elif params_regexp.match(line):
                    km = params_regexp.match(line).group(1)
                # Если получили локацию, дальше должен идти км
                # Дополнительно проверяем, не является ли блок пропускаемым
                elif location and not km or check_skipped(line, 'all'):
                    f_skip_block = True
                    break
                # Проверка, не нужно ли пропустить строку
                elif check_skipped(line, 'line'):
                    continue
                # Обработка полученного хлама
                elif line.startswith('Получено'):
                    s = line.split(':')
                    received.append(s[1].strip())
                    # if len(s) > 1:
                    #     num = ''.join(i for i in line if i.isdigit())
                    #     get[-1]['num'] = int(num) if num else 1
                # Обработка полученных бонусов
                elif line.startswith('Бонус'):
                    line = line[7:]
                    if '❤' in line:
                        continue
                    else:
                        bonus.append(line)

                else:
                    txt.append(line)
            # Если получили флаг пропустить блок, или не получили км, или не получили текстовку
            if f_skip_block or not km or not txt:
                continue
            km = int(km)
            txt = ' '.join(txt)

            # Убираем владельца локации
            if '(' in location:
                location = location[:location.index('(')]
            # Определяем зону
            zone = 'safe zone'
            if location.startswith('🚷'):
                zone = 'dark zone'
                location = location[2:]

            # Создаем ключи, если надо
            if txt not in res:
                res[txt] = {}
            if zone not in res[txt]:
                res[txt][zone] = {'received': {}, 'bonus': []}
            # res[txt] = res.get(txt, {})
            # res[txt][zone] = res.get(zone, {'get': [], 'location': [], 'km': [], 'bonus': []})

            block = res[txt][zone]
            if received:
                received = ', '.join(received)
                block['received'][received] = block['received'].get(received, 0) + 1
            if bonus:
                block['bonus'].append(bonus)

            # if km not in block['km']:
            #     block['km'].append(km)
            #
            # if location not in block['location']:
            #     block['location'].append(location)

# Убираем пустые списки
for data in res.values():
    for i in data.values():
        for key in copy(i):
            if not i[key]:
                del i[key]
            elif isinstance(i[key], list):
                i[key].sort()

with open(RESULT_FILE_NAME, 'w', encoding='utf8') as f:
    json.dump(res, f, indent=2, ensure_ascii=False)
