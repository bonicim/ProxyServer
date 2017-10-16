import socket
import time
import select
import sys
import _thread


BUFSIZE = 4096
HOST_NAME = socket.gethostname()
HOST_IP = socket.gethostbyname(HOST_NAME)
HOST_PORT = 8888
BACKLOG = 10
SLEEPYTIME = 3
HTTP_BAD_METHOD = b'HTTP/1.1 405 METHOD_NOT_ALLOWED\r\nConnection:close\r\n\r\n'
DEFAULT_CONNECTION_HEADER = b'Connection:close'
DEFAULT_HTTP_PORT = 80


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
                print('SUCCESS! Proxy server connected to client at: ', addr, ' at ', current_time(), '\n')
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
    print("HTTP Request is: ", http_req, '\n')

    print("Parsing HTTP request line...")
    time.sleep(3)
    req_line = parse_request_line(http_req)
    print("Request line is: ", req_line, '\n')

    print("Verifying that HTTP request is GET...")
    time.sleep(3)
    if not is_get_request(req_line):
        print("[*]Request from client is not a GET")
        cli_sck.sendall(HTTP_BAD_METHOD)
        sys.exit()
    else:
        print("[*]The HTTP request is a GET.", '\r\n')

    print("Verifying that URI is absolute...")
    time.sleep(3)
    verify_absolute_uri(req_line)

    print("Modifying HTTP request for web server...")
    time.sleep(3)
    mod_http_req = modify_http_request(http_req)
    print("[*]The HTTP request to be sent to the server: ", '\n', mod_http_req, '\n')

    print("Getting hostname and port...")
    time.sleep(3)
    host_port = get_hostname_port(req_line)
    print("[*]Successfully obtained hostname and port: ", host_port, '\n')

    try:
        print("Connecting to web server...", host_port[0], host_port[1])
        time.sleep(3)
        web_srv_sck = init_tcp_conn(host_port[0], host_port[1])
        print("Successful connection to host and port.", '\n')

        print("Sending modified request to web server...")
        time.sleep(3)
        web_srv_sck.sendall(mod_http_req)

        print("Receiving response...")
        time.sleep(SLEEPYTIME)
        while True:
            data = web_srv_sck.recv(BUFSIZE)
            if len(data) > 0:
                print("Sending data to client browser: ", data, '\n' )
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
    :return: byte object representation of an http request
    """
    req = b''
    while True:
        data = cli_sck.recv(BUFSIZE)
        req += data
        if req[len(req) - 4:len(req)] == b'\r\n\r\n':
            break
    return req


def parse_request_line(http_req):
    """
    Gets the request line (i.e. first line) of an HTTP request
    :param http_req is a byte object representation of an http request
    :return: string object of the request line
    """
    return http_req[:http_req.find(b'\r\n')].decode('utf-8')


def modify_http_request(http_req):
    """
    Ensures that http request uses a closed connection (HTTP version 1.0)
    and
    :param http_req: an byte object which is immutable
    :return: a byte array object representation of the modified http request
    """
    http_req_arr = convert_to_byte_array(http_req)
    http_req_arr = ensure_closed_connection(http_req_arr)
    http_req_arr = make_relative_uri(http_req_arr)
    http_req_arr = append_crlf(http_req_arr)
    return b''.join(http_req_arr)


def convert_to_byte_array(http_req):
    mod_http_req = bytearray(http_req)
    mod_http_req = mod_http_req.split(b'\r\n')
    return mod_http_req[:len(mod_http_req) - 2]


def ensure_closed_connection(http_req_arr):
    index_connection_header = get_index_connection_header(http_req_arr)
    if index_connection_header == -1:
        print("HTTP request does not have a connection header; "
              "appending connection header with value of close... ", '\r\n')
        time.sleep(3)
        http_req_arr.append(DEFAULT_CONNECTION_HEADER)
    else:
        print("Ensuring connection value is set to close...")
        time.sleep(SLEEPYTIME)
        http_req_arr[index_connection_header] = DEFAULT_CONNECTION_HEADER
        print("Current connection header is now set to: ", http_req_arr[index_connection_header], '\n')
    return http_req_arr


def make_relative_uri(http_req_arr):
    req_line = http_req_arr[0].decode('utf-8')
    url = get_url(req_line).split(":")[0]
    relative_uri = get_url_path(url)
    http_req_arr[0] = modify_url_to_relative_url(http_req_arr[0], relative_uri)
    return http_req_arr


def append_crlf(http_req_arr):
    http_req_arr = list(map(lambda b: b + b'\r\n', http_req_arr))
    http_req_arr[len(http_req_arr) - 1] += b'\r\n'
    return http_req_arr


def modify_url_to_relative_url(req_line, relative_uri):
    req_line_arr = req_line.split(b' ')
    req_line_arr[1] = relative_uri
    return b' '.join(req_line_arr)


def get_url(req_line):
    url = req_line.split(" ")[1]
    return url.split("://")[1]


def get_url_path(some_url):
    index = some_url.find('/')
    if index == -1:
        return b'/'
    else:
        return some_url[index:].encode('utf-8')


def get_index_connection_header(http_req_arr):
    for index in range(len(http_req_arr)):
        if http_req_arr[index].startswith(b'Connection'):
            return index
    return -1


def is_get_request(req_line):
    return req_line.split(' ')[0] == 'GET'


def verify_absolute_uri(req_line):
    if is_absolute_uri(req_line):
        print("[*]The requested URI is absolute.", '\n')
    else:
        print("The requested URI is NOT absolute. Proxy only supports absolute URI.")
        raise ValueError("The requested URI is NOT absolute. Proxy only supports absolute URI.")


def is_absolute_uri(req_line):
    req_uri = req_line.split(' ')
    return req_uri[1].find('http') == 0 and \
           req_uri[1].find('://') == 4 and \
           req_uri[1].find('www') == 7


def get_hostname_port(req_line):
    """
    Parses an HTTP request line to return its url and port. Assumes that
    req_line is a properly formatted request line
    :param req_line: string object of the request line
    :return: tuple consisting of a host_name (string) and a port (integer).
    """
    url = get_url(req_line)
    return get_hostname(url), get_port(url)


def get_hostname(url):
    end = url.find('/')
    if end != -1:
        return url[:end]
    else:
        return url


def get_port(url):
    colon = url.find(':')
    fwd_slash = url.find('/')
    if colon != -1:
        if fwd_slash == -1:
            return int(url[colon + 1:len(url)])
        else:
            return int(url[colon + 1:fwd_slash])
    else:
        return DEFAULT_HTTP_PORT


def init_tcp_conn(host_name, port):
    """
    Initializes and creates a TCP connection to host_name and port
    :param host_name: host name is a string
    :param port: port is an integer
    :return: socket to the web server that the client originally requested
    """
    real_srv_sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    real_srv_sck.connect((host_name, port))
    return real_srv_sck


def current_time():
    return time.ctime(time.time())


if __name__ == "__main":
    main()

main()
