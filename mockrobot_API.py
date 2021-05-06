'''Python 3.9.4'''
import socket
import time
import threading
import json


class mockrobot_API():
    def __init__(self):
        self.SERVER = '127.0.0.1'
        self.PORT = 1000
        self.BUFFER_SIZE = 1024
        self.FORMAT = 'utf-8'
        self.statusDict = {
                100: 'Idle',
                101: 'In Progress',
                102: 'Finished Successfully',
                103: 'Terminated With Error',
                -300: 'Bad Request, In Progress'
            }

        self.currentStatusID = 100
        self.main_addr = None #str of the first IP to connect

    def start_server(self):
        '''Starts server looks for connections and starts a thread per connection'''
        print(f'SERVER STARTING')
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.SERVER, self.PORT))
        print(f'SERVER LISTENING ON {self.SERVER}')
        server.listen()
        while True:
            conn, addr = server.accept()
            t = threading.Thread(target=self.handle_driver, args=(conn, addr))
            t.start()

    def handle_driver(self, conn, addr):
        '''
        Recieves commands and sends responses to commands

        Arguments:
            conn: object representing connection
            addr: tuple representing IP and port connected
        '''
        print(f'NEW CONNECTION: {addr}')
        #only accept commands from the first connected driver
        if self.main_addr == None: #check if server has existing connection
            self.main_addr = addr #update connection
            conn.send('WELCOME'.encode(self.FORMAT))
            while self.main_addr != None:
                try:
                    msg = conn.recv(self.BUFFER_SIZE).decode(self.FORMAT)
                    msg_dict = json.loads(msg) #unpack recieved message
                    cmd = msg_dict['command']
                    param = msg_dict['param']

                    if cmd != 'getCurrentStatusID': #for debugging to see commands and args
                        print(msg)

                    #perform command
                    if cmd == 'disconnect': #disconnect
                        response_dict = {'request_status': 200, 'data': self.currentStatusID}
                        response = json.dumps(response_dict).encode(self.FORMAT)
                        conn.send(response)
                        self.main_addr = None
                        print(f'DISCONNECTING: {addr}')
                    elif cmd == 'home': #home
                        conn.send(self.home())
                    elif cmd == 'pick': #pick
                        conn.send(self.pick(param))
                    elif cmd == 'place': #place
                        conn.send(self.place(param))
                    elif cmd == 'status': #give status ID
                        response_dict = {'request_status': 200, 'data': self.status(param)}
                        response = json.dumps(response_dict).encode(self.FORMAT)
                        conn.send(response) #give current process status
                    elif cmd == 'getCurrentStatusID':
                        response_dict = {'request_status': 200, 'data': self.getCurrentStatusID()}
                        response = json.dumps(response_dict).encode(self.FORMAT)
                        conn.send(response)
                    else: #unknown command response
                        response_dict = {'request_status': 400, 'data': 'UNKNOWN COMMAND'}
                        response = json.dumps(response_dict).encode(self.FORMAT)
                        conn.send(response)
                except ConnectionResetError: #if client forcefully closed, disconnect
                    self.main_addr = None
                    print(f'DISCONNECTING: {addr}')
        else: #tell other connections that server has existing connection
            conn.send('EXISTING_CONN'.encode(self.FORMAT))

    def home(self):
        #send error if in progress with negative processID
        if self.currentStatusID == 101:
            return {'request_status': 400, 'data': -300}

        #start fake homing process (2 seconds for testing)
        home_thread = threading.Thread(target=self.moveRobot, args=(2,))
        home_thread.start()
        self.currentStatusID = 101 #update status
        response_dict = {'request_status': 200, 'data': self.currentStatusID}
        response = json.dumps(response_dict).encode(self.FORMAT)
        return response

    def pick(self, sourceLocation):
        #send error if in progress with negative processID
        if self.currentStatusID == 101:
            return {'request_status': 400, 'data': -300}

        #start fake picking process (5 seconds for testing)
        pick_thread = threading.Thread(target=self.moveRobot, args=(5,))
        pick_thread.start()
        self.currentStatusID = 101 #update status
        response_dict = {'request_status': 200, 'data': self.currentStatusID}
        response = json.dumps(response_dict).encode(self.FORMAT)
        return response

    def place(self, destinationLocation):
        #send error if in progress with negative processID
        if self.currentStatusID == 101:
            return {'request_status': 400, 'data': -300}

        #start fake placing process (5 seconds for testing)
        place_thread = threading.Thread(target=self.moveRobot, args=(5,))
        place_thread.start()
        self.currentStatusID = 101 #update status
        response_dict = {'request_status': 200, 'data': self.currentStatusID}
        response = json.dumps(response_dict).encode(self.FORMAT)
        return response

    def status(self, processID):
        #convert statusID(int) to processStatus(str)
        processStatus = self.statusDict[processID]
        return processStatus

    def getCurrentStatusID(self):
        #gives current process statusID (int)
        return self.currentStatusID

    def moveRobot(self, op_time):
        '''
        Simulate robot move and interrupts/updates process status when driver aborts in progress
        
        Arguments:
            op_time: int representing seconds for operation
        '''
        update_rate = 0.05
        timer = 0
        while timer < op_time: #while timer is still ticking
            if self.main_addr == None: #if disconnected, give terminated error
                self.currentStatusID = 103 
                return #exit robot move
            timer += update_rate
            time.sleep(update_rate)
        self.currentStatusID = 102 #give postive ID if successful

test_API = mockrobot_API()
test_API.start_server()
