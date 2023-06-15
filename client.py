import socket
import json
import random
import hashlib
from comm_var import PORT, HEADER, FORMAT, CLIENT_MESSAGES
import time

class Client:
    SERVER = '192.168.0.152'
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER, PORT))
    print('Server Connection is established')
    hashing = hashlib.new("SHA256") # CHAP AUTHENCATION

    def send_msg(self, msg, sequence_number, session_id, username=None):
        try:
            if username is None:
                message = {
                    "msg_type": msg,
                    "sequence_number": sequence_number,
                    "session_id": session_id
                }
            else:
                message = {
                    "msg_type": msg,
                    "sequence_number": sequence_number,
                    "session_id": session_id,
                    "username":username
                }
            print(message)
            JSONmsg = json.dumps(message).encode(FORMAT)
            self.client.send(JSONmsg)
        except  Exception as e:
            print('send_msg error', e)

    def receive_msg(self):
        try:
            message = self.client.recv(HEADER)
            jsonmsg = json.loads(message.decode(FORMAT))
            print('received msg', jsonmsg)
            return jsonmsg
        except  Exception as e:
            print('receive_msg error', e)

    def server_handling(self):
        try:


            username = str(input('enter username: '))
            password = str(input('enter password: '))

            self.send_msg(None, None, None, username)  # Sending Username

            enc_password = self.hashing.update(bytes(password, 'utf-8'))
            encrypt_password = self.hashing.hexdigest()         # calculated the encrypted password

            message = self.receive_msg()  # received the challenge

            cha_res = encrypt_password + message['msg_type'] # calculated the challenge response
            self.send_msg(cha_res, None, None, None)        # sending the challenge response

            message = self.receive_msg()  # received the response after challenge
            if message['msg_type'] == 'WRONG PASSWORD':
                print('connection is closed because of wrong password')
            else:
                print('CONNECTION IS AUTHENTICATED, ASKING DATA REQUEST')


            '''AFTER AUTHENTICATED'''
            while True:

                session_id = random.randint(1, 100)
                sequence_number = 1

                self.send_msg(CLIENT_MESSAGES[sequence_number - 1], str(sequence_number), str(session_id), username)

                message = self.receive_msg()

                if message['msg_type'] == 'HELLO_ACK':
                    sequence_number += 1

                start_time = time.time()
                while True:
                    internal_time = time.time()
                    self.send_msg(CLIENT_MESSAGES[1], str(sequence_number), str(session_id))
                    message = self.receive_msg()
                    if message['msg_type'] == 'DATA_RESPONSE':
                        sequence_number += 1
                    if time.time()-internal_time < 5 and time.time()-start_time < 1800 :
                        time.sleep(5-(time.time()-internal_time))
                        if sequence_number>10:
                            break
                        continue
                    else:
                        self.send_msg(CLIENT_MESSAGES[sequence_number - 1], str(sequence_number), str(session_id))
        except Exception as e:
            print('Connection is closed because of wrong login')

p = Client()
p.server_handling()
