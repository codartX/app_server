#!/usr/bin/env python
# coding=utf-8
#
#  Created by Jun Fang on 15-12-10.
#  Copyright (c) 2015年 Jun Fang. All rights reserved.

import sys
reload(sys)
sys.setdefaultencoding("utf8")

import os.path
import re
import memcache
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado import gen

import handler.user

from model.user import UserModel

from tornado.options import define, options
from lib.session import Session, SessionManager
from jinja2 import Environment, FileSystemLoader

import psycopg2
import momoko

from cassandra.cluster import Cluster
from lib.tornado_cassandra import TornadoCassandra 

import logging

define("port", default = 80, help = "run on the given port", type = int)
define('postgres_node', default = '127.0.0.1', help = 'postgresql node ip')
define('cassandra_node', default = '127.0.0.1', help = 'cassandra node ip')

class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies = True,
            cookie_secret = "cookie_secret_code",
            login_url = "/login",
            autoescape = None,
            jinja2 = Environment(loader = FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")), trim_blocks = True),
            reserved = ["user", "home", "setting", "forgot", "login", "logout", "register", "admin"],
        )

        handlers = [
            (r"/", view.index.IndexHandler),
            (r"/login", view.user.LoginHandler),
            (r"/logout", view.user.LogoutHandler),
            (r"/nodes_list", view.node.LogoutHandler),
            (r"/nodes_nearby", view.node.GetNodesNearbyHandler),
            (r"/get_nodes", view.node.LogoutHandler),
            (r"/node/(.*)", view.node.LogoutHandler),
            (r"/get_pkts", view.node_pkt.LogoutHandler),
            (r"/get_latest_pkt", view.node_pkt.LogoutHandler),
            (r"/get_history", view.node_pkt.LogoutHandler),

            (r"/lora/push", view.node_pkt_push.NodePktPushHandler),

            (r"/(favicon\.ico)", tornado.web.StaticFileHandler, dict(path = settings["static_path"])),
            (r"/(sitemap.*$)", tornado.web.StaticFileHandler, dict(path = settings["static_path"])),
            (r"/(bdsitemap\.txt)", tornado.web.StaticFileHandler, dict(path = settings["static_path"])),
        ]

        tornado.web.Application.__init__(self, handlers, **settings)

        ioloop = tornado.ioloop.IOLoop.instance()

        self.db = momoko.Pool(dsn='dbname=lora user=postgres password=postgres host=localhost port=5432',
                              size=1,
                              ioloop=ioloop)

        future = application.db.connect()
        ioloop.add_future(future, lambda f: ioloop.stop())
        ioloop.start()
        future.result()

        self.cluster = Cluster(['127.0.0.1'])
        self.session = self.cluster.connect('lora')
        self.cass_conn = TornadoCassandra(self.session, ioloop=ioloop)
  
        # Have one global model for db query
        self.user_model = UserModel(self.db)
        self.node_model = NodeModel(self.db)
        self.node_pkt_model = NodePktModel(self.cass_conn)

        # Have one global session controller
        self.session_manager = SessionManager(settings["cookie_secret"], ["127.0.0.1:11211"], 0)

        # Have one global memcache controller
        self.mc = memcache.Client(["127.0.0.1:11211"])

def main():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()

