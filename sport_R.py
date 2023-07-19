# 测试程序-录制动作
import Vts
import websockets
import asyncio
import random

sport_file = "./sport/special/wink1.json"

async def vtube_run():
    # 连接上服务器,并初始化
    try:
        websocket = await websockets.connect('ws://127.0.0.1:8001')
        await Vts.init(websocket)
    except Exception:
        print("[VTS 无法连接]")
        return

    await Vts.vtube_read(websocket, sport_file)
    #await Vts.vtube_sportout(websocket, sport_file)
    while True:
        pass


asyncio.run(vtube_run())

