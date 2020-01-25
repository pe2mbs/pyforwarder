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
from socket import SHUT_RDWR
import select
import forwarder.api as API

from forwarder.tcp.transfer import TcpTransfer


def tcpWorker( listeners ):
    inputs = []
    inputs.extend( listeners )
    outputs = []
    excepts = inputs
    transfers = []
    API.logger.info( "Running the listeners" )
    try:
        while inputs and API.running:
            readable, writable, exceptional = select.select( inputs, outputs, excepts, 1.0 )
            for rd in readable:
                connection, client_address = rd.accept()
                connection.setblocking( 1 )
                try:
                    transfers.append( TcpTransfer( client_address, connection, rd ) )

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
        API.running = False

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
