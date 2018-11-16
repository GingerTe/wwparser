import json

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.event import listens_for
from sqlalchemy.ext.declarative import declarative_base
from engine import engine

Base = declarative_base()


class Data(Base):
    __tablename__ = 'data'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    user = Column(String, index=True)
    txt = Column(Text, index=True)
    location = Column(String, index=True)
    km = Column(Integer, index=True)
    received = Column(Text)
    bonus = Column(Text)
    zone = Column(String)

    def __init__(self, **kwargs):
        for attr in kwargs:
            self.__setattr__(attr, kwargs.get(attr))

    # def __repr__(self):
    #     return "<Data('%s','%s', '%s')>" % (self.name, self.fullname, self.password)


@listens_for(Data, 'before_insert')
def do_stuff(mapper, connect, target: Data):
    # target is an instance of Table
    target.bonus = "; ".join(target.bonus) or None
    target.received = "; ".join(target.received) or None


# Создание таблицы
Base.metadata.create_all(engine)
