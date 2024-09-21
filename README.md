# ChatBot

## 介绍

ChatBot是基于Python的开放源代码聊天机器人框架，它可以实现语音对话功能。

## 功能
[SenseVoice](https://github.com/FunAudioLLM/SenseVoice)实现音频转文字，[Ollama](https://github.com/ollama/ollama) [Qwen2](https://ollama.com/library/qwen2)模型生成交流文本，[ChatTTS](https://github.com/2noise/ChatTTS)实现文本转语音。

client.py, server.py, tool.py提供网络链接。

## 使用方法
### 下载项目
```shell
git clone https://github.com/BrowserOrientedProgramer/ChatBot.git
cd ChatBot
```
提示音

[tone.mp3](https://pixabay.com/zh/sound-effects/achive-sound-132273/) Sound Effect by <a href="https://pixabay.com/zh/users/liecio-3298866/?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=132273">LIECIO</a> from <a href="https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=132273">Pixabay</a>
### 安装依赖
```shell
conda create -n ChatBot python=3.10
conda activate ChatBot
pip install -r requirements.txt
```

### 提前开启Ollama
```shell
ollama serve
```
### 启动ChatBot
* 方法一：
```shell
python main.py
```
* 方法二：
    
服务器
```shell
python server.py --ip 127.0.0.1 --port 8080
```
    
客户端
```shell
python client.py --ip 127.0.0.1 --port 8080
```
