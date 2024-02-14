import sys
import threading
import signal

import flag_op
import qumcum_ctrl

def exit_program(signal, frame):
    print("Exiting...")
    qumcum_ctrl.qumcum_terminate()
    sys.exit(1)

threads = []

t1 = threading.Thread(target=flag_op.update_flag)
threads.append(t1)
t2 = threading.Thread(target=qumcum_ctrl.qumcum_main)
threads.append(t2)
t1.start()
t2.start()

signal.signal(signal.SIGINT, exit_program)
