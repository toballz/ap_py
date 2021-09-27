import os, sys
import random as rand
from argparse import ArgumentParser, ArgumentTypeError

cwd = os.getcwd()+"/"
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

 wlan_ap = input("[??] Input wireless adapter's name:(wlan0) ") or "wlan0"
 eth_ap = input("[??] Input internet access point name:(eth0) ") or "eth0"

 #..DNSMASQ CONFIG 1
 print("")
 print("[~~] Creating /dnsmasq.conf...")
 os.system("sudo service NetworkManager restart")
 os.system("sudo pkill dnsmasq")
 dnsmasq_txt = "#disable dnsmasq reading other files ~ /etc/resolv.conf for nameservers\nno-resolv\n\ninterface="+wlan_ap+"\n\n#starting_range,end_range,lease_time\ndhcp-range=10.0.0.3,10.0.0.20,12h\n\n#dns addresses to send to the clients\nserver=8.8.8.8\nserver=10.0.0.1\nno-hosts\n"
 write_file(cwd+"dnsmasq.conf", dnsmasq_txt)
 #...0

 #..HOSTAPD CONFIG 1
 print("")
 ssid = input("[??] Input ssid name:(Free-Wifi) ") or "Free-Wifi"
 rnd = rand.randint(0, 9)
 channel = input("[??] Input channel number:("+str(rnd)+") ") or str(rnd)

 hostapd_txt = "interface=" + wlan_ap + "\ndriver=nl80211\nssid=" + ssid + "\nhw_mode=g\nchannel=" + channel + "\nmacaddr_acl=0\nauth_algs=1\nignore_broadcast_ssid=0\n"
 print("")
 print("[~~] creating /hostapd.conf ...")
 write_file(cwd+"hostapd.conf", hostapd_txt)
 #...0

 #..IPTABLES 1
 print("")
 print("[~~] Configuring AP interface...")
 os.system("sudo ifconfig " + wlan_ap + " up 10.0.0.1 netmask 255.255.255.0")

 print("[~~] Applying iptables rules...")
 flushIpTables()
 os.system("sudo sysctl net.ipv4.ip_forward=1 > /dev/null 2>&1")
 os.system("sudo iptables --table nat --append POSTROUTING --out-interface " + eth_ap + " -j MASQUERADE")
 os.system("sudo iptables --append FORWARD --in-interface " + wlan_ap + " -j ACCEPT")
 os.system("sudo iptables -t nat -A POSTROUTING -o "+eth_ap+" -j MASQUERADE")
 #...0

 ###########################
 ###########################
 #start dnsmasq hostapd 1
 print("")
 print("[~~] Starting DNSMASQ server...")
 os.system("sudo pkill dnsmasq")
 os.system("sudo dnsmasq -C "+cwd+"dnsmasq.conf")
 print("[~~] Starting HOSTAPD server...")
 print("")
 input("[!!] Press Enter to continue: ")
 #############driftnet 1
 print("")
 fiDriftnet = input("[!?] Use Driftnet (y/N): ")
 if(fiDriftnet == "y"):
  os.system("sudo driftnet -i "+wlan_ap+" &")
 ##...0
 ##wireshark 1
 fiwireshark = input("[!?] Use wireshark (y/N): ")
 if(fiwireshark == "y"):
  os.system("sudo wireshark -i "+wlan_ap+" -k &")    
 ###################...0
 print("")
 print("")
 os.system("sudo killall hostapd > /dev/null 2>&1")
 os.system("sudo hostapd "+cwd+"hostapd.conf")
 #...0

 #end all
 flushIpTables()
 killSall()
 #...0
except:
 #..stop all
 flushIpTables()
 killSall()
 print("Error:-",sys.exc_info())
 #...0