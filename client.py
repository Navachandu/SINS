import socket
import json
import random
import hashlib
from comm_var import PORT, HEADER, FORMAT, CLIENT_MESSAGES
import time

class Client:
    SERVER = '141.26.183.239'
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER, PORT))
    print('Server Connection is established')
    hashing = hashlib.new("SHA256")

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

            session_id = random.randint(1, 100)
            sequence_number = 1
            while sequence_number < 3:
                username = str(input('enter username'))
                password = str(input('enter password'))
                print('sequence_number',sequence_number)
                self.send_msg(CLIENT_MESSAGES[sequence_number - 1], str(sequence_number), str(session_id), username)

                enc_password = self.hashing.update(bytes(password, 'utf-8'))
                encrypt_password = self.hashing.hexdigest()
                message = self.receive_msg()
                if message['response'] == encrypt_password:
                    print('YOU ARE AUTHENTICATED')
                    if message['msg_type'] == 'HELLO_ACK':
                        sequence_number += 1
                        break
                    else:
                        sequence_number -= 1
                        continue
                else:
                    if message['msg_type'] == 'INVALID_USER':
                        print(message['msg_type'])
                        continue

            start_time = time.time()
            while True:
                internal_time = time.time()
                self.send_msg(CLIENT_MESSAGES[sequence_number - 1], str(sequence_number), str(session_id))
                message = self.receive_msg()
                if message['msg_type'] == 'DATA_RESPONSE':
                    sequence_number += 1
                    print(message)
                if time.time()-internal_time < 5 and time.time()-start_time < 1800:
                    time.sleep(5-(time.time()-internal_time))
                    sequence_number -= 1
                    continue
                else:
                    self.send_msg(CLIENT_MESSAGES[sequence_number - 1], str(sequence_number), str(session_id))
        except Exception as e:
            print('server_handling error')

p = Client()
p.server_handling()
