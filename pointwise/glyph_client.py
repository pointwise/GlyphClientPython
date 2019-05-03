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

import os, time, socket, struct, errno, sys, re, platform

class GlyphError(Exception):
    """ This exception is raised when a command passed to the Glyph Server
        encounters an error. 
    """
    def __init__(self, command, message, *args, **kwargs):
        Exception.__init__(self, message, *args, **kwargs)
        self.command = command


class NoLicenseError(Exception):
    """ This exception is raised when a Glyph server subprocess could
        not acquire a valid Pointwise license.
    """
    def __init__(self, message, *args, **kwargs):
        Exception.__init__(self, message, *args, **kwargs)


class GlyphClient(object):
    """ This class is a wrapper around TCP client communications with a
        Glyph Server.  Optionally, it can start a batch Glyph Server process
        as a subprocess (which consumes a Pointwise license). To start
        a server subprocess, initialize the GlyphClient with port = 0.
        For Windows platforms, the default program to run is 'tclsh'. For
        Linux and Mac OS platforms, the default program is 'pointwise -b'.
        (Optionally, the 'prog' argument may be specified to indicate the
        program or shell script to run as the batch Glyph server process.
        This is typically used in environments where multiple versions of
        Pointwise are installed.)
    """

    def __init__(self, port=None, auth=None, version=None, host='localhost', \
            callback=None, prog=None, timeout=10):
        """ Initialize a GlyphClient object """
        self._port = port
        self._auth = auth
        self._host = host
        self._version = version
        self._timeout = timeout

        self._socket = None
        self._busy = False
        self._auth_failed = False
        self._serverVersion = None

        if self._port is None:
            self._port = os.environ.get('PWI_GLYPH_SERVER_PORT', '2807')

        if self._auth is None:
            self._auth = os.environ.get('PWI_GLYPH_SERVER_AUTH', '')

        if self._port == 0:
            self._startServer(callback, prog)


    def __del__(self):
        if hasattr(self, "_server") and self._server is not None:
            self._server.stdout = None
            self._server.stderr = None
            self._server.stdin = None
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


    def connect(self, retries=None):
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
                version (str): the Glyph version number to use for
                    compatibility. The string should be of the form X.Y.Z
                    where X, Y, and Z are positive integer values. The Y and
                    Z values are optional and default to a zero value. A blank
                    value always uses the current version. 
                retries (int): the number of times to retry the connection
                    before giving up. DEPRECATED: if not None, retries will be
                    used to determine a suitable value for timeout.

            Returns:
                bool: True if successfully connected, False otherwise.  If an
                    initial connection is made, but the Glyph Server is busy,
                    calling is_busy() will return True.
        """
        self._closeSocket()

        self._busy = False
        self._auth_failed = False

        timeout = self._timeout
        if retries is not None:
            timeout = 0.1 * retries

        start = time.time()
        while self._socket is None and time.time() - start < timeout:
            try:
                self._socket = self._connect(self._host, self._port)
            except:
                self._socket = None
            if self._socket is None:
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
            problem = None
            if self._version is not None:
                try:
                    self.control('version', self._version)
                except Exception as excCode:
                    problem = excCode
            self._serverVersion = self.eval('pw::Application getVersion')
            if problem is not None:
                m = re.search('Pointwise V(\d+).(\d+)', self._serverVersion)
                if len(m.groups()) == 2:
                    try:
                        serverVers = int(m.groups()[0]) * 10 + \
                            int(m.groups()[1])
                    except:
                        serverVers = 0
                    if serverVers >= 183:
                        self.close()
                        raise problem

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

        if hasattr(self, "_server") and self._server is not None and \
                hasattr(self, "_socket") and self._socket is not None:
            try:
                # request graceful shutdown of server
                self.eval("exit")
            except socket.error as err:
                pass

        self._closeSocket()

        if hasattr(self, "_server") and self._server is not None:
            # safe to call even if server has already shut down
            self._server.terminate()
            self._server.wait()

            # resource warnings may occur if pipes are not closed from the
            # client side (typically on Windows)
            if self._server.stdout is not None:
                try:
                    self._server.stdout.close()
                    self._server.stdout = None
                except IOError:
                    pass

            # wait for the pipe reader thread to finish
            if self._othread is not None:
                self._othread.join(0.5)
                del self._othread
                self._othread = None

            if self._server.stdin is not None:
                try:
                    self._server.stdin.close()
                    self._server.stdin = None
                except IOError:
                    pass

            if self._server.stderr is not None:
                try:
                    self._server.stderr.close()
                    self._server.stderr = None
                except IOError:
                    pass

            self._server = None


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

        try:
            self._send(type, command)
            response = self._recv()
        except socket.error as e:
            # Python 3: BrokenPipeError
            if e.errno == errno.EPIPE:
                raise GlyphError(command,
                        'The Glyph Server connection is closed')
            else:
                raise

        if response is None:
            if not self._socket.fileno() == -1:
                # socket is closed, assume command ended server session
                return None
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

        # Python 2: 'bytes' is an alias for 'str'
        # Python 3: 'bytes' is an immutable bytearray
        message_length = struct.unpack('!I', bytes(message_length))[0]
        if message_length == 0:
            return ('', '')

        message_bytes = self._recvall(message_length)
        if message_bytes is None:
            return None

        # Python 2: convert decoded bytes (type 'unicode') to string (type
        # 'str')
        type = str(message_bytes[0:8].decode('utf-8')).strip()
        payload = str(message_bytes[8:].decode('utf-8'))
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


    def _closeSocket(self):
        """ Close the connection with the Glyph server """
        if self._socket:
            if not self._socket.fileno() == -1:
                try:
                    self._socket.shutdown(socket.SHUT_RDWR)
                except:
                    None
                self._socket.close()
                del self._socket
            self._socket = None


    def _startServer(self, callback, prog):
        """ Create a server if possible on any open port """
        self._server = None
        self._othread = None
        try:
            if prog is None:
                if platform.system() == 'Windows':
                    prog = ['tclsh']
                else:
                    prog = ['pointwise', '-b']
            elif isinstance(prog, tuple):
                prog = list(prog)
            elif not isinstance(prog, list):
                prog = [prog]

            import shutil
            if not hasattr(shutil, 'which'):
                # Python 3: shutil.which exists
                shutil.which = __which__

            target = shutil.which(prog[0])

            if target is None:
                raise GlyphError('server', '%s not found in path' % prog[0])

            prog[0] = target

            # find an open port
            try:
                tsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tsock.settimeout(0)
                tsock.bind(('', 0))
                self._port = tsock.getsockname()[1]
            finally:
                tsock.close()
                time.sleep(0.1)

            if callback is None:
                def __default_callback__(*args):
                    pass
                callback = __default_callback__

            # start the server subprocess
            import subprocess
            self._server = subprocess.Popen(prog, stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            self._server.stdin.write(bytearray((
                "set server_ver [package require PWI_Glyph]\n" +
                "if { [package vcompare $server_ver 2.18.2] < 0 } {" +
                "  puts {Server must be 18.2 or higher}\n"
                "  exit\n"
                "}\n" +
                "puts $server_ver\n" +
                "pw::Script setServerPort %d\n" +
                "puts \"Server: [pw::Application getVersion]\"\n" +
                "pw::Script processServerMessages -timeout %s\n" +
                "puts \"Server: Subprocess completed.\n") %
                (self._port, str(int(self._timeout))), "utf-8"))
            self._server.stdin.flush()

            ver = self._server.stdout.readline().decode('utf-8')
            if re.match(r"\d+\.\d+\.\d+", ver) is None:
                callback(str(ver))
                for line in iter(self._server.stdout.readline, b''):
                    callback(str(line.decode('utf-8')))
                self.close()
                if re.match(r".*unable to obtain a license.*", ver):
                    raise NoLicenseError(ver)
                else:
                    raise GlyphError('server', ver)

            # wait for one line of output to ensure the server is set up
            # and a valid license has been obtained
            callback(self._server.stdout.readline().decode('utf-8'))

            # capture stdout/stderr from the server
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
                            # Python 2: convert decoded bytes to 'str'
                            self._cb(str(line.decode('utf-8')))
                    except Exception as ex:
                        self._error = str(ex)
                    self._ios = None

            self._othread = ReaderThread(self._server.stdout, callback)
            self._othread.start()
        except Exception as ex:
            if self._server is not None:
                self._server.kill()
                self._server.wait()
                self._server = None
            if self._othread is not None:
                self._othread.join(0.5)
                if self._othread._error is not None:
                    callback(self._othread._error)
            raise


def __which__(cmd, mode=os.F_OK | os.X_OK, path=None):
    """Given a command, mode, and a PATH string, return the path which
       conforms to the given mode on the PATH, or None if there is no such
       file.
       `mode` defaults to os.F_OK | os.X_OK. `path` defaults to the result
       of os.environ.get("PATH"), or can be overridden with a custom search
       path.

       Courtesy Python 3.3 source code, for Python 2.x backward compatibility.
    """

    # Check that a given file can be accessed with the correct mode.
    # Additionally check that `file` is not a directory, as on Windows
    # directories pass the os.access check.
    def __access_check__(fn, mode):
        return (os.path.exists(fn) and os.access(fn, mode) and
            not os.path.isdir(fn))

    # Short circuit. If we're given a full path which matches the mode
    # and it exists, we're done here.
    if __access_check__(cmd, mode):
        return cmd

    path = (path or os.environ.get("PATH", os.defpath)).split(os.pathsep)

    if sys.platform == "win32":
        # The current directory takes precedence on Windows.
        if os.curdir not in path:
            path.insert(0, os.curdir)

        # PATHEXT is necessary to check on Windows.
        pathext = os.environ.get("PATHEXT", "").split(os.pathsep)
        # See if the given file matches any of the expected path extensions.
        # This will allow us to short circuit when given "python.exe".
        matches = [cmd for ext in pathext if cmd.lower().endswith(ext.lower())]
        # If it does match, only test that one, otherwise we have to try
        # others.
        files = [cmd] if matches else [cmd + ext.lower() for ext in pathext]
    else:
        # On other platforms you don't have things like PATHEXT to tell you
        # what file suffixes are executable, so just pass on cmd as-is.
        files = [cmd]

    seen = set()
    for dir in path:
        dir = os.path.normcase(dir)
        if dir not in seen:
            seen.add(dir)
            for thefile in files:
                name = os.path.join(dir, thefile)
                if __access_check__(name, mode):
                    return name
    return None

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
