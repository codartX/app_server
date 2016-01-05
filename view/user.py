#!/usr/bin/env python
# coding=utf-8
#
#
#  Created by Jun Fang on 15-12-10.
#  Copyright (c) 2015年 Jun Fang. All rights reserved.

import time
import json
import hashlib
import tornado.web
from tornado import gen

from base import *

def do_login(self, user_info):
    self.session['id'] = user_info['id']
    self.session['username'] = user_info['username']
    self.session['email'] = user_info['email']
    self.session['password'] = user_info['password']
    self.session.save()
    self.update_current_user(user_info)

def do_logout(self):
    # destroy sessions
    self.session['id'] = None
    self.session['username'] = None
    self.session['email'] = None
    self.session['password'] = None
    self.session.save()

    # destroy cookies
    self.clear_cookie('user')

class LoginHandler(BaseHandler):
    def get(self, template_variables = {}):
        do_logout(self)
        self.render('user/login.html', **template_variables)

    @gen.coroutine
    def post(self, template_variables = {}):
        # validate the fields
        template_variables['errors'] = []
        email = self.get_argument('email', '')
        password = self.get_argument('password', '')

        if email and password:
            # continue while validate succeed
            template_variables['email'] = email
            template_variables['password'] = password
            secure_password = hashlib.sha1(password).hexdigest()
            user_info = yield self.user_model.get_user_by_email_and_pwd(email, secure_password)
            
            if(user_info):
                yield do_login(self, user_info)
                self.redirect(self.get_argument('next', '/'))
                return

        template_variables['errors'].append('Email or password is not correct')
        self.get(template_variables)

class LogoutHandler(BaseHandler):
    def get(self):
        do_logout(self)
        # redirect
        self.redirect(self.get_argument('next', '/'))

