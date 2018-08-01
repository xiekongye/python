import socket


def get_host(ip):
    try:
        result = socket.gethostbyaddr(ip)
        if result:
            return result[0], None
    except socket.herror as e:
        return None, e.message


def main():
    print(get_host('127.0.0.1'))


if __name__ == '__main__':
    main()
