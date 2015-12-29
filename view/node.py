#!/usr/bin/env python
# coding=utf-8
#
#
#  Created by Jun Fang on 15-12-10.
#  Copyright (c) 2015年 Jun Fang. All rights reserved.

import logging
import tornado.web
import json
from tornado import gen

class NodeListHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, template_variables = {}):
        self.render('nodes_list.html', **template_variables)

class AddNodeHandler(BaseHandler):
    @tornado.web.authenticated
    @gen.coroutine
    def post(self, template_variables = {}):
        name = self.get_argument('node_name', '')
        model = self.get_argument('node_model', '')
        node_eui = self.get_argument('node_eui', '')
        node_addr = self.get_argument('node_addr', '')
        app_eui = self.get_argument('app_eui', '')
        location = self.get_argument('location', '')

        try:
           loc_array = location.split(',')
           loc_point = Point(float(loc_array[1]), float(loc_array[0]))
        except Exception, e:
           logger.error('Lat lng error:%s' % str(e))
           loc_point = None

        if name and model and node_addr and node_eui:
            try:
                lora_node = {}
                lora_node['owner_id'] = request.user
                lora_node['name'] = name
                lora_node['model'] = model
                lora_node['node_eui'] = node_eui
                lora_node['node_addr'] = node_addr
                lora_node['app_eui'] = app_eui
                if loc_point:
                    lora_node['geometry'] = loc_point
                result = yield self.node_model.add_new_node(lora_node)
                if result is None:
                    return JsonResponse({'status': 'fail', 'message': 'Database fail'})
                
                user_info = self.get_current_user()
                user_info = yield self.user_model.get_user_by_id(user_info['id'])
                if user_info:
                    user_info['node_count'] += 1
                    result = yield set_user_info(user_info['id'], {'node_count': user_info['node_count']})
                    self.update_current_user(user_info)
                self.write(json.dumps({'status': 'success'}))
            except Exception, e:
                logger.error('Add node error:%s' % str(e))
                self.write(json.dumps({'status': 'fail', 'message': 'Database fail'}))
        else:
            self.write(json.dumps({'status': 'fail', 'message': 'Invalid form'}))

class NodeDetailHandler(BaseHandler):
    @tornado.web.authenticated
    @gen.coroutine
    def get(self, node_id, template_variables = {}):
        user_info = self.get_current_user()
        node = self.node_model.get_node_by_id(node_id)
        if node is None or node.owner_id != user_info['id']:
            self.render('404.html')
        if node.geometry:
            location = {'lat': node.geometry.y, 'lng': node.geometry.x}
        else:
            location = {}
        data = {
                'id': node.id,
                'name': node.name,
                'location': location,
                'model': node.model,
                'node_addr': node.node_addr,
                'node_eui': node.node_eui,
                'lora_version': node.lora_version
               }

        self.render('device_detail_amap.html', {'node': data})

class GetNodesNearbyHandler(BaseHandler):
    @tornado.web.authenticated
    @gen.coroutine
    def get(self, node_id, template_variables = {}):
        try:
            distance = float(self.get_argument('distance', 10.0))
            #if distance > 100:
            #    distance = 100
            lat = float(self.get_argument('lat', 0))
            lng = float(self.get_argument('lng', 0))
            if not lat or not lng:
                self.write(json.dumps({'nodes':[]}))
            searchPoint = Point(lng, lat)
            # Search database
            devices = LoraNode.objects.filter(owner=request.user, geometry__distance_lte=(searchPoint, D(km=distance)))
            # Return
            self.write(json.dumps({'nodes': [{
                                   'name': x.name,
                                   'location': [x.geometry.y, x.geometry.x],
                                   'model': x.model,
                                   'dev_addr': x.node_addr,
                                   'dev_eui': x.node_eui,
                                   'lora_version': x.lora_version,
                                   'id': x.id,
                                   } for x in nodes]}))
        except Exception, e:
            logger.error('Get nodes nearby error:%s' % str(e))
            self.write(json.dumps({'nodes': []}))


class GetNodesHandler(BaseHandler):
    @tornado.web.authenticated
    @gen.coroutine
    def get(self, device_id, template_variables = {}):
    try:
        start = int(request.GET.get('iDisplayStart', 0))
        limit = int(request.GET.get('iDisplayLength', 25))
        sort_col_num = request.GET.get('iSortCol_0', 0)
        sort_col_name = request.GET.get('mDataProp_{0}'.format(sort_col_num), 'value')
        search_text = request.GET.get('sSearch', '').lower()
        sort_dir = request.GET.get('sSortDir_0', 'asc')
        sort_dir_prefix = (sort_dir=='desc' and '-' or '')
        total, = UserProfile.objects.filter(user=request.user).values_list('node_count')[0]
        if search_text:
            q = Q()
            searches = search_text.split()
            for word in searches:
                q = q & (Q(name__contains=word)|Q(model__contains=word)|Q(dev_addr__contains=word)|
                         Q(dev_eui__contains=word))
            display = LoraNode.objects.filter(owner=request.user).filter(q).count()
            devices = LoraNode.objects.filter(owner=request.user).filter(q).order_by('{0}{1}'.format(sort_dir_prefix, sort_col_name))[start: start + limit]
        else:
            display = total
            devices = LoraNode.objects.filter(owner=request.user).order_by('{0}{1}'.format(sort_dir_prefix, sort_col_name))[start: start + limit]

        data = []
        for x in devices:
            if x.geometry:
                location = {'lat': x.geometry.y, 'lng': x.geometry.x}
            else:
                location = {}
            data.append({
                         'name': x.name,
                         'location': location,
                         'model': x.model,
                         'dev_addr': x.dev_addr,
                         'dev_eui': x.dev_eui,
                         'lora_version': x.lora_version,
                         'id': x.id
                        })

        result = {'iTotalRecords': total,                  # num records before applying any filters
                  'iTotalDisplayRecords':display , # num records after applying filters
                  'sEcho':request.GET.get('sEcho',1),      # unaltered from query
                  'aaData': data}

    except Exception, e:
        result = {'iTotalRecords': 0,                 # num records before applying any filters
                  'iTotalDisplayRecords': 0,              # num records after applying filters
                  'sEcho':request.GET.get('sEcho',1),     # unaltered from query
                  'aaData': []}

    return JsonResponse(result)
