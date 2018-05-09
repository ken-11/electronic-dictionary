#!/usr/bin/python3
from __future__ import unicode_literals
# coding=utf-8

from signal import *
from socket import *
import pymysql
from time import *
import sys
import os
from youdaoTest import query


def do_child(connfd, db):
    while True:
        msg = connfd.recv(128).decode()
        print("msg : ", msg)

        if msg[0] == 'R':
            do_register(connfd, msg, db)

        if msg[0] == 'L':
            do_login(connfd, msg, db)

        if msg[0] == 'Q':
            do_query(connfd, msg, db)

        if msg[0] == 'H':
            do_history(connfd, msg, db)

        if msg[0] == 'E':
            connfd.close()
            sys.exit(0)
    return


def do_register(connfd, msg, db):
    print("in register.......")
    cursor = db.cursor()
    s = msg.split(' ')
    name = s[1]
    passwd = s[2]

    sql = "select * from user where name = '%s'" % name
    cursor.execute(sql)
    data = cursor.fetchone()
    print(data)

    if data != None:
        connfd.send("FALL".encode())
        return

    sql = "insert into user values ('%s','%s')" % (name, passwd)

    try:
        cursor.execute(sql)
        db.commit()
        connfd.send('OK'.encode())
    except:
        connfd.send("FALL".encode())
        db.rollback()
        return
    else:
        print("register OK !")


def do_login(connfd, msg, db):
    print("in login.......")
    cursor = db.cursor()
    s = msg.split(' ')
    name = s[1]
    passwd = s[2]

    try:
        sql = "select * from user where name = '%s' and passwd = '%s'" % (
            name, passwd)
        cursor.execute(sql)
        data = cursor.fetchone()
        print(data)
    except:
        pass

    if data == None:
        connfd.send("FALL".encode())
    else:
        connfd.send('OK'.encode())

    return


def do_query(connfd, msg, db):
    print("in query.......")
    start = time()
    cursor = db.cursor()
    s = msg.split(' ')
    words = s[1]
    name = s[2]
    msg = query(words)
    connfd.send(msg.encode())
    insert_history(db, words, name)
    client.close()
    end = time()
    times = end - start
    print(times)


def do_history(connfd, msg, db):
    print('in history...')
    s = msg.split(' ')
    name = s[1]
    cursor = db.cursor()
    sql = 'select * from history where name = "%s"' % name
    try:
        cursor.execute(sql)
        data = cursor.fetchall()
        connfd.send('OK'.encode())
    except:
        connfd.send('FALL'.encode())
    sleep(0.1)
    for msg in data:
        name = msg[0]
        word = msg[1]
        time = msg[2]
        sleep(0.01)
        connfd.send(('%s %s %s' % (name, word, time)).encode())
    sleep(0.1)
    connfd.send('over'.encode())


def insert_history(db, words, name):
    time = ctime()
    cursor = db.cursor()
    sql = 'insert into history values ("%s","%s","%s")' % (name, words, time)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        print('into history failed')
        db.rollback()


def main():
    signal(SIGCHLD, SIG_IGN)
    db = pymysql.connect('localhost', 'root', '123456', 'dict')

    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    sockfd = socket()
    sockfd.bind((HOST, PORT))
    sockfd.listen(5)

    while True:
        try:
            connfd, addr = sockfd.accept()
            print("connect addr : ", addr)
        except KeyboardInterrupt:
            raise
        except:
            continue

        pid = os.fork()

        if pid < 0:
            print("create child process failed")
            connfd.close()
            continue
        elif pid == 0:
            sockfd.close()
            do_child(connfd, db)
        else:
            connfd.close()
            continue

    db.close()
    sockfd.close()
    sys.exit(0)


if __name__ == "__main__":
    main()
