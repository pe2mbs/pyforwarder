#
#   pyforwarder a raw socket proxy with optional SSL/TLS termination and trace capability
#   Copyright (C) 2018-2020 Marc Bertens-Nguyen m.bertens@pe2mbs.nl
#
#   This library is free software; you can redistribute it and/or modify
#   it under the terms of the GNU Library General Public License GPL-2.0-only
#   as published by the Free Software Foundation; either version 2 of the
#   License, or (at your option) any later version.
#
#   This library is distributed in the hope that it will be useful, but
#   WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#   Library General Public License for more details.
#
#   You should have received a copy of the GNU Library General Public
#   License GPL-2.0-only along with this library; if not, write to the
#   Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
#   Boston, MA 02110-1301 USA
#
import threading
from forwarder.tcp import TcpListener, tcpWorker
from forwarder.udp import udpListener, udpWorker
import forwarder.api as API


def worker():
    tcpListeners = []
    udpListeners = []
    for addr in API.config:
        protocol = addr.destination.portInfo.protocol
        if isinstance( protocol, str ):
            if protocol == 'tcp':
                tcpListeners.append( TcpListener( addr.source.addr,
                                                  addr.source.port,
                                                  destination = addr.destination ) )
            elif protocol == 'udp':
                udpListeners.extend( udpListener( addr ) )

        elif isinstance( protocol, ( list, tuple ) ):
            if 'tcp' in protocol:
                tcpListeners.append( TcpListener( addr.source.addr,
                                                  addr.source.port,
                                                  destination = addr.destination ) )
            elif 'udp' in protocol:
                udpListeners.extend( udpListener( addr ) )

    API.running = True
    tcpThread = None
    udpThread = None
    if len( tcpListeners ):
        tcpThread = threading.Thread( target = tcpWorker, args = ( tcpListeners, ) )
        tcpThread.start()

    if len( udpListeners ):
        udpThread = threading.Thread( target = udpWorker, args = ( udpListeners, ) )
        udpThread.start()

    if len( udpListeners ):
        udpThread.join()

    if len( tcpListeners ):
        tcpThread.join()

    return
