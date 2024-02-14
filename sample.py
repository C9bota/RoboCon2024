#coding: UTF-8

#
# ATTENTION: 当サンプルプログラムを動かす場合
#    コマンドプロンプトなどでbleakパッケージをインストールしてください
#    pipコマンドでbleakをインストール
#
#    pip install bleak
#

import asyncio
import qumcum_ble as qumcum

def set_adjust_value(no):
    (_, res) = qumcum.get_init()
    initial_angles_str = res.split(',')[1:]
    print(f'initial_angles: {initial_angles}')
    cmd = "900,0" + initial_angles_str[1:6] + "0"

# デバイスに接続する
# 引数は自分のクムクムの下4桁の番号に
# 書き換えてください
qumcum.connect('8D16')
"""
(resval, resstr) = qumcum.get_info()
print(f'Get Info result 1: {resval}')
print(f'Get Info result 2: {resstr}')
(_, res) = qumcum.get_init()
print(res.split(',')[1:])
initial_angles = list(map(lambda x: int(int(x)/10), res.split(',')[1:]))
print(initial_angles)
print(qumcum.get_motor_positions())
# for i in range(len(initial_angles)):
#    qumcum.motor_adjust(i+1, initial_angles[i])

qumcum.motor_power_on(500)
for i in range(len(initial_angles)):
    qumcum.motor_set_pos(i+1, initial_angles[i])

qumcum.motor_start()
qumcum.wait(2)
print(qumcum.get_motor_positions())
qumcum.motor_power_off()
"""
# qumcum.motor_angle_time(1, 0, 1000)
(_, res) = qumcum.get_init()
initial_angles = list(map(lambda x: int(x)/10, res.split(',')[1:]))
print(f'initial_angles: {initial_angles}')

# initial_1 = int(input("Initial Value of Motor #1 > "))
# for i in range(len(initial_angles)):
#     if i == 0:
#         qumcum.motor_adjust(1, initial_1)
#     else:
#         qumcum.motor_adjust(i+1, initial_angles[i])

initial_angles = list(map(lambda x: int(x)/10, res.split(',')[1:]))
print(f'initial_angles: {initial_angles}')
(_, res) = qumcum.set_motorpower()
print(f'Result of set_motorpower: {res}')
# qumcum.motor_angle_time(7, 45, 5000)
# qumcum.motor_angle_time(1, 45, 5000)
# qumcum.motor_angle_time(1, 50, 2000)
# qumcum.motor_start()
# qumcum.motor_angle_time(1, 89, 1000)
qumcum.motor_power_on(50)
# qumcum.motor_pos_all(90, 90, 90, 90, 90, 90, 90)
qumcum.motor_set_pos(1, 90)
# qumcum.motor_angle_time(1, 90, 500)
qumcum.motor_start()
qumcum.wait(2)
"""

qumcum.motor_angle_time(1, 120, 500)
qumcum.wait(0.1)
qumcum.motor_start(50)
qumcum.wait(0.7)

qumcum.motor_angle_time(1, 60, 500)
qumcum.wait(0.1)
qumcum.motor_start(50)
qumcum.wait(0.7)

qumcum.motor_angle_time(1, 90, 500)
qumcum.wait(0.1)
qumcum.motor_start(50)
qumcum.wait(0.7)

qumcum.motor_angle_time(7, 120, 500)
qumcum.wait(0.1)
qumcum.motor_start(50)
qumcum.wait(0.7)

qumcum.motor_angle_time(7, 60, 500)
qumcum.wait(0.1)
qumcum.motor_start(50)
qumcum.wait(0.7)

qumcum.motor_angle_time(7, 90, 500)
qumcum.wait(0.1)
qumcum.motor_start(50)
qumcum.wait(0.7)
"""

qumcum.motor_power_off()
# 発話スピード変更
# qumcum.voice_speed(100)
# 発話
# qumcum.voice('ohayo---')

qumcum.end()

#
# RGB-LED
#
"""
# RGB-LED点灯(赤)
qumcum.led_on(1)
# RGB-LED消灯(赤)
qumcum.led_off(1)

# RGB-LED点灯(緑)
qumcum.led_on(2)
# RGB-LED消灯(緑)
qumcum.led_off(2)

# RGB-LED点灯(青)
qumcum.led_on(3)
# RGB-LED消灯(青)
qumcum.led_off(3)

# トーン(A4)
qumcum.sound(261, 125)
# トーン(A4)
qumcum.sound(293, 125)
# トーン(A4)
qumcum.sound(329, 125)
# トーン(A4)
qumcum.sound(349, 125)
# トーン(A4)
qumcum.sound(391, 125)
# トーン(A4)
qumcum.sound(440, 125)
# トーン(A4)
qumcum.sound(493, 125)
# トーン(A4)
#qumcum.sound(523, 125)
# トーン(A3)
qumcum.sound(130, 125)

# 発話スピード変更
qumcum.voice_speed(100)
# 発話
qumcum.voice('ohayo---')

qumcum.voice_word('suutiyomu')

# 「いちにいさんよんごろく」と言う
qumcum.voice_number(123456)
# 「えーいちにいさんしーよんごろく」と言う
qumcum.voice_numalpha('A123C456')
# 「じゅうにまんさんぜんよんひゃくごじゅうろく」と言う
qumcum.voice_numkana(123456)
# 「じゅうろっぷん」と言う
qumcum.voice_numhun(16)
# 「じゅうにふん」と言う
qumcum.voice_numhun(12)
# 「じゅうろっぽん」と言う
qumcum.voice_numhon(16)
# 「じゅうにほん」と言う
qumcum.voice_numhon(12)

# しゃべり終わるまで待つ
qumcum.wait(12)

# モーター電源ON
qumcum.motor_power_on(500)

# モーター座標指定
qumcum.motor_set_pos(4, 80)
# モーター動作開始
qumcum.motor_start(True)

# モーター座標および動作時間指定
qumcum.motor_angle_multi_time(90, 90, 90, 90, 90, 90, 90, 500)
# モーター動作開始
qumcum.motor_start(True)

# モーター座標および動作時間指定
qumcum.motor_angle_multi_time(180, 90, 90, 90, 90, 90, 0, 300)
# モーター動作開始
qumcum.motor_start(True)

# モーター座標および動作時間指定
qumcum.motor_angle_multi_time(0, 90, 90, 90, 90, 90, 180, 600)
# モーター動作開始
qumcum.motor_start(True)

qumcum.wait(2)

# モーター電源OFF
qumcum.motor_power_off()

# Qumcumから切断
qumcum.end()
"""