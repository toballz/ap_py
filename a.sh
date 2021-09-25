#!/bin/bash

#Flush iptables
def_IpTablesFlush(){
 echo
 echo "[~~] Flushing..."
 sudo iptables --flush
 sudo iptables --table nat --flush
 sudo iptables --delete-chain
 sudo iptables --table nat --delete-chain
 sudo iptables --flush -t nat
 sudo iptables --table nat --delete-chain
}


#kill stop all
def_killAll(){
 echo
 echo "[~~] Resetting..."
 sudo dnsmasq stop >> /dev/null 2>&1
 sudo pkill dnsmasq >> /dev/null 2>&1
 sudo killall hostapd >> /dev/null 2>&1
 #sudo sysctl net.ipv4.ip_forward=0 >> /dev/null 2>&1
 echo "[~~] Restarting NetworkManager..."
 sudo service NetworkManager restart
} 
 
#get arguments
def_installUpdate(){
 sudo apt-get install hostapd
 sudo apt-get install dnsmasq
}



#begins

#wireless, internet interface


def_killAll
def_IpTablesFlush


#@@@@@ 1
read -p "[??] Input wireless adapter's name: (wlan0) " wlan_ap
wlan_ap=${wlan_ap:-wlan0}
read -p "[??] Input internet access point name: (eth0) " eth_ap
eth_ap=${eth_ap:-eth0}
#0

echo "[~~]configuring ifconfig..."
sudo ifconfig $wlan_ap up 10.0.0.1 netmask 255.255.255.0

#..IPTABLES 1
echo
echo "[~~] Configuring AP interface..."
sudo sysctl net.ipv4.ip_forward=1 >> /dev/null 2>&1
sudo iptables -t nat -A POSTROUTING -o eth_ap -j MASQUERADE
sudo iptables -A FORWARD -i eth_ap -o wlan_ap -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i wlan_ap -o eth_ap -j ACCEPT
#..IPTABLES 0

#dnsmasq 1
dnsmasq_txt="#disables dnsmasq reading other files like /etc/resolv.conf\nno-resolv\n\ninterface=$wlan_ap\n\n#Specify starting_range,end_range,lease_time\ndhcp-range=10.0.0.3,10.0.0.20,12h\n\n#dns addresses for clients\nserver=8.8.8.8\nserver=10.0.0.1\naddress=/#/10.0.0.1\nno-hosts"
sudo echo -e $dnsmasq_txt > /etc/dnsmasq.conf
#0

echo
#@@@@@ 1
read -p "[??] Input SSID name: (Free-Wifi) " ssid_ap
ssid_ap=${ssid_ap:-Free-Wifi}
read -p "[??] Input channel number: (4) " channel_ap
channel_ap=${channel_ap:-4}
#0

#hostapd 1
hostapd_txt="interface=$wlan_ap\n\nssid=$ssid_ap\n\nchannel=$channel_ap\n\ndriver=nl80211\n\nhw_mode=g\nmacaddr_acl=0\nauth_algs=1\nignore_broadcast_ssid=0"
sudo echo -e $hostapd_txt > $(pwd)/aa.conf
#0



#..start dnsmasq, hostapd.conf 1
echo
echo "[~~] Starting DNSMASQ server..."
sudo dnsmasq
echo "[~~] Starting HOSTAPD..."
sudo hostapd  $(pwd)/aa.conf
#0



def_killAll
def_IpTablesFlush
#..stop all, restart
