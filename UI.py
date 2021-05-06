'''Python 3.9.4'''
from tkinter import *

from driver_interface import *
import scheduler

MockRobot_Driver = DriverInterface() #create driver instance

def buttonpress(function, *args):
    #performs the driver function and prints return to text box
    execution_status = function(*args)
    msg_list.insert(END, f'{execution_status}')
    msg_list.see(END)

def update_status():
    #constantly updates process status of robot
    processStatus = MockRobot_Driver.processStatus
    lbl_processStatus.config(text=f'MockRobot Process Status: {processStatus}')
    root.after(100, update_status)

def update_connection():
    #constantly updates connection status to robot
    connected = MockRobot_Driver.connected
    if connected:
        lbl_connectionStatus.config(text=f'MockRobot Connection Status: Connected')
    else:
        lbl_connectionStatus.config(text=f'MockRobot Connection Status: Not Connected')
    root.after(100, update_connection)

#Begin UI
root = Tk()
root.title('Device Driver GUI')
root.geometry('525x700')

app = Frame(root)
app.grid()

#Define dropdown lists
op = StringVar(root)
menu_ops = OptionMenu(app, op, *scheduler.valid_operations)

pName1 = StringVar(root)
menu_pName1 = OptionMenu(app, pName1, *scheduler.valid_names)

pName2 = StringVar(root)
menu_pName2 = OptionMenu(app, pName2, *scheduler.valid_names)

#Define buttons
btn_OpenConnection = Button(
    app,
    text='Open Connection',
    width=25,
    height=4,
    command=lambda: buttonpress(MockRobot_Driver.OpenConnection, ent_IPAddress.get(), ent_Port.get()),
)
btn_Abort = Button(app, width=25, height=4, text='Abort', command=lambda: buttonpress(MockRobot_Driver.Abort))
btn_Initialize = Button(app, width=25, height=4, text='Initialize', command=lambda: buttonpress(MockRobot_Driver.Initialize))
btn_ExecuteOperation = Button(
    app,
    width=25,
    height=10,
    text='Execute Operation',
    command=lambda: buttonpress(
        MockRobot_Driver.ExecuteOperation,
        op.get(),
        [pName1.get(), pName2.get()],
        [ent_pValue1.get(), ent_pValue2.get()],
    ),
)

#Define entry, labels, and text box
ent_IPAddress = Entry(app, width=25, justify=LEFT)
ent_Port = Entry(app, width=25, justify=LEFT)
ent_pValue1 = Entry(app, width=25, justify=LEFT)
ent_pValue2 = Entry(app, width=25, justify=LEFT)
lbl_connectionStatus = Label(app, text=f'MockRobot Connection Status: Not Connected', width=40, height=1, justify=LEFT, anchor="w")
lbl_processStatus = Label(app, text=f'MockRobot Process Status: ', width=40, height=1, justify=LEFT, anchor="w")
lbl_IP = Label(app, text=f'Enter IP Address:', width=25, height=2, justify=RIGHT, anchor="e")
lbl_Port = Label(app, text=f'Enter Port:', width=25, height=2, justify=RIGHT, anchor="e")
lbl_ops = Label(app, text=f'Select Operation:', width=25, height=2, justify=RIGHT, anchor="e")
lbl_pName1 = Label(app, text=f'Select Source or Destination:', width=25, height=2, justify=RIGHT, anchor="e")
lbl_pValue1 = Label(app, text=f'Enter location value:', width=25, height=2, justify=RIGHT, anchor="e")
lbl_pName2 = Label(app, text=f'Select Source or Destination:', width=25, height=2, justify=RIGHT, anchor="e")
lbl_pValue2 = Label(app, text=f'Enter location value:', width=25, height=2, justify=RIGHT, anchor="e")
scrollbar = Scrollbar(app)
msg_list = Listbox(app, height=15, width=75, yscrollcommand=scrollbar.set)

#Setup grid
btn_OpenConnection.grid(row=2, column=3, rowspan=2)
lbl_IP.grid(row=2, column=1)
lbl_Port.grid(row=3, column=1)
ent_IPAddress.grid(row=2, column=2)
ent_Port.grid(row=3, column=2)
btn_Initialize.grid(row=4, column=3)
btn_ExecuteOperation.grid(row=5, column=3, rowspan=5)
lbl_ops.grid(row=5, column=1)
lbl_pName1.grid(row=6, column=1)
lbl_pValue1.grid(row=7, column=1)
lbl_pName2.grid(row=8, column=1)
lbl_pValue2.grid(row=9, column=1)
menu_ops.grid(row=5, column=2, sticky='ew')
menu_pName1.grid(row=6, column=2, sticky='ew')
ent_pValue1.grid(row=7, column=2)
menu_pName2.grid(row=8, column=2, sticky='ew')
ent_pValue2.grid(row=9, column=2)
btn_Abort.grid(row=10, column=3)

lbl_connectionStatus.grid(row=11, column=1, columnspan=2)
lbl_processStatus.grid(row=12, column=1, columnspan=2)
msg_list.grid(row=13, column=1, columnspan=3)
scrollbar.grid(row=13, column=4)

#Debugging quick default values
ent_IPAddress.insert(0, '127.0.0.1')
ent_Port.insert(0, '1000')
ent_pValue1.insert(0, '1')
ent_pValue2.insert(0, '2')
op.set(scheduler.valid_operations[0])
pName1.set(scheduler.valid_names[0])
pName2.set(scheduler.valid_names[0])

#Starts GUI loop and constantly updates status and connection
update_status()
update_connection()
root.mainloop()
