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

class ConfigSslTlsSet( object ):
    def __init__( self, cfg ):
        self.__cfg = cfg
        return

    @property
    def verify( self ):
        return self.__cfg.get( 'verify', True )

    @property
    def checkHost( self ):
        return self.__cfg.get( 'check-host', True )

    @property
    def required( self ):
        return self.__cfg.get( 'required', 'optional' )

    @property
    def certificate( self ):
        path_file = self.__cfg.get( 'certificate', None )
        if path_file is not None:
            path_file = os.path.abspath( path_file )

        return path_file

    @property
    def key( self ):
        path_file = self.__cfg.get( 'key', None )
        if path_file is not None:
            path_file = os.path.abspath( path_file )

        return path_file

    @property
    def caBundle( self ):
        path_file = self.__cfg.get( 'ca-bundle', None )
        if path_file is not None:
            path_file = os.path.abspath( path_file )

        return path_file
