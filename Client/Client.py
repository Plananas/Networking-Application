import socket
import threading
from Message import MessageHandler
import time


class Client:
    def __init__(self):
        # all the client's attributes
        self.PORT = 50000
        self.SERVER = socket.gethostbyname(socket.gethostname())
        self.ADDR = (self.SERVER, self.PORT)
        self.DISCONNECT_MESSAGE = "goodbye"
        self.messageHandler = 0
        self.Connected = False
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        # try to connect first
        try:
            self.client.connect(self.ADDR)
        except:
            print("[CONNECTION ERROR]Could not connect to host.\nEither the host isn't up or your not connected to the network.")

        try:
            #Message handler will deal with the sending of all messages.
            self.messageHandler = MessageHandler(self.client)
            self.Connected = True

        except:
            self.Connected = False

        threading.Thread(target=self.handle_server).start()

        # main runtime loop while we are connected.
        while self.Connected:
            try:
                # gets us to enter the message
                # ive added a slight delay to let the server process what we've sent and come up with a response
                message = ""
                time.sleep(1)
                message = str(input("[ENTER MESSAGE] "))
                client.send(message)
                if message == "!DISCONNECT":
                    self.connected = False
                    break
            except:
                print("\n[CONNECTION ERROR] Disconnecting")
                self.connected = False
                break

    def handle_server(self):
        # Constantly listening to the server for messages.
        while self.Connected:
            try:
                msg = self.messageHandler.read()

            except:
                print("\n[CONNECTION ERROR] Disconnecting")
                self.connected = False
                break
            print(f"{msg}")

    # this will send our message into the message handler
    def send(self, msg):
        time.sleep(0.5)
        if msg == "":
            # empty strings caused my encryption to give out bad results so ive added this to the client
            print("please dont send empty strings... it breaks the server.")
        else:
            write = self.messageHandler.write(msg)

# let's run out client!!!!
client = Client()
client.run()
