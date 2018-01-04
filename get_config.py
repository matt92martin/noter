import os
import sqlite3
import sys


def file_exists(fp):
    return os.path.isfile(fp)


def connect(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception, e:
        print e
    return None


def create_table(conn, sql):
    try:
        c = conn.cursor()
        c.execute(sql)
    except Exception, e:
        print e


def create_user(conn, user):
    sql = """INSERT INTO noter(user,location) VALUES(?,?)"""
    location = ""
    message = "Please enter the full path of your Noter file. (e.g., /home/user/noter.txt): "
    while location == "":
        enteredpath = raw_input(message)
        if file_exists(enteredpath):
            location = enteredpath
        else:
            message = "Invalid path! Please ensure your file is present. (e.g., /home/user/noter.txt): "

    c = conn.cursor()
    c.execute(sql, (user, location,))
    conn.commit()

    c.execute("SELECT user, location FROM noter WHERE id=?", (c.lastrowid,))
    last = c.fetchone()

    return last

def clear_user(conn, user):

    c = conn.cursor()
    c.execute('SELECT id FROM noter WHERE user=?', (user,))

    all = c.fetchmany(2)
    if len(all) != 1:
        c.close()
        sys.exit('Looks like there are more than 1 {} on record! Contact mmartin@focusvision.com'.format(user))

    c.execute('DELETE FROM noter WHERE id=?', c.fetchone())
    print 'Noter file not found. Reconfiguring {}...'.format(user)


def get_user(conn, user):

    try:
        c = conn.cursor()
        c.execute("SELECT user, location FROM noter WHERE user=? ", [user])

        userinfo = c.fetchone()
        if userinfo:
            noter_exists = file_exists(userinfo[1])
            if noter_exists:
                return userinfo

            if not noter_exists:
                clear_user(conn, user)

        userinfo = create_user(conn, user)
        return userinfo

    except Exception, e:
        print e

    return None


def get_or_create(db_file, user):

    sql = """CREATE TABLE IF NOT EXISTS noter (
              id INTEGER PRIMARY KEY,
              user TEXT,
              location TEXT
          );"""
    config = None
    conn = connect(db_file)
    if conn is not None:
        create_table(conn, sql)

        user, location = get_user(conn, user)
        return user, location

    conn.close()
