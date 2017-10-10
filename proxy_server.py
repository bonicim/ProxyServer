import socket
import time
import select

BUFSIZE = 4096
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
    try:
        # Step 1: Create server
        server_socket = start_srv_sck()
        print("SUCCESS! Server created at IP Address: ", HOST_IP, ' on port: ', HOST_PORT)
        print('Multi-threaded server listening for up to ', BACKLOG, ' connections.', "\n")
        print('Server listening........', '\n')

        # Step 2: Process each request
        handle_multi_threads(server_socket)

        # Step 3: Close socket if necessary
        server_socket.close()

    except IOError as err:
        print("I/O error: {0}".format(err))
    except ValueError:
        print("Could not convert data to an integer.")


def start_srv_sck():
    """
    Creates and starts the proxy server.
    :return: server socket
    """
    srv_sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv_sck.bind((HOST_IP, HOST_PORT))
    srv_sck.listen(BACKLOG)
    return srv_sck


def handle_multi_threads(srv_sck):
    """
    Configures the server to handle multi-threaded processes
    :param srv_sck: server socket
    :return: void
    """
    while True:
        read_sockets, write_sockets, err_sockets = select.select([srv_sck], [], [])
        for sock in read_sockets:
            if sock == srv_sck:
                client_socket, addr = sock.accept()
                read_sockets.append(client_socket)
                print('*** NEW CONNECTION ***********************************', '\n')
                print('SUCCESS! Server connected to: ', addr, ' at ', current_time(), '\n')
            else:
                _thread.start_new_thread(handler, (sock,))


def handler(cli_sck):
    """
    Processes an HTTP request from a client socket (which can come from
    a web client browser). Calls the real web server, receives the response,
    and forwards the response to the client socket. Does not support caching.
    Closes both the web server and client socket once all processing has completed.

    Raises:
        Socket error if socket creation failed
    :param cli_sck: client socket
    :return: void
    """
    http_req = get_request_line(cli_sck)
    host_port = parse_req_line(http_req)
    web_srv_sck = init_tcp_conn(host_port[0], host_port[1])
    while True:
        data = web_srv_sck.recv(BUFSIZE)
        if len(data) > 0:
            cli_sck.sendall(data)
        else:
            break
    web_srv_sck.close()
    cli_sck.close()


def get_request_line(cli_sck):
    """
    Gets the request line (i.e. first line) of an HTTP request
    :param cli_sck: client request
    :return: string object of the request line
    """
    req_line = b''
    while True:
        data = cli_sck.recv(BUFSIZE)
        req_line += data
        if data.find(b'\r\n') != -1:
            # we found the first \r\n which means we have the entire request line
            break
    return req_line


def parse_req_line(req):
    """
    Parses an HTTP request line to return its host name and port.
    :param req: string object of the request line
    :return: tuple consisting of a host_name (string) and a port (integer).
    """
    # TODO implement
    # get the first line of the request
    # break it into the host_name and port
    # if no port specified, default is 80
    # must check if host_name is absolute
    # must check for \r\n until it is found carriage return and line feed
    # must check that the req followed HTTP request protocol
    # must decode the request into a string object to allow for parsing
    return (host_name, port)


def init_tcp_conn(host_name, port):
    """
    Initializes and creates a TCP connection to host_name and port
    :param host_name: host name
    :param port: port
    :return: socket to the web server that the client originally requested

    Raises:
        Socket error if socket creation failed
    """
    # TODO must implement using try except
    return real_srv_sock


def current_time():
    return time.ctime(time.time())


if __name__ == "__main":
    main()

main()
