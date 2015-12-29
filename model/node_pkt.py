
#!/usr/bin/env python
# coding=utf-8
#
#  Created by Jun Fang on 15-12-10.
#  Copyright (c) 2015年 Jun Fang. All rights reserved.

from tornado import gen

class NodePktModel():
    def __init__(self, conn):
        self.conn = conn

    @gen.coroutine
    def add_new_pkt(self, dev_addr, pkt_info, up_or_down):
        try:
            for key in node:
                key_fields += '{0},'.format(key)
                value_fields += '{0},'.format(node[key])
            key_fields += 'dir'
            value_fields += '%d' % up_or_down
            sql = """
                    INSERT INTO node_pkt ({0}) VALUES ({1})
                  """.format(key_fields[0:-1], value_fields[0:-1])
            result = yield self.db.execute(sql)
            raise gen.Return(result)
        except Exception, e:
            logging.error('add_new_pkt error:%s' % str(e))
            raise gen.Return(None)

    @gen.coroutine
    def get_pkts_in_period(self, dev_addr, from_time, to_time):
        try:
            pkts = yield self.conn.execute('SELECT * from node_pkt WHERE dev_addr = ' + dev_addr +
                                           ' AND ts > ' + str(from_time) +
                                           ' AND ts < ' + str(to_time))
            raise gen.Return(pkt)
        except Exception, e:
            logging.error('get_pkts_in_period error:%s' % str(e))
            raise gen.Return(None)
