import serial
import threading
import time

class lora(object):

    def __init__(self, port="/dev/ttyS0"):

        self.serial = serial.Serial(port=port, baudrate=115200, timeout=0.1)
        self.debug = True


    def send_bytes(self, data):
        """ Send bytes through serial. Check if data is bytes """
        
        if self.debug:
            print(f"[+] SENDING {len(data)} bytes : {self.bytes_to_hex(data)}")
        
        self.serial.write(data)
        time.sleep(0.05) #minimal sleep time


    def receive(self):
        """ Check if data is received """

        data = self.serial.read(self.serial.in_waiting)

        if data and self.debug:
            print(f"[+] RECEIVED {len(data)} bytes : {self.bytes_to_hex(data)}")

        return data


    def listen_loop(self, callback):
        while self.running_listen:            
            data = self.receive()

            if data:
                callback(data)

            time.sleep(0.05) #minimal sleep time


    def listen(self, callback):
        
        self.running_listen = True
        self.t_receive = threading.Thread(target=self.listen_loop, args=[callback])
        self.t_receive.start()


    def close(self):
        self.serial.close()



    def bytes_to_hex(self, arr):
        return ' '.join(['{:02X}'.format(b) for b in arr])

