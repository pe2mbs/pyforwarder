from typing import Union, Optional
import hashlib
import base64
import json
import yaml


class SocketMixin():
    def _initProxy( self, address: Union[tuple, str, bytes], **kwargs ):
        data = self.recv( 9 )
        if not data.startswith( b'HELO' ):
            raise Exception( 'Invalid response from proxy server' )

        data += self.recv( int( data[ 5 : 8 ] ) )

        if isinstance( address, bytes ):
            address = address.decode( 'utf-8' ).split(':')

        elif isinstance( address, str ):
            address = address.split(':')

        m = hashlib.sha256()
        userpass = "{}:{}".format( kwargs.get( 'username', 'guest' ),
                                   kwargs.get( 'password', 'guest' ) )
        m.update( userpass.encode( "ascii" ) )
        params = { 'addr': address[ 0 ],
                   'port': address[ 1 ],
                   'userpass': base64.b64encode( m.digest() ).decode('utf-8') }

        if 'ssl-tls' in kwargs:
            ssltls = kwargs.get( 'ssl-tls', { } )
            if len( ssltls ) > 0:
                params[ 'use-ssl-tls' ] = kwargs.get( 'use-ssl-tls', True )
                newSslTls = {}
                if 'verify' in ssltls:
                    newSslTls[ 'verify' ] = ssltls[ 'verify' ]

                if 'required' in ssltls:
                    newSslTls[ 'required' ] = ssltls[ 'required' ]

                if 'check-host' in ssltls:
                    newSslTls[ 'check-host' ] = ssltls[ 'check-host' ]

                if 'certificate' in ssltls:
                    with open( ssltls[ 'certificate' ], 'r' ) as stream:
                        newSslTls[ 'certificate' ] = stream.read()

                if 'key' in ssltls:
                    with open( ssltls[ 'key' ], 'r' ) as stream:
                        newSslTls[ 'key' ] = stream.read()

                if 'ca-bundle' in ssltls:
                    with open( ssltls[ 'ca-bundle' ], 'r' ) as stream:
                        newSslTls[ 'ca-bundle' ] = stream.read()

                params[ 'ssl-tls' ] = newSslTls

        data = json.dumps( params )
        self.send( "OLEH {:03}:{}".format( len( data ), data ).encode( 'ascii' ) )
        return

    def _loadConfig( self, filename ):
        with open( filename, 'r' ) as stream:
            if filename.lower().endswith( '.json' ):
                config = json.load( stream )

            elif filename.lower().endswith( '.yaml' ):
                config = yaml.load( stream, Loader = yaml.Loader )

            else:
                raise Exception( "Invalid file type for {}".format( filename ) )

        return config