# encoding: utf-8
from sqlalchemy.orm import sessionmaker

from engine import engine
from model import Drop

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

received = set()
bonus = set()

for drop in session.query(Drop).distinct(Drop.txt, Drop.type).all():
    if drop.txt.startswith('📦'):
        continue
    locals()[drop.type].add(drop.txt)

with open('all received.txt', 'w', encoding='utf8') as f:
    for r in sorted(list(received)):
        f.write('{}\n'.format(r))

with open('all bonus.txt', 'w', encoding='utf8') as f:
    for r in sorted(list(bonus)):
        f.write('{}\n'.format(r))

print(bonus - received)
print(received - bonus)
