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
import traceback
import ssl
import json
import hashlib
import base64
import hexdump
import select
import threading
import forwarder.api as API
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR, gaierror

SEPLINE = '-' * 60


class TcpTransfer( threading.Thread ):
    SESSION_ID = 1

    def __init__( self, local, connection, sock ):
        self.__active = True
        threading.Thread.__init__( self )
        self.__session = TcpTransfer.SESSION_ID
        TcpTransfer.SESSION_ID += 1
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

        if self.__dest.proxy:
            API.logger.debug( "Session: {session:<10} SRC PROXY HELO 020:forwarder TCP proxy".format( session = self.__session ) )
            self.__conn.send( b"HELO 020:forwarder TCP proxy\n" )
            data = self.__conn.recv( 9 )
            if data.startswith( b'OLEH ' ):
                display = data.decode( 'utf-8' )
                data = self.__conn.recv( int( data[ 5:8 ] ) )
                display += data.decode( 'utf-8' )
                API.logger.debug( "Session: {session:<10} SRC PROXY {data}".format( session = self.__session,
                                                                                    data = display ) )
                data = json.loads( data.decode( 'utf-8' ) )
                m = hashlib.sha256()
                userpass = "{}:{}".format( self.__dest.username, self.__dest.password )
                m.update( userpass.encode( "ascii" ) )
                if data[ 'userpass' ] == base64.b64encode( m.digest() ).decode('utf-8'):
                    self.__dest.setProxy( data )

                else:
                    self.__conn.close()
                    raise Exception( "Incorrect username/password from client on OLEH" )

            else:
                self.__conn.close()
                raise Exception( "Incorrect answer from client on HELO -> {}".format( data ) )

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

        try:
            self.__destSock.connect( ( self.__dest.addr, self.__dest.port ) )

        except gaierror as exc:
            API.logger.debug( "Session: {session:<10} DST {addr}:{port} {exc}".format( session = self.__session,
                                                                            addr = self.__dest.addr,
                                                                            port = self.__dest.port,
                                                                            exc = exc ) )
            self.__conn.close()
            raise exc from None

        except Exception as exc:
            self.__conn.close()
            raise exc from None

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
                            API.logger.debug( "Session: {session:<10} SRC {local} DISCONNECT".format( local = self.__name, session = self.__session ) )
                            break

                        API.logger.debug( SEPLINE )
                        for line in data.decode( 'utf-8', 'replace' ).splitlines():
                            API.logger.debug( "Session: {session:<10} SRC {data}".format( session = self.__session, data = line ) )

                        if API.config.options.hexdump:
                            for line in hexdump.hexdump( data, 'generator' ):
                                API.logger.debug( "Session: {session:<10} SRC {data}".format( session = self.__session, data = line ) )

                        self.__destSock.sendall( data )

                    elif rd == self.__destSock:
                        data = self.__destSock.recv( 4096*5 )
                        if API.config.options.verbose or API.config.options.trace:
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

                        if API.config.options.hexdump:
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
