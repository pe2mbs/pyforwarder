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
import tempfile
from forwarder.cfg.ssltls import ConfigSslTlsSet
from forwarder.cfg.port import ConfigPort


class ConfigAddressSet( object ):
    def __init__( self, cfg, ports ):
        self.__cfg = cfg
        self.__ports    = ports
        return

    def toDict( self ):
        return self.__cfg

    @property
    def addr( self ):
        return self.__cfg.get( 'addr', '0.0.0.0' )

    @property
    def host( self ):
        return self.__cfg.get( 'addr', '0.0.0.0' )

    @property
    def port( self ):
        value = self.__cfg.get( 'port', 8000 )
        if isinstance( value, str ):
            value = self.__ports[ value ].port

        return value

    @port.setter
    def port( self, value ):
        self.__cfg[ 'port' ] = value
        return

    @property
    def portInfo( self ):
        value = self.__cfg.get( 'port', 8000 )
        if isinstance( value, str ):
            return self.__ports[ value ]

        elif isinstance( value, int ):
            for port, obj in self.__ports.items():
                if obj.port == value:
                    return obj

            return ConfigPort( 'unkn', {
                'port': value,
                'description': 'Unknown protocol',
                'protocol': [ 'tcp', 'udp' ]
            } )

        raise Exception( 'port value invalid, should be integer or str' )

    @property
    def proxy( self ):
        return self.__cfg.get( 'proxy', False )

    @property
    def username( self ):
        return self.__cfg.get( 'username', 'guest' )

    @property
    def password( self ):
        return self.__cfg.get( 'password', 'guest' )

    @property
    def useSslTls( self ):
        return self.__cfg.get( 'use-ssl-tls', False )

    @property
    def sslTls( self ):
        return ConfigSslTlsSet( self.__cfg.get( 'ssl-tls', {} ) )

    def setProxy( self, data ):
        self.__cfg[ 'addr' ] = data[ 'addr' ]
        self.__cfg[ 'port' ] = data[ 'port' ]
        self.__cfg[ 'username' ] = data.get( 'username', 'guest' )
        self.__cfg[ 'password' ] = data.get( 'password', 'guest' )
        if 'use-ssl-tls' in data:
            self.__cfg[ 'use-ssl-tls' ] = data[ 'use-ssl-tls' ]
            ssltls = data[ 'ssl-tls' ]
            if 'ca-bundle' in ssltls:
                with tempfile.NamedTemporaryFile( mode= 'w', delete = False ) as stream:
                    stream.write( ssltls[ 'ca-bundle' ] )
                    ssltls[ 'ca-bundle' ] = stream.name

            if 'certificate' in ssltls:
                with tempfile.NamedTemporaryFile( mode= 'w', delete = False ) as stream:
                    stream.write( ssltls[ 'certificate' ] )
                    ssltls[ 'certificate' ] = stream.name

            if 'key' in ssltls:
                with tempfile.NamedTemporaryFile( mode= 'w', delete = False ) as stream:
                    stream.write( ssltls[ 'key' ] )
                    ssltls[ 'key' ] = stream.name

            self.__cfg[ 'ssl-tls' ] = ssltls

        return
