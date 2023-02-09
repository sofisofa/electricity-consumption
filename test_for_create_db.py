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
    
    
    
    unstub()
    
    
if __name__ == "__main__":
    pytest.main([__file__])
    