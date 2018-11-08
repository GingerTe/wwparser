# coding: utf-8
import json
import os
import re
from io import StringIO

import lxml.html as html
import html2text
from lxml import etree

d = r'C:\Users\Kwert\Downloads\Telegram Desktop\ChatExport_08_11_2018'
# d = r'.'

skipped_words = ['ДНЕВНИК', 'проиграл', 'сражение', 'напал']

location_string = r'([А-я ]+)'
params_string = r'.*\d+/\d+ 🍗\d+% 🔋\d+/\d+ 👣(\d+)+км(.*)'
res = {}
# km = re.compile('.*([А-я ]+).*(\d+)км.*')
find_string = r'Найдено: .*?'

# regexp = re.compile('.*([А-я ]+).*(\d+)км\s*(.*)Найдено: (.+)(Получено: (.+))*')
# fight = '([^❤]+).*(\d+)км\s*(Во время вылазки на тебя напал\s*([^.]+)).*'

skipped = 'Найдено', 'Ты ранен', 'Потеряно', 'Проебано', 'Ты потерял', 'будет проводиться 👊Рейд', \
          'Подробности в /help и в игровых чатах.'


def check_skipped(l):
    for s in skipped:
        if s in l:
            return True
    return False


for name in os.listdir(d):
    if not name.endswith('.html'):
        continue

    with open(os.path.join(d, name), encoding='utf8') as f:
        data = f.read()

    # tree = html.parse(StringIO(data))
    doc = html.document_fromstring(data)
    for br in doc.xpath("*//br"):
        br.tail = "\n" + br.tail if br.tail else "\n"
    msgs = doc.find_class('text')

    for msg in msgs:

        content = msg.text_content().strip().split('\n')
        location = None
        km = None
        txt = []
        get = []
        skip = False
        skip_txt = False
        for index, line in enumerate(content):
            line = line.strip()
            if line and not location:
                location = line
            elif re.match(params_string, line):
                km = re.match(params_string, line).group(1)
            elif line and location and not km:
                skip = True
                break
            elif 'напал' in line:
                skip = True
                break
            elif check_skipped(line):
                continue
            elif 'Недалеко от себя ты заметил какого-то человека' in line \
                    or 'Недалеко ты заметил какого-то человека' in line:
                skip_txt = True
            elif line.startswith('Получено'):
                s = line.split(':')
                try:
                    get.append({
                        'name': s[1].strip()
                    })
                except:
                    print(line)
                if len(s) > 1:
                    num = ''.join(i for i in line if i.isdigit())
                    get[-1]['num'] = int(num) if num else 1

            elif not skip_txt:
                txt.append(line)
        if skip or not km:
            continue

        res[km] = res.get(km, []) + [{
            'location': location,
            'txt': ' '.join(txt),
            'get': get
        }]

with open('all.json', 'w', encoding='utf8') as f:
    json.dump(res, f, indent=2, ensure_ascii=False)
