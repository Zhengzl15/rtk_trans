#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : basestation_thread.py
# Author        : bssthu
# Project       : rtk_trans
# Description   : 
# 

import socket
import threading
import time
import log
import socketserver

BUFFER_SIZE = 4096


class BaseStationHandler(socketserver.StreamRequestHandler):
    """接收基站发送的差分数据"""

    def __init__(self, got_data_cb):
        """构造函数

        Args:
            base_station_port: 差分源服务器端口
            got_data_cb: 接收到数据包时调用的回调函数
        """
        #super().__init__()
        self.got_data_cb = got_data_cb
        self.recv_count = 0
        self.running = True

    def handle(self):
        """线程主函数

        循环运行，接受新的客户端的连接。
        """
        while self.running:
            data = self.rfile.readline().strip()
            cur_thread = threading.currentThread()
            log.info('recv from %s' % (self.client_address[0]))
            if data == None or len(data) == 0:
                break
            self.recv_count += 1
            self.got_data_cb(data, self.recv_count)
                
        log.info('thread: bye')

class BaseStationThread(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass
