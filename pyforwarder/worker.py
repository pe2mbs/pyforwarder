import traceback
import sys
from socket import SHUT_RDWR
import select
import pyforwarder.api as API
from pyforwarder.listener import Listener
from pyforwarder.transfer import Transfer


def worker():
    listeners = [  ]
    for addr in API.config:
        listeners.append( Listener( addr.source.addr,
                                 addr.source.port,
                                 destination = addr.destination ) )

    inputs = []
    inputs.extend( listeners )
    outputs = []
    excepts = inputs
    transfers = []
    API.logger.info( "Running the listeners" )
    try:
        while inputs:
            readable, writable, exceptional = select.select( inputs, outputs, excepts, 1.0 )
            for rd in readable:
                connection, client_address = rd.accept()
                connection.setblocking( 1 )
                try:
                    transfers.append( Transfer( client_address, connection, rd ) )

                except Exception as exc:
                    API.logger.error( traceback.format_exc() )

            for exc in exceptional:
                inputs.remove( exc )

            # On timeout of the select of after every connect
            # check if there are sessions closed to be cleaned up.
            idx = 0
            while idx < len( transfers ):
                if transfers[ idx ].cleanup():
                    transfers.remove( transfers[ idx ] )

                else:
                    idx += 1

    except KeyboardInterrupt:
        pass
    except Exception:
        API.logger.error( traceback.format_exc() )

    finally:
        API.logger.info( "shudown the listeners" )
        for sock in listeners:
            sock.shutdown( SHUT_RDWR )
            sock.close()

        for tr in transfers:
            tr.active = False
            if API.verbose:
                API.logger.info( "Joining tasks {}".format( tr ) )

            tr.join()

    return
