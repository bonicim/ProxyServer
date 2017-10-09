import socket
import _thread
import time
import select


BUFSIZE = 16
HOST_NAME = socket.gethostname()
HOST_IP = socket.gethostbyname(HOST_NAME)
HOST_PORT = 8888
BACKLOG = 10
SLEEPYTIME = 3


def main():
    init_srv_sck()


def init_srv_sck():
    """
    Initializes the multi-threaded proxy server handling HTTP requests.
    :return: void

    Raises:
        Socket error if socket creation failed
    """


def start_srv_sck():
    """
    Creates and starts the proxy server.
    :return: server socket
    """
    return srv_sck


def handle_multi_threads(srv_sock):
    """
    Configures the server to handle multi-threaded processes
    :param srv_sock: server socket
    :return: void
    """


def handler(cli_sck):
    """
    Processes an HTTP request from a client socket (which can come from
    a web client browser). Calls the real web server, receives the response,
    and forwards the response to the client socket. Does not support caching.
    :param cli_sck: client socket
    :return: void
    """


def parse_req_line(req):
    """
    Parses an HTTP request to return its host name and port.
    :param req: Byte object in HTTP request format
    :return: tuple consisting of a host_name (string) and a port (integer).
    """
    return (host_name, port)


def init_tcp_conn(host_name, port):
    """
    Initializes and creates a TCP connection to host_name and port
    :param host_name: host name
    :param port: port
    :return: socket to the web server that the client originally requested
    """
    return real_srv_sock


def recv_cli_sck_data(cli_sck):
    """
    Receives HTTP request data from the client socket
    :param cli_sck: client socket
    :return: byte object
    """
    return b''


if __name__ == "__main":
    main()

main()
