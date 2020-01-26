import forwarder.psocket as socket

proxyConfig = dict( proxy = ( "localhost", 18080 ),
                    username = 'guest',
                    password = 'guest' )

sock = socket.socket()
sock.connect( ( "smtp.gmail.com", 25 ), **proxyConfig )

data = sock.recv(1024)
print( data )
sock.close()
print( "Done" )