import forwarder.psocket as socket

proxyConfig = dict( proxy = ( "192.168.110.179", 18080 ),
                    username = 'guest',
                    password = 'guest' )

sock = socket.socket()
sock.connect( ( "mail.pe2mbs.nl", 25 ), **proxyConfig )

data = sock.recv(1024)
print( data )

sock.close()


print( "Done" )