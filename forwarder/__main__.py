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
import sys
import os
import getopt
import logging
import logging.config
import forwarder.api as API
import forwarder.cfg.options as OPTIONS
from forwarder.cfg.file import ConfigFile
from forwarder.worker import worker
from forwarder.version import __version__, __author__, __copyright__


def usage():
    print( '''
Syntax:
    forwarder.py [ <options> ] <config-file>
      
Options:
    -v              Verbose information 
    -t/--trace      Trace the communicatie
    -H/--hexdump    Hexdump the communicatie (works in trace mode)  
    -h/--help       This information
      
''' )


def banner():
    l1 = 64 - ( len( __version__ ) + len( __copyright__ ) )
    l2 = 66 - len( __author__ )
    print( """+{line}+
| Forwarder, {vers}, {copy}{fill1}|
| Written by {auth}{fill2}|
+{line}+""".format( vers = __version__, copy = __copyright__, auth = __author__,
                    line = '-' * 78, fill1 = ' ' * l1, fill2 = ' ' * l2 ) )


def main( argv ):
    banner()
    API.logger = logging.getLogger()
    try:
        opts, args = getopt.getopt( argv, "htHv", [ "help", "trace", "hexdump" ] )

    except getopt.GetoptError as err:
        # print help information and exit:
        print( str( err ) ) # will print something like "option -a not recognized"
        usage()
        sys.exit( 2 )

    for o,a in opts:
        if o == "-v":
            OPTIONS.verbose = True

        elif o in ( "-t","--trace"):
            OPTIONS.trace = True

        elif o in ( "-H","--hexdump" ):
            OPTIONS.hexd = True

        elif o in ( "-h", "--help" ):
            usage()
            sys.exit( 1 )

        else:
            assert False,"unhandled option"

    if len( args ) == 0:
        print( "Missing configuration file" )
        exit( -1 )

    configFile = os.path.abspath( args[ 0 ] )
    if os.path.isfile( configFile ):
        API.config = ConfigFile()
        API.config.load( configFile )

    else:
        print( "Configuration file '{}' could not be found".format( configFile ) )
        exit( -2 )

    logging.config.dictConfig( API.config.logging )
    API.logger.setLevel( logging.ERROR )
    if API.config.options.verbose:
        API.logger.setLevel( logging.INFO )

    if API.config.options.trace:
        API.logger.setLevel( logging.DEBUG )

    API.config.dump()
    worker()
    return


def start():
    import sys
    main( sys.argv[ 1: ] )


if __name__ == '__main__':
    start()
