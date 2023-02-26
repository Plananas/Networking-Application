import socket
import threading
import datetime

from ServerClientHandler import ClientHandler


class Server:
    def __init__(self, port=50000):
        # all the attributes of the server
        self.PORT = port
        self.SERVER = socket.gethostbyname(socket.gethostname())
        self.ADDR = (self.SERVER, self.PORT)
        self.ActiveConnections = 0
        self.clients = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    # Start the server!
    def run(self):

        # define what type of server we are using and bind it to the address
        self.server.bind(self.ADDR)
        self.server.listen()
        print(f"server is listening on {self.SERVER}\n")

        # Heartbeat will constantly run while the server is up
        #thread = threading.Thread(target=self.heartbeat)
        #thread.start()
        #
        # Main runtime loop for the server.
        # Server will always be open so while true is okay.
        while True:
            conn, addr = self.server.accept()
            print(conn)
            print(addr)
            clientHandler = ClientHandler(addr, conn, self)
            self.clients.append(clientHandler)
            handleclientThread = threading.Thread(target=clientHandler.handle_client)
            handleclientThread.start()
            self.ActiveConnections += 1

            print(f"Users Connected: {self.ActiveConnections}")

#############
# i have decided to put all the functions accessing admin info in the server itself rather than the client handler.
############
    # This will edit the server log with information from the each client.
    def serverlog(self, message, client):

        # will timestamp what the user sent and adds it to a log file.
        timestamp = datetime.datetime.now()
        logfile = open(f"userlog.adminlog", "a")
        # logs the details of each client.
        logfile.write(f"{timestamp} [{client.username}{client.addr}]: {message}\n")
        logfile.close()

    # This will grab the server log from a file when an admin wants to access it
    def getserverlog(self):
        try:
            userlog = open("userlog.adminlog", "r")
            userlograw = userlog.read()
            userlog.close()
        except:
            message = "Error reading logs."
        return userlograw

    # This will return the active users and their current state on the server.
    def showactiveconnections(self):
        clientlist = []
        # This should grab the username address and state of the client
        for client in self.clients:
            clientlist.append((f"[{client.username} {client.addr}] {client.currentState}"))
        return(clientlist)




# lets start the server!
print("[STARTING]")
theServer = Server()
theServer.run()