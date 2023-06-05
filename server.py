import socket
import json
from comm_var import PORT, HEADER, FORMAT, CLOSE_MSG, DATA
import threading


class Server:
    SERVER = socket.gethostbyname(socket.gethostname())
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER, PORT))

    def start_server(self):
        self.server.listen()
        print('server listening on ', self.SERVER)
        while True:
            connections_list = []
            connections, address = self.server.accept()
            print('address ', address)
            clients = threading.Thread(target=self.client_handling, args=(connections, address))
            clients.start()
            connections_list.append(address)
            print('active connections ', threading.activeCount() -1)


    def receive_msg(self, connections):
        message = connections.recv(HEADER)
        print('received message', message)
        jsonmsg= json.loads(message.decode(FORMAT))
        return jsonmsg

    def send_msg(self, client_socket,msg,sequence_number,session_id):
        message = {
            "msg_type": msg,
            "sequence_number": sequence_number,
            "sequence_id": session_id
        }
        JSONmsg = json.dumps(message).encode(FORMAT)
        print('sent messages', JSONmsg)
        client_socket.send(JSONmsg)

    def send_data(self, client_socket,msg,data,sequence_number,session_id):
        message = {
            "msg_type": msg,
            "data":data,
            "sequence_number": sequence_number,
            "sequence_id": session_id
        }
        JSONmsg = json.dumps(message).encode(FORMAT)
        print('sent data',JSONmsg)
        client_socket.send(JSONmsg)

    def client_handling(self, connections, address):
        while True:
            message = self.receive_msg(connections)
            #print('address', address)
            if message['msg_type'] == 'HELLO':
                self.send_msg(connections,'HELLO_ACK',message['sequence_number'],message['session_id'])
                continue
            elif message['msg_type'] == 'DATA_REQUEST':
                self.send_data(connections, 'DATA_RESPONSE', DATA, message['sequence_number'], message['session_id'])
                continue

            elif self.receive_msg(connections)['msg_type'] == 'CLOSE':
                print('connection is closed')
                connections.close()
                break

        print('connections ', connections)
        print('address ', address)



p = Server()
p.start_server()
