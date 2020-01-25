import socket

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ( 'localhost', 10001 )
print( 'starting up on %s port %s' % server_address )
sock.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
sock.bind( server_address )
server_address = ( 'localhost', 10003 )

while True:
    print( '\nwaiting to receive message' )
    data, address = sock.recvfrom( 4096 )

    print( 'received %s bytes from %s' % ( len( data ), address ) )
    print( data )

    if data:
        sent = sock.sendto( data, server_address )
        print( 'sent %s bytes back to %s' % ( sent, address ) )


