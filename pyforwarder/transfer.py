import traceback
import ssl
import json
import hexdump
import select
import threading
import pyforwarder.api as API
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR

SEPLINE = '-' * 60


class Transfer( threading.Thread ):
    SESSION_ID = 1

    def __init__( self, local, connection, sock ):
        self.__active = True
        threading.Thread.__init__( self )
        self.__session = Transfer.SESSION_ID
        Transfer.SESSION_ID += 1
        self.__name = "{}:{}".format( *local )
        self.__conn = connection
        self.__dest = sock.destination
        self.__destSock = socket( AF_INET, SOCK_STREAM )
        self.__sslSock = None
        API.logger.info( "Session: {session:<10} Incomming: {local}:{lport} on {remote}:{rport}".format(
                            session = self.__session,
                            local = local[ 0 ],
                            lport = local[ 1 ],
                            remote = sock.addr,
                            rport = sock.port ) )

        API.logger.debug( SEPLINE )
        API.logger.debug( "Session: {session:<10} SRC CONNECT".format( session = self.__session ) )
        if self.__dest.useSslTls:
            # need to handle SSL/TLS in the forwarder
            self.__sslSock = self.__destSock
            sslargs = {}
            if not self.__dest.sslTls.verify:
                API.logger.info( "Use SSL/TLS unferified context" )
                ssl._create_default_https_context = ssl._create_unverified_context

            else:
                sslargs[ 'cert_reqs' ] = ssl.CERT_NONE
                if self.__dest.sslTls.required:
                    if isinstance( self.__dest.sslTls.required, bool ):
                        sslargs[ 'cert_reqs' ] = ssl.CERT_REQUIRED if self.__dest.sslTls.required else ssl.CERT_OPTIONAL

                    elif isinstance( self.__dest.sslTls.required, str ):
                        if self.__dest.sslTls.required in ( 'yes', 'true' ):
                            sslargs[ 'cert_reqs' ] = ssl.CERT_REQUIRED

                        elif self.__dest.sslTls.required == 'optional':
                            sslargs[ 'cert_reqs' ] = ssl.CERT_OPTIONAL


                if  self.__dest.sslTls.caBundle is not None:
                    sslargs[ 'ca_certs' ] = self.__dest.sslTls.caBundle

                elif self.__dest.sslTls.certificate:
                    sslargs[ 'certfile' ] = self.__dest.sslTls.certificate
                    sslargs[ 'keyfile'  ] = self.__dest.sslTls.key

            API.logger.info( "SSL/TLS configuration parameters" )
            for key, value in sslargs.items():
                API.logger.info( "{:10}: {}".format( key, value ) )

            API.logger.info( "Verify    : {}".format( self.__dest.sslTls.verify ) )
            self.__destSock = ssl.wrap_socket( self.__destSock, **sslargs )
            if self.__dest.sslTls.verify:
                self.__destSock.context.verify_mode = ssl.CERT_OPTIONAL
                API.logger.info( "CheckHost : {}".format( self.__dest.sslTls.checkHost ) )
                self.__destSock.context.check_hostname = self.__dest.sslTls.checkHost

        self.__destSock.connect( ( self.__dest.addr, self.__dest.port ) )
        self.__remote = "{}:{}".format( *self.__destSock.getpeername() )
        API.logger.debug( "Session: {session:<10} DST CONNECT".format( session = self.__session ) )
        self.start()
        return

    @property
    def session( self ):
        return self.__session

    @property
    def active( self ):
        return self.__active

    @active.setter
    def active( self, value ):
        if not value:
            self.__active = False

        return

    def run( self ):
        try:
            API.logger.info( "Session: {sesion:<10} Starting the transfer {local} with {remote}".format(
                                sesion = self.__session,
                                local = self.__name,
                                remote = self.__remote ) )
            #
            #   __conn      = the socket to the client
            #   __destSock  = the socket to the actual server with optional SSL/TLS
            #
            inputs = [ self.__conn, self.__destSock ]
            outputs = []
            excepts = [ self.__conn, self.__destSock ]

            while self.__active:
                readable, writable, exceptional = select.select( inputs, outputs, excepts, 1.0 )
                for rd in readable:
                    if rd == self.__conn:
                        data = self.__conn.recv( 4096 * 5 )
                        API.logger.info( "Session: {session:<10} Receive {local:21} >> {remote:21} length {length}".format( local = self.__name,
                                                                                            length = len( data ),
                                                                                            remote = self.__remote,
                                                                                            session = self.__session ) )

                        if len( data ) == 0:    # close
                            self.__active = False
                            self.__conn.shutdown( SHUT_RDWR )
                            self.__conn.close()
                            self.__conn = None
                            API.logger.debug( SEPLINE )
                            API.logger.debug( "Session: {session:<10}: SRC {local} DISCONNECT".format( local = self.__name, session = self.__session ) )
                            break

                        API.logger.debug( SEPLINE )
                        for line in data.decode( 'utf-8', 'replace' ).splitlines():
                            API.logger.debug( "Session: {session:<10} SRC {data}".format( session = self.__session, data = line ) )

                        if API.hexd:
                            for line in hexdump.hexdump( data, 'generator' ):
                                API.logger.debug( "Session: {session:<10} SRC {data}".format( session = self.__session, data = line ) )

                        self.__destSock.sendall( data )

                    elif rd == self.__destSock:
                        data = self.__destSock.recv( 4096*5 )
                        if API.verbose or API.trace:
                            API.logger.info( "Session: {session:<10} Receive {remote:21} >> {local:21} length {length}{type}".format(
                                                remote = self.__remote,
                                                length = len( data ),
                                                type = "" if self.__sslSock is None else " (SSL/TLS)",
                                                local = self.__name,
                                                session = self.__session ) )

                        if len( data ) == 0:
                            self.__active = False
                            self.__destSock.shutdown( SHUT_RDWR )
                            self.__destSock.close()
                            self.__destSock = None
                            API.logger.debug( SEPLINE )
                            API.logger.debug( "Session: {session:<10} {type} DISCONNECT {remote}".format(
                                                type = "DST" if self.__sslSock is None else "SSL-DST",
                                                remote = self.__remote,
                                                session = self.__session ) )

                        API.logger.debug( SEPLINE )
                        for line in data.decode( 'utf-8', 'replace' ).splitlines():
                            API.logger.debug( "Session: {session:<10} {type} {data}".format(
                                            type = "DST" if self.__sslSock is None else "SSL-DST",
                                            data = line,
                                            session = self.__session ) )

                        if API.hexd:
                            for line in hexdump.hexdump( data, 'generator' ):
                                API.logger.debug( "Session: {session:<10} DST {data}".format(
                                                    session = self.__session,
                                                    data = line ) )

                        self.__conn.send( data )

                if not self.__active:
                    if not self.__conn:
                        self.__destSock.shutdown( SHUT_RDWR )
                        self.__destSock.close()
                        API.logger.debug( "Session: {session:<10} {type} DISCONNECT {remote}".format(
                                            type = "DST" if self.__sslSock is None else "SSL-DST",
                                            session = self.__session,
                                            remote = self.__remote ) )

                    if not self.__destSock:
                        self.__conn.shutdown( SHUT_RDWR )
                        self.__conn.close()
                        API.logger.debug( "Session: {session:<10} SRC DISCONNECT {local}".format(
                                            session = self.__session,
                                            local = self.__name ) )

                if len( exceptional ) > 0:
                    API.logger.error( "Session: {session:<10} Exception on socket: {local} with {remote}".format(
                                    session = self.__session,
                                    local = self.__name,
                                    remote = self.__remote ) )
                    break

        except Exception as exc:
            API.logger.critical( traceback.format_exc() )

        API.logger.info( "Session: {session:<10} Finished with transfer {local} with {remote}".format(
                        session = self.__session,
                        local = self.__name,
                        remote = self.__remote ) )
        self.__active = False
        return

    def cleanup( self ):
        if not self.__active:
            API.logger.info( "Session: {session:<10} Cleanup session {local} with {remote}".format(
                            session = self.__session,
                            local = self.__name,
                            remote = self.__remote ) )
            self.join()
            return True

        return False
