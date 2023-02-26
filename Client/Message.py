from EncryptDecrypt import AESCipher, DiffieHellman

class MessageHandler:
    def __init__(self, _conn):
        self.FORMAT = 'utf-8'
        self.HEADER = 64
        self.keyGen = DiffieHellman()
        self.conn = _conn
        #################Diffie Hellman key exchange!!#####################
        # as soon as we connect we need to get the encryption key from the server and send our own.
        ourKey = self.keyGen.publicPrivateKey()
        _conn.send(str(ourKey).encode(self.FORMAT))
        clientKey = _conn.recv(1024).decode(self.FORMAT)
        print("Generating Key....")
        Cipher_Key = self.keyGen.key(int(clientKey))
        print(f"the key: {Cipher_Key}")
        # key must be 16bytes
        self.Cipher = AESCipher(str(Cipher_Key))
        ###################################################################

    # Read the message sent from the client.
    def read(self):
        messages = []
        # sent message will always be in the format: Nonce, Ciphertext, Tag
        for x in range(0,3):
            # length checking all working nicely
            msg_length = self.conn.recv(self.HEADER).decode(self.FORMAT)
            msg_length = int(msg_length)
            if msg_length:
                messages.append(self.conn.recv(msg_length))

        message = self.Cipher.decrypt(messages[0], messages[1], messages[2])
        # This will be the final decoded message!
        try:
            message = message.decode('utf-8')

            return str(message)
        except:
            return("Error Decoding Message")

    # Write a message to the server!
    def write(self, message):
        messages = (self.Cipher.encrypt(message))

        for x in range(0,3):
            msg_length = len(messages[x])
            send_length = str(msg_length).encode(self.FORMAT)
            send_length += b' ' * (self.HEADER - len(send_length))
            self.conn.send(send_length)
            self.conn.send(messages[x])

