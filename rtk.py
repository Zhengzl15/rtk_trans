#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : rtk.py
# Author        : bssthu
# Project       : rtk_trans
# Description   : socket 转发数据
# 

import json
import log
from control_thread import ControlThread
from dispatcher_thread import DispatcherThread
from gps_thread import GPSThread
from basestation_thread import *
import threading


class Rtk:
    def __init__(self):
        self.basestation_server = None
        self.controller = None
        self.dispatcher = None
        self.gps_server = None

    def got_data_cb(self, data, rcv_count):
        """接收到差分数据的回调函数

        Args:
            data: 收到的数据包
            rcv_count: 收到的数据包的编号
        """
        print ('Got a message: %s' %data)
        self.dispatcher.data_queue.put((data, rcv_count))

    def got_client_cb(self, client_socket, address):
        """接受来自下层客户端的 socket 连接的回调函数

        Args:
            client_socket: 与客户端连接的 socket
            address: 客户端地址
        """
        self.dispatcher.add_client(client_socket, address)

    def got_command_cb(self, command):
        """接收到来自控制端口的指令的回调函数

        Args:
            command: 待处理的命令
        """
        if command == 'reset server':
            old_dispatcher = self.dispatcher
            self.dispatcher = DispatcherThread()
            old_dispatcher.running = False
            self.dispatcher.start()
        elif command == 'list':
            self.controller.msg_queue.put('client count: %d\r\n' % len(self.dispatcher.clients))
            for _id, sender in self.dispatcher.clients.copy().items():
                self.controller.msg_queue.put('%d: %s, %d\r\n' % (sender.sender_id, sender.address, sender.send_count))

    def main(self):
        # config
        config_file_name = 'conf/config.json'
        try:
            with open(config_file_name) as config_data:
                configs = json.load(config_data)
        except:
            print ('failed to load config from config.json.')
            return

        # log init
        log.initialize_logging(configs['enable_log'].lower() == 'true')
        log.info('Main: start')

        # threads
        self.basestation_server = BaseStationThread(('localhost', configs['basestation_port']), BaseStationHandler(self.got_data_cb))
        server_thread = threading.Thread(target=self.basestation_server.serve_forever)
        server_thread.setDaemon(True)
        server_thread.start()
        self.basestation_server.serve_forever()
        self.controller = ControlThread(configs['control_port'], self.got_command_cb)
        self.dispatcher = DispatcherThread()
        self.gps_server = GPSThread(configs['gps_port'], self.got_client_cb)

        #self.basestation_server.start()
        self.controller.start()
        self.dispatcher.start()
        self.gps_server.start()

        # keyboard
        try:
            print("enter 'q' to quit")
            while input() != 'q':
                print("enter 'q' to quit. rcv count: %d, client count: %d"
                      % (self.basestation_server.recv_count, len(self.dispatcher.clients)))
                if not self.basestation_server.running or not self.gps_server.running:
                    break
        except KeyboardInterrupt:
            pass

        # quit & clean up
        self.controller.running = False
        self.controller.join()
        self.basestation_server.running = False
        #self.basestation_server.join()
        self.gps_server.running = False
        self.gps_server.join()
        self.dispatcher.running = False
        self.dispatcher.join()
        log.info('Main: bye')


if __name__ == '__main__':
    rtk = Rtk()
    rtk.main()
