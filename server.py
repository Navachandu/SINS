import socket
import json
import hashlib
from comm_var import PORT, HEADER, FORMAT, DATA, SERVER_LOGIN
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
            print('received message', message)
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
            print('sent messages', JSONmsg)
            client_socket.send(JSONmsg)
        except Exception as e:
            print('send_msg error', e)

    def client_handling(self, connections, address):
        try:
            while True:
                message = self.receive_msg(connections)
                # print('address', address)
                if message['msg_type'] == 'HELLO':
                    print('username', message['username'])
                    #print('bytes', bytes(message['username']))
                    user = self.hashing.update(bytes(message['username'], 'utf-8'))
                    print('user', user)
                    enc_user = self.hashing.hexdigest()
                    print('enc_user', enc_user)

                    length = 0
                    print('before for loop')
                    for value in SERVER_LOGIN.keys():
                        print('value', value)
                        print('enc', enc_user)
                        if value == enc_user:
                            print('user matched')
                            self.send_msg(connections, 'HELLO_ACK', message['sequence_number'], message['session_id'],
                                          None, SERVER_LOGIN[value])
                        elif length < len(SERVER_LOGIN)-1:
                            length += 1
                            print(length)
                            continue
                        else:
                            self.send_msg(connections, 'INVALID_USER', message['sequence_number'], message['session_id'],
                                          None, SERVER_LOGIN[value])
                            print('INVALIED USER')
                            connections.close()

                elif message['msg_type'] == 'DATA_REQUEST':
                    self.send_msg(connections, 'DATA_RESPONSE', message['sequence_number'], message['session_id'], DATA)
                    continue

                elif self.receive_msg(connections)['msg_type'] == 'CLOSE':
                    print('connection is closed')
                    connections.close()
                    break

            print('connections ', connections)
            print('address ', address)
        except Exception as e:
            print('client handling error', e)


p = Server()
p.start_server()
