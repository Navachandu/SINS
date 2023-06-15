import socket
import json
import hashlib
from comm_var import PORT, HEADER, FORMAT, DATA, SERVER_LOGIN,CHALLENGE
import threading


class Server:
    try:
        SERVER = socket.gethostbyname(socket.gethostname())
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((SERVER, PORT))
        hashing = hashlib.new("SHA256")
    except Exception as e:
        print('server class error', e)

    def start_server(self):
        try:
            self.server.listen()
            print('server listening on ', self.SERVER)
            connections_list = []
            while True:
                connections, address = self.server.accept()
                print('connections',connections)
                print('address ', address)
                clients = threading.Thread(target=self.client_handling, args=(connections, address))
                clients.start()
                connections_list.append(address)
                print('active connections ', threading.active_count() - 1)
                print('connections_list', connections_list)
        except Exception as e:
            print('start_server error', e)

    def receive_msg(self, connections):
        try:
            message = connections.recv(HEADER)
            jsonmsg = json.loads(message.decode(FORMAT))
            return jsonmsg
        except Exception as e:
            print('receive_msg error', e)

    def send_msg(self, client_socket, msg, sequence_number, session_id, data=None, response=None):
        try:
            if response is None:
                message = {
                    "msg_type": msg,
                    "sequence_number": sequence_number,
                    "sequence_id": session_id,
                    "data": data
                }
            else:
                message = {
                    "msg_type": msg,
                    "sequence_number": sequence_number,
                    "sequence_id": session_id,
                    "data": data,
                    "response": response
                }

            JSONmsg = json.dumps(message).encode(FORMAT)
            #print('sent messages', JSONmsg)
            client_socket.send(JSONmsg)
        except Exception as e:
            print('send_msg error', e)

    def client_handling(self, connections, address):
        try:

            message = self.receive_msg(connections)  # received username
            user = self.hashing.update(bytes(message['username'], 'utf-8'))
            enc_user = self.hashing.hexdigest()
            for value in SERVER_LOGIN.keys():
                if value == enc_user:
                    print('USER NAME MATCHED')
                    self.send_msg(connections, CHALLENGE, None, None, None, None)
                    cha_res = SERVER_LOGIN[enc_user] + CHALLENGE
                    message = self.receive_msg(connections)
                   # print('mess',message)
                    if message['msg_type'] == cha_res:
                        print('YOU ARE AUTHENTICATED')
                        self.send_msg(connections, 'AUTHENTICATED', None, None, None, None)

                    else:
                        print('WRONG PASSWORD')
                        self.send_msg(connections, 'WRONG PASSWORD', None, None, None, None)
                        connections.close()
            while True:
                message = self.receive_msg(connections)
                if message['msg_type'] == 'HELLO':
                    self.send_msg(connections, 'HELLO_ACK', message['sequence_number'], message['session_id'],
                                  None, SERVER_LOGIN[value])

                elif message['msg_type'] == 'DATA_REQUEST':
                    self.send_msg(connections, 'DATA_RESPONSE', message['sequence_number'], message['session_id'], DATA)
                    print(message)
                    continue

                elif self.receive_msg(connections)['msg_type'] == 'CLOSE':
                    print('connection is closed')
                    connections.close()
                    break

            print('connections ', connections)
            print('address ', address)
        except Exception as e:
            print('Connection ')


p = Server()
p.start_server()
