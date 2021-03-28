from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import numpy as np


engine = create_engine('mysql+pymysql://root:password@localhost', echo=True)
#engine.execute("CREATE DATABASE adsb") #create db
engine.execute("USE adsb")
#engine.execute("DROP TABLE position_report;")

Base = declarative_base()

class PositionReport(Base):
    __tablename__ = 'position_report'
    id = Column(Integer, primary_key=True)
    hex = Column(String(6))
    flight = Column(String(8))
    alt_baro = Column(Integer)
    alt_geom = Column(Integer)
    gs = Column(Float)
    track = Column(Integer)
    geom_rate = Column(Integer)
    rsii = Column(Float)
    baro_rate = Column(Integer)
    nav_altitude_mcp = Column(Integer)
    lat = Column(Float)
    lon = Column(Float)
    squawk = Column(Integer)
    now = Column(DateTime)


#Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)

class Writer():
    def __init__(self, size_before_commit):
        self.size_before_commit = size_before_commit
        #self.to_be_committed = []
        self.set_empty()

    def set_empty(self):
        self.to_be_committed = []

    def add(self, position_report, session_maker):
        self.to_be_committed.append(position_report)
        if len(self.to_be_committed) > self.size_before_commit:
            self.commit_existing(session_maker)

    def commit_existing(self, session_maker):
        session = session_maker()
        for item in self.to_be_committed:
            session.add(item)
        session.commit()
        session.close()
        self.set_empty()


def nan_to_none(value):
    # isnan doesn't handle strings well
    is_nan = value != value
    return None if is_nan else value

def row_to_position_report(row):
    pr = PositionReport()
    pr.hex = nan_to_none(row.get('hex', None))
    pr.flight = nan_to_none(row.get('flight', None))
    pr.alt_baro = nan_to_none(row.get('alt_baro', None))
    pr.alt_geom = nan_to_none(row.get('alt_geom', None))
    pr.gs = nan_to_none(row.get('gs', None))
    pr.track = nan_to_none(row.get('track', None))
    pr.geom_rate = nan_to_none(row.get('geom_rate', None))
    pr.rssi = nan_to_none(row.get('rssi', None))
    pr.baro_rate = nan_to_none(row.get('baro_rate', None))
    pr.nav_altitude_mcp = nan_to_none(row.get('nav_altitude_mcp', None))
    pr.lat = nan_to_none(row.get('lat', None))
    pr.lon = nan_to_none(row.get('lon', None))
    pr.squawk = nan_to_none(row.get('squawk', None))
    now = nan_to_none(row.get('now', None))
    if now is not None:
        now = datetime.datetime.fromtimestamp(now)
    pr.now = now
    return pr




import pandas as pd
import requests
import json
import time

writer = Writer(300)

def sample(writer, Session):
    path = 'http://192.168.1.110/skyaware/data/aircraft.json'
    try:
        j = json.loads(requests.get(path, timeout = 5).text)
        now = j['now']
        df = pd.DataFrame(j['aircraft'])
        df['now'] = now
        df['hex'] = df['hex'].str[-6:]
        prs = df.apply(row_to_position_report, axis=1).tolist()
        for pr in prs:
            writer.add(pr, Session)
    except requests.exceptions.Timeout:
        pass


while True:
    try:
        sample(writer, Session)
        time.sleep(1)
    except KeyboardInterrupt:
        writer.commit_existing(Session)

