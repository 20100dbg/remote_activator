import sx126x
import sys
import time
import RPi.GPIO as GPIO
from signal import signal, SIGINT

def handler(signal_received, frame):
    GPIO.cleanup()
    exit(0)

def activer_relais(pin_relais):
    GPIO.output(pin_relais, True)
    time.sleep(1)
    GPIO.output(pin_relais, False)

def send(msgkey, addr):
    msgkey = msgkey.to_bytes(1, 'big')
    addr = addr.to_bytes(1, 'big')

    msgraw = msgkey + addr
    #print(f"sending {msgraw}")
    lora.sendraw(msgraw)

def getmsgkey(msgvalue):
    idx = list(msg.values()).index(msgvalue)
    return list(msg.keys())[idx]

def listener(addr_local, pin_relais):

    while True:
        data = lora.receive()

        if data:

            msgvalue = int.from_bytes(data[0:1])

            tab_addr = [int.from_bytes(data[i:i+1]) for i in range(1,len(data))]
            
            #print(f"to : {tab_addr} - MSG : {getmsgkey(msgvalue)}")

            if addr_local not in tab_addr and tab_addr[0] != 255: # 255 = broadcast
                continue
            
            if msg["PING"] == msgvalue:
                send(msg["PONG"], addr_local)
            elif msg["FIRE"] == msgvalue:
                activer_relais(pin_relais)

        time.sleep(0.001)


def main():
    signal(SIGINT, handler)

    global msg
    msg = {"PING": 0, "PONG": 1, "FIRE": 2 }

    addr_local = int(sys.argv[1])
    pin_relais = 17

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin_relais, GPIO.OUT, initial=GPIO.LOW)

    #AIR_DATA_RATE = 0.3, 1.2, 2.4, 4.8, 9.6, 19.2, 38.4, 62.5
    #initialize lora
    global lora
    lora = sx126x.sx126x(channel=18,address=addr_local,network=0, txPower='22', airDataRate='9.6', packetSize='32')
    listener(addr_local, pin_relais)



if __name__ == '__main__':
    
    if len(sys.argv) != 2:
        print('Usage :', sys.argv[0], "<local address>")
    else:
        main()
