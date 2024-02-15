# Qumcumを歩かせるサンプル
# web版実行環境(https://personal.qumcum.com/python/editor/python-live/)
# のみで検証済み
# 注意事項：PCから実行させたい場合，
#   1. Qumcumへの接続処理
#   2. モータのON／OFF処理
# を入れる必要がある

import qumcum_ble as qumcum

# 定数 --------------------
val = 1 #次の動きに行くまでの待機時間

# 各サーボモータの番号 -------
kubi = 4
asi_L = 5
asi_R = 3
momo_L = 6
momo_R = 2


# うごく
def move(part, pos, interval):
    # モーター座標指定
    qumcum.motor_set_pos(part, pos)
    # モーター動作開始
    qumcum.motor_start(True)
    qumcum.wait(interval)

# 右足で立つ
def stand_R(interval):
    move(asi_L, 90, val)
    move(asi_R, 90, val)
    move(asi_L, 60, val)
    move(asi_R, 110, val)

# 左足で立つ
def stand_L(interval):
    move(asi_R, 90, val)
    move(asi_L, 90, val)
    move(asi_R, 120, val)
    move(asi_L, 70, val)

# 2歩進む
def walk_2steps(val):
    # 右足で立つ
    stand_R(val)

    # 左足を前に
    move(momo_R, 68, val)
    move(momo_L, 90, val)

    # 左足で立つ
    stand_L(val)

    # 右足を前に
    move(momo_L, 110, val)
    move(momo_R, 90, val)


# メイン処理 ---------------------------
# 歩く
walk_2steps(val)
walk_2steps(val)
walk_2steps(val)
walk_2steps(val)
walk_2steps(val)
walk_2steps(val)

# 終了動作 -----------------------------
# 真っ直ぐにする
move(asi_L, 90, val)
move(asi_R, 90, val)
move(momo_R, 90, val)
move(momo_L, 90, val)
