#!/usr/bin/env python
# coding=utf-8

import tornado.web
import json
import logging
from base import *

class NodePktPushHandler(BaseHandler):
    def post(self):
        try:
            data = json.loads(self.request.body)
            ns_id = data['txpk']['nsid']
        except Exception as e:
            logging.error('Invalid argument')
            return self.write(json.dumps({'status': 'fail', 'reason': 'Invalid argument'}))

        try:
            self.application.producer.send_messages(str(ns_id), json.dumps(data))
        except Exception as e:
            logging.error('Send msg to Kafka fail:%s' % str(e))
            return self.write(json.dumps({'status': 'fail', 'reason': 'Routing msg fail'}))

        return self.write(json.dumps({'status': 'success'}))
