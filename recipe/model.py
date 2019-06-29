from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.event import listens_for
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from engine import engine

Base = declarative_base()


class Txt(Base):
    __tablename__ = 'txt'
    id = Column(Integer, primary_key=True)
    txt = Column(String, index=True)


class Data(Base):
    __tablename__ = 'data'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    user = Column(String, index=True)
    txt_id = Column(Integer, ForeignKey('txt.id'))
    txt = relationship("Txt")
    location = Column(String, index=True)
    km = Column(Integer, index=True)
    # received = Column(Text)
    # bonus = Column(Text)
    zone = Column(String)
    drop = relationship("Drop", backref="data")

    def __init__(self, **kwargs):
        for attr in kwargs:
            self.__setattr__(attr, kwargs.get(attr))


class Drop(Base):
    __tablename__ = 'drop'
    id = Column(Integer, primary_key=True)
    drop_type = Column(String, index=True)
    type = Column(String, index=True)
    txt = Column(String, index=True)
    num = Column(Integer, default=1)
    data_id = Column(Integer, ForeignKey('data.id'))

    def __repr__(self):
        return self.txt


class DungeonDrop(Base):
    __tablename__ = 'dungeon_drop'
    id = Column(Integer, primary_key=True)
    type = Column(String, index=True)
    txt = Column(String, index=True)
    num = Column(Integer, default=1)
    km = Column(Integer, index=True)
    forward_id = Column(Integer)
    location_name = Column(String)

    def __repr__(self):
        return 'Dungeon Drop <{}{}>'.format(self.km, self.txt)


class DropType:
    RECEIVED = 'received'
    BONUS = 'bonus'


class Type:
    FOOD = 'food'
    METAL = 'metal'
    TRUNK = 'trunk'
    MATS = 'mats'
    OTHER = 'other'


# @listens_for(Data, 'before_insert')
# def do_stuff(mapper, connect, target: Data):
#     # target is an instance of Table
#     target.bonus = "; ".join(target.bonus) or None
#     target.received = "; ".join(target.received) or None


# Создание таблицы
Base.metadata.create_all(engine)
