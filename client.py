'''client has to create unique session id'''

import socket
import json
import random
from comm_var import PORT, HEADER, FORMAT, CLOSE_MSG, CLIENT_MESSAGES
import time

class Client:
    SERVER = '141.26.182.57'
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER, PORT))
    print('Server Connection is established')

    def send_msg(self,msg,sequence_number,session_id):
        message={
            "msg_type": msg,
            "sequence_number":sequence_number,
            "session_id":session_id
        }
        print(message)
        JSONmsg= json.dumps(message).encode(FORMAT)
        self.client.send(JSONmsg)


    def receive_msg(self):
        message = self.client.recv(HEADER)
        jsonmsg = json.loads(message.decode(FORMAT))
        print('received msg',jsonmsg)
        return jsonmsg

    def server_handling(self):
        session_id = random.randint(1,100)
        sequence_number = 1
        while sequence_number <3:
            self.send_msg(CLIENT_MESSAGES[sequence_number-1],str(sequence_number),str(session_id))
            message = self.receive_msg()
            if message['msg_type'] == 'HELLO_ACK':
                sequence_number+=1
                break
            else:
                sequence_number -= 1
                continue
        start_time = time.time()
        while True:
            internal_time=time.time()
            self.send_msg(CLIENT_MESSAGES[sequence_number - 1], str(sequence_number), str(session_id))
            message = self.receive_msg()
            if message['msg_type'] == 'DATA_RESPONSE':
                sequence_number += 1
                print(message)
            if time.time()-internal_time<5 and time.time()-start_time<1800:
                time.sleep(5-(time.time()-internal_time))
                sequence_number -= 1
                continue
            else:
                self.send_msg(CLIENT_MESSAGES[sequence_number - 1], str(sequence_number), str(session_id))










p=Client()
p.server_handling()
