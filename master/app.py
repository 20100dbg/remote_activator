import gevent
import sx126x
import threading
import time
from flask import Flask, request
from flask_socketio import SocketIO, emit
from signal import signal, SIGINT

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*',async_mode='gevent')

#ied = {name, isActif, lastPing, lastPong}

@app.route("/")
def main():
    response = make_response(open('templates/main.html', 'r').read())
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    
    #return open('templates/main.html', 'r').read()
    return response


@socketio.on('name')
def name(params):
    _id = int(params['id'])
    dict_ied[_id][0] = params['name']
    update()


@socketio.on('fire')
def fire(params):
    _id = int(params['id'])

    if _id == 255:
        global fire_global
        msg_send = 'FIRE_OFF' if fire_global else 'FIRE_ON'
        fire_global = not fire_global
    else:
        msg_send = 'FIRE_OFF' if dict_ied[_id][1] else 'FIRE_ON'
    
    send(_id, msg_send)
    update()


@socketio.on('ping')
def ping(params):
    _id = int(params['id'])
    _time = int(params['time'])

    if _id == 255:
        global ping_global
        ping_global = _time
        
        for x in dict_ied:
            dict_ied[x][2] = _time
    else:
        dict_ied[_id][2] = _time
    
    send(_id, 'PING')


def add_ied(_id):
    dict_ied[_id] = ["IED " + str(_id), False, ping_global, ping_global]


@socketio.on('update')
def update():
    print("update", dict_ied)
    socketio.emit('update', dict_ied)


def handler_msg(_id, msgvalue):
    msgkey = getmsgkey(msgvalue)

    if msgkey == "PONG":
        if _id not in dict_ied:
            add_ied(_id)
        dict_ied[_id][3] = dict_ied[_id][2]

    elif msgkey == "ACK_FIRE_ON":
        dict_ied[_id][1] = True
    elif msgkey == "ACK_FIRE_OFF":
        dict_ied[_id][1] = False

    update()



def listener():
    global lora

    while isRunning:
        data = lora.receive()

        if data:
            addr = int.from_bytes(data[0:1])
            msgvalue = int.from_bytes(data[1:2])
            handler_msg(addr, msgvalue)
            #print("FROM :", addr, " - MSG :", getmsgkey(msgvalue))

        time.sleep(0.01)


def send(addr, msgid):
    global lora

    addr = addr.to_bytes(1, 'big')
    m = msg[msgid].to_bytes(1, 'big')
    
    lora.sendraw(addr + m)


def getmsgkey(msgvalue):
    idx = list(msg.values()).index(msgvalue)
    return list(msg.keys())[idx]


global dict_ied
dict_ied = {}

global fire_global
fire_global = False

global ping_global
ping_global = 0

global isRunning
isRunning = True

global lastTime
lastTime = 0

global msg
msg = {"PING": 0, "PONG": 1, "FIRE_ON": 2, "ACK_FIRE_ON" : 3, "FIRE_OFF": 4, "ACK_FIRE_OFF" : 5 }

global lora

#AIR_DATA_RATE = 0.3, 1.2, 2.4, 4.8, 9.6, 19.2, 38.4, 62.5
lora = sx126x.sx126x(channel=18,address=0,network=0, txPower='22', airDataRate='9.6', packetSize='32')

t_receive = threading.Thread(target=listener)
t_receive.start()
