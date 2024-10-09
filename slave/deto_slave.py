import sx126x
import sys
import time
import RPi.GPIO as GPIO
from signal import signal, SIGINT

def handler(signal_received, frame):
    GPIO.cleanup()
    exit(0)

def activer_relais(on):
    global pin_relais    
    GPIO.output(pin_relais, not on)

def setArmed(state):
    isArmed = state

def send(addr, msgkey):
    addr = addr.to_bytes(1, 'big')
    msgkey = msgkey.to_bytes(1, 'big')
    lora.sendraw(addr + msgkey)

def getmsgkey(msgvalue):
    idx = list(msg.values()).index(msgvalue)
    return list(msg.keys())[idx]

def listener():
    isArmed = False
    global addr_local

    while True:
        data = lora.receive()

        if data and len(data) == 2:

            addr = int.from_bytes(data[0:1])
            msgvalue = int.from_bytes(data[1:2])

            print("to :", addr, " - MSG :", getmsgkey(msgvalue))

            if addr != addr_local and addr != 255: # 255 = broadcast
                continue

            if msg["PING"] == msgvalue:
                send(addr_local, msg["PONG"])
            elif msg["FIRE_ON"] == msgvalue:
                activer_relais(True)
                send(addr_local, msg["ACK_FIRE_ON"])
            elif msg["FIRE_OFF"] == msgvalue:
                activer_relais(False)
                send(addr_local, msg["ACK_FIRE_OFF"])

        time.sleep(0.01)


def main():
    signal(SIGINT, handler)

    global msg
    msg = {"PING": 0, "PONG": 1, "FIRE_ON": 2, "ACK_FIRE_ON" : 3, "FIRE_OFF": 4, "ACK_FIRE_OFF" : 5 }

    global addr_local
    addr_local = int(sys.argv[1])
    
    global pin_relais
    pin_relais = 17

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin_relais, GPIO.OUT, initial=GPIO.HIGH)

    #initialize lora
    global lora

    #AIR_DATA_RATE = 0.3, 1.2, 2.4, 4.8, 9.6, 19.2, 38.4, 62.5

    lora = sx126x.sx126x(channel=18,address=addr_local,network=0, txPower='22', airDataRate='9.6', packetSize='32')
    listener()

if __name__ == '__main__':
    
    if len(sys.argv) != 2:
        print('Usage :', sys.argv[0], "<local address>")
    else:
        main()
