#coding: UTF-8

import qumcum_ble as qumcum

ID = '8D16'
sales_pitch = [
    "irasshaimase--",
    "oyatude hitoyasumi simasenka"
]

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

def move_then_stop(duration=1):
    """
    前進を開始し、セリフを喋る。
    指定した時間の間にセリフを喋り、前進する
    
    Args:
        duration (int): 前進する時間
    """
    qumcum.set_motorpower()
    qumcum.motor_power_on(50)
    qumcum.motor_pos_all(90, 90, 90, 90, 90, 90, 90)
    qumcum.motor_start(False)
    qumcum.voice_word(sales_pitch[0])
    qumcum.voice_word(sales_pitch[1])
    qumcum.wait(duration)
    qumcum.motor_power_off()
    qumcum.wait(0.7)

if __name__ == "__main__":
    qumcum_init(ID)
    move_then_stop(10)
    qumcum_terminate()