import asyncio, websockets
from snownlp import SnowNLP
import sympy as sp
import threading, queue, multiprocessing
import Vts
import VoiceVox
import json
import random
import time


# 别乱填，全局变量
action_file = ""
emotion_data = 0
# 创建锁
lock = threading.Lock()

# 正弦波函数，负责待机时动作,amplitude 振幅,frequency 频率,phase_shift 相位差,shifting 初始偏移
def waiting_sport(time, amplitude = 2, frequency = 0.6, shifting = 0):
    # 定义符号变量
    x = sp.symbols('x')

    # 计算正弦波函数的表达式，振幅为amplitude，频率为1 Hz
    sin_expr = amplitude * sp.sin(2 * sp.pi * frequency * x) + shifting

    # 计算正弦波函数的值，并将结果精确到8位小数
    value = sin_expr.subs(x, time).evalf(8)

    return float(value)

# 头，眼，眉，以及微笑
async def waiting_model(time):
    FaceAngleZ = waiting_sport(time,amplitude=2.5)
    FaceAngleY = waiting_sport(time,amplitude=1)
    FaceAngleX = waiting_sport(time,amplitude=1.5, frequency = 0.25)
    Brows = waiting_sport(time,amplitude=0.025, frequency = 0.5, shifting=0.55)
    EyeOpenLeft = EyeOpenRight = waiting_sport(time, amplitude=10, frequency = 0.5, shifting = 10)
    EyeRightX = waiting_sport(time, amplitude=0.1, frequency = 0.5)
    MouthSmile = waiting_sport(time, amplitude=0.08, frequency = 0.5, shifting=0.6)


    parameter_values = [{"id": "FaceAngleX", "value": FaceAngleX}, 
                        {"id": "FaceAngleY", "value": FaceAngleY}, 
                        {"id": "FaceAngleZ", "value": FaceAngleZ},
                        {"id": "EyeOpenLeft", "value": EyeOpenLeft},
                        {"id": "EyeOpenRight", "value": EyeOpenRight},
                        {"id": "EyeRightX", "value": EyeRightX},
                        {"id": "Brows", "value": Brows},
                        {"id": "MouthSmile", "value": MouthSmile}]
    return parameter_values


async def vtube_run():
    global action_file
    # 连接上服务器,并初始化
    try:
        websocket = await websockets.connect('ws://127.0.0.1:8001')
        await Vts.init(websocket)
        print("[VTS 初始化完成]")
    except Exception:
        print("[VTS 无法连接]")
        return

    time = 0    # 超级重要的时间参数
    while True:
        if action_file != "":
            if emotion_data >= 0.6:  # active状态
                Brows_shifting = 0.55 + ((emotion_data - 0.6)/4)
                MouthSmile_shifting = 0.6 + ((emotion_data - 0.6)/2)
                if emotion_data >= 0.8:
                    await Vts.vtube_hotkeys(websocket, "脸红")
            elif 0.4 < emotion_data < 0.6:    # neutral状态
                Brows_shifting = 0.55
                MouthSmile_shifting = 0.6
            elif emotion_data <= 0.4:    # negative状态
                Brows_shifting = 0.5 - ((0.4 - emotion_data)/4)
                MouthSmile_shifting = 0.5 - ((0.4 - emotion_data)/2)
                if emotion_data <= 0.2:
                    await Vts.vtube_hotkeys(websocket, "脸黑")

            file_now = action_file
            with open(file_now, "r") as config_file:     # 读文件
                data = json.load(config_file)
            time = 0
            for i in range(len(data)):
                Brows = waiting_sport(time,amplitude=0.025, frequency = 0.5, shifting=Brows_shifting)
                MouthSmile = waiting_sport(time, amplitude=0.08, frequency = 0.5, shifting=MouthSmile_shifting)
                parameter_values = data[i]
                parameter_values.append({"id": "Brows", "value": Brows})
                parameter_values.append({"id": "MouthSmile", "value": MouthSmile})
                await Vts.vtube_control(websocket, parameter_values)
                await asyncio.sleep(0.02)
                time += 0.02
                if file_now != action_file:
                    await Vts.parameter_values_homing(websocket, parameter_values)
                    break
            if emotion_data >= 0.8:
                await Vts.vtube_hotkeys(websocket, "脸红")
            if emotion_data <= 0.4:
                await Vts.vtube_hotkeys(websocket, "脸黑")
            time = 0
            if file_now == action_file:
                special_probability = random.randint(0,100)
                if special_probability <= 60 and emotion_data >= 0.4:     # 随机触发wink
                    wink_sport = random.randint(2,2)
                    file_now = f"./sport/special/wink{wink_sport}.json"
                    await Vts.parameter_values_homing(websocket, parameter_values)
                    parameter_values = await Vts.vtube_sportout(websocket, file_now)     # 不准打断,谁打断wink我跟谁急
                    parameter_values.append({"id": "MouthSmile", "value": MouthSmile})
                await Vts.parameter_values_homing(websocket, parameter_values)
                with lock:
                    action_file = ""
        else:
            # 无动作就傻站着
            parameter_values = await waiting_model(time)
            await Vts.vtube_control(websocket, parameter_values)
            await asyncio.sleep(0.02)
            time += 0.02


def vtube_worker():
    asyncio.run(vtube_run())


def emotion_with_action(text_data):
    global action_file
    global emotion_data
    while True:
        text = text_data.get()
        emotion = SnowNLP(text)
        print(f"[语句'{text}'的情绪值]:", emotion.sentiments) # 0.976923 positive
        emotion_data = emotion.sentiments
        num = random.randint(5,9)
        file = f"./sport/neutral/sport{num}.json"
        with lock:
            action_file = file


# 翻译线程，输入文本，翻译为日文，提供给VOICEVOX
def translate_JA(text_data, tts_data):
    while True:
        text = text_data.get()
        print("[文本]:", text)
        text_ja = VoiceVox.translateGoogle(text, "JA")
        print("[翻译器][日语]:", text_ja)
        tts_data.put(text_ja)


# 语音输出线程， 输入日文
def voice_out(text_data, text_1, tts_data):
    global action_file
    VV = VoiceVox.Voicevox()
    file = "./output.txt"
    while True:
        tts = tts_data.get()
        text = text_data.get()

        try:
            # 生成字幕
            VoiceVox.generate_subtitle(text, file)

            # 语音生成，speaker请看speaker.josn
            audio = VV.speak_1(text = tts, speaker = 46)

            # 等待语音生成完成，再启动情绪分析动作选择
            text_1.put(text)

            # 语音阅读
            VV.speak_2(audio)
        except Exception:
            print("[VoiceVox ERROR]")
        finally:
            # 清空字幕
            VoiceVox.clear_subtitle(file)


def main(text_data):
    # 创建各自处理队列
    text_1 = queue.Queue()
    text_2 = queue.Queue()
    text_3 = queue.Queue()
    tts_data = queue.Queue()
    # 创建各自线程
    thread1 = threading.Thread(target=vtube_worker, )
    thread1.start()
    thread2 = threading.Thread(target=emotion_with_action, args=(text_1, ))
    thread2.start()
    thread3 = threading.Thread(target=translate_JA, args=(text_2, tts_data))
    thread3.start()
    thread4 = threading.Thread(target=voice_out, args=(text_3, text_1, tts_data))
    thread4.start()

    # 主线程负责处理数据并下发
    while True:
        text = text_data.get()
        text_2.put(text)
        text_3.put(text)

    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()

if __name__ == '__main__':
    text = multiprocessing.Queue(maxsize=0)
    VTUBE = multiprocessing.Process(target=main, args=(text, ))
    VTUBE.start()

    while True:
        q = input("[请输入语句]:\n")
        text.put(q)

    VTUBE.join()
