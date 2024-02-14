import threading
import time
import network

shared_flag = False
lock = threading.Lock()

def update_flag():
    global shared_flag
    while True:
        remote_flag = network.get_flag()
        with lock:
            # 通信処理
            shared_flag = remote_flag
            print("update_flag(): Up Flag")

        time.sleep(15)

def check_flag():
    """
    共有メモリ上のフラグの値を返す
    """
    global shared_flag
    with lock:
        return shared_flag

def down_flag():
    """
    共有メモリ上のフラグを見て、TrueであればFalseにする
    Falseであればなにもしない
    """
    global shared_flag
    with lock:
        if shared_flag:
            shared_flag = False
            print("check_flag(): Down Flag")