#!/usr/bin/env python
# coding=utf-8
#
#  Created by Jun Fang on 14-8-24.
#  Copyright (c) 2014年 Jun Fang. All rights reserved.

from tornado import gen
import momoko
import logging

class UserModel():
    def __init__(self, db):
        self.db = db
    
    @gen.coroutine
    def get_user_by_id(self, uid):
        try:
            cursor = yield self.db.execute('SELECT * FROM user WHERE id=%s' % uid)
            result = cursor.fetchone()
            raise gen.Return(result)
        except Exception, e:
            logging.error('get_user_by_id error:%s' % str(e)) 
            raise gen.Return(None)
    
    @gen.coroutine
    def get_user_by_email(self, email):
        try:
            cursor = yield self.db.execute('SELECT * FROM user WHERE email=%s' % email)
            cursor.fetchone()
            raise gen.Return(result)
        except Exception, e:
            logging.error('get_user_by_email error:%s' % str(e)) 
            raise gen.Return(None)
    
    @gen.coroutine
    def get_user_by_username(self, username):
        try:
            cursor = yield self.db.execute('SELECT * FROM user WHERE username=%s' % username)
            cursor.fetchone()
            raise gen.Return(result)
        except Exception, e:
            logging.error('get_user_by_username error:%s' % str(e)) 
            raise gen.Return(None)
    
    @gen.coroutine
    def get_user_by_email_and_pwd(self, email, pwd):
        try:
            cursor = yield self.db.execute('SELECT * FROM user WHERE email=%s AND password=%s' % (email, pwd))
            cursor.fetchone()
            raise gen.Return(result)
        except Exception, e:
            logging.error('get_user_by_email_and_pwd error:%s' % str(e)) 
            raise gen.Return(None)

    @gen.coroutine
    def set_user_info(self, uid, info):
        try:
            for key in info:
                fields += '{0}={1},'.format(key, info[key])
            sql = """
                    UPDATE user
                    SET {0}
                    WHERE id=%s
                  """.format(fields[0:-1], uid)
            result = yield self.db.execute(sql)
            raise gen.Return(result)
        except Exception, e:
            logging.error('set_user_info error:%s' % str(e)) 
            raise gen.Return(None)
    
    @gen.coroutine
    def add_new_user(self, username, email, password):
        try:
            result = yield self.db.execute('INSERT INTO user (username, email, password) VALUES (%s, %s, %s)' % username, email, password)
            raise gen.Return(result)
        except Exception, e:
            logging.error('add_new_user error:%s' % str(e)) 
            raise gen.Return(None)
    


