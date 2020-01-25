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
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR
import forwarder.api as API
import hexdump


def udpListener( addr ):
    return ( UdpListener( addr.source, addr.destination ),
             UdpListener( addr.destination, addr.source ) )


SEPLINE = '-' * 60


class UdpListener():
    def __init__( self, src, dst ):
        self.__srcAddr = src
        self.__dstAddr = dst
        self.__srcSock = socket( AF_INET, SOCK_DGRAM )
        self.__srcSock.setsockopt( SOL_SOCKET, SO_REUSEADDR, 1 )
        self.__srcSock.bind( ( src.addr, src.port) )
        self.__dstSock = socket( AF_INET, SOCK_DGRAM )
        API.logger.info( 'UDP listening on {}:{} forward to {}:{} = "{}"'.format( src.addr, src.port,
                                                                                  dst.addr,
                                                                                  dst.port,
                                                                                  dst.portInfo.description ) )
        return

    def __del__( self ):
        self.__srcSock.close()
        return

    @property
    def destination( self ):
        return self.__dstAddr

    @property
    def source( self ):
        return self.__srcAddr

    @property
    def dstSocket( self ):
        return self.__dstSock

    @property
    def srcSocket( self ):
        return self.__srcSock

    def fileno( self ):
        return self.__srcSock.fileno()

    def sendto( self, buffer ):
        dest_address = ( self.__dstAddr.host,
                         self.__dstAddr.port )
        self.__dstSock.sendto( buffer, dest_address )
        return

    def recvfrom( self, size ):
        return self.__srcSock.recvfrom( size )

    def transfer( self, size ):
        data, address = self.__srcSock.recvfrom( size )
        API.logger.debug( SEPLINE )
        API.logger.info( "UDP Receive from {remote}:{rport} length {length}".format( remote = address[ 0 ],
                                                                                     rport = address[ 1 ],
                                                                                     length = len( data ) ) )
        for line in data.decode( 'utf-8', 'replace' ).splitlines():
            API.logger.debug( "UDP DATA: {data}".format( data = line ) )

        if API.hexd:
            for line in hexdump.hexdump( data, 'generator' ):
                API.logger.debug( "UDP {data}".format( data = line ) )

        dest_address = (self.__dstAddr.host,
                        self.__dstAddr.port)
        API.logger.info(
            "UDP Transmit to {remote}:{rport} length {length}".format( remote = self.__dstAddr.addr,
                                                                       rport = self.__dstAddr.port,
                                                                       length = len( data ) ) )
        self.__dstSock.sendto( data, dest_address )
        return

    def close( self ):
        self.__dstSock.close()
        return self.__srcSock.close()
