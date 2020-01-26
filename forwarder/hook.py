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
import socket
from typing import Union, Optional
import forwarder._psockmixin
proxyConfig = None

_socket = socket.socket

class _hookSocket( _socket, forwarder._psockmixin.SocketMixin ):
    """This is a snap-in replacement for the socket.socket class.
    The connect() end connect_ex() calls have optional the following
    parameters:

    proxy:          str, bytes or tuple with the connection parameters (address, port)
    username:       str with the username configured in pyforwarder
    password:       str with the password configured in pyforwarder
    ssl-tls:        dict with the additional SSL/TLS parameters
    *   verify:         true/false verify the certifcate
    *   check-host:     true/false verify the certifcate hostname
    *   required:       true/false/"optional"
    *   certificate:    str with the data from certificate file
    *   key:            str with the data from key file
    *   ca-bundle:      str with the data from ca-build file

    """
    def __init__( self, family: int = socket.AF_INET, type: int = socket.SOCK_STREAM,
                        proto: int = 0, fileno: Optional[int] = None ):
        _socket.__init__( self, family, type, proto, fileno )
        return



    def connect( self, address: Union[tuple, str, bytes] ) -> None:
        global proxyConfig

        if proxyConfig is not None:
            _socket.connect( self, tuple( proxyConfig[ 'proxy' ] ) )
            self._initProxy( address, **proxyConfig )

        elif 'RAW_PROXY_CFG' in os.environ:
            proxyConfig = self._loadConfig( os.environ[ 'RAW_PROXY_CFG' ] )
            _socket.connect( self, tuple( proxyConfig[ 'proxy' ] ) )
            self._initProxy( address, **proxyConfig )

        else:
            _socket.connect( self, address )

        return

    def connect_ex(self, address: Union[tuple, str, bytes] ) -> int:
        global proxyConfig

        if proxyConfig is not None:
            _socket.connect( self, tuple( proxyConfig[ 'proxy' ] ) )
            self._initProxy( address, **proxyConfig )

        elif 'RAW_PROXY_CFG' in os.environ:
            proxyConfig = self._loadConfig( os.environ[ 'RAW_PROXY_CFG' ] )
            _socket.connect_ex( self, tuple( proxyConfig[ 'proxy' ] ) )
            self._initProxy( address, **proxyConfig )

        else:
            _socket.connect_ex( self, address )

        return


socket.socket = _hookSocket