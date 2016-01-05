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
from base import *

class GetPktsHandler(BaseHandler):
    @tornado.web.authenticated
    @gen.coroutine
    def get(self, template_variables = {}):
        try:
            dev_addr = request.GET.get('dev_addr', '')
            start = int(request.GET.get('iDisplayStart', 0))
            limit = int(request.GET.get('iDisplayLength', 25))

            total = LoraUplinkPacket.objects.filter(dev_addr=dev_addr).count()
            packets = LoraUplinkPacket.objects.filter(dev_addr=dev_addr).order_by('-ts')[start: start+limit]

            data = []
            for x in packets:
                data.append({
                             'time': x.ts,
                             'app_data': x.data,
                            })

            result = {'iTotalRecords': total,                  # num records before applying any filters
                      'iTotalDisplayRecords': total, # num records after applying filters
                      'sEcho':request.GET.get('sEcho',1),      # unaltered from query
                      'aaData': data}

        except Exception, e:
            logger.error('Get packets:%s' % str(e))
            result = {'iTotalRecords': 0,                 # num records before applying any filters
                      'iTotalDisplayRecords': 0,              # num records after applying filters
                      'sEcho':request.GET.get('sEcho',1),     # unaltered from query
                      'aaData': []}

        return JsonResponse(result)

class GetLatestPktInfoHandler(BaseHandler):
    @tornado.web.authenticated
    @gen.coroutine
    def get(self, template_variables = {}):
        try:
            dev_addr = request.GET.get('dev_addr')
            node = LoraNode.objects.get(owner=request.user, dev_addr=dev_addr)
        except Exception, e:
            logger.error('Get latest pkt info, get node error:%s' % str(e))
            return JsonResponse({'status': 'fail', 'message': 'Invalid Device Address'})

        try:
            up_packet = LoraUplinkPacket.objects.filter(dev_addr=dev_addr).order_by('-ts').limit(1)
            if up_packet:
                last_sf = up_packet[0].datr.split('BW')[0]
                last_snr = up_packet[0].lsnr
                last_rssi = up_packet[0].rssi
                last_up_frame = up_packet[0].ts
            else:
                last_sf = '-'
                last_snr = '-'
                last_rssi = '-'
                last_up_frame = '-'
            return JsonResponse({'status': 'success', 'data': {'last_sf': last_sf, 'last_snr': last_snr,
                                                               'last_rssi': last_rssi, 'last_up_frame': last_up_frame}})
        except Exception, e:
            logger.error('Get latest pkt info error:%s' % str(e))
            return JsonResponse({'status': 'fail', 'message': 'Database fail'})

class GetHistoryHandler(BaseHandler):
    @tornado.web.authenticated
    @gen.coroutine
    def get(self, template_variables = {}):
        try:
            dev_addr = request.GET.get('dev_addr')
            node = LoraNode.objects.get(owner=request.user, dev_addr=dev_addr)
        except Exception, e:
            logger.error('Get history error, get node:%s' % str(e))
            return JsonResponse({'status': 'fail', 'message': 'Invalid Device Address'})

        try:
            start_timestamp = int(request.GET.get('start_timestamp', time.time()))
            days = int(request.GET.get('range', 10))#days
            if start_timestamp:
                start_time = datetime.fromtimestamp(start_timestamp)
                up_packets = LoraUplinkPacket.objects.filter(dev_addr=dev_addr, ts__gt=start_time - timedelta(days=days), ts__lt=start_time)
                down_packets = LoraDownlinkPacket.objects.filter(dev_addr=dev_addr, ts__gt=start_time - timedelta(days=days), ts__lt=start_time)
            else:
                up_packets = LoraUplinkPacket.objects.filter(dev_addr=dev_addr, ts__gt=datetime.uctnow() - timedelta(days=days), ts__lt=datetime.uctnow())
                down_packets = LoraDownlinkPacket.objects.filter(dev_addr=dev_addr, ts__gt=datetime.uctnow() - timedelta(days=days), ts__lt=datetime.utcnow())

            data = []
            uplink_data = {}
            downlink_data = {}
            rssi_data = {}
            snr_data = {}
            sf_data = {}
            snr_sum = 0.0
            rssi_sum = 0

            if up_packets:
                delta_time = up_packets[-1].ts - up_packets[0].ts
                average_pkts = len(up_packets)/(delta_time.days+1)
            else:
                average_pkts = 0

            for pkt in up_packets:
                key = str(pkt.ts.date().month)+'.'+str(pkt.ts.date().day)
                if key in uplink_data:
                    uplink_data[key] = uplink_data[key] + 1
                else:
                    uplink_data[key] = 1

                if key in rssi_data:
                    rssi_data[key] = [rssi_data[key][0] + 1,  rssi_data[key][1] + pkt.rssi]
                else:
                    rssi_data[key] = [1, pkt.rssi]

                if key in snr_data:
                    snr_data[key] = [snr_data[key][0] + 1,  snr_data[key][1] + pkt.lsnr]
                else:
                    snr_data[key] = [1, pkt.lsnr]

                sf = int(pkt.datr.split('BW')[0][2:])
                if sf in sf_data:
                    sf_data[sf] = sf_data[sf] + 1
                else:
                    sf_data[sf] = 1

                snr_sum = snr_sum + pkt.lsnr
                rssi_sum = rssi_sum + pkt.rssi

            for key in rssi_data:
                rssi_data[key] = rssi_data[key][1]/rssi_data[key][0]

            for key in snr_data:
                snr_data[key] = snr_data[key][1]/snr_data[key][0]

            if len(up_packets):
                average_snr = snr_sum/len(up_packets)
                average_rssi = rssi_sum/len(up_packets)
            else:
                average_snr = 0
                average_rssi = 0

            for pkt in down_packets:
                key = str(pkt.ts.date().month)+'.'+str(pkt.ts.date().day)
                if key in downlink_data:
                    downlink_data[key] = downlink_data[key] + 1
                else:
                    downlink_data[key] = 1

            return JsonResponse({'status': 'success', 'data': {'rssi_data': rssi_data, 'snr_data': snr_data, 'sf_data': sf_data,
                                                               'uplink_data': uplink_data, 'downlink_data': downlink_data,
                                                               'packets': average_pkts, 'snr': average_snr, 'rssi': average_rssi}})
        except Exception, e:
            logger.error('Get history error:%s' % str(e))
            return JsonResponse({'status': 'fail', 'message': 'Database fail'})

