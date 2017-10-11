import socket
import time
import select
import sys

BUFSIZE = 4096
HOST_NAME = socket.gethostname()
HOST_IP = socket.gethostbyname(HOST_NAME)
HOST_PORT = 8888
BACKLOG = 10
SLEEPYTIME = 3
HTTP_BAD_METHOD = b'HTTP/1.1 405 METHOD_NOT_ALLOWED\r\nConnection:close\r\n\r\n'


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
    print("Getting HTTP request...")
    time.sleep(3)
    http_req = get_http_request(cli_sck)
    print("HTTP Request is: ", http_req, '\n')  # http_req is a bytes object

    print("Getting HTTP request line...")
    time.sleep(3)
    req_line = get_request_line(http_req)  # req_line is a string object
    print("Request line is: ", req_line, '\n')

    print("Verifying that HTTP request is GET...")
    time.sleep(3)
    if not is_get_request(req_line):
        print("Request from client is not a GET")
        cli_sck.sendall(HTTP_BAD_METHOD)
        sys.exit()

    print("Verifying that uri is absolute...", '\n')
    time.sleep(3)
    verify_absolute_uri(req_line)

    print("Modifying HTTP request for web server...")
    time.sleep(3)
    mod_http_req = modify_http_request(http_req)
    print("The HTTP request to be sent to the server: ", mod_http_req, '\n')

    print("Parsing HTTP request line for host and port...")
    time.sleep(3)
    host_port = parse_req_line(req_line)
    print("Successfully parsed host and port: ", host_port, '\n')

    try:
        print("Connecting to web server...")
        time.sleep(3)
        web_srv_sck = init_tcp_conn(host_port[0], host_port[1])
        print("Successful connection to host and port at socket: ", web_srv_sck, '\n')

        # send the actual request
        print("Sending modified request to web server...: ")
        time.sleep(3)
        web_srv_sck.sendall(mod_http_req)

        # wait for response
        print("Waiting for response...")
        time.sleep(3)
        while True:
            data = web_srv_sck.recv(BUFSIZE)
            if len(data) > 0:
                cli_sck.sendall(data)
            else:
                break
        web_srv_sck.close()
        cli_sck.close()
    except IOError as err:
        print("I/O error: {0}".format(err))
    except ValueError:
        print("Could not convert data to an integer.")


def get_http_request(cli_sck):
    """
    Returns the HTTP request
    :param cli_sck: client socket
    :return: http request in byte object type
    """
    req = b''
    while True:
        data = cli_sck.recv(BUFSIZE)
        req += data
        if data == '\r\n' and req[len(req) - 4:len(req)] == b'\r\n\r\n':
            break
    return req


def get_request_line(http_req):
    """
    Gets the request line (i.e. first line) of an HTTP request
    :param http_req http request in byte object
    :return: string object of the request line
    """
    return http_req[:http_req.find(b'\r\n')].decode('utf-8')


def modify_http_request(http_req):
    mod_http_req = ensure_closed_connection(http_req)
    return http_req


def ensure_closed_connection(http_req):
    req_arr = http_req.split(b'/r/n')
    if http_req.count(b'Connection') > 0:
        print()
        # make a copy of http req and mutate it
        # remove Keep alive header
        # make copy
        # add Connection header
        # check for close and keep-alive
        # if close, don't do anythhing
        # if keep-alive change it
    else:
        req_updated = bytearray(http_req)
        req_updated = req_updated[:len(req_updated) - 2]
        req_updated += b'Connection:close\r\n\r\n'
        return req_updated


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
    req_line_arr = req_line.split(' ')  # breaks request line into its 3 pieces
    uri = req_line_arr[1].split('://')[1]  # removes the 'http://' from URI
    host_name = get_host_name(uri)
    port = get_port(uri)
    return host_name, port


def get_host_name(uri):
    end = uri.find('/')
    if end != -1:
        return uri[:end]
    else:
        return uri


def get_port(uri):
    colon = uri.find(':')
    if colon != -1:
        int(uri[colon + 1:len(uri)])
    else:
        # no port given; default port is 80
        return 80


def init_tcp_conn(host_name, port):
    """
    Initializes and creates a TCP connection to host_name and port
    :param host_name: host name is a string
    :param port: port is an integer
    :return: socket to the web server that the client originally requested
    """
    real_srv_sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    real_srv_sck.bind((host_name, port))
    return real_srv_sck


def current_time():
    return time.ctime(time.time())


if __name__ == "__main":
    main()

main()
