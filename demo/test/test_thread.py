import threading


def run():
    print(threading.current_thread().name)


if __name__ == '__main__':
    t1 = threading.Thread(target=run)
    t1.start()
