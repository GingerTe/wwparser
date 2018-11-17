# encoding: utf-8
from sqlalchemy.orm import sessionmaker

from engine import engine
from model import Data

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

received = set()
bonus = set()

for data in session.query(Data).all():
    if data.received:
        if data.received.startswith('📦'):
            continue
        received = received.union(
            set([' '.join([x for x in x.split() if not x[0].isdigit()]) for x in data.received.split('; ')]))
    if data.bonus:
        if data.bonus.startswith('📦'):
            continue
        bonus = bonus.union(
            set([' '.join([x for x in x.split() if not x[0].isdigit()]) for x in data.bonus.split('; ')]))

with open('all received.txt', 'w', encoding='utf8') as f:
    for r in sorted(list(received)):
        f.write('{}\n'.format(r))

with open('all bonus.txt', 'w', encoding='utf8') as f:
    for r in sorted(list(bonus)):
        f.write('{}\n'.format(r))

print(bonus - received)
print(received - bonus)
