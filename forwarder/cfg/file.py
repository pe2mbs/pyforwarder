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
import logging
import io
import yaml
import json
from forwarder.cfg.options import ConfigOptions
from forwarder.cfg.port import ConfigPort
from forwarder.cfg.ports import WELL_DEFINED_PORTS
from forwarder.cfg.host import ConfigHost

logger = logging.getLogger()


class ConfigFile( object ):
    def __init__(self):
        self.__hosts    = {}
        self.__ports    = {}
        self.__cfg      = {}
        return

    def load( self, filename ):

        with open( filename, 'r' ) as stream:
            if filename.lower().endswith( ".json" ):
                self.__cfg = json.load( stream )

            elif filename.lower().endswith( ".yaml" ):
                self.__cfg = yaml.load( stream, Loader = yaml.Loader )

            else:
                print( "Configuration file format is invalid" )
                exit( -3 )

        if self.version == 1:
            raise Exception( "Invalid config version, must be version 2")

        self.__ports = {}
        for portname, value in WELL_DEFINED_PORTS.items():
            self.__ports[ portname ] = ConfigPort( portname, value )

        for portname, value in self.__cfg.get( "ports", {} ).items():
            self.__ports[ portname ] = ConfigPort( portname, value )

        self.__hosts = []
        for host in self.__cfg.get( 'hosts', [] ):
            self.__hosts.append( ConfigHost( host, self.__ports ) )

        return

    def save( self, filename ):
        with open( filename, 'w' ) as stream:
            if filename.lower().endswith( ".json" ):
                json.dump( self.__cfg, stream )

            elif filename.lower().endswith( ".yaml" ):
                yaml.dump( self.__cfg, stream, Loader = yaml.Dumper )

            else:
                print( "Configuration file format is invalid" )
                exit( -3 )

        return

    @property
    def version( self ):
        return self.__cfg.get( 'version', 1 )

    @property
    def hosts( self ):
        return [ h.toDict() for h in self.__hosts ]

    @property
    def ports( self ):
        return [ { p: values.toDict() } for p, values in self.__ports.items() ]

    def lookupPort( self, port_name ):
        if port_name in self.__ports:
            return self.__ports[ port_name ]

        return None

    def __iter__( self ):
        return iter( self.__hosts )

    @property
    def options( self ):
        return ConfigOptions( self.__cfg.get( 'options', {} ) )

    def dump( self ):
        stream = io.StringIO()
        yaml.dump( self.__cfg, stream, Dumper = yaml.Dumper, default_flow_style = False )
        stream.seek(0,0)
        for line in stream.readlines():
            logger.debug( line.replace( '\n', '' ) )

        return

    @property
    def logging( self ):
        return self.__cfg.get( 'logging', {
            "version": 1,
            'formatters': {
                    'trace': {
                        'class': 'logging.Formatter',
                        'format': '%(asctime)s %(levelname)-8s %(message)s'
                    },
                    'verbose': {
                        'class': 'logging.Formatter',
                        'format': '%(asctime)s %(message)s'
                    }
                },
                'handlers': {
                    'console': {
                        'class': 'logging.StreamHandler',
                        'formatter': 'verbose',
                        'level': 'INFO',
                    },
                    'file': {
                        'class': 'logging.FileHandler',
                        'filename': 'trace.log',
                        'mode': 'w',
                        'formatter': 'trace',
                        'level': 'DEBUG'
                    },
                },
                'root': {
                    'level': 'DEBUG',
                    'handlers': [ 'console', 'file' ]
                },
        } )
