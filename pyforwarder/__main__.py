import sys
import os
import ssl
import getopt
import json
import yaml
import hexdump
from socket import socket, AF_INET, SOCK_STREAM
import select
import threading

__version__     = '0.10.001'
__author__      = 'Marc Bertens-Nguyen'
__copyright__   = 'equensWorldline se, the Netherlands'

ports = {
    'http': 80,
    'https': 443,
    'imaps': 993,
    'smtps': 587,
    'smtps_old': 465,
}

global verbose
verbose = False

global trace
trace = False

global hexd
hexd = False

global config
config = {
    'ports': ports,
    'hosts': [
        { 'source':         { 'addr': '0.0.0.0', 'port': 8008 },
          'destination':    { 'addr': 'defmcrvmx007.defm.awl.atosorigin.net', 'port': 'imaps' } },
        { 'source':         { 'addr': '0.0.0.0', 'port': 8009 },
          'destination':    { 'addr': 'defmvmx009.defm.awl.atosorigin.net', 'port': 'smtps' } },
        { 'source':         { 'addr': 'localhost','port': 8010 },
          'destination':    { 'addr': 'sts20029','port': 'http' } },
    ]
}

SEPLINE = '-' * 60

class Listener( socket ):
    def __init__( self, host, port, destination, listen = 2 ):
        self.__host = host
        self.__port = port
        self.__dest = destination
        socket.__init__( self, AF_INET, SOCK_STREAM )
        self.bind( (host,port) )
        self.listen( listen )
        global verbose
        if verbose:
            print( 'listening on',(host,port) )

        self.setblocking( False )
        return

    @property
    def destination( self ):
        return self.__dest


class Transfer( threading.Thread ):
    def __init__( self, name, connection, destination ):
        global verbose, trace
        self.__active = True
        threading.Thread.__init__( self )
        self.__name = name
        self.__conn = connection
        self.__dest = destination
        self.__destSock = socket( AF_INET, SOCK_STREAM )
        self.__sslSock = None
        if trace:
            print( SEPLINE )
            print( "SRC: CONNECT" )

        if 'protocol' in self.__dest:
            if self.__dest[ 'protocol' ] == 'ssltls':
                # need to handle SSL/TLS in the forwarder
                self.__sslSock = self.__destSock
                sslVerify = self.__dest[ 'ssl-verify' ] if 'ssl-verify' in self.__dest else True
                if verbose or trace:
                    print( "sslVerify: {}".format( sslVerify ) )

                sslargs = {}
                if not sslVerify:
                    if verbose or trace:
                        print( "Use unferified context" )

                    ssl._create_default_https_context = ssl._create_unverified_context

                else:
                    sslargs = {
                        'cert_reqs': ssl.CERT_NONE,
                    }
                    if 'ssl-required' in self.__dest:
                        value = self.__dest[ 'ssl-required' ]
                        if isinstance( value, bool ):
                            sslargs[ 'cert_reqs' ] = ssl.CERT_REQUIRED if value else ssl.CERT_OPTIONAL

                        elif isinstance( value, str ):
                            if value in ( 'yes', 'true' ):
                                sslargs[ 'cert_reqs' ] = ssl.CERT_REQUIRED

                            elif value == 'optional':
                                sslargs[ 'cert_reqs' ] = ssl.CERT_OPTIONAL

                    if 'ssl-certificate' in self.__dest:
                        sslargs[ 'certfile' ] = os.path.abspath( self.__dest[ 'ssl-certificate' ] )
                        sslargs[ 'keyfile'  ] = os.path.abspath( self.__dest[ 'ssl-key' ] )

                    elif 'ssl-cert-bundle' in self.__dest:
                        sslargs[ 'ca_certs' ] =  os.path.abspath( self.__dest[ 'ssl-cert-bundle' ] )

                if verbose or trace:
                    print( json.dumps( sslargs, indent = 4 ) )

                self.__destSock = ssl.wrap_socket( self.__destSock, **sslargs )
                if sslVerify:
                    self.__destSock.context.verify_mode = ssl.CERT_OPTIONAL

                    sslCheckHost = self.__dest[ 'ssl-check-host' ] if 'ssl-check-host' in self.__dest else True
                    if verbose or trace:
                        print( "sslCheckHost: {}".format( sslCheckHost ) )

                    self.__destSock.context.check_hostname = sslCheckHost



        self.__destSock.connect( ( self.__dest[ 'addr' ], self.__dest[ 'port' ] ) )
        if trace:
            print( "DST: CONNECT" )

        self.__destSock.setblocking( 0 )
        self.start()
        return

    @property
    def active( self ):
        return self.__active

    def run( self ):
        global verbose, hexd, trace
        try:
            if verbose or trace:
                print( "Starting the transfer: {}".format( self.__name ) )

            inputs = [ self.__conn, self.__destSock ]
            outputs = []
            excepts = [ self.__conn, self.__destSock ]
            while self.__conn and self.__destSock:
                readable, writable, exceptional = select.select( inputs, outputs, excepts )
                for rd in readable:
                    if rd == self.__conn:
                        data = self.__conn.recv( 4096*5 )
                        if verbose or trace:
                            print( "Receive source {} {}".format( self.__name, len( data ) ) )

                        if len( data ) == 0:    # close
                            self.__conn.close()
                            self.__conn = None
                            if trace:
                                print( SEPLINE )
                                print( "SRC: DISCONNECT" )

                            break

                        if trace:
                            print( SEPLINE )
                            print( "SRC: {}".format( data ) )
                            if hexd:
                                for line in hexdump.hexdump( data, 'generator' ):
                                    print( "SRC: {}".format( line ) )

                        self.__destSock.sendall( data )

                    elif rd == self.__destSock:
                        data = self.__destSock.recv( 4096*5 )
                        if verbose or trace:
                            print( "Receive dest {} {}".format( self.__name, len( data ) ) )

                        if len( data ) == 0:
                            self.__destSock.close()
                            self.__destSock = None
                            if trace:
                                print( SEPLINE )
                                print( "DST: DISCONNECT" )

                            break

                        if trace:
                            print( SEPLINE )
                            print( "DST: {}".format( data ) )
                            if hexd:
                                for line in hexdump.hexdump( data, 'generator' ):
                                    print( "DST: {}".format( line ) )

                        self.__conn.send( data )

                if not self.__conn:
                    self.__destSock.close()
                    if verbose or trace:
                        print( "DST: DISCONNECT" )

                    break

                if not self.__destSock:
                    self.__conn.close()
                    if verbose or trace:
                        print( "SRC: DISCONNECT" )

                    break

                if len( exceptional ) > 0:
                    if verbose or trace:
                        print( "exception on socket: {}".format( self.__name ) )

                    break

        except Exception as exc:
            print( exc, file = sys.stderr )

        if verbose or trace:
            print( "Finished with transfer: {}".format( self.__name ) )

        self.__active = False
        return


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
    global config, verbose, trace, hexd
    banner()
    try:
        opts, args = getopt.getopt( sys.argv[ 1: ],"htHv",[ "help", "trace", "hexdump" ] )

    except getopt.GetoptError as err:
        # print help information and exit:
        print( str( err ) ) # will print something like "option -a not recognized"
        usage()
        sys.exit( 2 )

    configFile = None
    for o,a in opts:
        if o == "-v":
            verbose = True

        elif o in ( "-t","--trace"):
            trace = True

        elif o in ( "-H","--hexdump" ):
            hexd = True

        elif o in ( "-h", "--help" ):
            usage()
            sys.exit()

        else:
            assert False,"unhandled option"

    if len( args ) == 0:
        print( "Missing configuration file" )
        exit(-1)

    configFile = args[ 0 ]
    if os.path.isfile( configFile ):
        if configFile.lower().endswith( ".json" ):
            config = json.load( open( configFile, 'r' ) )

        elif configFile.lower().endswith( ".yaml" ):
            config = yaml.load( open( configFile,'r' ) )

        else:
            print( "Configuration file format is invalid" )
            exit( -3 )

    else:
        print( "Configuration file could not be found" )
        exit( -2 )

    if 'ports' not in config:
        config[ 'ports' ] = ports

    for addr in config[ 'hosts' ]:
        for key in addr:
            if isinstance( addr[ key ][ 'port' ], str ):
                addr[ key ][ 'port' ] = config[ 'ports' ][ addr[ key ][ 'port' ] ]

    if verbose:
        print( json.dumps( config, indent = 4 ) )

    inputs = [  ]
    for addr in config[ 'hosts' ]:
        inputs.append( Listener( addr[ 'source' ][ 'addr' ],
                                 addr[ 'source' ][ 'port' ],
                                 destination = addr[ 'destination' ] ) )

    outputs = []
    excepts = inputs
    transfers = []
    if verbose:
        print( "running the listeners" )

    while inputs:
        readable, writable, exceptional = select.select( inputs, outputs, excepts )
        for rd in readable:
            connection, client_address = rd.accept()
            connection.setblocking( 1 )
            try:
                if verbose:
                    print( "Incomming: {}".format( client_address ) )

                transfers.append( Transfer( "{}:{}".format( *client_address ), connection, rd.destination ) )

            except Exception as exc:
                print( exc, file = sys.stderr )

        for exc in exceptional:
            inputs.remove( exc )

        idx = 0
        while idx < len( transfers ):
            if not transfers[ idx ].active:
                if verbose:
                    print( "cleanup {}".format( transfers[ idx ] ) )

                transfers.remove( transfers[ idx ] )

            else:
                idx += 1

    for tr in transfers:
        if verbose:
            print( "joining {}".format( tr ) )

        tr.join()

    return


main( sys.argv[ 1 : ] )

