import sys
import os
import getopt
import logging
import logging.config
import pyforwarder.api as API
from pyforwarder.config import ConfigFile
from pyforwarder.worker import worker

__version__     = '0.11.002'
__author__      = 'Marc Bertens-Nguyen'
__copyright__   = '(c) 2019 - 2020, Marc Bertens-Nguyen, the Netherlands'


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
        opts, args = getopt.getopt( sys.argv[ 1: ], "htHv", [ "help", "trace", "hexdump" ] )

    except getopt.GetoptError as err:
        # print help information and exit:
        print( str( err ) ) # will print something like "option -a not recognized"
        usage()
        sys.exit( 2 )

    for o,a in opts:
        if o == "-v":
            API.verbose = True

        elif o in ( "-t","--trace"):
            API.trace = True

        elif o in ( "-H","--hexdump" ):
            API.hexd = True

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

    API.config.options.updateGlobals()
    logging.config.dictConfig( API.config.logging )
    API.logger.setLevel( logging.ERROR )
    if API.config.options.verbose:
        API.logger.setLevel( logging.INFO )

    if API.config.options.trace:
        API.logger.setLevel( logging.DEBUG )

    API.config.dump()
    worker()
    return


# main( sys.argv[ 1 : ] )
