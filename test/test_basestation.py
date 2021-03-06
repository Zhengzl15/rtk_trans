#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import socket
import sys
import time

def test():
    HOST = '123.57.250.117'    # The remote host
    PORT = 10181             # The same port as used by the server
    s = None
    for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        try:
            s = socket.socket(af, socktype, proto)
        except socket.error:
            s = None
            continue
        try:
            s.connect(sa)
        except socket.error:
            s.close()
            s = None
            continue
        break
    if s is None:
        print 'could not open socket'
        sys.exit(1)

    #发送一千次
    for i in range(0, 1000):
        s.sendall('Hello, world')
        time.sleep(1) #100ms
        print 'send a message'
    s.close()
    print 'Done'

if __name__ == '__main__':
    test()