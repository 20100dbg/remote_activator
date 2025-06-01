import gevent
import threading
import time
from lora import lora
from flask import Flask, request, make_response
from flask_socketio import SocketIO, emit
from enum import Enum

class MsgType(Enum):
    PING = 1
    PING_ACK = 2
    FIRE = 3
    FIRE_ACK = 4


#sync - type - size - payload

sync_word = b"\xB5\x62"

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*',async_mode='gevent')

@app.route("/")
def main():
    tpl = open('templates/main.html', 'r').read()
    #tpl = tpl.replace('{{nb_ied}}', str(nb_ied))

    response = make_response(tpl)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@socketio.on('fire')
def fire(params):

    if len(params['id']) > 0:
        tab_ied = [int(id_ied) for id_ied in params['id']]

        for x in range(2):
            lora.send_bytes(build_message(MsgType.FIRE.value, bytes(tab_ied)))
            time.sleep(0.1)



@socketio.on('ping')
def ping(params):

    global ping_time
    ping_time = int(params['time'])

    if len(params['id']) > 0:
        tab_ied = [int(id_ied) for id_ied in params['id']]        
        lora.send_bytes(build_message(MsgType.PING.value, bytes(tab_ied)))


@socketio.on('update')
def update():
    socketio.emit('update', dict_ied)



##########
#
# LoRa
#
##########

def find_sync(data, idx_start=0):
    for idx in range(idx_start, len(data)):
        if data[idx:idx+len(sync_word)] == sync_word:
            return idx

    return -1


def listen_loop(callback):
    """ Check if data is received """
    
    buffer_receive = b''
    last_receive = 0
    
    while True:
        data = lora.receive()

        if data:
            buffer_receive += data
            last_receive = time.time()

        while True:
            idx_start = find_sync(buffer_receive)

            if idx_start >= 0:
                buffer_receive = buffer_receive[idx_start:]

                idx_end = find_sync(buffer_receive, idx_start=2)
                
                if idx_end == -1:
                    idx_end = len(buffer_receive)

                packet = buffer_receive[idx_start:idx_end]

                callback(packet)
                buffer_receive = buffer_receive[idx_end:]                        
            else:
                break


        #time.sleep(0.05) #minimal sleep time
        time.sleep(0.1)



def callback_lora(data):
    """ Handles every message received from LoRa """

    msg_type = data[2]
    msg_size = data[3]
    msg_from = data[4]

    if msg_type == MsgType.PING_ACK.value:
        
        if msg_from not in dict_ied:
            add_ied(msg_from)
        
        if ping_time > dict_ied[msg_from][1]:
            dict_ied[msg_from][1] = ping_time

        dict_ied[msg_from][2] = dict_ied[msg_from][1]

    update()


def build_message(type, data):

    size = len(data)
    packet = sync_word
    packet += type.to_bytes(1, 'big')
    packet += size.to_bytes(1, 'big')
    packet += data
    return packet




##########
#
# xxx
#
##########


def add_ied(id_ied):
    dict_ied[id_ied] = ["IED " + str(id_ied), ping_time, ping_time]


def bytes_to_hex(arr):
    return ' '.join(['{:02X}'.format(b) for b in arr])

dict_ied = {}
nb_ied = 3

global ping_time
ping_time = 0

for x in range(1,nb_ied+1):
    add_ied(x)


lora = lora(port="/dev/ttyS0")

t_receive = threading.Thread(target=listen_loop, args=[callback_lora])
t_receive.start()

