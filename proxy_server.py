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
    req_line = get_request_line(cli_sck)

    verify_get_request(req_line)
    verify_absolute_uri(req_line)

    host_port = parse_req_line(req_line)
    # init will check if conn was successful
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
    return req_line.decode('utf-8')


def verify_get_request(req_line):
    if is_get_request(req_line):
        print("Request from client is a GET")
    else:
        print("Request from client is not a GET")
        raise ValueError("Proxy only supports GET")


def is_get_request(req_line):
    return req_line.split(' ')[0] == 'GET'


def verify_absolute_uri(req_line):
    if is_absolute_uri(req_line):
        print("The requested URI is absolute.")
    else:
        print("The requested URI is NOT absolute. Proxy only supports absolute URI.")
        raise ValueError("The requested URI is NOT absolute. Proxy only supports absolute URI.")


def is_absolute_uri(req_line):
    req_uri = req_line.split(' ')
    return req_uri[1].find('http') == 0 and req_uri[1].find('://') == 4


def parse_req_line(req_line):
    """
    Parses an HTTP request line to return its host name and port. Assumes that
    req_line is a properly formatted request line
    :param req: string object of the request line
    :return: tuple consisting of a host_name (string) and a port (integer).
    """
    # TODO implement
    req_line_arr = req_line.split(' ')
    uri = req_line_arr[1]
    

    # break it into the host_name and port
    # if no port specified, default is 80
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
