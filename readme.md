使用 Raspberry Pi 3 進行感側器資料蒐集

說明：
本範例使用 Raspberry Pi 3 (RPi) 與 NodeMCU 建構一環境資訊蒐集系統，範例分為3部份
    * envinfo_server：使用RPi作為主機接收所有感側器回傳的資料
    * envinfo_client_rpi：使用RPi作為感側器的示範
    * envinfo_client_nodemcu：使用NodeMCU作為感側器的示範

安裝：
<envinfo_server>

1.將 RPi 設定為區域網路型的無線存取點 (Wireless Access Point, WAP)

1.1. RPi 系統安裝
請參考 INSTALLING OPERATING SYSTEM IMAGES (https://www.raspberrypi.org/documentation/installation/installing-images/)

1.2. 環境設定
請參考 RASPI-CONFIG (https://www.raspberrypi.org/documentation/configuration/raspi-config.md)

1.3. 套件庫更新
$ sudo apt-get update -y && sudo apt-get upgrade -y

1.4. 網路組態設定
$ sudo nano /etc/network/interfaces

auto eth0
iface eth0 inet dhcp

allow-hotplug wlan0  
iface wlan0 inet static  
    address 10.10.0.1
    netmask 255.255.255.0
    network 10.10.0.0
    broadcast 10.10.0.255

1.5. 關閉 dhcpcd 功能
$ sudo systemctl disable dhcpcd

1.6. 安裝 hostapd ，將RPi的wifi作為WAP
$ sudo apt-get install hostapd

1.7. 設定hostapd.conf
$ sudo nano /etc/hostapd/hostapd.conf

# This is the name of the WiFi interface we configured above
interface=wlan0
# Use the nl80211 driver with the brcmfmac driver
driver=nl80211
# This is the name of the network
ssid=Pi3-AP
# Use the 2.4GHz band
hw_mode=g
# Use channel 6
channel=6
# Enable 802.11n
ieee80211n=1
# Enable WMM
wmm_enabled=1
# Enable 40MHz channels with 20ns guard interval
ht_capab=[HT40][SHORT-GI-20][DSSS_CCK-40]
# Accept all MAC addresses
macaddr_acl=0
# Use WPA authentication
auth_algs=1
# Require clients to know the network name
ignore_broadcast_ssid=0
# Use WPA2
wpa=2
# Use a pre-shared key
wpa_key_mgmt=WPA-PSK
# The network passphrase
wpa_passphrase=raspberry
# Use AES, instead of TKIP
rsn_pairwise=CCMP

1.8. 測試hostapd是否運作正常，使用裝置連入WAP
$ sudo hostapd /etc/hostapd/hostapd.conf

1.9. 修改預設 hostapd 設定
$ sudo nano /etc/default/hostapd
將其變更為：
DAEMON_CONF="/etc/hostapd/hostapd.conf"

1.10. 安裝DNAMASQ
$ sudo apt-get install dnsmasq

1.11. 設定DNSMASQ
$ sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig  
$ sudo nano /etc/dnsmasq.conf

# Use interface wlan0
interface=wlan0
# Explicitly specify the address to listen on
listen-address=10.10.0.1,127.0.0.1
# Routing PTR queries to nameservers
server=/10.10.in-addr.arpa/10.10.0.1
# Bind to the interface to make sure we aren't sending things elsewhere
bind-interfaces
# Add other name servers here, with domain specs if they are for non-public domains.
server=/localnet/10.10.0.1
# Never forward addresses in the non-routed address spaces.
bogus-priv
# disable listening eth0
no-dhcp-interface=eth0
# Delays sending DHCPOFFER and proxydhcp replies for at least the specified number of seconds.
dhcp-reply-delay=2
# Assign IP addresses between 10.10.0.50 and 10.10.0.150 with a 12 hour lease time
dhcp-range=10.10.0.50,10.10.0.150,12h

1.12. 將本機的name對應IP寫入
$ sudo nano /etc/hosts

10.10.0.1      master

2. 安裝範例程式 envinfo_server

2.1. 從 GitHub 取得範例程式碼

2.1.1. 安裝 Git 套件
$ sudo apt-get install git

2.1.2. 建立應用程式佈署用的資料夾
$ sudo mkdir /var/www/webapps && cd /var/www/webapps

2.3. 修改佈署資料夾的擁有者
$ sudo chown pi:pi /var/www/webapps

2.4. 從 GitHub 複製本範例程式碼
$ git clone xxxxxxxxxxxxxxxxxxxxxxxxx

2.2. MariaDB 安裝、設定與資料庫佈署

2.2.1. 安裝 mariadb-server 套件
$ sudo apt-get install mariadb-server

2.2.2. MariaDB 安全行設定
$ sudo mysql_secure_installation

2.2.3. 測試安裝
$ mysqladmin -u root -p version

[OUTPUT]
mysqladmin  Ver 9.1 Distrib 10.1.26-MariaDB, for debian-linux-gnu on x86_64
Copyright (c) 2000, 2017, Oracle, MariaDB Corporation Ab and others.

Server version          10.1.26-MariaDB-0+deb9u1
Protocol version        10
Connection              Localhost via UNIX socket
UNIX socket             /var/run/mysqld/mysqld.sock
Uptime:                 1 hour 23 min 22 sec

Threads: 1  Questions: 1  Slow queries: 0  Opens: 17  Flush tables: 1  Open tables: 11  Queries per second avg: 0.000

2.2.4. 建立資料庫、資料表與登入帳號

2.2.4.1. 登入 MariaDB
$ mysql -u root -p

2.2.4.2. 建立資料庫 envinfo
MariaDB [(none)] > CREATE DATABASE envinfo CHARACTER SET UTF8;

2.2.4.3. 建立使用者 envuser
MariaDB [(none)] > CREATE USER envuser@localhost IDENTIFIED BY 'envuserpassword';

2.2.4.4. 授予 envuser 於 envinfo 資料庫的權限
MariaDB [(none)] > GRANT ALL PRIVILEGES ON envinfo.* TO envuser@localhost;

2.2.4.5. 切換至 envinfo 資料庫
MariaDB [(none)] > use envinfo;

2.2.4.6. 建立資料表 (sql指令請參考檔案schema.sql)

2.3. 範例程式安裝與測試

2.3.1. 安裝相關套件
$ sudo apt-get install python-pip python-dev python-virtualenv nginx

2.3.2. 切換路徑至範例程式碼資料夾
$ cd /var/www/webapps

2.3.3. 依據資料庫設定的使用者帳號與密碼修改 settings.ini

2.3.4. 建立虛擬環境
$ cd ./envinfo_server
$ virtualenv venv

2.3.5. 啟動虛擬環境
$ source venv/bin/activate

2.3.6. 從 requirements.txt 安裝套件相關套件
(venv) $ pip install -r requirements.txt

2.3.7. 測試範例程式是否能正確運作 (使用瀏覽器開啟)
(venv) $ python wsgi.py

2.3.8. 使用 gunicorn 測試範例程式是否正常運行
(venv) $ gunicorn -w2 -b0.0.0.0:8000 wsgi:app

2.3.9. 關閉虛擬環境
(venv) $ deactivate

2.4. 範例程式生產環境佈署 (使用 gunicorn + nginx + systemd)

2.4.1. 建立systemd daemon
$ sudo nano /etc/systemd/system/envinfo.service

[Unit]
Description=Gunicorn instance to serve myapp
After=network.target

[Service]
User=pi
Group=pi
WorkingDirectory=/var/www/webapps/envinfo
Environment="PATH=/var/www/webapps/envinfo/venv/bin"
ExecStart=/var/www/webapps/envinfo/venv/bin/gunicorn --workers 2 --bind 127.0.0.1:2200 wsgi:app

[Install]
WantedBy=multi-user.target

2.4.2. 啟動systemd daemon設定維開機啟動
$ sudo systemctl start envinfo
$ sudo systemctl enable envinfo

2.4.2. 檢查daemon啟動狀況
$ sudo systemctl status envinfo

2.4.3. 設定nginx代理轉發
2.4.3.1 測試nginx使否正常啟動，開啟browser鍵入IP，是否帶入nginx預設頁面

2.4.3.2 備份default
$ sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.bak

2.4.3.3. 建立新的設定
$ sudo nano /etc/nginx/sites-available/envinfo

server {
    listen 80;
    server_name master;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /var/www/webapps/envinfo;
    }

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:2200;
    }
}

2.4.3.4. 移除default連結，並建立myapp連結
$ sudo rm /etc/nginx/sites-enabled/default
$ sudo ln -s /etc/nginx/sites-available/envinfo /etc/nginx/sites-enabled

2.4.3.5. 測試nginx設定
$ sudo nginx -t

2.4.3.6. 重新啟動nginx服務
$ sudo systemctl restart nginx

2.4.3.7 開啟browser檢查
http://master 或 http://10.10.0.1