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
import hashlib
import base64
import socket
import json
import yaml
from typing import Union, Optional
proxyConfig = None

_socket = socket.socket

class TcpSocket( _socket ):
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

    def _initProxy( self, address: Union[tuple, str, bytes], **kwargs ):
        data = socket.socket.recv( self, 1024 )
        if not data.startswith( b'HELO' ):
            raise Exception( 'Invalid response from proxy server' )

        if isinstance( address, bytes ):
            address = address.decode( 'utf-8' ).split(':')

        elif isinstance( address, str ):
            address = address.split(':')

        m = hashlib.sha256()
        userpass = "{}:{}".format( kwargs.get( 'username', 'guest' ),
                                   kwargs.get( 'password', 'guest' ) )
        m.update( userpass.encode( "ascii" ) )
        params = { 'addr': address[ 0 ],
                   'port': address[ 1 ],
                   'userpass': base64.b64encode( m.digest() ).decode('utf-8') }

        if 'ssl-tls' in kwargs:
            ssltls = kwargs.get( 'ssl-tls', { } )
            if len( ssltls ) > 0:
                params[ 'use-ssl-tls' ] = kwargs.get( 'use-ssl-tls', True )
                newSslTls = {}
                if 'verify' in ssltls:
                    newSslTls[ 'verify' ] = ssltls[ 'verify' ]

                if 'required' in ssltls:
                    newSslTls[ 'required' ] = ssltls[ 'required' ]

                if 'check-host' in ssltls:
                    newSslTls[ 'check-host' ] = ssltls[ 'check-host' ]

                if 'certificate' in ssltls:
                    with open( ssltls[ 'certificate' ], 'r' ) as stream:
                        newSslTls[ 'certificate' ] = stream.read()

                if 'key' in ssltls:
                    with open( ssltls[ 'key' ], 'r' ) as stream:
                        newSslTls[ 'key' ] = stream.read()

                if 'ca-bundle' in ssltls:
                    with open( ssltls[ 'ca-bundle' ], 'r' ) as stream:
                        newSslTls[ 'ca-bundle' ] = stream.read()

                params[ 'ssl-tls' ] = newSslTls

        data = json.dumps( params )
        _socket.send( self, "OLEH {:03}:{}".format( len( data ), data ).encode( 'ascii' ) )
        return

    def connect( self, address: Union[tuple, str, bytes], **kwargs ) -> None:
        global proxyConfig

        if 'proxy' in kwargs:
            proxy = kwargs[ 'proxy' ]
            if not isinstance( proxy, ( tuple, str, bytes ) ):
                raise Exception( 'Invalid prox address' )

            _socket.connect( self, proxy )
            self._initProxy( address, **kwargs )

        elif proxyConfig is not None:
            _socket.connect( self, tuple( proxyConfig[ 'proxy' ] ) )
            self._initProxy( address, **proxyConfig )

        elif 'RAW_PROXY_CFG' in os.environ:
            filename = os.environ[ 'RAW_PROXY_CFG' ]
            with open( filename, 'r' ) as stream:
                if filename.lower().endswith( '.json' ):
                    proxyConfig = json.load( stream )

                elif filename.lower().endswith( '.yaml' ):
                    proxyConfig = yaml.load( stream, Loader = yaml.Loader )

                else:
                    raise Exception( "Invalid file type for {}".format( filename ) )

            _socket.connect( self, tuple( proxyConfig[ 'proxy' ] ) )
            self._initProxy( address, **proxyConfig )

        else:
            _socket.connect( self, address )

        return

    def connect_ex(self, address: Union[tuple, str, bytes], **kwargs ) -> int:
        if 'proxy' in kwargs:
            proxy = kwargs[ 'proxy' ]
            if not isinstance( proxy, ( tuple, str, bytes ) ):
                raise Exception( 'Invalid prox address' )

            _socket.connect_ex( self, proxy )
            self._initProxy( address, **kwargs )

        else:
            _socket.connect_ex( self, address )

        return


socket.socket = TcpSocket