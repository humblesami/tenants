import os
import sys
import json
import shutil
import psycopg2
import importlib
import traceback

import sam_pytools
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class Command(BaseCommand):
    help = 'setting up db i.e. create db or drop db for dev purpose'
    settings_dir = os.path.dirname(__file__)
    str = 'website/management/commands'
    base_directory = ''
    if str in settings_dir:
        base_directory = settings_dir.replace(str, '')
    else:
        str = 'website\\management\\commands'
        base_directory = settings_dir.replace(str, '')

    def drop_create_db(self, root_path):
        res = 'Unknown'
        database_info = settings.DATABASES['default']
        db_engine = database_info['ENGINE']
        if db_engine.endswith('sqlite3') or db_engine.endswith('sqlite3_backend'):
            db_path = root_path + '/db.sqlite3'
            if os.path.exists(db_path):
                os.remove(db_path)
            return 'created'
        else:
            db_con = None
            if db_engine.endswith('postgresql') or db_engine.endswith('postgresql_backend'):
                db_con = psycopg2.connect(
                    host="localhost", user=database_info['USER'],
                    dbname='postgres', password=database_info['PASSWORD']
                )
                db_con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                cur = db_con.cursor()
                disconnect_query = f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{database_info['NAME']}'
                  AND pid <> pg_backend_pid();
                """
                cur.execute(disconnect_query)
                drop_query = f"DROP DATABASE IF EXISTS {database_info['NAME']}"
                cur.execute(drop_query)
                create_query = f"CREATE DATABASE {database_info['NAME']}"
                cur.execute(create_query)
            if db_con:
                importlib.import_module('del')
                db_con.close()
                return 'created'
            else:
                return ' failed to connect'

    def add_arguments(self, parser):
        parser.add_argument(
            '-hard', '--hard', action='store_true',
            help='drop database if exists and create new one'
        )

    def handle(self, *args, **kwargs):
        try:
            root_path = settings.BASE_DIR
            res = self.drop_create_db(root_path)
            if res == 'created':
                call_command('makemigrations')
                call_command('migrate')
                fixture_path = './fixtures.json'
                if os.path.isfile(fixture_path):
                    call_command('loaddata', fixture_path)
                print('Dropped, Created, Migrated, loaded successfully')
            elif res == 'already exists':
                print('Already created')
            else:
                print('Failed because ' + res)
        except:
            error_message = sam_pytools.LogUtils.get_error_message()
            print('Error ' + error_message)
