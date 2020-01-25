from forwarder.psocket import TcpSocket

sock = TcpSocket()
sock.connect( ( "mail.pe2mbs.nl", 25 ), proxy = ( "192.168.110.179", 18080 ) )

data = sock.recv(1024)
print( data )

sock.close()

print( "Done" )