from sqlalchemy import create_engine
import os

engine = create_engine('sqlite:///{}'.format(os.path.join(os.path.dirname(__file__), 'db.sqlite')), echo=False)
