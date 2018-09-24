#! /usr/bin/env python

#
# Copyright 2018 (c) Pointwise, Inc.
# All rights reserved.
#
# This sample Python script is not supported by Pointwise, Inc.
# It is provided freely for demonstration purposes only.
# SEE THE WARRANTY DISCLAIMER AT THE BOTTOM OF THIS FILE.
#

"""
This module provides a wrapper around TCP communication of a client with
a Glyph Server.

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

import os, time, socket, struct

class GlyphError(Exception):
    """ This exception is raised when a command passed to the Glyph Server
        encounters an error. 
    """
    def __init__(self, command, message, *args, **kwargs):
        Exception.__init__(self, message, *args, **kwargs)
        self.command = command


class GlyphClient(object):
    """ This class is a wrapper around TCP client communications with a
        Glyph Server.  Optionally, it can start a batch Glyph Server process
        as a subprocess (which consumes a Pointwise license). To start
        a server subprocess, initialize the GlyphClient with port = 0.
    """

    def __init__(self, port=None, auth=None, host='localhost', callback=None):
        """ Initialize a GlyphClient object """
        self._port = port
        self._auth = auth
        self._host = host

        self._socket = None
        self._busy = False
        self._auth_failed = False
        self._serverVersion = None

        if self._port is None:
            self._port = os.environ.get('PWI_GLYPH_SERVER_PORT', '2807')

        if self._auth is None:
            self._auth = os.environ.get('PWI_GLYPH_SERVER_AUTH', '')

        if self._port == 0:
            self._startServer(callback)


    def __del__(self):
        self.close()


    def __eq__(self, other):
        return self is other


    def __enter__(self):
        """ When using GlyphClient as a context manager, connect and return self
        """
        if not self.connect():
            if self._auth_failed:
                raise GlyphError('connect', 'Glyph Server AUTH failed')
            elif self._busy:
                raise GlyphError('connect', 'Glyph Server BUSY')
            else:
                raise GlyphError('connect', 'Could not connect to Glyph Server')
        return self


    def __exit__(self, *args):
        """ When using GlyphClient as a context manager, disconnect """
        self.close()

    def __str__(self):
        s = 'GlyphClient(' + str(self._host) + '@' + str(self._port) + \
            ') connected=' + str(self.is_connected())
        if self.is_connected():
            s = s + ' Server=' + self._serverVersion
        return s


    def connect(self, retries=5):
        """ Connect to a Glyph server at the given host and port.

            Args:
                port (str): the port number of the Glyph Server to connect to.
                    If the port is not given, it defaults to the environment
                    variable PWI_GLYPH_SERVER_PORT, or 2807 if not defined.
                auth (str): the authorization code of the Glyph Server.  If the
                    auth is not given, it defaults to the environment variable
                    PWI_GLYPH_SERVER_AUTH, or an empty string if not defined.
                host (str): the host name of the Glyph Server to connect to.
                    The default value is 'localhost'.
                retries (int): the number of times to retry the connection
                    before giving up.

            Returns:
                bool: True if successfully connected, False otherwise.  If an
                    initial connection is made, but the Glyph Server is busy,
                    calling is_busy() will return True.
        """
        self.close()

        self._busy = False
        self._auth_failed = False

        while self._socket is None and retries > 0:
            try:
                self._socket = self._connect(self._host, self._port)
            except:
                self._socket = None
            if self._socket is None:
                retries -= 1
                time.sleep(0.1) # sleep for a bit before retry

        if self._socket is None:
            return False

        self._send('AUTH', self._auth)

        response = self._recv()
        if response is None:
            self._socket.close()
            self._socket = None
            return False

        rtype, payload = response

        self._auth_failed = (rtype == 'AUTHFAIL')
        self._busy = (rtype == 'BUSY')

        if rtype != 'READY':
            self.close()
        else:
            self._serverVersion = self.eval('pw::Application getVersion')

        return self._socket is not None


    def is_busy(self):
        """ Check if the reason for the last failed attempt to connect() was
            because the Glyph Server is busy.

            Returns:
                bool: True if the last call to connect failed because the
                    Glyph Server was busy, False otherwise.
        """
        return self._busy 


    def auth_failed(self):
        """ Check if the reason for the last failed attempt to connect() was
            because the Glyph Server authentication failed.

            Returns:
                bool: True if the last call to connect failed because the
                    Glyph Server authentication failed, False otherwise.
        """
        return self._auth_failed


    def eval(self, command):
        """ Evaluate a Glyph command on the Glyph Server, including nested
            commands and variable substitution.

            Args:
                command (str): A Glyph command to be evaluated on the
                Glyph Server.

            Returns:
                str: The result from evaluating the command on the Glyph Server.

            Raises:
                GlyphError: If the command evaluation on the Glyph Server
                resulted in an error.
        """
        return self._sendcmd('EVAL', command)


    def command(self, command):
        """ Execute a Glyph command on the Glyph Server, with no support
            for nested commands and variable substitution.

            Args:
                command (str): A JSON encoded string of an array of a
                    Glyph command and the parameters to be executed.

            Returns:
                str: The JSON encoded string result from executing the
                    command on the Glyph Server.

            Raises:
                GlyphError: If the command execution on the Glyph Server
                    resulted in an error.
        """
        return self._sendcmd('COMMAND', command)


    def control(self, setting, value=None):
        """ Send a control message to the Glyph Server

            Args:
                setting (str): The name of the control setting
                value (str): The value to set the setting to. If none the value
                    will only be queried. 

            Returns:
                str: The current value of the control setting

            Raises:
                GlyphError: If the control setting or the value is invalid.
        """
        command = setting
        if value is not None:
            command += '=' + value
        return self._sendcmd('CONTROL', command)
    
    
    def get_glyphapi(self):
        """ Creates and returns a GlyphAPI object for this client
            
            Returns: 
                GlyphAPI object for automatic Glyph command execution
                through this client connection
        """
        from pointwise import glyphapi
        if not self.is_connected():
            self.connect()

        if self.is_connected():
            return glyphapi.GlyphAPI(glyph_client=self)
        else:
            raise GlyphError('GlyphAPI',
                    'The client is not connected to a Glyph Server')
    
    
    def is_connected(self):
        """ Check if there is a connection to the Glyph Client
            
            Returns:
                True if there is a valid connection, False otherwise.
        """
        result = False
        try:
            result = self._socket is not None and self.ping()
        except:
            result = False
        return result    
    
    
    def ping(self):
        """ Ping the Glyph Server

            Returns:
                bool: True if the the Glyph Server was successfully pinged,
                    False otherwise.
        """
        result = False
        try:
            result = self._sendcmd('PING', '') == "OK"
        except:
            result = False
        return result


    def close(self):
        """ Close the connection with the Glyph server """
        if self._socket:
            self._socket.close()
            self._socket = None

            if hasattr(self, "_server") and self._server is not None:
                self._server.terminate()
                if self._othread is not None:
                    self._othread.join(0.1)


    def disconnect(self):
        """ Close the connection with the Glyph server """
        self.close()


    def _connect(self, host, port):
        """ Helper function for connecting a socket to the given host and port
        """
        # try to connect using both IPv4 and IPv6
        s = None
        for res in socket.getaddrinfo(host, port, socket.AF_UNSPEC,
                socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                s = socket.socket(af, socktype, proto)
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
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


    def _sendcmd(self, type, command):
        """ Helper function for sending a command to the Glyph Server """
        if self._socket is None:
            raise GlyphError(command,
                    'The client is not connected to a Glyph Server')

        self._send(type, command)
        response = self._recv()
        if response is None:
            raise GlyphError(command, 'No response from the Glyph Server')

        type, payload = response
        if type != 'OK':
            raise GlyphError(command, payload)

        return payload


    def _send(self, type, payload):
        """ Helper function for sending a message on the socket """
        message_bytes = type.encode('utf-8').ljust(8) + payload.encode('utf-8')
        message_length = struct.pack('!I', len(message_bytes))
        self._socket.sendall(message_length)
        self._socket.sendall(message_bytes)


    def _recv(self):
        """ Helper function for receiving a message on the socket """
        message_length = self._recvall(4)
        if message_length is None:
            return None

        message_length = struct.unpack('!I', bytes(message_length))[0]
        if message_length == 0:
            return ('', '')

        message_bytes = self._recvall(message_length)
        if message_bytes is None:
            return None

        type = message_bytes[0:8].strip().decode('utf-8')
        payload = message_bytes[8:].decode('utf-8')
        return (type, payload)


    def _recvall(self, size):
        """ Helper function to recv size bytes or return None if EOF is hit """
        data = bytearray()
        while len(data) < size:
            packet = self._socket.recv(size - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

    def puts(self, *args):
        self.eval("puts {%s}" % ' '.join(args))


    def _startServer(self, callback):
        """ Create a server if possible on any open port """
        self._server = None
        self._othread = None
        try:
            # Find tclsh in the current path
            from shutil import which
            tclsh = os.environ.get('PWI_GLYPH_SERVER_TCLSH', 'tclsh')
            tclsh = which(tclsh)
            if tclsh is None:
                raise GlyphError('server', 'tclsh not found in path')

            # find an open port
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tsock:
                tsock.settimeout(0)
                tsock.bind(('', 0))
                self._port = tsock.getsockname()[1]
                tsock.close()
                time.sleep(0.1)

            # start the server subprocess
            import subprocess
            if callback is not None:
                self._server = subprocess.Popen(tclsh, stdin=subprocess.PIPE, \
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            else:
                self._server = subprocess.Popen(tclsh, stdin=subprocess.PIPE, \
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            self._server.stdin.write(bytes((
                "package require PWI_Glyph 2\n" +
                "pw::Script setServerPort %d\n" +
                "puts \"Server: [pw::Application getVersion]\"\n" +
                "while 1 { pw::Script processServerMessages }\n") %
                self._port, "utf-8"))
            self._server.stdin.flush()

            # capture stdout/stderr from the server
            if callback is not None:
                import threading
                class ReaderThread(threading.Thread):
                    def __init__(self, ios, callback):
                        threading.Thread.__init__(self)
                        self._ios = ios
                        self._error = None
                        self._cb = callback
                        self.daemon = True

                    def run(self):
                        try:
                            for line in iter(self._ios.readline, b''):
                                self._cb(line.decode('utf-8'))
                        except Exception as ex:
                            self._error = str(ex)

                self._othread = ReaderThread(self._server.stdout, callback)
                self._othread.start()
        except Exception as ex:
            if self._server is not None:
                self._server.kill()
            if self._othread is not None:
                self._othread.join(0.5)
                if callback is not None and self._othread._error is not None:
                    callback(self._othread._error)
            raise

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
