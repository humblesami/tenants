import os
import json
import importlib
from psycopg2 import Error
from psycopg2 import connect
from django.core.management import call_command
from django.core.management.base import BaseCommand
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

class Command(BaseCommand):
    help = 'setting up db i.e. create db or drop db for dev purpose'
    settings_dir = os.path.dirname(__file__)
    base_directory = settings_dir.replace('website/management/commands', '')
    def connect_database(self, database_info = {}):
        con = None
        try:
            con = connect(dbname=database_info['default']['NAME'],
                    user=database_info['default']['USER'],
                    host=database_info['default']['HOST'],
                    password=database_info['default']['PASSWORD'])
            con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            return con
        except Error as error:
            str_error = error.args[0]
            return str_error

    def connect_main_database(self, database_info = {}):
        con = None
        try:
            con = connect(dbname='postgres',
                    user=database_info['default']['USER'],
                    host=database_info['default']['HOST'],
                    password=database_info['default']['PASSWORD'])
            con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            return con
        except Error as error:
            str_error = error.args[0]
            return str_error

    def init_execution(self, hard_reset, create):
        database_info = {}
        res = 'Unknown'
        path = ''
        try:
            path = (self.base_directory+'/config.json')
            path = path.replace('\\/', '\\')
            path = path.replace('//', '/')
            with open(path, 'r') as config:
                database_info = json.load(config)
        except:
            return 'Configuration File not found. at '+path

        main_database_connection = self.connect_main_database(database_info)
        if main_database_connection is str:
            return main_database_connection

        main_database_cursor = main_database_connection.cursor()
        if hard_reset:
            try:
                main_database_cursor.execute('DROP DATABASE if exists ' + database_info['default']['NAME'])
                main_database_cursor.execute('CREATE DATABASE ' + database_info['default']['NAME'])
                res = 'done'
            except Error as error:
                str_error = error.args[0]
                res = str_error
        elif create:
            try:
                main_database_cursor.execute('CREATE DATABASE ' + database_info['default']['NAME'])
            except Error as error:
                str_error = error.args[0]
                res = str_error
        main_database_cursor.close()
        main_database_connection.close()
        return res

    def add_arguments(self, parser):
        parser.add_argument('-hard', '--hard',
                            action='store_true',
                            help='drop database if exists and create new one')
        parser.add_argument('-c', '--create',
                            action='store_true',
                            help='create database if does not exists')

    def handle(self, *args, **kwargs):
        hard_reset = kwargs['hard']
        create = kwargs['create']
        if hard_reset:
            create = False
        res = self.init_execution(hard_reset, create)
        if res == 'done':
            print('Database created')
            importlib.import_module('del')
            call_command('makemigrations')
            call_command('makemigrations', 'website', 'tenant_only' ,'customers', 'auth_t')
            call_command('migrate')
            call_command('loaddata', 'website/fixtures/data.json')
        else:
            print('failed ' + res)