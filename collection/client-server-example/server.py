import functools
import logging
import os
import socket

import click
from click.core import Group
from daemons.prefab import run


LOG = logging.getLogger(__name__)


class AppServer:

    class __open_socket__:

        @property
        def host(self):
            return self._host

        @property
        def port(self):
            return self._port

        @property
        def family(self):
            return self._family

        @property
        def type(self):
            return self._type

        @property
        def protocol(self):
            return self._proto

        @property
        def fileno(self):
            return self._fileno

        @property
        def socket(self):
            return self._socket

        @property
        def status(self):
            return self._socket_status

        def __init__(self, host, port, **attrs):
            self._host   = host
            self._port   = int(port)
            self._family = attrs.get("family", None) or socket.AF_INET
            self._type   = attrs.get("type", None) or socket.SOCK_STREAM
            self._proto  = attrs.get("proto", None) or -1
            self._fileno = attrs.get("filno", None)

            attrs = dict(
                family=self._family,
                type=self._type,
                proto=self._proto,
                fileno=self._fileno
            )
            self._socket = socket.socket(**attrs)
            self._socket.bind((self._host, self._port))
            self._socket.listen()

            self._socket_status = "OPEN"
            LOG.debug(f"Opened connection on {self._host}:{self._port}")

        def close(self):
            try:
                self._socket.close()
            finally:
                self._socket_status = "CLOSED"
                LOG.debug(f"Closed connection from {self._host}:{self._port}")
                return None

        def __del__(self):
            try:
                if self._socket_status == "OPEN":
                    LOG.warn(f"Socket on {self._host}:{self._port} still open at termination")
            finally:
                return None

        def __enter__(self):
            return self

        def __exit__(self, etype, eval, tracebk):
            self.close()

    host = "127.0.0.1"
    port = 47716

    def open(self, host: str = None, port: int = None, **attrs):
        host = host or self.host
        port = port or self.port

        return self.__open_socket__(host, port, **attrs)

    def __init__(self, host: str = None, port: int = None):
        self.host = self.parse_host(host)
        self.port = self.parse_port(port)

    def parse_host(self, host):
        if host == "localhost" or not host:
            return self.host
        return host

    def parse_port(self, port):
        if not port:
            return self.port
        return int(port)


class AppDaemon(run.RunDaemon):

    def run(self):
        
        with AppServer().open() as server:
            LOG.debug("Listening...")
            while self._is_running:
                self.receive_incoming(server)

    def receive_incoming(self, server: AppServer.__open_socket__, buffsize: int = None):
        conn, addr = server.socket.accept()
        with conn:
            LOG.debug(f"Connection from {addr}")
            while True:
                data = conn.recv(buffsize or 1024)
                if not data: break
                LOG.info(f"Recieved from connection: {data!r}")
                conn.sendall(data)

    def start(self):
        self._is_running = True
        super().start()

    def stop(self):
        self._is_running = False
        super().stop()


def register_group(func=None, parent: click.Group = None, name: str = None, **attrs):

    def inner(fn):
        fnname = fn.__name__.replace("_", "-")
        
        @parent.group(name=name or fnname, **attrs)
        @click.pass_context
        def sub_inner(*args, **kwargs):
            return fn(*args, **kwargs)

        return sub_inner

    if func:
        return inner(func)
    return inner


def register_children(parent: click.Group, children: list, **attrs):

    def register_subfunc(child):
        if isinstance(child, click.Command):
            parent.add_command(child, **attrs)
        elif isinstance(child, click.Group):
            register_group(child, parent, **attrs)

    for child in children:
        register_subfunc(child)


class Controller:

    def __init__(self, config: dict = {}, commands: list = []):

        @click.group()
        def dispatch():
            pass

        self.load_commands(dispatch, commands)

        self.pidfile  = self.parse_pidfile(config)
        self.logfile  = self.parse_logfile(config)
        self.app      = AppDaemon(pidfile=self.pidfile)
        self.dispatch = dispatch

        logging.basicConfig(filename=self.logfile, level=logging.DEBUG)

    def load_commands(self, cli: Group, commands: list):

        @click.command()
        def start():
            self.app.start()

        @click.command()
        def stop():
            self.app.stop()

        @click.command()
        def restart():
            self.app.restart()

        @click.command()
        def status():
            print(f"daemon status: {self.app._is_running}")

        register_children(cli, commands + [start, stop, restart, status])

    def parse_pidfile(self, config: dict):
        default = os.path.join(os.getcwd(), "app.pid")
        return config.get("pidfile", None) or default

    def parse_logfile(self, config: dict):
        default = os.path.join(os.getcwd(), "app.log")
        return config.get("logfile", None) or default


if __name__ == "__main__":
    exit(Controller().dispatch())
