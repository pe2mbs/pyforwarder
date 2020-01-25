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
from forwarder.cfg.addr import ConfigAddressSet


class ConfigHost( object ):
    def __init__( self, cfg, ports ):
        self.__src = ConfigAddressSet( cfg[ 'source' ], ports )
        self.__dst = ConfigAddressSet( cfg[ 'destination' ], ports )
        self.__enabled  = cfg.get( 'enabled', True )
        return

    @property
    def enabled( self ):
        return self.__enabled

    @property
    def source( self ):
        return self.__src

    @property
    def destination( self ):
        return self.__dst

    def toDict( self ):
        return { 'source': self.__src.toDict(),
                 'destination': self.__dst.toDict() }

