# **使用 Raspberry Pi 3 進行感測器資料蒐集**

本範例使用 Raspberry Pi 3 (RPi) 與 NodeMCU 建構一環境資訊蒐集系統，範例分為3部份
- envinfo_server：使用RPi作為主機接收所有感測器回傳的資料
- envinfo_client_rpi：使用RPi作為感測器的示範
- envinfo_client_nodemcu：使用NodeMCU作為感測器的示範

## **目錄**
0. [系統架構說明](#0-系統架構說明)
1. [RPi 作業系統安裝、設定與套件更新](#1-rpi作業系統安裝、設定與套件更新)
2. [將 RPi 打造成無線存取點 (Wireless Access Point, WAP)](#2-將-rpi-打造成無線存取點-wireless-access-point-wap)
3. [安裝與佈署本範例程](#3-安裝與佈署本範例程式)
    - [取得範例程式碼](#取得範例程式碼)
    - [MariaDB 安裝、設定與資料庫佈署](#mariadb-安裝、設定與資料庫佈署)
    - [建立資料庫、資料表與登入帳號](#建立資料庫、資料表與登入帳號)
    - [程式碼設定與試運行](#程式碼設定與試運行)
    - [生產環境佈署 (使用 gunicorn + nginx + systemd)](#生產環境佈署-使用-gunicorn-nginx-systemd)

### **0. 系統架構說明**
<這裡放一張圖並說明>

### **1. RPi作業系統安裝、設定與套件更新**
(1) RPi 系統安裝    
請參考 [INSTALLING OPERATING SYSTEM IMAGES](https://www.raspberrypi.org/documentation/installation/installing-images/)

(2) 環境設定   
請參考 [RASPI-CONFIG](https://www.raspberrypi.org/documentation/configuration/raspi-config.md)

(3) 套件庫更新
<pre>
$ sudo apt-get update -y && sudo apt-get upgrade -y
</pre>

### **2. 將 RPi 打造成無線存取點 (Wireless Access Point, WAP)**
(1) 網路組態設定
<pre>
$ sudo nano /etc/network/interfaces
</pre>
修改文件內容 **(注意：網路界面名稱可能因為 Predictable Network Interface Names 而與本說明不同)**
<pre>
auto eth0
iface eth0 inet dhcp

allow-hotplug wlan0  
iface wlan0 inet static  
    address 10.10.0.1
    netmask 255.255.255.0
    network 10.10.0.0
    broadcast 10.10.0.255
</pre>

(2) 關閉 dhcpcd 功能
<pre>
$ sudo systemctl disable dhcpcd
</pre>

(3) 安裝 hostapd ，將RPi的wifi作為WAP
<pre>
$ sudo apt-get install hostapd
</pre>

(4) 設定 hostapd.conf
<pre>
$ sudo nano /etc/hostapd/hostapd.conf
</pre>
修改文件內容
<pre>
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
</pre>

(5) 測試 hostapd 是否運作正常，使用裝置連入 WAP
<pre>
$ sudo hostapd /etc/hostapd/hostapd.conf
</pre>


(6) 修改預設 hostapd 設定     
<pre>
$ sudo nano /etc/default/hostapd
</pre>
修改文件內容
<pre>
DAEMON_CONF="/etc/hostapd/hostapd.conf"
</pre>

(6) 安裝 DNAMASQ
<pre>
$ sudo apt-get install dnsmasq
</pre>

(7) 設定DNSMASQ   
備份 dnsmasq.conf
<pre>
$ sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
</pre>
建立新的 dnsmasq.conf
<pre>
$ sudo nano /etc/dnsmasq.conf
</pre>
修改文件內容
<pre>
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
</pre>

(8) 將本機的 hostname 對應IP寫入
<pre>
$ sudo nano /etc/hosts
</pre>
修改文件內容
<pre>
10.10.0.1      master
</pre>

### **3. 安裝與佈署本範例程式**

#### 取得範例程式碼
(1) 從 GitHub 取得範例程式碼    
安裝 Git 套件
<pre>
$ sudo apt-get install git
</pre>
(2) 建立應用程式佈署用的資料夾
<pre>
$ sudo mkdir /var/www/webapps && cd /var/www/webapps
</pre>
(3) 修改佈署資料夾的擁有者
<pre>
$ sudo chown pi:pi /var/www/webapps
</pre>
(4) 從 GitHub 複製本範例程式碼
<pre>
$ git clone https://github.com/chilinwei/envinfo_server.git
</pre>

#### MariaDB 安裝、設定與資料庫佈署
(1) 安裝 mariadb-server 套件
<pre>
$ sudo apt-get install mariadb-server
</pre>
(2) MariaDB 安全行設定
<pre>
$ sudo mysql_secure_installation
</pre>
(3) 測試安裝
<pre>
$ mysqladmin -u root -p version
</pre>
登入成功並顯示系統資訊
<pre>
mysqladmin  Ver 9.1 Distrib 10.1.26-MariaDB, for debian-linux-gnu on x86_64
Copyright (c) 2000, 2017, Oracle, MariaDB Corporation Ab and others.

Server version          10.1.26-MariaDB-0+deb9u1
Protocol version        10
Connection              Localhost via UNIX socket
UNIX socket             /var/run/mysqld/mysqld.sock
Uptime:                 1 hour 23 min 22 sec

Threads: 1  Questions: 1  Slow queries: 0  Opens: 17  Flush tables: 1  Open tables: 11  Queries per second avg: 0.000
</pre>

#### 建立資料庫、資料表與登入帳號
(1) 登入 MariaDB
<pre>
$ mysql -u root -p
</pre>
(2) 建立資料庫 envinfo
<pre>
MariaDB [(none)] > CREATE DATABASE envinfo CHARACTER SET UTF8;
</pre>
(3) 建立使用者 envuser
<pre>
MariaDB [(none)] > CREATE USER envuser@localhost IDENTIFIED BY 'envuserpassword';
</pre>
(4) 授予 envuser 於 envinfo 資料庫的權限
<pre>
MariaDB [(none)] > GRANT ALL PRIVILEGES ON envinfo.* TO envuser@localhost;
</pre>
(5) 切換至 envinfo 資料庫
<pre>
MariaDB [(none)] > use envinfo;
</pre>
(6) 建立資料表 (sql指令請參考檔案 [schema.sql](/schema.sql))

#### 程式碼設定與試運行
(1) 安裝相關套件
<pre>
$ sudo apt-get install python-pip python-dev python-virtualenv nginx
</pre>
(2) 切換路徑至範例程式碼資料夾
<pre>
$ cd /var/www/webapps
</pre>
(3) 依據資料庫設定的使用者帳號與密碼修改 [settings.ini](/settings.ini)

(4) 建立虛擬環境
切換路徑
<pre>
$ cd ./envinfo_server
</pre>
建立虛擬環境
<pre>
$ virtualenv venv
</pre>
(5) 啟動虛擬環境 (Linux環境)
<pre>
$ source venv/bin/activate
</pre>
(6) 從 requirements.txt 安裝套件相關套件
<pre>
(venv) $ pip install -r requirements.txt
</pre>
(7) 測試範例程式是否能正確運作
<pre>
(venv) $ python wsgi.py
</pre>
使用瀏覽器開啟 http://127.0.0.1:5000 或 http://localhost:5000

(8) 使用 gunicorn 測試範例程式是否正常運行
<pre>
(venv) $ gunicorn -w2 -b0.0.0.0:8000 wsgi:app
</pre>
使用瀏覽器開啟 http://<本機ip>:8000

(9) 關閉虛擬環境
<pre>
(venv) $ deactivate
</pre>

#### 生產環境佈署 (使用 gunicorn + nginx + systemd)
(1) 建立 systemd daemon
<pre>
$ sudo nano /etc/systemd/system/envinfo.service
</pre>
建立以下內容
<pre>
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
</pre>
(2) 啟動 systemd daemon 設定維開機啟動
<pre>
$ sudo systemctl start envinfo
$ sudo systemctl enable envinfo
</pre>
(3) 檢查 daemon 啟動狀況
<pre>
$ sudo systemctl status envinfo
</pre>
(4) 設定 nginx 代理轉發   
A. 測試nginx使否正常啟動，開啟瀏覽器鍵入IP，是否帶入 nginx 預設頁面

B. 備份 default
<pre>
$ sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.bak
</pre>
C. 建立新的設定
<pre>
$ sudo nano /etc/nginx/sites-available/envinfo
</pre>
建立以下內容
<pre>
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
</pre>
D. 移除 default 連結，並建立 envinfo 連結
<pre>
$ sudo rm /etc/nginx/sites-enabled/default
$ sudo ln -s /etc/nginx/sites-available/envinfo /etc/nginx/sites-enabled
</pre>
E. 測試 nginx 設定
$ sudo nginx -t

G. 重新啟動 nginx 服務
$ sudo systemctl restart nginx

H. 開啟瀏覽器檢查
http://<本機ip / Hostname>
