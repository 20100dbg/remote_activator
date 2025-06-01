## Introduction
Control one or many remote switches using LoRa, from your smartphone.


![Software stack](https://github.com/20100dbg/remote_activator/blob/master/software_stack.png)



## Repository content

This repo contains everything to build this project from scratch.

- lora-e5 contains code to re-program the Lora-e5-mini board for both master and slave
- master_web contains the backend code that is placed on the pi zero
- models contains Freecad files of cases for both master and slave

And this Readme file gives detailed instructions to setup LoRa-e5-mini boards and the complete backend stack on the pi zero.



## Hardware
The master is using a [pi zero 2 W](https://www.gotronic.fr/art-carte-raspberry-pi-zero-2-w-34463.htm) and a [LoRa-e5-mini](https://www.gotronic.fr/art-carte-wio-e5-mini-113990939-33674.htm). 

The pi zero is powered with an external battery


LiPo Amigo Pro https://www.gotronic.fr/art-chargeur-lipo-amigo-pro-pim612-38175.htm
Accu LiPo 1500 mAh https://www.gotronic.fr/art-accu-lipo-3-7-vcc-1500-mah-thym-bat-37198.htm


## Wiring

Master

![Master wiring](https://github.com/20100dbg/remote_activator/blob/master/wiring_master.png)


Slave

![Slave wiring](https://github.com/20100dbg/remote_activator/blob/master/wiring_slave.png)


## Program LoRa-e5-mini board

The code is in master and slave directories.
Follow this guide : https://github.com/20100dbg/LoRa


## Install flask stack on Rpi

mkdir remote_activator
cd remote_activator
python -m venv .venv
source .venv/bin/activate


#### Install packages
```
pip install pyserial flask flask-socketio gevent gunicorn
```

```
sudo apt update
sudo apt install nginx hostapd dnsmasq
```



#### DNS conf

Create `/etc/dnsmasq.d/090_wlan0.conf` with this content

```
interface=wlan0
dhcp-range=10.3.141.50,10.3.141.255,255.255.255.0,12h
dhcp-option=6,10.3.141.1
no-resolv
server=1.1.1.1
address=/remote_activator.com /10.3.141.1
```

#### Nginx conf

Edit `/etc/nginx/nginx.conf`, add **into** http section :

```
server {
    listen       80;
    listen       [::]:80;
    server_name  remote_activator.com;

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:5000;
    }

    location /socket.io {
        proxy_pass http://127.0.0.1:5000/socket.io;
        proxy_redirect off;
        proxy_buffering off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_hide_header Access-Control-Allow-Origin;
    }
}
```

#### Create gunicorn service

Create `/etc/systemd/system/gunicorn.service` with this content :

```
[Unit]
Description=gunicorn
After=network.target

[Service]
User=rpi
WorkingDirectory=/home/rpi/remote_activator/
ExecStart=/home/rpi/remote_activator/gunicorn.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Create wifiap service

Create `/etc/systemd/system/wifiap.service` with this content :

```
[Unit]
Description=wifiap
After=network.target

[Service]
User=rpi
WorkingDirectory=/home/rpi/remote_activator/
ExecStart=/home/rpi/remote_activator/wifiap.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Add entry in /etc/hosts

```
10.3.141.1 remote_activator.com
```


#### hostapd conf

Edit `/etc/hostapd/hostapd.conf` with this content :

```
interface=wlan0
driver=nl80211
ssid=remote_activator
hw_mode=g
channel=6
beacon_int=100
dtim_period=2
max_num_sta=255
rts_threshold=2347
fragm_threshold=2346

#auth_algs=0
wpa=2
wpa_passphrase=Azerty123+
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
```

#### IP conf

Edit `/etc/network/interfaces.d/00-static` with this content :

```
auto wlan0
iface wlan0 inet static
address 10.3.141.1
netmask 255.255.255.0
netmask 255.255.255.0
```

#### Register services

```
sudo systemctl enable wifiap.service
sudo systemctl enable gunicorn.service
sudo systemctl daemon-reload
```

#### Reboot to finish

```
sudo reboot
```


## References

https://medium.com/@chandan-sharma/powering-flask-with-websockets-ca9f5a097ad9
