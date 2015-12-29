#!/usr/bin/env python
# coding=utf-8
#
#  Created by Jun Fang on 15-12-10.
#  Copyright (c) 2015年 Jun Fang. All rights reserved.

from tornado import gen

class NodeModel():
    def __init__(self, db):
        self.db = db
    
    @gen.coroutine
    def add_new_node(self, node, lat, lng):
        try:
            for key in node:
                key_fields += '{0},'.format(key)
                value_fields += '{0},'.format(node[key])
            if lat and lng:
                key_fields += 'geometry'
                value_fields += 'ST_SetSRID(ST_MakePoint({0}, {1}), 4326)'.format(lng, lat) 
            sql = """
                    INSERT INTO node ({0}) VALUES ({1})
                  """.format(key_fields[0:-1], value_fields[0:-1])
            result = yield self.db.execute(sql)
            raise gen.Return(result)
        except Exception, e:
            logging.error('add_new_node error:%s' % str(e))
            raise gen.Return(None)
    
    @gen.coroutine
    def get_node(self, owner_id, node_addr):
        try:
            cursor = yield self.db.execute('SELECT * FROM node WHERE node_addr={0} and owner_id={1}'.format(dev_addr, owner_id))
            result = cursor.fetchone()
            raise gen.Return(result)
        except Exception, e:
            logging.error('get_node error:%s' % str(e)) 
            raise gen.Return(None)
    
    @gen.coroutine
    def get_node_by_id(self, owner_id, node_id):
        try:
            cursor = yield self.db.execute('SELECT * FROM node WHERE id={0} AND owner_id={1}'.format(node_id, owner_id))
            result = cursor.fetchone()
            raise gen.Return(result)
        except Exception, e:
            logging.error('get_node_by_id error:%s' % str(e)) 
            raise gen.Return(None)

    @gen.coroutine
    def get_node_nearby(self, owner_id, lat, lng, distance, limit):
        try:
            cursor = yield self.db.execute('SELECT * FROM node WHERE owner_id={0} AND st_dWithin(geometry,\'SRID=4326;POINT({1} {2})\', {3})='.format(owner_id, lng, lat, distance*1000))
            if limit:
                nodes = cursor.fetchmany(limit) 
            else:
                nodes = cursor.fetchall() 
            raise gen.Return(nodes)
        except Exception, e:
            logging.error('get_node_nearby error:%s' % str(e)) 
            raise gen.Return(None)

    @gen.coroutine
    def get_user_nodes_list(self, owner_id, start, limit, orders, conditions):
        try:
            cursor = yield self.db.execute('SELECT * FROM node WHERE owner_id=%s' % owner_id) 
            cursor.scroll(start)
            nodes = cursor.fetchmany(limit) 
            raise gen.Return(nodes)
        except Exception, e:
            logging.error('get_user_all_devices error:%s' % str(e)) 
            raise gen.Return(None)
    
    @gen.coroutine
    def set_node_info(self, dev_addr, info):
        try:
            for key in info:
                fields += '{0}={1},'.format(key, info[key])
            sql = """
                    UPDATE user
                    SET {0}
                    WHERE dev_addr=%s
                  """.format(fields[0:-1], dev_addr)
            result = yield self.db.execute(sql)
            raise gen.Return(result)
        except Exception, e:
            logging.error('set_node_info error:%s' % str(e)) 
            raise gen.Return(None)
