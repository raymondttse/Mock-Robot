'''Python 3.9.4'''
import socket
import time
import threading
import json

import scheduler


class DriverInterface():
    def __init__(self):
        self.BUFFER_SIZE = 1024
        self.FORMAT = 'utf-8'

        self.driver = None #class: socket
        self.processStatus = None #string: current robot process status
        self.connected = False #boolean: connection to robot

    def OpenConnection(self, IPAddress, Port):
        '''
        Begins connection with robot and starts thread to constantly update process status

        Arguments:
            IPAddress: string representing IP
            Port: string representing port number

        Returns: string documenting success or error that occurred
        '''
        if self.connected:
            return '<DRIVER ERROR> MockRobot already connected'
        if not Port.isdigit():
            return '<INPUT ERROR> Input valid port number'

        try:
            Port = int(Port)
            self.driver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.driver.connect((IPAddress, Port))
            
            #get the first msg if connection went through
            conn_status = self.driver.recv(self.BUFFER_SIZE).decode(self.FORMAT)
            #only officially connect if there is no existing connection
            if conn_status == 'EXISTING_CONN':
                return '<SERVER ERROR> More than one client attempting to connect'
            else:
                self.connected = True
                #begin thread to constantly update process status
                get_processStatus_thread = threading.Thread(target=self.get_processStatus)
                get_processStatus_thread.start()
                return '<SUCCESS> Connected to MockRobot!'
        except: #return this if connecting/recieving did not work
            return '<DRIVER ERROR> Connection failed...'

    def get_processStatus(self):
        '''
        Constantly updates process status by getting status ID and getting string from ID
        '''
        check_processID = self.request_API('getCurrentStatusID')
        prev_processID = None
        while self.connected: #while connected to robot, check ID
            check_processID = self.request_API('getCurrentStatusID')
            #only send request to understand what ID means if it changes
            if check_processID != prev_processID:
                self.processStatus = self.request_API('status', check_processID)
            prev_processID = check_processID
            time.sleep(0.01) #do this every 0.01 seconds

    def request_API(self, cmd, arg=None):
        '''
        Sends request to robot API and returns response
        
        Arguments:
            cmd: string representing command to be sent
            arg: string or int representing arguments of command

        Returns: string or int of the command's return robot-side,
                 or string documenting error
        '''
        #encode command so sendable through TCP/IP and send it
        msg = self.pack_request(cmd, arg)  
        self.driver.send(msg)
        #recieve response and decode it
        raw_response = self.driver.recv(self.BUFFER_SIZE)
        response = self.unpack_response(raw_response)
        #print(msg, response) #for debugging
        return response

    def pack_request(self, cmd, arg=None):
        '''
        Converts command and arg into JSON format
        ie. {'command': cmd, 'param': arg}

        Arguments:
            cmd: string representing command to be sent
            arg: string or int representing arguments of command
        
        Return: message encoded by format(utf-8) to send through TCP/IP
        '''
        #python dictionary representation of JSON
        d = {'command': cmd, 'param': arg} 
        #converts dictionary to JSON string and encodes
        msg = json.dumps(d).encode(self.FORMAT) 
        return msg

    def unpack_response(self, raw_msg):
        '''
        Converts raw message in JSON to python dictionary and gives
        content of the message
        ie. {'request_status': 200, 'data': your data}

        Arguments:
            raw_msg: bytes encoded by server

        Return: string or int of the data OR string documenting error
        '''
        py_dict = json.loads(raw_msg) #convert JSON to python dict
        data = py_dict['data']
        #check if API request was recognized
        if py_dict['request_status'] == 200: #success
            return data
        elif py_dict['request_status'] == 400: #server returned error
            return f'<SERVER ERROR> {data}'

    def Initialize(self):
        '''
        Sends home command to robot so it's in automation ready state

        Returns: string documenting success or error that occurred
        '''
        if not self.connected:
            return '<DRIVER ERROR> No connection available'
        elif self.processStatus == 'In Progress':
            return '<DRIVER ERROR> Process already in progress'

        #sends home command
        home_thread = threading.Thread(target=self.ExecuteQueue, args=([['home', None]],))
        home_thread.start()
        return '<SUCCESS> Homing process initiated'

    def ExecuteOperation(self, operation, parameterNames, parameterValues):
        '''
        Tells robot to perform operation with given parameters

        Arguments:
            operation: string representing operation name
            parameterNames(parallel index): list of strings with names of params
            parameterValues(parallel index): list of strings with values of params

        Returns: string documenting success or error that occurred
        '''
        if not self.connected:
            return '<DRIVER ERROR> No connection available'
        elif self.processStatus == 'In Progress':
            return '<DRIVER ERROR> Process already in progress'

        #collect values so easier to read
        pName1, pName2 = parameterNames[0], parameterNames[1]
        pValue1 = int(parameterValues[0]) if parameterValues[0] != '' else parameterValues[0]
        pValue2 = int(parameterValues[1]) if parameterValues[1] != '' else parameterValues[1]

        #check valid values from "scheduler program"
        if scheduler.check_valid_locs(parameterValues) != True:
            return '<INPUT ERROR> Input valid location values'
        #if pick or place
        elif operation == 'Pick' or operation == 'Place':
            if pValue1 == '':
                return '<INPUT ERROR> Input location value in first row'
            elif pName2 != 'None' or pValue2 != '':
                return '<INPUT ERROR> Delete entries in second row'

            if operation == 'Pick': #use pick helper function
                return self.handle_Pick(pName1, pName2, pValue1, pValue2)
            elif operation == 'Place': #use place helper function
                return self.handle_Place(pName1, pName2, pValue1, pValue2)
        #if transfer
        elif operation == 'Transfer': #use transfer helper function
            return self.handle_Transfer(pName1, pName2, pValue1, pValue2, parameterNames, parameterValues)
        #don't recognize operation
        else:
            return '<INPUT ERROR> Input valid operation'

    def handle_Pick(self, pName1, pName2, pValue1, pValue2):
        #helper function for picking, returns string of success or error
        if pName1 != 'Source Location':
            return '<INPUT ERROR> Select Source Location for Picking'
        elif pName2 == 'None' and pValue2 == '':
            #send pick command
            pick_thread = threading.Thread(target=self.ExecuteQueue, args=([['pick', pValue1]],))
            pick_thread.start()
            return '<SUCCESS> Picking process initiated'

    def handle_Place(self, pName1, pName2, pValue1, pValue2):
        #helper function for placing, returns string of success or error
        if pName1 != 'Destination Location':
            return '<INPUT ERROR> Select Destination Location for Placing'
        elif pName2 == 'None' and pValue2 == '':
            #send place command
            place_thread = threading.Thread(target=self.ExecuteQueue, args=([['place', pValue1]],))
            place_thread.start()
            return '<SUCCESS> Placing process initiated'
    
    def handle_Transfer(self, pName1, pName2, pValue1, pValue2, parameterNames, parameterValues):
        #helper function for transfer, returns string of success or error
        if pName1 == 'None' or pName2 == 'None' or pName1 == pName2:
            return '<INPUT ERROR> Select Source and Destination for Transfer'
        elif pValue1 == pValue2:
            return '<INPUT ERROR> Cannot Transfer same location'
        elif pValue1 == '' or pValue2 == '':
            return '<INPUT ERROR> Input all location values for Transfer'
        else:
            #finds indeces of names so that pick goes first always
            i_src = parameterNames.index('Source Location')
            i_dst = parameterNames.index('Destination Location')
            #send pick, then place command as queue
            transfer_thread = threading.Thread(
                target=self.ExecuteQueue, 
                args=([['pick', int(parameterValues[i_src])], ['place', int(parameterValues[i_dst])]],))
            transfer_thread.start()
            return '<SUCCESS> Transfer process initiated'

    def ExecuteQueue(self, queue):
        '''
        Tells robot to perform operation from queue one at a time
        *implemented so longer queues could be executed from a scheduler program, etc*

        Arguments:
            queue: list of lists containing series of commands to be sent to robot
            ie. [['pick', '2'], ['place', '1']]
        '''
        #while queue is not empty and still connected to robot
        while queue != [] and self.connected:
            time.sleep(0.05)
            #check if robot is doing anything
            if self.processStatus != 'In Progress':
                #only send command if not doing anything and remove from queue
                print(queue[0])
                self.request_API(queue[0][0], queue[0][1])
                queue.pop(0)

    def Abort(self):
        '''
        Terminates connection with robot server

        Returns: string documenting success or error that occurred
        '''
        if not self.connected:
            return '<DRIVER ERROR> No connection available'

        self.request_API('disconnect')
        self.driver.close()
        self.connected = False
        self.processStatus = 'Unknown'
        return '<SUCCESS> Disconnected from MockRobot!'
