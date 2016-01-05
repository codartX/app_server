#!/usr/bin/env python
# coding=utf-8

import tornado.web
import json
import logging
from base import *

class NodePktRecvHandler(BaseHandler):
    def post(self):
