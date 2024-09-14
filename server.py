import argparse
import socket
import ChatTTS
import torch
import torchaudio
import json
import requests
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess
# NOTE: ollama must be running for this to work, start the ollama app or run `ollama serve`

record_file = "temp_recording.wav"
play_file = "temp_play.wav"
messages = []

ollama_model = "qwen2:0.5b"
ollama_url = "http://localhost:11434"

chat_machine = ChatTTS.Chat()
chat_machine.load(compile=False) 

ar_model_dir = "iic/SenseVoiceSmall"
ar_model = AutoModel(
    model=ar_model_dir,
    trust_remote_code=True,
    vad_model="fsmn-vad",
    vad_kwargs={"max_single_segment_time": 30000},
    device="cuda:0",
)

def chat(messages):
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
            # the response streams one token at a time, print that as we receive it
            print(content, end="", flush=True)
        if body.get("done", False):
            message["content"] = output
            return message
        
def process(input_file, output_file):
    res = ar_model.generate(
        input=input_file,
        cache={},
        language="auto",  # "zh", "en", "yue", "ja", "ko", "nospeech"
        use_itn=True,
        batch_size_s=60,
        merge_vad=True,  #
        merge_length_s=15,
    )
    user_input = rich_transcription_postprocess(res[0]["text"])
    print(user_input)
    if not user_input:
        exit()
    print()
    messages.append({"role": "user", "content": user_input})
    message = chat(messages)
    wavs = chat_machine.infer(message["content"])
    torchaudio.save(output_file, torch.from_numpy(wavs[0]), 24000)

def receive_send_file(receive_file, send_file, host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"服务器正在 {host}:{port} 上等待连接...")

    conn, addr = server_socket.accept()
    print(f"与 {addr} 连接成功!")
    while True:
        with open(f'{receive_file}', 'wb') as f:
            print(f"正在接收文件...{receive_file}")
            flag = True
            while flag:
                data = conn.recv(1024)
                if data.find(b'EOF')!= -1:
                    flag = False
                    data = data.decode()[:-3].encode()
                f.write(data)

        print("文件接收完毕!")

        process(receive_file, send_file)

        with open(f'{send_file}', 'rb') as f:
            print(f"正在发送文件...{send_file}")
            conn.sendall(f.read())
            conn.send(b'EOF')

        print("文件发送完毕!")

    conn.close()
    server_socket.close()

if __name__ == '__main__':
    paser = argparse.ArgumentParser()
    paser.add_argument('--ip', type=str, default='127.0.0.1', help='IP address of the server')
    paser.add_argument('--port', type=int, default=5000, help='Port number of the server')

    args = paser.parse_args()

    receive_send_file(record_file, play_file, args.ip, args.port)