import os
import pyforwarder.api as API
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

class Listener( socket ):
    def __init__( self, addr, port, destination, listen = 2 ):
        self.__addr = addr
        self.__port = port
        self.__dest = destination
        if self.destination.useSslTls:
            filename = self.destination.sslTls.certificate
            if filename is not None and not os.path.isfile( filename ):
                raise Exception( "Missing SSL/TLS certificate file" )

            filename = self.destination.sslTls.key
            if filename is not None and not os.path.isfile( filename ):
                raise Exception( "Missing SSL/TLS key file" )

            filename = self.destination.sslTls.caBundle
            if filename is not None and not os.path.isfile( filename ):
                raise Exception( "Missing SSL/TLS ca-bundle file" )

        socket.__init__( self, AF_INET, SOCK_STREAM )
        # Avoid "OSError: [Errno 98] Address already in use" when shutting down and restarting
        self.setsockopt( SOL_SOCKET, SO_REUSEADDR, 1 )
        self.bind( ( self.addr, self.port ) )
        self.listen( listen )

        API.logger.info( 'listening on {}:{} forward to {}:{} = "{}"'.format( self.addr,
                                                                       self.port,
                                                                       self.destination.addr,
                                                                       self.destination.port,
                                                                       self.destination.portInfo.description ) )
        self.setblocking( False )
        return

    def __del__( self ):
        self.close()
        return

    @property
    def destination( self ):
        return self.__dest

    @property
    def addr( self ):
        return self.__addr

    @property
    def port( self ):
        return self.__port