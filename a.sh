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
 echo "\n[~~] Stopping..."
 sudo dnsmasq stop
 sudo pkill dnsmasq
 sudo killall hostapd
 #sudo sysctl net.ipv4.ip_forward=0
 echo "[~~] Restarting NetworkManager..."
 sudo service NetworkManager restart
} 
 
#get arguments
def_installUpdate(){
 sudo apt-get install hostapd
 sudo apt-get install dnsmasq
 sudo apt-get install nano
}



#begins

#wireless, internet interface
wlan_ap="wlan0"
eth_ap="eth0"


def_killAll
def_IpTablesFlush

echo "[~~]configuring ifconfig..."
sudo ifconfig $wlan_ap up


#..IPTABLES 1
echo
echo "[~~] Configuring AP interface..."

sudo sysctl net.ipv4.ip_forward=1
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT
#..IPTABLES 0

#dnsmasq0
dnsmasq_txt="#disables dnsmasq reading any other files like /etc/resolv.conf\nno-resolv\n\ninterface=$wlan_ap\n\n#Specify starting_range,end_range,lease_time\ndhcp-range=10.0.0.3,10.0.0.20,12h\n\n#dns addresses for clients\nserver=8.8.8.8\nserver=10.0.0.1\nno-hosts"
sudo echo -e $dnsmasq_txt > /etc/dnsmasq.conf
#1





#..start dnsmasq, hostapd.conf 1
echo
echo "[~~] Starting DNSMASQ server..."
sudo dnsmasq
echo "[~~] Starting HOSTAPD..."
sudo hostapd  /home/l/hostapd.conf
#..start dnsmasq, hostapd.conf 0



def_killAll
def_IpTablesFlush
#..stop all, restart
