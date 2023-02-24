#!/usr/bin/env python3

import pytest
import psycopg2
import create_database
from mockito import when, mock, verify, unstub

DB_NAME = 'DB_NAME'
DB_USER = 'DB_USER'
DB_PW = 'DB_PW'
DB_PORT = 'DB_PORT'
DB_HOST = 'DB_HOST'


class TestClassCreateDatabase:
    def test_connected_to_database(self):
        conn_info = {
            "host": DB_HOST,
            "port": DB_PORT,
            "user": DB_USER,
            "password": DB_PW,
        }
        
        dummy_conn = mock()
        when(psycopg2).connect(
            database=DB_NAME,
            host=conn_info['host'],
            user=conn_info['user'],
            password=conn_info['password'],
            port=conn_info['port'],
        ).thenReturn(dummy_conn)
        
        conn = create_database.connect_to_database(DB_NAME, conn_info)
        assert conn == dummy_conn
    
    def test_not_connected_to_database(self):
        conn_info = {
            "host": DB_HOST,
            "port": DB_PORT,
            "user": DB_USER,
            "password": DB_PW,
        }
        
        when(psycopg2).connect(
            database=DB_NAME,
            host=conn_info['host'],
            user=conn_info['user'],
            password=conn_info['password'],
            port=conn_info['port'],
        ).thenRaise(Exception)
        
        with pytest.raises(Exception):
            create_database.connect_to_database(DB_NAME, conn_info)
    
    def test_database_created(self):
        # Given
        conn_info = {
            "host": DB_HOST,
            "port": DB_PORT,
            "user": DB_USER,
            "password": DB_PW,
        }
        
        dummy_conn = mock()
        dummy_cur = mock()
        when(psycopg2).connect(
            host=conn_info['host'],
            user=conn_info['user'],
            password=conn_info['password'],
            port=conn_info['port'],
        ).thenReturn(dummy_conn)
        when(dummy_conn).cursor().thenReturn(dummy_cur)
        
        when(dummy_cur).execute(...).thenReturn(None)
        when(dummy_cur).fetchone(...).thenReturn(False)
        when(dummy_conn).close().thenReturn(None)
        when(dummy_cur).close().thenReturn(None)
        
        # when
        db_created= create_database.create_db(DB_NAME, conn_info)
        
        # then
        assert db_created == True
    
    def test_database_not_created(self):
        # Given
        conn_info = {
            "host": DB_HOST,
            "port": DB_PORT,
            "user": DB_USER,
            "password": DB_PW,
        }
        
        create_db_query = f"CREATE DATABASE {DB_NAME}"
        search_query = f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'"
        
        dummy_conn = mock()
        dummy_cur = mock()
        when(psycopg2).connect(
            host=conn_info['host'],
            user=conn_info['user'],
            password=conn_info['password'],
            port=conn_info['port'],
        ).thenReturn(dummy_conn)
        when(dummy_conn).cursor().thenReturn(dummy_cur)

        when(dummy_cur).execute(search_query).thenReturn(None)
        when(dummy_cur).fetchone(...).thenReturn(False)
        when(dummy_cur).execute(create_db_query).thenRaise(Exception)
        when(dummy_conn).close().thenReturn(None)
        when(dummy_cur).close().thenReturn(None)
        
        # when
        db_created = create_database.create_db(DB_NAME, conn_info)
    
        # then
        assert db_created == False

    def test_database_exists(self):
        # Given
        conn_info = {
                "host": DB_HOST,
                "port": DB_PORT,
                "user": DB_USER,
                "password": DB_PW,
            }

        search_query = f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'"

        dummy_conn = mock()
        dummy_cur = mock()
        
        when(psycopg2).connect(
            host=conn_info['host'],
            user=conn_info['user'],
            password=conn_info['password'],
            port=conn_info['port'],
            ).thenReturn(dummy_conn)
        
        when(dummy_conn).cursor().thenReturn(dummy_cur)

        when(dummy_cur).execute(search_query).thenReturn(None)
        when(dummy_cur).fetchone(...).thenReturn(True)
        when(dummy_conn).close().thenReturn(None)
        when(dummy_cur).close().thenReturn(None)
    
        # when
        db_exists = create_database.create_db(DB_NAME, conn_info)
    
        # then
        assert db_exists == True
        
    def test_query_executed(self):
        #Given
        fake_query = 'This is a query'
        dummy_conn = mock()
        dummy_cur = mock()
        when(dummy_conn).cursor().thenReturn(dummy_cur)
        when(dummy_cur).execute(fake_query).thenReturn(None)
        
        #when
        query_executed = create_database.execute_query(fake_query, dummy_conn)
        
        #then
        assert query_executed == True
        
    def test_query_not_executed(self):
        #Given
        fake_query = 'This is a query'
        dummy_conn = mock()
        dummy_cur = mock()
        when(dummy_conn).cursor().thenReturn(dummy_cur)
        when(dummy_cur).execute(fake_query).thenRaise(Exception)
        #when
        query_executed = create_database.execute_query(fake_query, dummy_conn)
        #then
        assert query_executed == False
        
    unstub()


if __name__ == "__main__":
    pytest.main([__file__])
