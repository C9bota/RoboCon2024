import sys
import threading
import signal
import time

import network
import qumcum_ctrl

shared_flag = False
lock = threading.Lock()

def update_flag(lock):
    global shared_flag
    while True:
        remote_flag = network.get_flag()
        with lock:
            # 通信処理
            shared_flag = remote_flag
            print("update_flag(): Up Flag")

        time.sleep(15)

def exit_program(signal, frame):
    print("Exiting...")
    sys.exit(1)

threads = []

t1 = threading.Thread(target=update_flag, args=(lock, ))
threads.append(t1)
t2 = threading.Thread(target=qumcum_ctrl.qumcum_main, args=(lock, ))
threads.append(t2)
t1.start()
t2.start()

signal.signal(signal.SIGINT, exit_program)
