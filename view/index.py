#!/usr/bin/env python
# coding=utf-8
#
#
#  Created by Jun Fang on 14-8-24.
#  Copyright (c) 2014年 Jun Fang. All rights reserved.

import time
import json
import tornado.web
from tornado import gen

from base import *

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class IndexHandler(BaseHandler):
    @tornado.web.authenticated
    @gen.coroutine
    def get(self, template_variables = {}):
        try:
            total_device_count, = UserProfile.objects.filter(user=request.user).values_list('node_count')[0]
        except Exception, e:
            total_device_count = 0
            pass

        try:
            client_ip = get_client_ip(request)
            g = GeoIP()
            lat,lng = g.lat_lon(client_ip)
            location = {'lat': lat, 'lng': lng}
            #return render(request, 'dashboard.html', {'total_device_count': total_device_count, 'user_location': location})
            return render(request, 'dashboard_amap.html', {'total_device_count': total_device_count, 'user_location': location})
        except Exception, e:
            logger.error('Dashboard error:%s' % str(e))
            #return render(request, 'dashboard.html', {'total_device_count': total_device_count})
            return render(request, 'dashboard_amap.html', {'total_device_count': total_device_count})

