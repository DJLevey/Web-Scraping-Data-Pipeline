'''Uploader Module

This module contains functions used to upload data to aws services, and to
retrieve a list of previously scraped urls.
'''

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
    '''Uploads a folder to a AWS Bucket

    Takes a given sample ID and searches for its corrasponding data folder,
    then uploades its contents to a AWS S3 Bucket.

    Args:
        id: The id of a race to upload
        bucket: The name of the targeted S3 bucket.

    Returns:
        bool: True if upload was successful. False otherwise.
    '''
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


def upload_folder_to_bucket(bucket: str) -> None:
    ''' Uploads entire raw data folder to bucket

    Iterated through every subfolder, then calls upload_to_bucket_by_id

    Args:
        bucket: The name of the S3 bucket.
    '''
    folder = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '../raw_data/')
    for x in os.listdir(folder):
        upload_to_bucket_by_id(x, bucket)


def upload_to_rds_by_id(id: str, db: dict) -> bool:
    '''Uploads JSON file to AWS RDS

    Takes a given sample ID and searches for its corrasponding data folder,
    then uploads its contents race and runner tables.

    Args:
        id: The id of a race to upload
        db: Dict containing parameters used in building SQLAlchemy Engine.
    '''
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


def upload_folder_to_rds(db: dict) -> None:
    '''Uploades all JSON files to RDS.

    Args:
        db: Dict containing parameters used in building SQLAlchemy Engine.
    '''
    folder = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '../raw_data/')
    for x in os.listdir(folder):
        upload_to_bucket_by_id(x, db)
    return


def get_retrieved_urls(db: dict) -> list:
    '''Get list of previously scraped URLs

    Retrieves all URLs from race table

    Returns:
        db (dict): Dict containing parameters used in building an
            SQLAlchemy Engine.
    '''
    engine = _connect_to_rds(db)
    if 'race' not in engine.table_names():
        _create_race_table(engine)
    con = engine.connect()
    race_urls = pd.read_sql('SELECT url FROM race', con)
    con.close()
    return race_urls.values.reshape(-1).tolist()


def get_no_event_urls(db: dict) -> list:
    '''Get list of urls with no event to scrape.

    Retrieves all URLs from no_event table

    Returns:
        db (dict): Dict containing parameters used in building an
            SQLAlchemy Engine.
    '''
    engine = _connect_to_rds(db)
    if 'no_event' not in engine.table_names():
        _create_no_event_table(engine)
    con = engine.connect()
    no_event_urls = pd.read_sql('SELECT url FROM no_event', con)
    con.close()
    return no_event_urls.values.reshape(-1).tolist()


def no_event_insert(db: dict, url: str) -> None:
    '''Adds url to no_event table

    Args:
        db (dict): Dict containing parameters used in building an
            SQLAlchemy Engine.
    '''
    engine = _connect_to_rds(db)
    if 'no_event' not in engine.table_names():
        _create_no_event_table(engine)
    url_dataframe = pd.DataFrame.from_dict({'url': [url]})
    conn = engine.connect()
    try:
        url_dataframe.to_sql(
            'no_event', conn, if_exists='append', index=False
            )
    except IntegrityError as e:
        print(e)
    conn.close()


def _race_insert(engine: Engine, race: dict) -> None:
    '''Insert rows to race table

    Creates the race table if none exists, then inserts a row.

    Params:
        engine (Engine): SQLAlchemy Engine to connect to the RDS.
        race (dict): A dictionary of all the runners in a given race.
    '''
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
    '''Insert rows to runner table

    Creates the runner table if none exists, then inserts rows.

    Params:
        engine (Engine): SQLAlchemy Engine to connect to the RDS.
        runners (dict): A dictionary of all the runners in a given race.
    '''
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
    '''Create SQLALchemy Engine

    Creates an Engine from a dictionary.

    Args:
        db (dict): A dictionary parsed from the config file
            with parameters for the RDS.
    Returns:
        Engine: SQLAlchemy Engine to connect to the RDS.
    '''
    engine = create_engine(
        f"{db['DATABASE_TYPE']}+{db['DBAPI']}://{db['USER']}"
        f":{db['PASSWORD']}@{db['ENDPOINT']}:{db['PORT']}"
        f"/{db['DATABASE']}"
        )
    return engine


def _create_race_table(conn: Connection):
    ''' Create race table if none exists.

    Table used to store the data for each race.

    Args:
        conn (Connection): SQLAlchemy connection to the RDS.
    '''
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
    meta.create_all(conn)


def _create_runner_table(conn: Connection) -> None:
    ''' Create runner table if none exists.

    Table used to store a horses participation in an event.

    Args:
        conn (Connection): SQLAlchemy connection to the RDS.
    '''
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
    meta.create_all(conn)


def _create_no_event_table(conn: Connection) -> None:
    ''' Create no_event table if none exists.

    Table used to list urls with no event on that date.

    Args:
        conn (Connection): SQLAlchemy connection to the RDS.
    '''
    meta = MetaData()
    Table(
        'no_event', meta,
        Column('url', String, primary_key=True)
    )
    meta.create_all(conn)
