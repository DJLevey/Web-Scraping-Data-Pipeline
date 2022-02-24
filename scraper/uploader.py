import boto3
from botocore.exceptions import ClientError
from sqlalchemy import Integer, create_engine, Table, Column, String, MetaData
from sqlalchemy.engine.base import Connection
import pandas as pd
import json
import os


def upload_to_bucket_by_id(id: str, bucket='aicorebucket828') -> bool:
    s3_client = boto3.client('s3')
    folder = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), f'../raw_data/{id}')
    for x in os.listdir(folder):
        if x.startswith(id):
            try:
                s3_client.upload_file(
                    os.path.join(folder, x),
                    bucket,
                    os.path.split(x)[1]
                )
            except ClientError as e:
                print(e)
                return False
    return True


def upload_folder_to_bucket(bucket='aicorebucket828'):
    folder = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '../raw_data/')
    for x in os.listdir(folder):
        upload_to_bucket_by_id(x)


def upload_to_rds_by_id(id: str, db) -> bool:
    folder = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), f'../raw_data/{id}')
    for x in os.listdir(folder):
        if x.endswith('.json'):
            with open(os.path.join(folder, x), 'r') as f:
                data = json.load(f)
                _race_insert(
                    {i: data[i] for i in data if i != 'runners'},
                    db
                    )
                engine = _connect_to_rds(db)
                _runner_insert(engine, data.pop('runners'), db)
    return True


def create_table(db) -> bool:
    meta = MetaData()
    meta = _create_race_table(meta)
    meta.create_all(_connect_to_rds(db))
    return True


def _race_insert(engine, race, db) -> bool:
    engine = _connect_to_rds(db)
    race = {x: [y] for x, y in race.items()}
    race_dataframe = pd.DataFrame.from_dict(race)
    race_dataframe.to_sql('race', engine, if_exists='replace')
    return engine


def _runner_insert(engine, runners, db) -> bool:
    return engine


def _connect_to_rds(db) -> Connection:
    engine = create_engine(
        f"{db['DATABASE_TYPE']}+{db['DBAPI']}://{db['USER']}"
        f":{db['PASSWORD']}@{db['ENDPOINT']}:{db['PORT']}"
        f"/{db['DATABASE']}"
        )
    print(engine.table_names())
    return engine.connect()


def _create_race_table(meta) -> MetaData:
    Table(
        'race', meta,
        Column('uuid', String, primary_key=True, nullable=False),
        Column('id', String, unique=True, nullable=False),
        Column('date', String, nullable=False),
        Column('race_number', Integer, nullable=False),
        Column('class', String, nullable=False),
        Column('length', Integer, nullable=False),
        Column('going', String, nullable=False),
        Column('course', String, nullable=False),
        Column('prize', String, nullable=False),
        Column('pace', String, nullable=False),
        Column('url', String, nullable=False),
        Column('image_link', String, nullable=False)
    )
    return meta


def _create_runner_table(meta) -> MetaData:
    Table(
        'runner', meta,
        Column('uuid', String, primary_key=True),
        Column('race_id', String, nullable=False),
        Column('place', Integer, nullable=False),
        Column('number', Integer, nullable=False),
        Column('name', String, nullable=False),
        Column('jockey', String, nullable=False),
        Column('trainer', String, nullable=False),
        Column('actual weight', String, nullable=False),
        Column('declared_weight', String, nullable=False),
        Column('draw', Integer, nullable=False),
        Column('length_behind_winner', String, nullable=False),
        Column('running_positions', String, nullable=False),
        Column('finish_time', String, nullable=False),
        Column('win_odds', String, nullable=False),
        Column('url', String, nullable=False)
    )
    return meta
