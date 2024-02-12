#coding: UTF-8
"""

file   : qumcum_ble.py
brief  : API for Qumcum robot communication via BLE.
date   : Created at 2022/01/27
author : N.Kameda

Copyright (c) 2022, Cammy Co.,Ltd.. All rights reserved.

"""
"""
 ATTENTION: 当パッケージを使うプログラムを動かす場合
    コマンドプロンプトなどでbleakパッケージをインストールしてください
    pipコマンドでbleakをインストール

    pip install bleak
    
"""

import time
import asyncio
from bleak import BleakScanner, BleakClient

# イベントループ
__qum_event_loop = asyncio.new_event_loop()
# 通信用デバイスオブジェクト
__qum_com_device = None
# 通信用オブジェクト
__qum_com_obj = None

class QumComBle(BleakClient):
    ROBO_TX_SERVICE  = 'ff6b1548-8fe6-11e7-abc4-cec278b6b50a'
    ROBO_RX_SERVICE  = 'ff6b1426-8fe6-11e7-abc4-cec278b6b50a'

    rx_data = ""

    __value = 0
    __dump_size = 1024 
    __received_flag = False
    __ready_flag = False
    __client = None

    def __init__(self, address_or_device):
        self.__client = BleakClient(address_or_device)
	    # R3J対応 ロボットの種別ごとに送信方法を分ける -->
        self.__robot_type = -1
	    # R3J対応 --> ロボットの種別ごとに送信方法を分ける

    # R3J対応 ロボットの種別ごとに送信方法を分ける -->
    def setRobotType(self, robot_type):
        self.__robot_type = robot_type
    # R3J対応 --> ロボットの種別ごとに送信方法を分ける

    ## @brief [関数] バイト配列の文字列変換処理
    #def __getstring(byte_data):
    #    """
    #    _getstring
    #    Get String values from binary data
    #    """
    #    data = str(byte_data, 'utf-8')
    #    #data = byte_data.decode('ascii')
    #    data2 = data.replace("\r\n", "")
    #    return data

    def _notification_handler(self, sender, data):
        #global value
        #global rx_data
        #global data_dump_size
        #global ready_flag
        #global received_flag
        
        #rx_data.append(int.from_bytes(data, byteorder="big"))
        if len(self.rx_data) >= self.__dump_size:
            self.rx_data = ""

        if(data[2] == 0x40): # カンマの次が'@'は以降がバイナリデータ
            self.__received_flag = True
            temp = '#,@'
            state = int(data[3])
            battery_level = int(data[4])
            rip = int.from_bytes(data[5:7], 'big')
            mic = int.from_bytes(data[7:9], 'big')
            #print("State=" + str(state) + " BatteryLevel=" + str(battery_level) + " Rip=" + str(rip) + " Mic=" + str(mic))
            temp = temp + "," + str(state) + "," + str(battery_level) + "," + str(rip) + "," + str(mic)
        else:
            temp = data.decode()

        if(temp.find('$,') == 0):
            # 途中の電文(続きがある)
            temp = temp[2:]
        elif(temp.find('#,') == 0):
            # 最後の電文
            temp = temp[2:]
            #print(temp)
            self.__received_flag = True
        
        if('#READY' in temp):
            print("Received ready!!")
            self.__ready_flag = True

        self.rx_data = self.rx_data + temp
        if(self.__received_flag):
            #print(self.rx_data)
            self.__value = 0

    async def connect(self):
        #global rx_data
        #global ready_flag
        #global received_flag
        try:
            print("Start connect.")
            # 通信用データの初期化
            self.__received_flag = False
            self.__ready_flag = False
            self.rx_data = ""
            time.sleep(0.05)
            # デバイスと接続
            await self.__client.connect()
            # 通知(受信イベント)ハンドラの設定
            await self.__client.start_notify(self.ROBO_RX_SERVICE, self._notification_handler)
            # 起動完了('#READY'受信)待ち
            print("Waiting robot ready...")
            count = 120		# R3J対応でタイムアウトまでの時間を延ばしました
            self.__ready_flag = False
            while(self.__ready_flag != True):
                await asyncio.sleep(0.1)
                # TODO: ここでタイムアウト処理が必要
                count = count - 1
                if(0 >= count):
                    break
            if((self.__ready_flag == False) and (0 >= count)):
                print("Connect failure(time out).")
                return -1

            print("Wait end.")

        except Exception as e:
            print(e)

        return 0

    async def disconnect(self):
        print("Start disconnect.")
        await self.__client.disconnect()
        await asyncio.sleep(.2)
        print("Disconnected.")

    async def _send_command(self, cmd):
        #global rx_data
        #global received_flag

        try:
            #print("Command: " + cmd)
            # R3J対応 コマンドの分割送信ができるようにする
            if cmd[0] != '$':
                cmd = cmd + "\x0a"

            write_value = bytes(cmd, encoding='utf-8', errors='replace')

            # 送信前の通信用データのクリア
            self.__received_flag = False
            self.rx_data = ""
            # コマンドを送信する
            # R3J対応 bleakライブラリのバージョンアップで引数を追加(ないとR3Jでは受信を検知できない)
            #await self.__client.write_gatt_char(self.ROBO_TX_SERVICE, write_value)
            await self.__client.write_gatt_char(self.ROBO_TX_SERVICE, write_value, True)
            return 0
        except Exception as e:
            print(e)
            return -1
    
    # R3J対応 ロボットの種別ごとに送信方法を分ける -->
    # R3J専用送信処理
    async def send_command_r3j(self, cmd):
        sep_length = 18
        msg = cmd
        # 電文を19文字ごとに区切って送信する
        while(len(msg) > sep_length) :
            tmp = msg[:sep_length]
            msg = msg[sep_length:]
            await self._send_command('$' + tmp)
        return await self._send_command('#' + msg)

    # R321J用送信処理(通常はこちらを使う)
    async def send_command_r321j(self, cmd):
        return await self._send_command(cmd)

    async def send_command(self, cmd):
        if self.__robot_type == 0:
            # R3Jの場合
            return await self.send_command_r3j(cmd)
        elif self.__robot_type == 1:
            # R321Jの場合
            return await self.send_command_r321j('#' + cmd)
        else:
            print("ERROR: Unknown robot type")
            return -1
    # R3J対応 -->ロボットの種別ごとに送信方法を分ける

    async def wait_response(self):
        #global rx_data
        #global received_flag

        try:
            # 応答待ち
            while(self.__received_flag != True):
                await asyncio.sleep(0.1)
                # TODO: ここでタイムアウト処理が必要
            # レスポンスを取得する
            return self.rx_data
        except Exception as e:
            print(e)

    async def send_recv_command(self, cmd, wait_resp = False):
        try:
            # コマンド送信
            # 送信に失敗した場合は応答待ちはしない
            if(await self.send_command(cmd) != 0):
                return -1

            if(wait_resp == True):
                # 応答待ち
                return await self.wait_response()
            
            return "ok"
        except Exception as e:
            print(e)

def detection_callback(device, advertisement_data):
    #if ('QUMCUM32' in str(device.name).upper()) or ('R3J' in str(device.name).upper()):
        ## R321JかR3Jが見つかった場合
        #print(device.address, "RSSI:", device.rssi, advertisement_data)
        return

async def found_ble_device(name):
	# bleakライブラリのバージョンアップにともなう変更
    #scanner = BleakScanner()
    #scanner.register_detection_callback(detection_callback)
    scanner = BleakScanner(detection_callback)

    # スキャン時間
    scan_time_sec = 5.0

    print('Start found robot: ' + name)
    print('Start scan scan time=' + str(scan_time_sec) + "(sec)")
    await scanner.start()
    #await asyncio.sleep(5.0)
    await asyncio.sleep(scan_time_sec)
    await scanner.stop()
    print('End scan')

    for d in scanner.discovered_devices:
        if ('QUMCUM32' in str(d.name).upper()) or ('R3J' in str(d.name).upper()):
            #print(d)
            # R321JかR3Jが見つかった場合
            ln = len(name)
            ld = len(d.name)
            if (name == d.name[(ld - ln):ld]):
                print('Found robot: ' + name)
                return d

    print('ERROR: Not found robot: ' + name)

    return None

def search_device(event_loop, name):
    return event_loop.run_until_complete(found_ble_device(name))

def __qum_function(cmd, wait_resp = False):
    res = __qum_event_loop.run_until_complete(__qum_com_obj.send_recv_command(cmd, wait_resp))
    print("Receive data: " + res)
    return res

#--------------------------------------
# _getstring
#--------------------------------------
def _getstring(byte_data):
    data = str(byte_data, 'utf-8')
    data2 = data.replace("\r\n", "")
    return data2

#--------------------------------------
# get_lib_ver
#--------------------------------------
def get_lib_ver():
    """
    ライブラリのバージョンを取得する

    Args:
        なし

    Returns:
        str: バージョンを表す文字列(1.0.0.1など)

    """
    return "1.0.1.1"

#--------------------------------------
# get_lasterror
#--------------------------------------
def get_lasterror():
    """
    API実行時の最終エラーコードを取得する

    Args:
        なし

    Returns:
        int: 処理結果(0:成功、0以外:エラー)

    """
    return

#--------------------------------------
# wait
#--------------------------------------
def wait(time_sec):
    """
    一定時間待つ(1の場合1秒)、time.sleepを呼ぶだけです

    Args:
        time_sec: 待ち時間(単位:秒)

    Returns:
        int: 処理結果(0:成功、0以外:エラー)

    """
    time.sleep(time_sec)
    return

#
# R3J対応 以降ロボットへの送信コマンドの先頭の'#'は
#         送信処理内で自動付加するように変更しました
#
#--------------------------------------
# connect
#--------------------------------------
def connect( name ):
    """
    Qumcumと接続し通信を開始する

    Args:
        name (str): 接続用識別子

    Returns:
        int: 処理結果(0:成功、0以外:エラー)

    """
    global __qum_event_loop
    global __qum_com_obj

    try:
        device = search_device(__qum_event_loop, name)
        if(not device):
            return -1
        __qum_com_obj = QumComBle(device)
        if(not __qum_com_obj):
            return -1
        
	    # R3J対応 ロボットの種別ごとに送信方法を分ける -->
        if ('QUMCUM32' in str(device.name).upper()):
            # R321Jの場合
            #print("Robot type is R321J")
            __qum_com_obj.setRobotType(1)
        elif ('R3J' in str(device.name).upper()):
            # R3Jの場合
            #print("Robot type is R3J")
            __qum_com_obj.setRobotType(0)
	    # R3J対応 --> ロボットの種別ごとに送信方法を分ける

        __qum_event_loop.run_until_complete(__qum_com_obj.connect())
        ret = 0
    except:
        ret = -1

    return ret

#--------------------------------------
# end
#--------------------------------------
def end():
    """
    Qumcumとの通信を終了する

    Args:
        なし

    Returns:
        int: 処理結果(0:成功、0以外:エラー)

    """
    global __qum_event_loop
    global __qum_com_obj

    try:
        __qum_event_loop.run_until_complete(asyncio.sleep(0.5))
        __qum_event_loop.run_until_complete(__qum_com_obj.disconnect())
        ret = 0
    except:
        ret = -1

    return ret

#--------------------------------------
# get_sensor_value
#--------------------------------------
def get_sensor_value():
    """
    超音波センサ計測値を取得する
    直前のコマンド実行結果から保持した値です。

    Args:
        なし

    Returns:
        int: 処理結果(0:成功、0以外:エラー)
        str: 取得値(処理結果が0:成功の時のみ)

    """
    try:
        # コマンドを送信して実行させる
        res = __qum_function("140", True)
        res1 = res.split(',')
        ret = 0, res1[3]
    except:
        ret = -1, "NG"

    return ret

#--------------------------------------
# get_mic_value
#--------------------------------------
def get_mic_value():
    """
    マイク計測値を取得する
    直前のコマンド実行結果から保持した値です。

    Args:
        なし

    Returns:
        int: 処理結果(0:成功、0以外:エラー)
        str: 取得値(処理結果が0:成功の時のみ)

    """
    try:
        # コマンドを送信して実行させる
        res = __qum_function("140", True)
        res1 = res.split(',')
        ret = 0, res1[4]
    except:
        ret = -1, "NG"

    return ret

#--------------------------------------
# get_motor_power
#--------------------------------------
def get_motor_power():
    """
    モーター電源状態を取得する
    直前のコマンド実行結果から保持した値です。

    Args:
        なし

    Returns:
        int: 処理結果(0:成功、0以外:エラー)
        str: 取得値(処理結果が0:成功の時のみ)

    """
    try:
        res = __qum_function("140", True)
        res1 = res.split(',')
        ret = 0, res1[2]
    except:
        ret = -1, "NG"

    return ret

#--------------------------------------
# get_motor_position
#--------------------------------------
def get_motor_position(no):
    """
    モーター座標値を取得する(1軸分のみ)
    直前のコマンド実行結果から保持した値です。

    Args:
        no (int): モーターの番号(1 ~ 7)

    Returns:
        int: 処理結果(0:成功、0以外:エラー)
        str: 取得値(処理結果が0:成功の時のみ)

    """
    try:
        index = no - 1
        res = __qum_function("140", True)
        ret = 0, res
    except:
        ret = -1, "NG"

    return ret

#--------------------------------------
# get_motor_positions
#--------------------------------------
def get_motor_positions():
    """
    モーター座標値を取得する(7軸分すべて)
    直前のコマンド実行結果から保持した値です。

    Args:
        なし

    Returns:
        int: 処理結果(0:成功、0以外:エラー)
        str: 取得値(処理結果が0:成功の時のみ)
                1: モーター1の角度(0 ~ 180)
                2: モーター2の角度(55 ~ 125)
                3: モーター3の角度(55 ~ 125)
                4: モーター4の角度(0 ~ 180)
                5: モーター5の角度(55 ~ 125)
                6: モーター6の角度(55 ~ 125)
                7: モーター7の角度(0 ~ 180)

    """
    try:
        res = __qum_function("140", True)
        ret = 0, res
    except:
        ret = -1, "NG"

    return ret

#--------------------------------------
# set_motorpower
#--------------------------------------
def set_motorpower():
    """
    モーター電源の供給を再開する

    Args:
        なし

    Returns:
        int: 処理結果(0:成功、0以外:エラー)
        str: 取得値(処理結果が0:成功の時のみ)

    """
    try:
        res = __qum_function("803", True)
        ret = 0, res
    except:
        ret = -1, "NG"

    return ret

#--------------------------------------
# get_init
#--------------------------------------
def get_init():
    """
    モーター初期位置を取得する

    Args:
        なし

    Returns:
        int: 処理結果(0:成功、0以外:エラー)
        str: 取得値(処理結果が0:成功の時のみ)

    Note:
        'INI,869,920,820,899,800,810,820'左記のようなフォーマットで格納され
        INI,<モーター1の初期位置>,<モーター2の初期位置>, ... ,<モーター7の初期位置>
        となり、それぞれ1/10度単位の3桁の数値がbuffに格納されます

    """
    try:
        res = __qum_function("804", True)
        ret = 0, res
    except:
        ret = -1, "NG"

    return ret

#--------------------------------------
# get_info
#--------------------------------------
def get_info():
    """
    ロボットの基本情報を取得する

    Args:
        なし

    Returns:
        int: 処理結果(0:成功、0以外:エラー)
        str: 取得値(処理結果が0:成功の時のみ)

    Note:
        'INF,Qumcum,CRETARIA,2.01.03A,001EC066DE60'左記のようなフォーマットで格納され
        INF,Qumcum,CRETARIA,<ファームウェアバージョン>,<ロボットのMACアドレス>がbuffに格納されます

    """
    try:
        res = __qum_function("805", True)
        ret = 0, res
    except:
        ret = -1, "NG"

    return ret

#--------------------------------------
# get_position
#--------------------------------------
def get_position():
    """
    モーター座標値を取得する

    Args:
        なし

    Returns:
        int: 処理結果(0:成功、0以外:エラー)
        str: 取得値(処理結果が0:成功の時のみ)

    Note:
        【結果は検討中】

    """
    try:
        res = __qum_function("142", True)
        ret = 0, res
    except:
        ret = -1, "NG"

    return ret

#--------------------------------------
# motor_adjust
#--------------------------------------
def motor_adjust(no, val):
    """
    モーター調整値を設定する

    Args:
        no (int): モーターの番号(1:右手、2:右足、3:右足首、4:頭、5:左足首、6:左足、7:左手)
        val: モーター調整値(1/10度単位)

    Returns:
        int: 処理結果(0:成功、0以外:エラー)

    """
    try:
        index = no - 1
        cmd = "810," + str(index) + "," + str(val).zfill(4)
        res = __qum_function(cmd, True)
        ret = 0, res
    except:
        ret = -1, "NG"

    return ret

#--------------------------------------
# led_on
#--------------------------------------
def led_on(color):
    """
    RGB-LEDで指定した色をON(点灯)させる

    Args:
        color (int): 1:赤、2:青、3:緑

    Returns:
        int: 処理結果(0:成功、0以外:エラー)

    """
    try:
        cmd = "100," + str(color)
        print("cmd:" + cmd)
        res = __qum_function(cmd, True)
        ret = 0, res
    except:
        ret = -1, "NG"

    return ret

#--------------------------------------
# led_off
#--------------------------------------
def led_off(color):
    """
    RGB-LEDで指定した色をOFF(消灯)させる

    Args:
        color (int): 1:赤、2:青、3:緑

    Returns:
        int: 処理結果(0:成功、0以外:エラー)

    """
    try:
        cmd = "101," + str(color)
        print("cmd:" + cmd)
        res = __qum_function(cmd, True)
        ret = 0, res
    except:
        ret = -1, "NG"

    return ret

#--------------------------------------
# sound
#--------------------------------------
def sound(freq, time_ms):
    """
    指定した時間(msec)だけ指定した周波数の音を発生させる

    Args:
        freq (int): 出力させる周波数
        time_ms (float): 出力する時間(単位:msec)

    Returns:
        int: 処理結果(0:成功、0以外:エラー)

    """
    try:
        cmd = "110," + str(freq).zfill(5) + "," + str(time_ms).zfill(4)
        print("cmd:" + cmd)
        res = __qum_function(cmd, True)
        ret = 0, res
    except:
        ret = -1, "NG"

    return ret

#--------------------------------------
# voice_speed
#--------------------------------------
def voice_speed(speed):
    """
    発話する速度を指定する

    Args:
        speed (int): 発話速度(30-300)

    Returns:
        int: 処理結果(0:成功、0以外:エラー)

    """
    try:
        cmd = "120," + str(speed).zfill(3)
        print("cmd:" + cmd)
        res = __qum_function(cmd, True)
        ret = 0, res
    except:
        ret = -1, "NG"

    return ret

#--------------------------------------
# voice
#--------------------------------------
def voice(words):
    """
    発話する

    Args:
        words (str): 発話させる言葉(ローマ字読み)

    Returns:
        int: 処理結果(0:成功、0以外:エラー)

    """
    try:
        cmd = "121," + str(words)
        print("cmd:" + cmd)
        res = __qum_function(cmd, True)
        ret = 0, res
    except:
        ret = -1, "NG"

    return ret


#--------------------------------------
# voice_word
#--------------------------------------
def voice_word(words):
    """
    発話する

    Args:
        words (str): 発話させる言葉(ローマ字読み)

    Returns:
        int: 処理結果(0:成功、0以外:エラー)

    """
    return voice(words)

#--------------------------------------
# voice_number
#--------------------------------------
def voice_number(number):
    """
    数値を数字としてそのまま発話する

    Args:
        number (int): 発話させる数値

    Returns:
        int: 処理結果(0:成功、0以外:エラー)

    """
    try:
        words = "<NUM VAL=" + str(number) + ">"
        cmd = "121," + str(words)
        print("cmd:" + cmd)
        res = __qum_function(cmd, True)
        ret = 0, res
    except:
        ret = -1, "NG"

    return ret

#--------------------------------------
# voice_numalpha
#--------------------------------------
def voice_numalpha(num_str):
    """
    数値を数値文字列としてそのまま発話する

    Args:
        number (str): 発話させる数値を表現した文字列

    Returns:
        int: 処理結果(0:成功、0以外:エラー)

    """
    try:
        words = "<ALPHA VAL=" + str(num_str) + ">"
        cmd = "121," + str(words)
        print("cmd:" + cmd)
        res = __qum_function(cmd, True)
        ret = 0, res
    except:
        ret = -1, "NG"

    return ret

#--------------------------------------
# voice_numkana
#--------------------------------------
def voice_numkana(number):
    """
    数値を桁を含めて発話する

    Args:
        number (int): 発話させる数値

    Returns:
        int: 処理結果(0:成功、0以外:エラー)

    """
    try:
        words = "<NUMK VAL=" + str(number) + ">"
        cmd = "121," + str(words)
        print("cmd:" + cmd)
        res = __qum_function(cmd, True)
        ret = 0, res
    except:
        ret = -1, "NG"

    return ret

#--------------------------------------
# voice_numhun
#--------------------------------------
def voice_numhun(number):
    """
    数値を「〇〇分」として発話する

    Args:
        number (int): 発話させる数値

    Returns:
        int: 処理結果(0:成功、0以外:エラー)

    """
    try:
        words = "<NUMK VAL=" + str(number) + " COUNTER=hun>"
        cmd = "121," + str(words)
        print("cmd:" + cmd)
        res = __qum_function(cmd, True)
        ret = 0, res
    except:
        ret = -1, "NG"

    return ret

#--------------------------------------
# voice_numhon
#--------------------------------------
def voice_numhon(number):
    """
    数値を「〇〇本」として発話する

    Args:
        number (int): 発話させる数値

    Returns:
        int: 処理結果(0:成功、0以外:エラー)

    """
    try:
        words = "<NUMK VAL=" + str(number) + " COUNTER=hon>"
        cmd = "121," + str(words)
        print("cmd:" + cmd)
        res = __qum_function(cmd, True)
        ret = 0, res
    except:
        ret = -1, "NG"

    return ret



#--------------------------------------
# motor_power_on
#--------------------------------------
def motor_power_on(motor_time_ms):
    """
    モーター電源をONにする

    Args:
        motor_time_ms (int): 初期モーター動作時間(単位:msec)

    Returns:
        int: 処理結果(0:成功、0以外:エラー)

    """
    try:
        cmd = "130"
        print("cmd:" + cmd)
        res = __qum_function(cmd, True)
        time.sleep(0.3)	# R3J対応 コマンド送信に間をおく
        cmd = "133,9," + str(motor_time_ms).zfill(4)
        print("cmd:" + cmd)
        res = __qum_function(cmd, True)
        ret = 0, res
    except:
        ret = -1, "NG"

    return ret

#--------------------------------------
# motor_power_off
#--------------------------------------
def motor_power_off():
    """
    モーター電源をOFFにする

    Args:
        なし

    Returns:
        int: 処理結果(0:成功、0以外:エラー)

    """
    try:
        cmd = "131"
        print("cmd:" + cmd)
        res = __qum_function(cmd, True)
        ret = 0, res
    except:
        ret = -1, "NG"

    return ret

#--------------------------------------
# motor_set_pos
#--------------------------------------
def motor_set_pos(no, pos):
    """
    モーターを指定した角度(絶対位置)に移動する

    Args:
        no (int): モーターの番号(1:右手、2:右足、3:右足首、4:頭、5:左足首、6:左足、7:左手)
        pos (int): モーターの角度(絶対位置)

    Returns:
        int: 処理結果(0:成功、0以外:エラー)

    Warning:この関数だけではモーターは動きません。
         動かすには'motor_start'関数をコールしてください

    """
    try:
        index = no - 1
        cmd = "132," + str(index) + "," + str(pos).zfill(3)
        print("cmd:" + cmd)
        res = __qum_function(cmd, True)
        ret = 0, res
    except:
        ret = -1, "NG"

    return ret

#--------------------------------------
# motor_start
#--------------------------------------
def motor_start(no_wait=False):
    """
    モーターを指定した角度(絶対位置)に移動させる

    Args:
        なし

    Returns:
        int: 処理結果(0:成功、0以外:エラー)

    """
    try:
        cmd = "134"
        if(no_wait):
            cmd = cmd + ",1";
        else:
            cmd = cmd + ",0";
        print("cmd:" + cmd)
        res = __qum_function(cmd, True)
        ret = 0, res
    except:
        ret = -1, "NG"

    return ret

#--------------------------------------
# motor_pos_all
#--------------------------------------
def motor_pos_all( pos1, pos2, pos3, pos4, pos5, pos6, pos7):
    """
    全モーター(7つ)の角度をセットする

    Args:
        pos1 (int): モーター1の角度(0 ~ 180)
        pos2 (int): モーター2の角度(55 ~ 125)
        pos3 (int): モーター3の角度(55 ~ 125)
        pos4 (int): モーター4の角度(0 ~ 180)
        pos5 (int): モーター5の角度(55 ~ 125)
        pos6 (int): モーター6の角度(55 ~ 125)
        pos7 (int): モーター7の角度(0 ~ 180)

    Returns:
        int: 処理結果(0:成功、0以外:エラー)

    Warning:この関数だけではモーターは動きません。
         動かすには'motor_start'関数をコールしてください

    """
    try:
        cmd = "136," + str(pos1).zfill(3) + ","
        cmd = cmd + str(pos2).zfill(3) + ","
        cmd = cmd + str(pos3).zfill(3) + ","
        cmd = cmd + str(pos4).zfill(3) + ","
        cmd = cmd + str(pos5).zfill(3) + ","
        cmd = cmd + str(pos6).zfill(3) + ","
        cmd = cmd + str(pos7).zfill(3)
        print("cmd:" + cmd)
        res = __qum_function(cmd, True)
        ret = 0, res
    except:
        ret = -1, "NG"

    return ret

#--------------------------------------
# motor_angle_time
#--------------------------------------
def motor_angle_time(no, pos, motor_time):
    """
    モーターの角度(絶対位置)、動作時間を指定する

    Args:
        no (int): モーターの番号(1 ~ 7)
        pos (int): モーターの角度(0 ~ 180、no=2,3,5,6 は 55 ~ 125)
        motor_time (int): モーターの動作時間

    Returns:
        int: 処理結果(0:成功、0以外:エラー)

    Warning:この関数だけではモーターは動きません。
         動かすには'motor_start'関数をコールしてください

    """
    try:
        index = no - 1
        cmd = "150," + str(index) + "," + str(pos).zfill(3) + "," + str(motor_time).zfill(4)
        print("cmd:" + cmd)
        res = __qum_function(cmd, True)
        ret = 0, res
    except:
        ret = -1, "NG"

    return ret

#--------------------------------------
# motor_angle_multi_time
#--------------------------------------
def motor_angle_multi_time(pos1, pos2, pos3, pos4, pos5, pos6, pos7, motor_time):
    """
    全モーター(7つ)の角度をセットする

    Args:
        pos1 (int): モーター1の角度(0 ~ 180)
        pos2 (int): モーター2の角度(55 ~ 125)
        pos3 (int): モーター3の角度(55 ~ 125)
        pos4 (int): モーター4の角度(0 ~ 180)
        pos5 (int): モーター5の角度(55 ~ 125)
        pos6 (int): モーター6の角度(55 ~ 125)
        pos7 (int): モーター7の角度(0 ~ 180)
        motor_time (int): モーターの動作時間

    Returns:
        int: 処理結果(0:成功、0以外:エラー)

    Warning:この関数だけではモーターは動きません。
         動かすには'motor_start'関数をコールしてください

    """
    try:
        cmd = "151," + str(pos1).zfill(3) + ","
        cmd = cmd + str(pos2).zfill(3) + ","
        cmd = cmd + str(pos3).zfill(3) + ","
        cmd = cmd + str(pos4).zfill(3) + ","
        cmd = cmd + str(pos5).zfill(3) + ","
        cmd = cmd + str(pos6).zfill(3) + ","
        cmd = cmd + str(pos7).zfill(3) + ","
        cmd = cmd + str(motor_time).zfill(4)
        print("cmd:" + cmd)
        res = __qum_function(cmd, True)
        ret = 0, res
    except:
        ret = -1, "NG"

    return ret



# end of file
