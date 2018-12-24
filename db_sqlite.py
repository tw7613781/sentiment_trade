'''
db_sqlite module provide a db rapper for sqlite
'''

import sqlite3

def db_init(cmd_sql):
    '''
    create table
    '''
    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()
    cursor.execute(cmd_sql)
    cursor.close()
    conn.close()


def db_select(cmd_sql):
    '''
    select op
    '''
    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()
    cursor.execute(cmd_sql)
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    # return a 2-dimension array including sql select result
    return records


def db_insert(cmd_sql, params):
    '''
    insert op
    '''
    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()
    cursor.execute(cmd_sql, params)
    cursor.close()
    conn.commit()
    conn.close()
