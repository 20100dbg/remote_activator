import gevent
import sx126x
import threading
import time
from flask import Flask, request, make_response
from flask_socketio import SocketIO, emit
from signal import signal, SIGINT

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*',async_mode='gevent')

#ied = {name, lastPing, lastPong}

@app.route("/")
def main():
    tpl = open('templates/main.html', 'r').read()
    tpl = tpl.replace('{{nb_ied}}', str(nb_ied))
    response = make_response(tpl)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@socketio.on('fire')
def fire(params):
    tab_ied = [int(id_ied) for id_ied in params['id']]
    send(tab_ied, "FIRE")


@socketio.on('ping')
def ping(params):
    global ping_time
    ping_time = int(params['time'])    
    tab_ied = [int(id_ied) for id_ied in params['id']]

    #On envoie les PING un par un pour laisser le temps aux slaves de répondre

    if tab_ied[0] == 255:
        tab_ied = range(1, nb_ied + 1)
    
    for id_ied in tab_ied:
        send([id_ied], 'PING')
        time.sleep(3.5)


def add_ied(id_ied):
    dict_ied[id_ied] = ["IED " + str(id_ied), ping_time, ping_time]


@socketio.on('update')
def update():
    socketio.emit('update', dict_ied)
    #print(dict_ied)


def handler_msg(msgvalue, id_ied):

    #print(f"from : {id_ied} - MSG : {getmsgkey(msgvalue)}")

    if msg["PONG"] == msgvalue:
        if id_ied not in dict_ied:
            add_ied(id_ied)
        
        if ping_time > dict_ied[id_ied][1]:
            dict_ied[id_ied][1] = ping_time

        dict_ied[id_ied][2] = dict_ied[id_ied][1]

    update()



def listener():
    global lora

    while True:
        data = lora.receive()

        if data:
            msgvalue = int.from_bytes(data[0:1])
            addr = int.from_bytes(data[1:2])
            handler_msg(msgvalue, addr)

        time.sleep(0.01)


def send(tab_ied, msgid):
    global lora

    m = msg[msgid].to_bytes(1, 'big')
    
    #Concatener les adresses
    b_ied = b''
    for id_ied in tab_ied:
        b_ied += id_ied.to_bytes(1, 'big')
    
    msgraw = m + b_ied
    #print(f"sending {msgid} to {tab_ied} : {msgraw}")

    lora.sendraw(msgraw)
    time.sleep(0.01)


def getmsgkey(msgvalue):
    idx = list(msg.values()).index(msgvalue)
    return list(msg.keys())[idx]


global nb_ied
nb_ied = 3

global dict_ied
dict_ied = {}

global ping_time
ping_time = 0

global msg
msg = {"PING": 0, "PONG": 1, "FIRE": 2 }

#AIR_DATA_RATE = 0.3, 1.2, 2.4, 4.8, 9.6, 19.2, 38.4, 62.5
global lora
lora = sx126x.sx126x(channel=18,address=0,network=0, txPower='22', airDataRate='9.6', packetSize='32')

t_receive = threading.Thread(target=listener)
t_receive.start()
