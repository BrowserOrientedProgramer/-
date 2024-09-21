import argparse
import socket
import wave
import pyaudio
import playsound

record_file = "temp_record.wav"
play_file = "temp_play.wav"

def record_audio(wave_out_path, record_second):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    with wave.open(wave_out_path, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        for _ in range(0, int(RATE / CHUNK * record_second)):
            data = stream.read(CHUNK)
            wf.writeframes(data)
        stream.stop_stream()
        stream.close()
        p.terminate()

def main(ip, port):
    while True:
        # 记录并发送语音
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((ip, port))

        playsound.playsound('tone.mp3')
        record_audio(record_file, 5)

        with open(record_file, 'rb') as f:
            conn.sendall(f.read())
        conn.close()
        print('Send voice data successfully.')

        # 接收并播放语音
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((ip, port))
        with open(play_file, 'wb') as f:
            while (data := conn.recv(1024)) != b'':
                f.write(data)
        conn.close()
        print('Receive voice data successfully.')

        playsound.playsound(play_file)

if __name__ == '__main__':
    paser = argparse.ArgumentParser()
    paser.add_argument('--ip', type=str, default='127.0.0.1', help='IP address of the server')
    paser.add_argument('--port', type=int, default=5000, help='Port number of the server')

    args = paser.parse_args()

    main(args.ip, args.port)