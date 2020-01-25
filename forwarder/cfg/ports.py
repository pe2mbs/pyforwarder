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




