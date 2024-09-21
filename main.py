import json
import pyaudio
import numpy as np
import wave
import requests
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess
# NOTE: ollama must be running for this to work, start the ollama app or run `ollama serve`

import ChatTTS
import torch
import torchaudio
import playsound

chat_machine = ChatTTS.Chat()
chat_machine.load(compile=False) 

record_file = "temp_record.wav"
play_file = "temp_play.wav"

ollama_model = "qwen2:0.5b"
ollama_url = "http://localhost:11434"

ar_model_dir = "iic/SenseVoiceSmall"
ar_model = AutoModel(
    model=ar_model_dir,
    # trust_remote_code=True,
    disable_update=True,
    vad_model="fsmn-vad",
    vad_kwargs={"max_single_segment_time": 30000},
    # device="cuda:0",
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
        if body.get("done", False):
            message["content"] = output
            return message
        
def detect_silence(data, threshold=1000, chunk_size=1024):
    audio_data = np.frombuffer(data, dtype=np.int16)
    return np.mean(np.abs(audio_data)) < threshold

# Function to record audio from the microphone and save to a file
def record_audio(file_path, silence_threshold=512, silence_duration=4.0, chunk_size=1024):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=chunk_size)
    frames = []
    print("Recording...")
    silent_chunks = 0
    speaking_chunks = 0
    while True:
        data = stream.read(chunk_size)
        frames.append(data)
        if detect_silence(data, threshold=silence_threshold, chunk_size=chunk_size):
            silent_chunks += 1
            if silent_chunks > silence_duration * (16000 / chunk_size):
                break
        else:
            silent_chunks = 0
            speaking_chunks += 1
        if speaking_chunks > silence_duration * (16000 / chunk_size) * 10:
            break
    print("Recording stopped.")
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(file_path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(16000)
    wf.writeframes(b''.join(frames))
    wf.close()

def main():
    messages = []
    while True:
        playsound.playsound('tone.mp3')
        record_audio(record_file)

        res = ar_model.generate(
            input=record_file,
            cache={},
            language="auto",  # "zh", "en", "yue", "ja", "ko", "nospeech"
            use_itn=True,
            batch_size_s=60,
            merge_vad=True,  #
            merge_length_s=15,
        )
        user_input = rich_transcription_postprocess(res[0]["text"])
        print(user_input)
        print()
        messages.append({"role": "user", "content": user_input})
        message = chat(messages)
        print(message["content"])
        wavs = chat_machine.infer(message["content"])
        torchaudio.save(play_file, torch.from_numpy(wavs[0]), 24000)
        playsound.playsound(play_file)
        messages.append(message)
        print("\n\n")
        
if __name__ == "__main__":
    main()