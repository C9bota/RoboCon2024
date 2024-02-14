#coding: UTF-8

import qumcum_ble as qumcum

ID = '8D16'
sales_pitch = [
    "irasshaimase--",
    "oyatude hitoyasumi simasenka"
]

def check_flag(lock):
    """
    共有メモリ上のフラグの値を返す
    """
    global shared_flag
    with lock:
        return shared_flag

def down_flag(lock):
    """
    共有メモリ上のフラグを見て、TrueであればFalseにする
    Falseであればなにもしない
    """
    global shared_flag
    with lock:
        if shared_flag:
            shared_flag = False
            print("check_flag(): Down Flag")

def qumcum_init(id=''):
    """iniialize"""
    qumcum.connect(id)
    qumcum.voice_speed(80)

def qumcum_terminate():
    """Terminate"""
    qumcum.motor_power_off()
    qumcum.end()

def get_initial_angle():
    (ret, res) = qumcum.get_init()
    if ret == 0:
        initial_angles = list(map(lambda x: int(x)/10, res.split(',')[1:]))
    else:
        initial_angles = list()
    return initial_angles
    # print(f'initial_angles: {initial_angles}')

def move_then_stop(duration_walk=1):
    """
    前進を開始し、セリフを喋る。
    指定した時間以上は動き続け、その間にセリフを喋る

    Args:
        duration_walk (int): 前進する時間 (sec)
    """
    qumcum.set_motorpower()
    qumcum.motor_power_on(50)
    qumcum.motor_pos_all(90, 90, 90, 90, 90, 90, 90)
    qumcum.motor_start(False)
    qumcum.voice_word(sales_pitch[0])
    qumcum.voice_word(sales_pitch[1])
    qumcum.wait(duration_walk)
    qumcum.motor_power_off()
    qumcum.wait(0.7)

def stop_and_speech(duration_stop=1):
    """
    停止したまま、セリフを喋る。
    指定した時間以上止まっている
    
    Args:
        duration_stop (int): 停止する時間 (sec)
    """
    qumcum.voice_word(sales_pitch[0])
    qumcum.wait(duration_stop)

def qumcum_main(lock):
    """
    Qumcum制御メイン
    """
    qumcum_init(ID)     # 初期化
    try:
        while True:     # メイン無限ループ (Outer)
            while True: # メイン無限ループ (Inner)
                if check_flag(lock):
                    break
                move_then_stop(5)
                if check_flag(lock):
                    break
                stop_and_speech(5)
            down_flag(lock)
    finally:
        qumcum_terminate()  # 終了処理

if __name__ == "__main__":
    qumcum_init(ID)
    move_then_stop(10)
    qumcum_terminate()