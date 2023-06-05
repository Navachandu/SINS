from client import Client
from server import Server


# Press the green button in the gutter to run the script.clear
if __name__ == '__main__':
    print('ds')
    server_obj = Server()
    server_obj.start_server()

    client_obj=Client()
    client_obj.hhh()

