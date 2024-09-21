import argparse
import socket
import requests
import json

import torch
import torchaudio
import ChatTTS
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess
# NOTE: ollama must be running for this to work, start the ollama app or run `ollama serve`


ollama_model = "qwen2:0.5b"
ollama_url = "http://localhost:11434"

record_file = "temp_record.wav"
play_file = "temp_play.wav"

ar_model_dir = "iic/SenseVoiceSmall"
ar_model = AutoModel(
    model=ar_model_dir,
    trust_remote_code=True,
    vad_model="fsmn-vad",
    vad_kwargs={"max_single_segment_time": 30000},
    # device="cuda:0",
)

chattts = ChatTTS.Chat()
chattts.load(compile=False)

def ollama_chat(messages):
    r = requests.post(
        ollama_url + "/api/chat",
        json={"model": ollama_model, "messages": messages, "stream": True},
    )
    r.raise_for_status()
    output = ""
    for line in r.iter_lines():
        body = json.loads(line)
        if "error" in body:
            raise Exception(body["error"])
        if body.get("done") is False:
            message = body.get("message", "")
            content = message.get("content", "")
            output += content
        if body.get("done", False):
            message["content"] = output
            return message

def stt(voice_file):
    res = ar_model.generate(
        input=voice_file,
        cache={},
        language="auto",
        use_itn=True,
        batch_size_s=60,
        merge_vad=True,
        merge_length_s=15,
    )
    return rich_transcription_postprocess(res[0]["text"])

def voice_chat(messages, voice_file, replay_file):
    user_input = stt(voice_file)
    print(f"User: {user_input}\n")
    messages.append({"role": "user", "content": user_input})
    message = ollama_chat(messages)
    wavs = chattts.infer(message["content"])
    print(f"Ollama: {message['content']}\n")
    torchaudio.save(replay_file, torch.from_numpy(wavs[0]), 24000)

def main(ip, port):
    messages = []
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip, port))
    s.listen(5)
    print('Waiting for connection...')

    while True:
        # 接受客户端音频
        conn, _ = s.accept()
        with open(record_file, "wb") as f:
            while (data := conn.recv(1024)) != b'':
                f.write(data)
        conn.close()
        print('Data recived')

        voice_chat(messages, record_file, play_file)

        # 返回客户端音频
        conn, _ = s.accept()
        with open(play_file, "rb") as f:
            conn.sendall(f.read())
        conn.close()
        print('Data sent')


if __name__ == '__main__':
    paser = argparse.ArgumentParser()
    paser.add_argument('--ip', type=str, default='127.0.0.1', help='IP address of the server')
    paser.add_argument('--port', type=int, default=5000, help='Port number of the server')

    args = paser.parse_args()

    main(args.ip, args.port)