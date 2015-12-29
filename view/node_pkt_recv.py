#!/usr/bin/env python
# coding=utf-8

import tornado.web
import json
import logging

class NodePktRecvHandler(tornado.web.RequestHandler):
    def post(self):
