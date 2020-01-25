import socket
import sys

# Create a UDP socket
sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
sock.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
server_address = ( '192.168.110.179', 10002 )
sock.bind( server_address )
server_address = ( '192.168.110.179', 10000 )
message = b'This is the message.  It will be repeated.'

try:

    # Send data
    print( 'sending "%s"' % message )
    sent = sock.sendto( message, server_address )

    # Receive response
    print( 'waiting to receive' )
    data, server = sock.recvfrom( 4096 )
    print( 'received "%s"' % data )

finally:
    print( 'closing socket' )
    sock.close()

