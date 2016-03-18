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

BUFFER_SIZE = 4096


class BaseStationThread(threading.Thread):
    """接收基站发送的差分数据"""

    def __init__(self, base_station_port, got_data_cb):
        """构造函数

        Args:
            base_station_port: 差分源服务器端口
            got_data_cb: 接收到数据包时调用的回调函数
        """
        super().__init__()
        self.base_station_port = base_station_port
        self.got_data_cb = got_data_cb
        self.recv_count = 0
        self.running = True

    def run(self):
        """线程主函数

        循环运行，接受新的客户端的连接。
        """
        log.info('server thread: start, port: %d' % self.base_station_port)
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(('0.0.0.0', self.base_station_port))
            server.listen(1)
            server.settimeout(3)    # timeout: 3s
            while self.running:
                try:
                    conn, address = server.accept()
                    conn.settimeout(3)
                    data = conn.recv(BUFFER_SIZE)
                    if len(data) == 0:
                        raise RuntimeError('socket connection broken')
                    self.recv_count += 1
                    log.debug('rcv %d bytes. id: %d' % (len(data), self.rcv_count))
                    self.got_data_cb(data, self.recv_count)
                except socket.timeout:
                    pass
            server.close()
            log.info('server thread: bye')
        except Exception as e:
            log.error('server thread error: %s' % e)
            self.running = False
