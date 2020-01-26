import forwarder.psocket
import socket
import requests

forwarder.psocket.proxyConfig = {
    'proxy': [ "192.168.110.179", 18080 ],
    'username': 'guest',
    'password': 'guest'
}

sock = socket.socket()
sock.connect( ( "mail.pe2mbs.nl", 25 ) )

data = sock.recv(1024)
print( data )

sock.close()

#
#   Do a HTTP call with requests
#
result = requests.get( "http://google.nl" )
print( result.content.decode( 'utf-8' ) )

#
#   Do a HTTPS call with requests
#   Note that in goes in clear-text where the rest
#   of the session is SSL/TLS encrypted
#
result = requests.get( "https://google.nl" )
print( result.content.decode( 'utf-8' ) )



print( "Done" )