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
import os
import forwarder.api as API
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR


class TcpListener( socket ):
    def __init__( self, addr, port, destination, listen = 2 ):
        self.__addr = addr
        self.__port = port
        self.__dest = destination
        if self.destination.useSslTls:
            filename = self.destination.sslTls.certificate
            if filename is not None and not os.path.isfile( filename ):
                raise Exception( "Missing SSL/TLS certificate file" )

            filename = self.destination.sslTls.key
            if filename is not None and not os.path.isfile( filename ):
                raise Exception( "Missing SSL/TLS key file" )

            filename = self.destination.sslTls.caBundle
            if filename is not None and not os.path.isfile( filename ):
                raise Exception( "Missing SSL/TLS ca-bundle file" )

        socket.__init__( self, AF_INET, SOCK_STREAM )
        # Avoid "OSError: [Errno 98] Address already in use" when shutting down and restarting
        self.setsockopt( SOL_SOCKET, SO_REUSEADDR, 1 )
        self.bind( ( self.addr, self.port ) )
        self.listen( listen )
        if self.destination.proxy:
            API.logger.info( 'TCP listening on {}:{} as a raw proxy'.format( self.addr, self.port ) )

        else:
            API.logger.info( 'TCP listening on {}:{} forward to {}:{} = "{}"'.format( self.addr,
                                                                       self.port,
                                                                       self.destination.addr,
                                                                       self.destination.port,
                                                                       self.destination.portInfo.description ) )
        self.setblocking( False )
        return

    def __del__( self ):
        self.close()
        return

    @property
    def destination( self ):
        return self.__dest

    @property
    def addr( self ):
        return self.__addr

    @property
    def port( self ):
        return self.__port