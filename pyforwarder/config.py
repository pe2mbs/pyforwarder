import io
import os
import yaml
import json
import sys
import pyforwarder.api as API


WELL_DEFINED_PORTS = {
    "ftp":          { "port": 20, "description": "file transfer protocol", "protocol": "tcp" },
    "ftpc":         { "port": 21, "description": "file transfer protocol control", "protocol": "tcp" },
    "ssh":          { "port": 22, "description": "Secure Shell", "protocol": "tcp" },
    "telnet":       { "port": 23, "description": "Telnet", "protocol": "tcp" },
    "smtp":         { "port": 25, "description": "Simple Mail Transfer Protocol, verzending van e-mail (MTA)", "protocol": "tcp" },
    "dns":          { "port": 53, "description": "Domain Name System", "protocol": "udp" },
    "dhcpc":        { "port": 67, "description": "Domain Name System client", "protocol": "udp" },
    "dhcps":        { "port": 68, "description": "Domain Name System server", "protocol": "udp" },
    "tftp":         { "port": 69, "description": "Trivial File Transfer Protocol", "protocol": "udp" },
    "http":         { "port": 80, "description": "Hypertext Transfer Protocol", "protocol": [ "tcp", 'udp' ] },
    "pop3":         { "port": 110, "description": "Post Office Protocol 3, receive of e-mail", "protocol": "tcp" },
    "nntp":         { "port": 119, "description": "Network News Transfer Protocol", "protocol": "tcp" },
    "ntp":          { "port": 123, "description": "Network Time Protocol", "protocol": "tcp" },
    "netbns":       { "port": 137, "description": "NetBIOS Name Service", "protocol": "udp" },
    "netbds":       { "port": 138, "description": "NetBIOS Name Service", "protocol": "udp" },
    "netbss":       { "port": 139, "description": "NetBIOS Session Service", "protocol": "tcp" },
    "imap":         { "port": 143, "description": "Internet Message Access Protocol", "protocol": "tcp" },
    "snmp":         { "port": 161, "description": "Simple Network Management Protocol", "protocol": "udp" },
    "snmptrap":     { "port": 162, "description": "Simple Network Management Protocol, getriggerde notificaties", "protocol": "udp" },
    "ldap":         { "port": 389, "description": "Lightweight Directory Access Protocol", "protocol": "tcp" },
    "https":        { "port": 443, "description": "HyperText Transfer Protocol over TLS/SSL", "protocol": "tcp" },
    "smb":          { "port": 445, "description": "Direct Hosting / SMB (Samba) over TCP", "protocol": "tcp" },
    "smtps-alt":    { "port": 465, "description": "Simple Mail Transfer Protocol over TLS/SSL", "protocol": "tcp" },
    "dhcpc-alt":    { "port": 546, "description": "Domain Name System (ipv6) client", "protocol": "udp" },
    "dhcps-alt":    { "port": 547, "description": "Domain Name System (ipv6) server", "protocol": "udp" },
    "msn":          { "port": 569, "description": "Multiple Subscriber Number", "protocol": "tcp" },
    "smtps":        { "port": 587, "description": "Simple Mail Transfer Protocol, verzending van uitgaande e-mail (MSA)[16]", "protocol": "tcp" },
    "ftps":         { "port": 990, "description": "File Transfer Protocol over SSL", "protocol": "tcp" },
    "imaps":        { "port": 993, "description": "Internet Message Access Protocol over TLS/SSL", "protocol": "tcp" },
    "pop3s":        { "port": 995, "description": "Post Office Protocol 3, ontvangen van e-mail over TLS/SSL", "protocol": "tcp" },
    "socks":        { "port": 1080, "description": "SOCKS proxy", "protocol": "tcp" },
    "openvpn":      { "port": 1194, "description": "OpenVPN", "protocol":  [ "tcp", 'udp' ] },
    "mysql":        { "port": 3306, "description": "MySQL databasesysteem", "protocol":  [ "tcp", 'udp' ] },
    "rdp":          { "port": 3389, "description": "Remote Desktop Protocol", "protocol": "tcp" },
    "daap":         { "port": 3689, "description": "Digital Audio Access Protocol", "protocol": "tcp" },
    "postgresql":   { "port": 5432, "description": "PostgreSQL databasesysteem", "protocol":  [ "tcp", 'udp' ] },
    "vnc":          { "port": 5800, "description": "Virtual Network Computing", "protocol": "tcp" },
    "vnc-alt":      { "port": 5900, "description": "Virtual Network Computing", "protocol": "tcp" },
    "gp2p":         { "port": 5900, "description": "Gnutella p2p netwerk", "protocol": "tcp" },
    "http-alt":     { "port": 8080, "description": "WWW caching service proxyservers and Apache Tomcat", "protocol": "tcp" },
}


class ConfigPort( object ):
    def __init__( self, port_name, settings ):
        self.__portName = port_name
        self.__settings = settings
        return

    @property
    def portName( self ):
        return self.__portName

    @property
    def port( self ):
        return self.__settings[ 'port' ]

    @property
    def description( self ):
        return self.__settings[ 'description' ]

    @property
    def protocol( self ):
        return self.__settings[ 'protocol' ]

    def toDict( self ):
        return { self.__portName: self.__settings }


class ConfigSslTlsSet( object ):
    def __init__( self, cfg ):
        self.__cfg = cfg
        return

    @property
    def verify( self ):
        return self.__cfg.get( 'verify', True )

    @property
    def checkHost( self ):
        return self.__cfg.get( 'check-host', True )

    @property
    def required( self ):
        return self.__cfg.get( 'required', 'optional' )

    @property
    def certificate( self ):
        path_file = self.__cfg.get( 'certificate', None )
        if path_file is not None:
            path_file = os.path.abspath( path_file )

        return path_file

    @property
    def key( self ):
        path_file = self.__cfg.get( 'key', None )
        if path_file is not None:
            path_file = os.path.abspath( path_file )

        return path_file

    @property
    def caBundle( self ):
        path_file = self.__cfg.get( 'ca-bundle', None )
        if path_file is not None:
            path_file = os.path.abspath( path_file )

        return path_file


class ConfigAddressSet( object ):
    def __init__( self, cfg, ports ):
        self.__cfg = cfg
        self.__ports    = ports
        return

    def toDict( self ):
        return self.__cfg

    @property
    def addr( self ):
        return self.__cfg.get( 'addr', '0.0.0.0' )

    @property
    def port( self ):
        value = self.__cfg.get( 'port', 8000 )
        if isinstance( value, str ):
            value = self.__ports[ value ].port

        return value

    @property
    def portInfo( self ):
        value = self.__cfg.get( 'port', 8000 )
        if isinstance( value, str ):
            return self.__ports[ value ]

        elif isinstance( value, int ):
            for port, obj in self.__ports.items():
                if obj.port == value:
                    return value

            return ConfigPort( 'unkn', {
                'port': value,
                'description': 'Unknown protocol',
                'protocol': [ 'tcp', 'udp' ]
            } )

        raise Exception( 'port value invalid, should be integer or str' )

    @property
    def useSslTls( self ):
        return self.__cfg.get( 'use-ssl-tls', False )

    @property
    def sslTls( self ):
        return ConfigSslTlsSet( self.__cfg.get( 'ssl-tls', {} ) )


class ConfigHost( object ):
    def __init__( self, cfg, ports ):
        self.__src = ConfigAddressSet( cfg[ 'source' ], ports )
        self.__dst = ConfigAddressSet( cfg[ 'destination' ], ports )
        self.__enabled  = cfg.get( 'enabled', True )
        return

    @property
    def enabled( self ):
        return self.__enabled

    @property
    def source( self ):
        return self.__src

    @property
    def destination( self ):
        return self.__dst

    def toDict( self ):
        return { 'source': self.__src.toDict(),
                 'destination': self.__dst.toDict() }


class ConfigOptions( object ):
    def __init__( self, cfg ):
        self.__cfg = cfg
        return

    @property
    def verbose( self ):
        return self.__cfg.get( 'verbose', API.verbose )

    @property
    def trace( self ):
        return self.__cfg.get( 'trace', API.trace )

    @property
    def hexdump( self ):
        return self.__cfg.get( 'hexdump', API.hexd )

    def updateGlobals( self ):
        API.verbose = self.verbose
        API.trace   = self.trace
        API.hexd    = self.hexdump
        return


class ConfigFile( object ):
    def __init__(self):
        self.__hosts    = {}
        self.__ports    = {}
        self.__cfg      = {}
        return

    def load( self, filename ):
        if filename.lower().endswith( ".json" ):
            with open( filename, 'r' ) as stream:
                self.__cfg = json.load( stream )

        elif filename.lower().endswith( ".yaml" ):
            with open( filename, 'r' ) as stream:
                self.__cfg = yaml.load( stream, Loader = yaml.Loader )

        else:
            print( "Configuration file format is invalid" )
            exit( -3 )

        if self.version == 1:
            raise Exception( "Invalid config version, must be version 2")

        self.__ports = {}
        for portname, value in WELL_DEFINED_PORTS.items():
            self.__ports[ portname ] = ConfigPort( portname, value )

        for portname, value in self.__cfg.get( "ports", {} ).items():
            self.__ports[ portname ] = ConfigPort( portname, value )

        self.__hosts = []
        for host in self.__cfg.get( 'hosts', [] ):
            self.__hosts.append( ConfigHost( host, self.__ports ) )

        return

    def save( self, filename ):
        with open( filename, 'w' ) as stream:
            yaml.dump( self.__cfg, stream, Loader = yaml.Dumper )
        return

    @property
    def version( self ):
        return self.__cfg.get( 'version', 1 )

    @property
    def hosts( self ):
        return [ h.toDict() for h in self.__hosts ]

    @property
    def ports( self ):
        return [ { p: values.toDict() } for p, values in self.__ports.items() ]

    def lookupPort( self, port_name ):
        if port_name in self.__ports:
            return self.__ports[ port_name ]

        return None

    def __iter__( self ):
        return iter( self.__hosts )

    @property
    def options( self ):
        return ConfigOptions( self.__cfg.get( 'options', {} ) )

    def dump( self ):
        stream = io.StringIO()
        yaml.dump( self.__cfg, stream, Dumper = yaml.Dumper, default_flow_style = False )
        stream.seek(0,0)
        for line in stream.readlines():
            API.logger.debug( line.replace( '\n', '' ) )

        return

    @property
    def logging( self ):
        return self.__cfg.get( 'logging', {
            "version": 1,
            'formatters': {
                    'trace': {
                        'class': 'logging.Formatter',
                        'format': '%(asctime)s %(levelname)-8s %(message)s'
                    },
                    'verbose': {
                        'class': 'logging.Formatter',
                        'format': '%(asctime)s %(message)s'
                    }
                },
                'handlers': {
                    'console': {
                        'class': 'logging.StreamHandler',
                        'formatter': 'verbose',
                        'level': 'INFO',
                    },
                    'file': {
                        'class': 'logging.FileHandler',
                        'filename': 'mplog.log',
                        'mode': 'w',
                        'formatter': 'trace',
                        'level': 'DEBUG'
                    },
                },
                'root': {
                    'level': 'DEBUG',
                    'handlers': [ 'console', 'file' ]
                },
        } )
