import boto3
from botocore.exceptions import ClientError
from sqlalchemy import Integer, create_engine, Table, Column
from sqlalchemy import String, MetaData
from sqlalchemy.engine.base import Connection, Engine
from sqlalchemy.exc import IntegrityError
import pandas as pd
import json
import os


def upload_to_bucket_by_id(id: str, bucket: str) -> bool:
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
    print('Id not found.')
    return False


def upload_folder_to_bucket(bucket: str):
    folder = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '../raw_data/')
    for x in os.listdir(folder):
        upload_to_bucket_by_id(x)


def upload_to_rds_by_id(id: str, db: dict) -> bool:
    engine = _connect_to_rds(db)
    folder = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), f'../raw_data/{id}')
    for x in os.listdir(folder):
        if x.endswith('.json'):
            with open(os.path.join(folder, x), 'r') as f:
                data = json.load(f)
                _race_insert(
                    engine,
                    {i: data[i] for i in data if i != 'runners'}
                    )
                _runner_insert(engine, data.pop('runners'))
    return True


def get_retrieved_urls(db: dict):
    '''Get list of previously scraped URLs

    Iterates through the raw_data floder andr etrieves a list of
    previously scraped URLs from the json files.

    Returns:
        list (str): A list of URLs.
    '''
    engine = _connect_to_rds(db)
    if 'race' in engine.table_names():
        con = engine.connect()
        urls = pd.read_sql('SELECT url FROM race', con)
        return urls.values.reshape(-1).tolist()
    return []


def _race_insert(engine: Engine, race: dict) -> None:
    if 'race' not in engine.table_names():
        _create_race_table(engine)
    race = {x: [y] for x, y in race.items()}
    race_dataframe = pd.DataFrame.from_dict(race)
    conn = engine.connect()
    try:
        race_dataframe.to_sql(
            'race', conn, if_exists='append', index=False
            )
    except IntegrityError as e:
        print(e)
    conn.close()


def _runner_insert(engine: Engine, runners: dict) -> None:
    if 'runner' not in engine.table_names():
        _create_runner_table(engine)
    runners_dataframe = pd.DataFrame().from_dict(runners)
    conn = engine.connect()
    try:
        runners_dataframe.to_sql(
            'runner', conn, if_exists='append', index=False
            )
    except IntegrityError as e:
        print(e)
    conn.close()


def _connect_to_rds(db: dict) -> Engine:
    engine = create_engine(
        f"{db['DATABASE_TYPE']}+{db['DBAPI']}://{db['USER']}"
        f":{db['PASSWORD']}@{db['ENDPOINT']}:{db['PORT']}"
        f"/{db['DATABASE']}"
        )
    return engine


def _create_race_table(engine: Connection):
    meta = MetaData()
    Table(
        'race', meta,
        Column('uuid', String, nullable=False),
        Column('race_id', String, primary_key=True,
               nullable=False, unique=True),
        Column('date', String, nullable=False),
        Column('race_number', Integer, nullable=False),
        Column('class', String, nullable=False),
        Column('length', Integer, nullable=False),
        Column('going', String, nullable=False),
        Column('course', String, nullable=False),
        Column('prize', Integer, nullable=False),
        Column('pace', String, nullable=False),
        Column('url', String, nullable=False),
        Column('image_link', String, nullable=False)
    )
    meta.create_all(engine)


def _create_runner_table(engine: Connection) -> MetaData:
    meta = MetaData()
    Table(
        'runner', meta,
        Column('uuid', String, unique=True),
        Column('race_id', String, primary_key=True, nullable=False),
        Column('horse_id', String, primary_key=True, nullable=False),
        Column('place', String),
        Column('number', String),
        Column('name', String, nullable=False),
        Column('jockey', String, nullable=False),
        Column('trainer', String, nullable=False),
        Column('actual_weight', String, nullable=False),
        Column('declared_weight', String, nullable=False),
        Column('draw', String, nullable=False),
        Column('length_behind_winner', String, nullable=False),
        Column('running_positions', String, nullable=False),
        Column('finish_time', String, nullable=False),
        Column('win_odds', String, nullable=False),
        Column('url', String, nullable=False)
    )
    meta.create_all(engine)
