# ChatBot

## 介绍

ChatBot是基于Python的开放源代码聊天机器人框架，它可以实现文本对话、语音对话、语音合成、语音识别等功能。

## 功能
[SenseVoice](https://github.com/FunAudioLLM/SenseVoice)实现音频转文字，[Ollama](https://github.com/ollama/ollama) [Qwen2](https://ollama.com/library/qwen2)模型生成交流文本，[ChatTTS](https://github.com/2noise/ChatTTS)实现文本转语音

## 使用方法
下载项目
```shell
git clone https://github.com/BrowserOrientedProgramer/ChatBot.git
cd ChatBot
```
安装依赖
```shell
conda create -n ChatBot python=3.10
conda activate ChatBot
pip install -r requirements.txt
```

提前开启Ollama
```shell
ollama serve
```
启动ChatBot
```shell
python main.py
```
