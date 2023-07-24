# VTS-Sports
输入文本，根据文本输出生成l2d动作和表情  
测试版本仅供参考

## 简易使用说明:  
先安装库  
`pip install -r requirements.txt`    
打开Vtube studio, VOICEVOX  
运行`vtube.py`  
输入文字体验使用  
<<<<<<< HEAD
！！！请确保VTS里有"脸黑""脸红"热键！！！  

## 修改语音TTS:  
在`vtube.py`找到`VoiceOut_with_Emotion`函数  
将对应`语音生成`和`语音阅读`处代码更换  
翻译线程自行选择删不删,不删不想要日语可以把翻译输出改成中文    

## 动作录制讲解:  
提前打开Vtube Studio和摄像头
打开`sport_R.py`,现设置存储路径`sport_file`,再运行  
`sport_file`为存储路径,现有`./sport/active`,`./sport/neutral`,`./sport/negative`三个存储位置  
开始录制会有提示，按下右shift结束录制  
录制完成后会提示并播放一遍进行检查    
=======

## 动作录制讲解
### 动作库内置所有动作都是错误的，需要自行重新录制
提前打开Vtube Studio和摄像头
打开`sport_R.py`  
`sport_file`为存储路径  
运行`Vts.vtube_read(websocket, sport_file)`时开始录制，按下右shift结束录制  
运行`Vts.vtube_sportout(websocket, sport_file)`时播放动作  
>>>>>>> f8fc7f0a7f1c194a0c99b8eadf5c87d072413986
录制参数仅有FaceAngleX，FaceAngleY，FaceAngleZ，EyeRightX，EyeRightY，EyeOpenLeft，EyeOpenRight  
分别对应：头左右转向，头上下转向，头左右倾斜，眼球左右，眼球上下，左眼皮，右眼皮。  
