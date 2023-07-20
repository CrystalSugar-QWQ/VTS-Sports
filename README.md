# VTS-Sports
输入文本，根据文本输出生成l2d动作和表情

## 简易使用说明:
先安装库  
`pip install -r requirements.txt`    
打开Vtube studio  
VOICEVOX可以不开  
运行`vtube.py`  
输入文字体验使用  

## 动作录制讲解
打开`sport_R.py`  
`sport_file`为存储路径  
运行`Vts.vtube_read(websocket, sport_file)`时开始录制  
运行`Vts.vtube_sportout(websocket, sport_file)`时播放动作  
