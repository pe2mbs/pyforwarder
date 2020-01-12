# pyforwarder a TCP/IP communication trace tool with SSL/TLS termination.

With this tool you can intercept communication between a server an a client, 
assuming that you can alter the communication parameters off the client.

It can optionally also perform the SSL/TLS termination to the server, so that
the communication to the client is in clear text.

It can handle multiple sessions, multimple servers ans ports at the same time.

At this moment only TCP sessions are supported.


## Basic operation
The basic operation is simple start the pyforwarder with a configuration file.

```bash

> pyforwarder config-example.yaml

```

Depending on the settings it shows the program banner and optionally verbose 
and trace information what is happing.


## Configuration
The configuration file can be a YAML or JSON formatted file. The example below 
shows the YAML format.
   
```yaml
version: 2
options:
  trace: true
  hexdump: true
  verbose: true
logging:
  version: 1
  formatters:
    trace:
      class: logging.Formatter
      format: '%(asctime)s %(levelname)-8s %(message)s'
    verbose:
      class: logging.Formatter
      format: '%(asctime)s %(message)s'
  handlers:
    console:
      class: logging.StreamHandler
      level: INFO
      formatter: verbose
      stream: ext://sys.stdout
    file:
      level: DEBUG
      class: logging.FileHandler
      encoding: utf-8
      filename: tracefile.log
      mode: w
      formatter: trace
  root:
    level: DEBUG
    handlers:
    - console
    - file
hosts:
- source:
    addr: 0.0.0.0
    port: 8008
  destination:
    addr: mail.pe2mbs.nl
    port: imaps
    use-ssl-tls: true
    ssl-tls:
      verify: false
      check-host: false
      required: optional
      #ca-bundle: yourDomain.ca-bundle
- source:
    port: 8009
  destination:
    addr: mail.pe2mbs.nl
    port: smtps
    use-ssl-tls: false
    ssl-tls:
      verify: false
      check-host: false
      required: optional
      #certificate: certifcate.pem
      #key: private-key.key
- source:
    addr: localhost
    port: 8010
  destination:
    addr: daecon.pe2mbs.nl
    port: 25057
    use-ssl-tls: false
  enabled: false
ports:
  http-spotweb:
    port: 25057
    description: http-alternate
    protocol: TCP   
```

### version
The `version` at root level must be 2 at this time. 

### options
The `options` at root level can also be set via the command line, but the 
settings in the configuration file are always leading.

### logging
The `logging` at root level defines how the application does its logging. 
When this is omitted the default is as defined in the example above. When 
you want greater detail on the console just change the `level` in 
`logging.handlers.console` to **DEBUG** then the same detail as in the log
file is shown on the console.   
   
### hosts
The `hosts` is a list of host source/destination configuration items.   
Each list item constists out of the following items;
* `source`
* `destination`
* `enabled` is a flag (**true**/**false**) of the host configuration is active, 
            when omitted the default is **true**.

#### source 
The `source` has two attributes;
* `addr`: the address to listen on, when omitted the 0.0.0.0 address shall be 
          used therefore the the listen is on all network adaptors.
* `port`: the port to listen on.          

#### destination
The `destination` has two attributes;
* `addr`: the address to connect to when an incomming connection is established 
          on the source.
* `port`: the port to to connect to.
* `use-ssl-tls`: is a flag (**true**/**false**) whether the SSL/TLS termination is
                 enabled for the session. When enabled the `ssl-tls` attributes 
                 will be used to set extra SSL/TLS parameters.
* `ssl-tls` this may contain the following attributes `verify`, `check-host`, 
            `required` , `ca-bundle`, `certificate` and `key`.                           

##### verify
With `verify` the certicate verifcation can be enabled or disabled, the default
is **true**
 
##### check-host
With `check-host` the host name verifcation can be enabled or disabled, the 
default is **true**

##### required
With `required` the host certicate can be required, optional or none. The values
* **true**: required
* **false**: none
* **optional**: optional   

##### ca-bundle
The `ca-bundle` is the filename to the CA bundle with the certicates: CA and client.
  
##### certificate
The `certificate` is the filename to the client certicate. 

##### key
The `key` is the filename to the client private key file.

### ports
The `ports` is a dictionary of port defintions. This is an optional attrbute and 
is an addition to the predefined ports. Each entry constist out of a unique 
protocol name with the following attributes;
* port: the port number
* description: the description of the protcol
* protocol: may be set to TCP and/or UDP, when both need to be set the list syntax
            is used. 

```yaml
  ftp:          
    port: 20
    description: file transfer protocol
    protocol: tcp
  ftpc:         
    port: 21
    description: file transfer protocol control
    protocol: tcp
  ssh:          
    port: 22
    description: Secure Shell
    protocol: tcp
  telnet:       
    port: 23
    description: Telnet", "protocol": "tcp" },
  smtp:        
    port: 25
    description: Simple Mail Transfer Protocol, verzending van e-mail (MTA)
    protocol: tcp
  dns:         
    port: 53
    description: Domain Name System
    protocol: udp
  dhcpc:       
    port: 67
    description: Domain Name System client
    protocol: udp
  dhcps:       
    port: 68
    description: Domain Name System server
    protocol: udp
  tftp:        
    port: 69
    description: Trivial File Transfer Protocol
    protocol: udp
  http:        
    port: 80
    description: Hypertext Transfer Protocol
    protocol: 
    - tcp
    - udp
  pop3:        
    port: 110
    description: Post Office Protocol 3, receive of e-mail
    protocol: tcp
  nntp:        
    port: 119
    description: Network News Transfer Protocol
    protocol: tcp
  ntp:         
    port: 123
    description: Network Time Protocol
    protocol: tcp
  netbns:      
    port: 137
    description: NetBIOS Name Service
    protocol: udp
  netbds:      
    port: 138
    description: NetBIOS Name Service
    protocol: udp
  netbss:      
    port: 139
    description: NetBIOS Session Service
    protocol: tcp
  imap:        
    port: 143
    description: Internet Message Access Protocol
    protocol: tcp
  snmp:        
    port: 161
    description: Simple Network Management Protocol
    protocol: udp
  snmptrap:    
    port: 162
    description: Simple Network Management Protocol, getriggerde notificaties
    protocol: udp
  ldap:        
    port: 389
    description: Lightweight Directory Access Protocol
    protocol: tcp
  https:       
    port: 443
    description: HyperText Transfer Protocol over TLS/SSL
    protocol: tcp
  smb:         
    port: 445
    description: Direct Hosting / SMB (Samba) over TCP
    protocol: tcp
  smtps-alt:   
    port: 465
    description: Simple Mail Transfer Protocol over TLS/SSL
    protocol: tcp
  dhcpc-alt:   
    port: 546
    description: Domain Name System (ipv6) client
    protocol: udp
  dhcps-alt:   
    port: 547
    description: Domain Name System (ipv6) server
    protocol: udp
  msn:         
    port: 569
    description: Multiple Subscriber Number
    protocol: tcp
  smtps:       
    port: 587
    description: Simple Mail Transfer Protocol, verzending van uitgaande e-mail (MSA)[16]
    protocol: tcp
  ftps:        
    port: 990
    description: File Transfer Protocol over SSL
    protocol: tcp
  imaps:       
    port: 993
    description: Internet Message Access Protocol over TLS/SSL
    protocol: tcp
  pop3s:       
    port: 995
    description: Post Office Protocol 3, ontvangen van e-mail over TLS/SSL
    protocol: tcp
  socks:       
    port: 1080
    description: SOCKS proxy
    protocol: tcp
  openvpn:     
    port: 1194
    description: OpenVPN
    protocol: 
    - tcp
    - udp
  mysql:       
    port: 3306
    description: MySQL databasesysteem
    protocol:
    - tcp
    - udp
  rdp:         
    port: 3389
    description: Remote Desktop Protocol
    protocol: tcp
  daap:        
    port: 3689
    description: Digital Audio Access Protocol
    protocol: tcp
  postgresql:  
    port: 5432
    description: PostgreSQL databasesysteem
    protocol: 
    - tcp
    - udp
  vnc:         
    port: 5800
    description: Virtual Network Computing
    protocol: tcp
  vnc-alt:     
    port: 5900
    description: Virtual Network Computing
    protocol: tcp
  gp2p:        
    port: 5900
    description: Gnutella p2p netwerk
    protocol: tcp
  http-alt:    
    port: 8080
    description: WWW caching service proxyservers and Apache Tomcat
    protocol: tcp
```