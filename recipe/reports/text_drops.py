# encoding: utf-8
from operator import and_

from openpyxl import Workbook
from sqlalchemy.orm import sessionmaker

from engine import engine
from model import Data, Drop, Type, Txt

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

wb = Workbook()
ws = wb.active

txt = ('Возле палаток ты нашел разобранного робота-помощника. '
       'Похоже, что "инженер", копавшийся в нем, не особо разбирался '
       'в стоимости деталей, потому что самое ценное — ядерную батарею — он оставил на месте.')
ws.append([txt])
ws.append(['Локация встречалась', session.query(Data).filter(Data.txt.has(txt=txt)).count()])
res = {}
for data in session.query(Drop).join(Data).filter(and_(Data.txt.has(txt=txt), Drop.type == Type.TRUNK)):
    res[data.txt] = res.get(data.txt, 0) + 1

for r in sorted(res):
    if res[r]:
        ws.append([r, res[r]])
ws.column_dimensions['A'].width = 25
wb.save('text_drop.xlsx')

wb.close()
session.close()
