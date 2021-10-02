#!/usr/bin/python3
import os, sys
import random as rand
from argparse import ArgumentParser, ArgumentTypeError

try:
 #Flush iptables 1
 def flushIpTables():
  os.system("sudo iptables --flush")
  os.system("sudo iptables --table nat --flush")
  os.system("sudo iptables --delete-chain")
  os.system("sudo iptables --table nat --delete-chain")
  os.system("sudo iptables --flush -t nat")
  os.system("sudo iptables --table nat --delete-chain")
 #...0

 #write file function
 def write_file(path, s):
  os.system("sudo echo -e \""+s+"\" > "+path)
  os.system("sudo sed -i 's/\r//' "+path)
 #...0

 #kill stop all
 def killSall():
  print("")
  print("[~~] Stopping...")
  os.system("sudo pkill dnsmasq > /dev/null 2>&1")
  os.system("sudo killall hostapd > /dev/null 2>&1")
  os.system("sudo sysctl net.ipv4.ip_forward=0 > /dev/null 2>&1")
  print("[~~] Restarting Network-Manager...")
  os.system("sudo service NetworkManager restart")
  print("!done..")
  #...0

 ###################################################
 ###################################################
 os.system("sudo echo")

 wadapter = os.listdir('sys/class/net/')
 wlan_ap = input("[??] Input wireless adapter's name:("+os.listdir('sys/class/net/')[2]+") ") or wadapter[2]
 eth_ap = input("[??] Input internet access point name:("+os.listdir('sys/class/net/')[1]+") ") or wadapter[1]

 #..HOSTAPD CONFIG 1
 ssid = input("[??] Input ssid name:(Free-Wifi) ") or "Free-Wifi"
 rnd = rand.randint(1, 9)
 channel = input("[??] Input channel number:("+str(rnd)+") ") or str(rnd)

 hostapd_txt = "interface=" + wlan_ap + "\ndriver=nl80211\nssid=" + ssid + "\nhw_mode=g\nchannel=" + channel + "\nmacaddr_acl=0\nauth_algs=1\nignore_broadcast_ssid=0\n"
 print("")
 print("[~~] creating /hostapd.conf ...")
 write_file("/tmp/acp_hostapd.conf", hostapd_txt)
 #...0

 #..IPTABLES 1
 print("[~~] Configuring AP interface...")
 os.system("sudo ifconfig " + wlan_ap + " up 10.0.0.1 netmask 255.255.255.0")

 print("[~~] Applying iptables rules...")
 flushIpTables()
 os.system("sudo sysctl net.ipv4.ip_forward=1 > /dev/null 2>&1")
 os.system("sudo iptables --table nat --append POSTROUTING --out-interface " + eth_ap + " -j MASQUERADE")
 os.system("sudo iptables --append FORWARD --in-interface " + wlan_ap + " -j ACCEPT")
 os.system("sudo iptables -t nat -A POSTROUTING -o "+eth_ap+" -j MASQUERADE")
 #...0


 #..DNSMASQ CONFIG 3
 print("[~~] Creating /dnsmasq.conf...")
 os.system("sudo service NetworkManager restart")
 os.system("sudo pkill dnsmasq")
 dnsmasq_txt = "#disable etc/resolv.conf\nno-resolv\n\ninterface="+wlan_ap+"\n\n#starting_range,end_range,lease_time\ndhcp-range=10.0.0.3,10.0.0.20,12h\n\n#dns addresses to send to the clients\nserver=8.8.8.8\nserver=0.0.0.0\nno-hosts\n"
 #...2

 ###########################
 ###########################
 print("")
 ##Driftnet 1
 fiDriftnet = input("[!?] Use Driftnet (y/N): ")
 if(fiDriftnet == "y"):
  os.system("sudo driftnet -i "+wlan_ap+" &")
 ##wireshark 1
 fiwireshark = input("[!?] Use wireshark (y/N): ")
 if(fiwireshark == "y"):
  os.system("sudo wireshark -i "+wlan_ap+" -k > /dev/null 2>&1 &")
 ##captivePortal 1
 ficaptivePortal = input("[!?] Enable captivePortal (y/N): ")
 if(ficaptivePortal == "y"):
  dnsmasq_txt += "dhcp-option=3,10.0.0.1\ndhcp-option=6,10.0.0.1\naddress=/#/10.0.0.1\n"
  fihttpDirectory = input("[!?] HTTP Directory:(/var/www/html/) ") or "/var/www/html/"
  while(os.path.isdir(fihttpDirectory) == False):
   fihttpDirectory = input("[!?] Directory do not exist try again: ") or "/var/www/html/"
 #...0

#######...0

 #..DNSMASQ CONFIG 1
 write_file("/tmp/acp_dnsmasq.conf", dnsmasq_txt)
 input("[!!] Press Enter to continue: ")
 #...0
 
 if(ficaptivePortal == "y"):
  #start redirect http server:80 1
  print("")
  print("[~~] Starting http redirect server ...")
  os.system("sudo service apache2 stop > /dev/null 2>&1 &")
  os.system("kill -9 $(ps -A | grep python | awk '{print $1}')")
  os.system("python3 /usr/local/bin/acp_serv.py 80 http://10.0.0.1:233 > /dev/null 2>&1 &")
  #...0
  #start real http server:233 1
  print("[~~] Starting http main server ...")
  os.system("python3 -m http.server 233 --directory "+fihttpDirectory+" > /dev/null 2>&1 &")
 #$$$$$$$$$$$$$$$$
 print("[~~] Starting DNSMASQ server...")
 os.system("sudo pkill dnsmasq")
 os.system("sudo dnsmasq -C /tmp/acp_dnsmasq.conf")
 #stay wake video 1
 print("[~~] Starting stay awake video ...")
 os.system("vlc /usr/local/bin/acp_stay_awake.mp4 --loop > /dev/null 2>&1 &")
 #...0
 #start dnsmasq hostapd 1
 print("[~~] Starting HOSTAPD server...")
 print("")
 os.system("sudo killall hostapd > /dev/null 2>&1")
 os.system("sudo hostapd /tmp/acp_hostapd.conf")
 #...0

 #end all
 print("")
 flushIpTables()
 killSall()
 #...0
except:
 #..stop all
 flushIpTables()
 killSall()
 print("Error:-",sys.exc_info())
 #...0
