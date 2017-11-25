#!/usr/bin/python

import psycopg2
from config import config


def drop_tables():
    """ drop tables in the PostgreSQL database"""
    commands = (
        """
        DROP TABLE btc_dip;;
        """,
        """
        DROP TABLE ohlcv;
        """,
        """ 
        DROP TABLE prices;
        """,
        """ 
        DROP TABLE total_balance_history;
        """,
        """ 
        DROP TABLE balances;
        """,
        """
        DROP TABLE history;
        """,
        """
        DROP TABLE potentials;
        """,
        """
        DROP TABLE actives;
        """)
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """ CREATE TABLE ohlcv (
            pair VARCHAR(255) NOT NULL,
            timestamp_ut INTEGER NOT NULL,
            open NUMERIC NOT NULL,
            high NUMERIC NOT NULL,
            low NUMERIC NOT NULL,
            close NUMERIC NOT NULL,
            volume INTEGER NOT NULL
            )
        """,
        """ CREATE TABLE btc_dip (
            timestamp_ut INTEGER NOT NULL,
            price NUMERIC NOT NULL,
            primary key(timestamp_ut)
            )
        """,
        """ CREATE TABLE prices (
            exchange VARCHAR(20) NOT NULL,
            pair VARCHAR(12) NOT NULL,
            price NUMERIC NOT NULL,
            primary key(exchange, pair)
            )
        """,
        """ CREATE TABLE total_balance_history (
            balance_date VARCHAR(20) NOT NULL,
            exchange VARCHAR(20) NOT NULL,
            coin VARCHAR(12) NOT NULL,
            btc_value NUMERIC NOT NULL,
            usd_value NUMERIC NOT NULL,
            primary key (balance_date, exchange, coin)
            )
        """,
        """ CREATE TABLE balances (
            exchange VARCHAR(20) NOT NULL,
            coin VARCHAR(12) NOT NULL,
            amount NUMERIC NOT NULL,
            primary key(exchange, coin)
            )
        """,
        """ CREATE TABLE potentials (
            pair VARCHAR(12) NOT NULL PRIMARY KEY,
            ttl INTEGER NOT NULL DEFAULT 5,
            adx INTEGER NOT NULL,
            adx_start_ut INTEGER NOT NULL,
            direction VARCHAR(4) NOT NULL,
            start_price NUMERIC NOT NULL,
            periods_active INTEGER DEFAULT 0,
            hot BOOLEAN default FALSE,
            trigger NUMERIC DEFAULT 0,
            low_price NUMERIC DEFAULT 0,
            high_price NUMERIC DEFAULT 0
            )
        """,
        """ CREATE TABLE history (
            pair VARCHAR(12) NOT NULL,
            active_type VARCHAR(12) NOT NULL,
            ut_entered INTEGER NOT NULL,
            ut_exited INTEGER NOT NULL,
            direction VARCHAR(4) NOT NULL,
            price NUMERIC NOT NULL,
            exit_price NUMERIC NOT NULL,
            amount NUMERIC NOT NULL,
            profit NUMERIC NOT NULL
            )
        """,
        """ CREATE TABLE actives (
            pair VARCHAR(12) NOT NULL PRIMARY KEY,
  	    active_type VARCHAR(12) NOT NULL,
            ut_bought INTEGER NOT NULL,
	    direction VARCHAR(4) NOT NULL,
            price NUMERIC NOT NULL,
            amount numeric NOT NULL,
            stop_price NUMERIC NOT NULL,
            limit_price NUMERIC NOT NULL
            )
        """)
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    drop_tables()
    create_tables()
