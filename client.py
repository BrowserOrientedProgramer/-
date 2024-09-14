from tool import record_audio

import argparse
import socket
import playsound

record_file = "temp_recording.wav"
play_file = "temp_play.wav"

def send_receive_file(send_file, receive_file, host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    while True:
        playsound.playsound("tone.mp3")
        record_audio(send_file)

        with open(send_file, 'rb') as f:
            print(f"正在发送文件: {send_file}...")
            client_socket.sendall(f.read())
            client_socket.send(b'EOF')

        print("文件发送完毕!")

        with open(receive_file, 'wb') as f:
            print(f"正在接收文件: {receive_file}...")
            flag = True
            while flag:
                data = client_socket.recv(1024)
                if data.find(b'EOF')!= -1:
                    flag = False
                    data = data.decode()[:-3].encode()
                f.write(data)
            
        print("文件接收完毕!")

        playsound.playsound(receive_file)

    client_socket.close()

if __name__ == '__main__':
    paser = argparse.ArgumentParser()
    paser.add_argument('--ip', type=str, default='127.0.0.1', help='IP address of the server')
    paser.add_argument('--port', type=int, default=5000, help='Port number of the server')

    args = paser.parse_args()
    send_receive_file(record_file, play_file, args.ip, args.port)
        