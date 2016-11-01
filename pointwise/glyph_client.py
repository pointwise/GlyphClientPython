#! /usr/bin/env python

#
# Copyright 2016 (c) Pointwise, Inc.
# All rights reserved.
#
# This sample Python script is not supported by Pointwise, Inc.
# It is provided freely for demonstration purposes only.
# SEE THE WARRANTY DISCLAIMER AT THE BOTTOM OF THIS FILE.
#

"""
This module provides a wrapper around TCP communication of a client with a Glyph Server.

Example:
    from pointwise import GlyphClient, GlyphError

    glf = GlyphClient()
    if glf.connect():
        try:
            result = glf.eval('pw::Application getVersion')
            print('Pointwise version is {0}'.format(result))
        except GlyphError as e:
            print('Error in command {0}\n{1}'.format(e.command, e))

    elif glf.is_busy():
        print('The Glyph Server is busy')
    elif glf.auth_failed():
        print('Glyph Server authentication failed')
    else:
        print('Failed to connect to the Glyph Server')

"""

import os
import time
import socket
import struct

class GlyphError(Exception):
    """
    This exception is raised when a command passed to the Glyph Server
    encounters an error. 
    """
    def __init__(self, command, message, *args, **kwargs):
        Exception.__init__(self, message, *args, **kwargs)
        self.command = command

class GlyphClient:
    """
    This class is a wrapper around TCP client communications with a Glyph Server. 
    """
    def __init__(self):
        """
        Initialize a GlyphClient object
        """
        self._socket = None
        self._busy = False
        self._auth_failed = False

    def connect(self, port=None, auth=None, host='localhost', retries=5):
        """
        Connect to a Glyph server at the given host and port.

        Args:
            port (str): the port number of the Glyph Server to connect to.
                If the port is not given, it defaults to the environment
                variable PWI_GLYPH_SERVER_PORT, or 2807 if not defined.
            auth (str): the authorization code of the Glyph Server.  If the
                auth is not given, it defaults to the environment variable
                PWI_GLYPH_SERVER_AUTH, or an empty string if not defined.
            host (str): the host name of the Glyph Server to connect to.
                The default value is 'localhost'.
            retries (int): the number of times to retry the connection before
                giving up.

        Returns:
            bool: True if successfully connected, False otherwise.  If an
                initial connection is made, but the Glyph Server is busy,
                calling is_busy() will return True.
        """
        if self._socket:
            self.close()

        self._busy = False
        self._auth_failed = False

        if port is None:
            port = os.environ.get('PWI_GLYPH_SERVER_PORT', '2807')

        if auth is None:
            auth = os.environ.get('PWI_GLYPH_SERVER_AUTH', '')

        self._socket = self._connect(host, port)
        while self._socket is None and retries > 0:
            retries -= 1
            time.sleep(0) # sleep to allow events to process
            self._socket = self._connect(host, port)

        if self._socket is None:
            return False

        self._send('AUTH', auth)

        response = self._recv()
        if response is None:
            self._socket.close()
            self._socket = None
            return False

        type, payload = response
        if type != 'READY':
            self._auth_failed = (type == 'AUTHFAIL')
            self._busy = (type == 'BUSY')
            self._socket.close()
            self._socket = None
            return False

        return True

    def is_busy(self):
        """
        Check if the reason for the last failed attempt to connect() was
        because the Glyph Server is busy.

        Returns:
            bool: True if the last call to connect failed because the
                Glyph Server was busy, False otherwise.
        """
        return self._busy 

    def auth_failed(self):
        """
        Check if the reason for the last failed attempt to connect() was
        because the Glyph Server authentication failed.

        Returns:
            bool: True if the last call to connect failed because the
                Glyph Server authentication failed, False otherwise.
        """
        return self._auth_failed 

    def eval(self, command):
        """
        Evaluate a Glyph command on the Glyph Server.

        Args:
            command (str): A Glyph command to be evaluated on the Glyph Server.

        Returns:
            str: The result from evaluating the command on the Glyph Server.

        Raises:
            GlyphError: If the command evaluation on the Glyph Server resulted
                in an error.
        """
        if self._socket is None:
            raise GlyphError(command, 'The client is not connected to a Glyph Server')

        self._send('EVAL', command)
        response = self._recv()
        if response is None:
            raise GlyphError(command, 'No response from the Glyph Server')

        type, payload = response
        if type != 'OK':
            raise GlyphError(command, payload)

        return payload

    def close(self):
        """
        Close the connection with the Glyph server
        """
        if self._socket:
            self._socket.close()
            self._socket = None

    def _connect(self, host, port):
        """
        Helper function for connecting a socket to the given host and port
        """
        # try to connect using both IPv4 and IPv6
        s = None
        for res in socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                s = socket.socket(af, socktype, proto)
            except (socket.error, OSError) as msg:
                s = None
                continue
            try:
                s.connect(sa)
            except (socket.error, OSError) as msg:
                s.close()
                s = None
                continue
            break
        return s

    def _send(self, type, payload):
        """
        Helper function for sending a message on the socket
        """
        message_bytes = type.encode('utf-8').ljust(8) + payload.encode('utf-8')
        message_length = struct.pack('!I', len(message_bytes))
        self._socket.sendall(message_length)
        self._socket.sendall(message_bytes)

    def _recv(self):
        """
        Helper function for receiving a message on the socket
        """
        message_length = self._recvall(4)
        if message_length is None:
            return None

        message_length = struct.unpack('!I', message_length)[0]
        if message_length == 0:
            return ('', '')

        message_bytes = self._recvall(message_length)
        if message_bytes is None:
            return None

        type = message_bytes[0:8].strip().decode('utf-8')
        payload = message_bytes[8:].decode('utf-8')
        return (type, payload)

    def _recvall(self, size):
        """
        Helper function to recv size bytes or return None if EOF is hit
        """
        data = ''
        while len(data) < size:
            packet = self._socket.recv(size - len(data))
            if not packet:
                return None
            data += packet
        return data


#
# DISCLAIMER:
# TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, POINTWISE DISCLAIMS
# ALL WARRANTIES, EITHER EXPRESS OR IMPLIED, INCLUDING, BUT NOT LIMITED
# TO, IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE, WITH REGARD TO THIS SCRIPT.  TO THE MAXIMUM EXTENT PERMITTED 
# BY APPLICABLE LAW, IN NO EVENT SHALL POINTWISE BE LIABLE TO ANY PARTY 
# FOR ANY SPECIAL, INCIDENTAL, INDIRECT, OR CONSEQUENTIAL DAMAGES 
# WHATSOEVER (INCLUDING, WITHOUT LIMITATION, DAMAGES FOR LOSS OF 
# BUSINESS INFORMATION, OR ANY OTHER PECUNIARY LOSS) ARISING OUT OF THE 
# USE OF OR INABILITY TO USE THIS SCRIPT EVEN IF POINTWISE HAS BEEN 
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGES AND REGARDLESS OF THE 
# FAULT OR NEGLIGENCE OF POINTWISE.
#