from enum import Enum
from Message import MessageHandler
import time


class State(Enum):
    Start = 1
    Echo = 2
    Write = 3
    Read = 4
    Login = 5
    Signup = 6
    AdminViewLog = 7
    AdminViewActive = 8
    Add = 9
    Error = 99

class ClientHandler:
    def __init__(self, _addr, _conn, _device):
        # all the client's attributes
        self.currentState = State.Start
        self.previousState = None
        self.DISCONNECT_MESSAGE = "goodbye"
        self.addr = _addr
        self.conn = _conn
        self.messageHandler = 0
        self.admin = False
        self.username = False
        self.connected = False
        self.device = _device
        self.count = 0


    def handle_client(self):
        addr = self.addr
        conn = self.conn
        self.log(f"{addr} has connected")
        print(f"{addr} has connected")

        # Message Handler deals with all the message sending.
        self.messageHandler = MessageHandler(conn)

        # We only want to do this stuff while a user is connected.
        self.connected = True
        while self.connected:
            try:
                # before anything we need to make sure the user has an account:
                while self.username == False:
                        self.currentState = State.Login
                        msg = self.login()
                        if self.username:
                            self.currentState = State.Start
                            self.previousState = State.Login
                        self.send(msg)


                msg = self.receive()
                print(f"Received {msg}")
                # Our message handlers
                if msg == self.DISCONNECT_MESSAGE:
                    self.log(f"user {addr} has disconnected")
                    print(f"user {addr} has disconnected")
                    self.connected = False
                else:
                    # Handle simple states with client->server, server-> client pattern
                    if self.currentState == State.Start:
                        msg = self.start(msg)
                    elif self.currentState == State.Echo:
                        msg = self.echo(msg)
                    elif self.currentState == State.Write:
                        msg = self.write()
                    elif self.currentState == State.Read:
                        msg = self.read()
                    elif self.currentState == State.AdminViewLog and self.admin:
                        msg = self.viewClientLog()
                    elif self.currentState == State.AdminViewActive and self.admin:
                        msg = self.viewActive()
                    elif self.currentState == State.Add:
                        msg = self.add(msg)
                    else:
                        msg = self.handleError(msg)
                    print(f"[({self.username}){addr}] {msg}")

                    self.send(msg)
            except:
                self.log(f"error with client {addr}")
                print(f"error with client {addr}")
                break
        # removes us from the connected clients list
        self.device.clients.remove(self)
        self.device.ActiveConnections -= 1
        conn.close()

    # this checks whether we need to change function
    def stateCheck(self, message):
        message = message.lower()

        if message.startswith("echo") and self.currentState != State.Echo:
            self.previousState = self.currentState
            self.currentState = State.Echo
            return "Moving to Echo"
        elif message.startswith("write") and self.currentState != State.Write:
            self.previousState = self.currentState
            self.currentState = State.Write
            return self.write()
        elif message.startswith("read") and self.currentState != State.Read:
            self.previousState = self.currentState
            self.currentState = State.Read
            return self.read()
        # only an admin can do this!
        elif message.startswith("logs") and self.admin:
            self.previousState = self.currentState
            self.currentState = State.AdminViewLog
            return self.viewClientLog()
        elif message.startswith("active") and self.admin:
            self.previousState = self.currentState
            self.currentState = State.AdminViewActive
            return self.viewActive()
        elif message.startswith("add"):
            self.previousState = self.currentState
            self.currentState = State.Add
            return "Moving to Add"
        else:
            return False
# this is the state once the user has logged in and is choosing the options.
    def start(self, message):
        message = self.stateCheck(message)
        if not message:
            message = self.handleError("That was not a valid command")

        return message
##### Logging in! ######
# I apologise for how long this function ended out to be.
    def login(self):
        self.send("Do you have an account(y/n)")
        response = self.receive()
        if response == "y":
            # Get us the login information
            loginfile = open("pass.password", "r")
            self.send("Please enter your username")
            username = self.receive()
            self.send("Please enter your password")
            password = self.receive()

            passlist = loginfile.read().split("\n")
            loginfile.close()
            # Go through the list of passwords and find us the correct combo
            # last bit in list is always a \n so this will remove the errors
            for x in range(0, len(passlist)-1):
                # each line at the moment is the username, password, and if they are admin.
                try:
                    data = passlist[x].split(",")
                    if f"{data[0]},{data[1]}" == f"{username}, {password}":
                        # If they are there we can log the user in
                        self.username = username
                        if data[2] == " True":
                            self.admin = True
                        message = f"successfully logged in as {username}"
                        print(f"{username} has logged in, admin = {self.admin}")
                        break
                    else:
                        message = self.handleError("Error logging in: incorrect login details")
                except:
                    message = self.handleError("Some kind of error checking username and password.")
        elif response == "n":
            self.currentState = State.Signup
            self.previousState = State.Login
            message = self.signup()
        else:
            print("response was not correct")
            message = self.handleError("wrong input entered, please use (n) or (y)")

        return message

#####Sign Up!!#####
    def signup(self):
        self.send("Please enter a username, followed by a password")
        username = self.receive()
        password = self.receive()
        # we don't want passwords to contain commas or they could fake themselves admin
        if (password.find(",") < 0) and (username.find(",") < 0):
            try:
                passwordfile = open("pass.password", "a")
                # we will write the username as a square cipher value encrypted using the password as a key.
                # then save the password as an encrypted value using the username as a key.
                passwordfile.write(f"{username}, {password}, False\n")
                message = "Sucessfully created account!"
                passwordfile.close()
            except:
                message = self.handleError("Could not sign up, maybe an error with input?")
        else:
            message = self.handleError("Username or password contained illegal character.")
        return message



    # Returns the message the user sent to us.
    def echo(self, message):

        changestate = self.stateCheck(message)
        if changestate:
            message = changestate

        return message
    # adds a number to a tally.
    def add(self, message):
        changestate = self.stateCheck(message)
        try:
            if changestate:
                message = changestate
            else:

                    self.count += int(message)
                    message = f"{self.count} is the current count"
        except:
            message = self.handleError("Incorrect value entered. Try entering a whole number")
        return message

    # user can write to a specified file.
    def write(self):

        self.send("Please enter the file you would like to write to\nfollowed by what you want to write:")
        file = self.receive()
        text = self.receive()
        try:
            file1 = open(f"{file}.txt", "a")
            file1.write(f"{text}\n")
            message = f"Written {text} to {file}.txt\n--Returning to start--"
            file1.close()
            self.previousState = State.Write
            self.currentState = State.Start
        except:
            message = self.handleError("Error opening file, possibly entered an incorrect file name.")

        return message

    # user can read a specified file.
    def read(self):
        self.send("Please enter the file you would like to read.")
        file = self.receive()
        try:
            file1 = open(f"{file}.txt", "r")
            message = f"--Contents of {file}.txt--\n{file1.read()}\n--Returning to start--"
            file1.close()
            self.previousState = State.Read
            self.currentState = State.Start
        except:
            message = self.handleError("Error opening file, possibly entered an incorrect file name.")
        return message

    # admin will receive the whole server log.
    # further improvement would be to send a section of the log instead of the whole thing.
    # or maybe even send it as a file rather than a string.
    def viewClientLog(self):
        message = f"--Here is the user log--\n{self.device.getserverlog()}\n--returning to start"
        self.previousState = State.AdminViewLog
        self.currentState = State.Start
        return message

    # admin can see the currently active users and their state.
    def viewActive(self):
        connections = self.device.showactiveconnections()
        connectionstr = ""
        for connection in connections:
            connectionstr += f"{connection}\n"
        message = f"--Here are the active users--\n{connectionstr}\n--returning to start"
        self.previousState = State.AdminViewActive
        self.currentState = State.Start
        return message

    # This will make sure an error is sent back to the user telling them what went wrong.
    # returns them to start to try again.
    def handleError(self, message):
        self.currentState = State.Start
        self.previousState = State.Error
        self.log(f"--Error: {message}")
        return f"--Error: {message}"

    # this sends the message to the message handler.
    def send(self, msg):
        self.messageHandler.write(msg)

    # grabs an incoming message from the message handler.
    def receive(self):
        message = self.messageHandler.read()
        self.log(message)

        return message

    #can call the log function to log errors connnections and incoming messages.
    def log(self, message):
        # we don't want to add the user's login to the log file
        if self.currentState != State.Login and self.currentState != State.Signup:
            self.device.serverlog(message, self)
