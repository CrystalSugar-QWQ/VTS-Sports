import json
import asyncio
from png import png_base64
import time

PLUGIN_NAME = "Akato's sport"
PLUGIN_DEVELOPER = "by sugar"
REQUEST_ID = "VTubeAkato"
API_VERSION = "1.0"


# 验证并获取令牌
# 返回值信息：
# "authenticationToken" 是API 身份验证的令牌
async def vtube_token(websocket):
    payload = {
        "apiName": "VTubeStudioPublicAPI",
        "apiVersion": API_VERSION,
        "requestID": REQUEST_ID,
        "messageType": "AuthenticationTokenRequest",
        "data": {
            "pluginName": PLUGIN_NAME,
            "pluginDeveloper": PLUGIN_DEVELOPER,
            "pluginIcon": png_base64
        }
    }

    await websocket.send(json.dumps(payload))
    json_data = await websocket.recv()
    pack = json.loads(json_data)
    authtoken = pack['data']['authenticationToken']
    # print(authtoken)
    return authtoken


# 使用已有的令牌进行验证
# 返回值信息：
# true or false
async def vtube_plugin(websocket, authtoken):
    payload = {
        "apiName": "VTubeStudioPublicAPI",
        "apiVersion": API_VERSION,
        "requestID": REQUEST_ID,
        "messageType": "AuthenticationRequest",
        "data": {
            "pluginName": PLUGIN_NAME,
            "pluginDeveloper": PLUGIN_DEVELOPER,
            "authenticationToken": authtoken
        }
    }
    await websocket.send(json.dumps(payload))
    json_data = await websocket.recv()
    pack = json.loads(json_data)
    a = pack['data']['authenticated']
    return a


# 获取当前统计信息
# 返回值信息：
# "uptime"包含自 VTube Studio 启动以来的毫秒数。
# "framerate"是当前渲染 FPS 值。
# "allowedPlugins"是用户当前允许使用 VTube Studio 的插件数量，
# "connectedPlugins"是当前连接到 VTube Studio API 的插件数量。
# "startedWithSteam"如果应用已使用 Steam 启动，则为 true，否则为 false
# （如果文件.bat已用于在没有 Steam 的情况下启动 VTS）。
async def vtube_statistics(websocket):
    payload = {
        "apiName": "VTubeStudioPublicAPI",
        "apiVersion": API_VERSION,
        "requestID": REQUEST_ID,
        "messageType": "StatisticsRequest",
    }

    await websocket.send(json.dumps(payload))
    json_data = await websocket.recv()
    # print(json_data)
    return json_data


async def vtube_control(websocket, parameter_values):
    payload = {
        "apiName": "VTubeStudioPublicAPI",
        "apiVersion": API_VERSION,
        "requestID": REQUEST_ID,
        "messageType": "InjectParameterDataRequest",
        "data": {
            "faceFound": False,
            "mode": "set",
            "parameterValues": parameter_values
        }
    }

    await websocket.send(json.dumps(payload))
    json_data = await websocket.recv()
    # print(json_data)
    return json_data


async def vtube_hotkeys(websocket, key):
    payload = {
        "apiName": "VTubeStudioPublicAPI",
        "apiVersion": API_VERSION,
        "requestID": REQUEST_ID,
        "messageType": "HotkeyTriggerRequest",
        "data": {
            "hotkeyID": key
        }
    }
    await websocket.send(json.dumps(payload))
    json_data = await websocket.recv()
    # print(json_data)
    return json_data



async def vtube_request(websocket):
    payload = {
        "apiName": "VTubeStudioPublicAPI",
        "apiVersion": API_VERSION,
        "requestID": REQUEST_ID,
        "messageType": "InputParameterListRequest"
    }

    await websocket.send(json.dumps(payload))
    json_data = await websocket.recv()
    data = json.loads(json_data)
    # print(data["data"]["defaultParameters"])

    FaceAngleX = data["data"]["defaultParameters"][3]["value"]
    FaceAngleY = data["data"]["defaultParameters"][4]["value"]
    FaceAngleZ = data["data"]["defaultParameters"][5]["value"]
    EyeRightX = data["data"]["defaultParameters"][18]["value"]
    EyeRightY = data["data"]["defaultParameters"][19]["value"]
    Brows = data["data"]["defaultParameters"][8]["value"]
    EyeOpenLeft = data["data"]["defaultParameters"][14]["value"]
    EyeOpenRight = data["data"]["defaultParameters"][15]["value"]

    parameter_values = [{"id": "FaceAngleX", "value": FaceAngleX},
                        {"id": "FaceAngleY", "value": FaceAngleY},
                        {"id": "FaceAngleZ", "value": FaceAngleZ},
                        {"id": "EyeRightX", "value": EyeRightX},
                        {"id": "EyeRightY", "value": EyeRightY},
                        {"id": "EyeOpenLeft", "value": EyeOpenLeft},
                        {"id": "EyeOpenRight", "value": EyeOpenRight}
                        ]

    return parameter_values


# 动作复位
async def parameter_values_homing(websocket, now):
    time = 20.000000

    FaceAngleX = now[0]["value"]
    FaceAngleY = now[1]["value"]
    FaceAngleZ = now[2]["value"]
    EyeRightX = now[3]["value"]
    EyeRightY = now[4]["value"]
    EyeOpenLeft = now[5]["value"]
    EyeOpenRight = now[6]["value"]
    Brows = now[7]["value"]
    MouthSmile = now[8]["value"]

    FaceAngleX_add = 0 - (FaceAngleX / time)
    FaceAngleY_add = 0 - (FaceAngleY / time)
    FaceAngleZ_add = 0 - (FaceAngleZ / time)
    EyeRightX_add = 0 - (EyeRightX / time)
    EyeRightY_add = 0 - (EyeRightY / time)

    Brows_add = 0
    if Brows > 0.55:
        Brows_add = 0 - ((Brows-0.55) / time)
    elif Brows < 0.55:
        Brows_add = ((0.55-Brows) / time)

    MouthSmile_add = 0
    if MouthSmile > 0.6:
        MouthSmile_add = 0 - ((MouthSmile-0.6) / time)
    elif MouthSmile < 0.6:
        MouthSmile_add = ((0.6-MouthSmile) / time)

    EyeOpenLeft_add = 0 
    if EyeOpenLeft < 1:
        EyeOpenLeft_add = ((1 - EyeOpenLeft) / time)

    EyeOpenRight_add = 0 
    if EyeOpenRight < 1:
        EyeOpenRight_add = ((1 - EyeOpenRight) / time)
    
    for i in range(20):
        FaceAngleX += FaceAngleX_add
        FaceAngleY += FaceAngleY_add
        FaceAngleZ += FaceAngleZ_add
        EyeRightX += EyeRightX_add
        EyeRightY += EyeRightY_add
        Brows += Brows_add
        MouthSmile += MouthSmile_add
        EyeOpenLeft += EyeOpenLeft_add
        EyeOpenRight += EyeOpenRight_add

        parameter_values = [
            {"id": "FaceAngleX", "value": FaceAngleX},
            {"id": "FaceAngleY", "value": FaceAngleY},
            {"id": "FaceAngleZ", "value": FaceAngleZ},
            {"id": "EyeRightX", "value": EyeRightX},
            {"id": "EyeRightY", "value": EyeRightY},
            {"id": "EyeOpenLeft", "value": EyeOpenLeft},
            {"id": "EyeOpenRight", "value": EyeOpenRight},
            {"id": "Brows", "value": Brows},
            {"id": "MouthSmile", "value": MouthSmile}]
        await vtube_control(websocket, parameter_values)
        await asyncio.sleep(0.03)
    