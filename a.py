#!/usr/bin/python3
import os, sys, socket, subprocess
import random as rand
from argparse import ArgumentParser, ArgumentTypeError

try:
 #Flush iptables 1
 def flushIpTables():
  print("[~~] Flushing IP Tables...")
  os.system("sudo iptables --flush;\
	sudo iptables --table nat --flush;\
	sudo iptables --delete-chain;\
	sudo iptables --table nat --delete-chain;\
	sudo iptables --flush -t nat;\
	sudo iptables --table nat --delete-chain")
 #...0

 #write file function
 def write_file(path, s):
   def _run_cmd_write(cmd_args, s):
    # write a file using sudo
    p = subprocess.Popen(cmd_args,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                shell=False, universal_newlines=True)
    p.stdin.write(s)
    p.stdin.close()
    p.wait()
   _run_cmd_write(("/usr/bin/sudo", "/usr/bin/tee", path), s)
   os.system("sudo sed -i 's/\r//' "+path+";\
   	 sudo dos2unix "+path+" > /dev/null 2>&1")
 #...0

 #kill stop all
 def killSall():
  print("")
  print("[~~] Stopping...")
  flushIpTables()
  os.system("sudo pkill dnsmasq > /dev/null 2>&1;\
	sudo killall hostapd > /dev/null 2>&1;\
	sudo sysctl net.ipv4.ip_forward=0 > /dev/null 2>&1")
  print("[~~] Killing http server...")
  os.system("kill -9 $(ps -A | grep python | awk '{print $1}') > /dev/null 2>&1 &")
  
  #..Network.conf 1
  print("[~~] Restoring backup NetworkManager.conf...")
  os.system("sudo rm /etc/NetworkManager/NetworkManager.conf > /dev/null 2>&1")
  os.system("sudo mv /etc/NetworkManager/NetworkManager.conf.acp_backup /etc/NetworkManager/NetworkManager.conf > /dev/null 2>&1")
  print("[~~] Restarting Network-Manager...")
  os.system("sudo service NetworkManager restart")
  #...0
  print("!done..")
  #...0

 ###################################################
 ###################################################
 os.system("sudo echo")

 wadapter = socket.if_nameindex()
 wlan_ap = input("[??] Input wireless adapter's name:("+wadapter[2][1]+") ") or wadapter[2][1]
 eth_ap = input("[??] Input internet access point name:("+wadapter[1][1]+") ") or wadapter[1][1]

 #..HOSTAPD CONFIG 1
 ssid = input("[??] Input ssid name:(Free-Wifi) ") or "Free-Wifi"
 rnd = rand.randint(1, 9)
 channel = input("[??] Input channel number:("+str(rnd)+") ") or str(rnd)

 print("")
 print("[~~] creating /hostapd.conf ...")
 hostapd_txt = "interface="+wlan_ap+"\ndriver=nl80211\nssid=" + ssid + "\nhw_mode=g\nchannel=" + channel + "\nmacaddr_acl=0\nauth_algs=1\nignore_broadcast_ssid=0\n"
 write_file("/tmp/acp_hostapd.conf", hostapd_txt)
 #...0

 #..DNSMASQ CONFIG 1
 print("[~~] Creating /dnsmasq.conf...") 
 os.system("sudo pkill dnsmasq")
 dnsmasq_txt = "#disable etc/resolv.conf\nno-resolv\n\ninterface="+wlan_ap+"\n\n#starting_range,end_range,lease_time\ndhcp-range=10.0.0.3,10.0.0.20,12h\n\n#dns addresses to send to the clients\nserver=8.8.8.8\nserver=8.8.4.4\nno-hosts\n"
 write_file("/tmp/acp_dnsmasq.conf", dnsmasq_txt)
 #...0

 #..Network.conf 1
 print("[~~] Backing up NetworkManager.conf...")
 os.system("sudo mv /etc/NetworkManager/NetworkManager.conf /etc/NetworkManager/NetworkManager.conf.acp_backup > /dev/null 2>&1;")
 networkManager_txt = "[main]\nplugins=keyfile\n\n[keyfile]\nunmanaged-devices=interface-name:"+wlan_ap+"\n"
 print("[~~] Editing NetworkManager.conf...")
 write_file("/etc/NetworkManager/NetworkManager.conf", networkManager_txt)
 os.system("sudo service NetworkManager restart")
 #...0

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
  fihttpDirectory = input("[!?] HTTP Directory:(/var/www/html/) ") or "/var/www/html/"
  while(os.path.isdir(fihttpDirectory) == False):
   fihttpDirectory = input("[!?] Directory do not exist try again: ") or "/var/www/html/"
 #...0
#############...0
#############...0
 
 #..IPTABLES 1
 print("")
 flushIpTables()
 print("[~~] Configuring AP interface...")
 os.system("sudo ifconfig " + wlan_ap + " up 10.0.0.1 netmask 255.255.255.0")

 print("[~~] Applying iptables rules...")
 if(ficaptivePortal == "y"):
  os.system("sudo iptables -t nat -A PREROUTING -i "+wlan_ap+"  -p tcp --dport 80 -j DNAT  --to-destination  10.0.0.1;\
	sudo iptables -t nat -A PREROUTING -i "+wlan_ap+" -p tcp --dport 430 -j DNAT --to-destination  10.0.0.1;\
	sudo iptables -t nat -A POSTROUTING -j MASQUERADE")
 else:
  os.system("sudo sysctl net.ipv4.ip_forward=1 > /dev/null 2>&1;\
	sudo iptables --table nat --append POSTROUTING --out-interface " + eth_ap + " -j MASQUERADE;\
	sudo iptables --append FORWARD --in-interface " + wlan_ap + " -j ACCEPT;\
	sudo iptables -t nat -A POSTROUTING -o "+eth_ap+" -j MASQUERADE")
 #...0
 
 print("")
 input("[!!] Press Enter to continue: ")
 
 if(ficaptivePortal == "y"):
  #start redirect http server:80 1
  print("[~~] Starting http redirect server:80 ...")
  os.system("sudo service apache2 stop > /dev/null 2>&1;\
	kill -9 $(ps -A | grep python | awk '{print $1}') > /dev/null 2>&1;\
	python3 /usr/local/bin/acp_serv.py 80 http://10.0.0.1:233 > /dev/null 2>&1 &")
  #...0
  #start real http server:233 1
  print("[~~] Starting http homepage server:233 ...")
  os.system("python3 -m http.server 233 --directory "+fihttpDirectory+" > /dev/null 2>&1 &")
  #...0
 #$$$$$$$$$$$$$$$$


 #start dnsmasq hostapd 1
 print("[~~] Starting DNSMASQ server...")
 os.system("sudo pkill dnsmasq;\
	sudo dnsmasq -C /tmp/acp_dnsmasq.conf")
 print("[~~] Starting HOSTAPD server...")
 os.system("sudo killall hostapd > /dev/null 2>&1;\
	sudo hostapd /tmp/acp_hostapd.conf")
 #...0

 #end all 1
 killSall()
 #...0
except:
 #..stop all 1
 print("")
 killSall()
 print("Error:-",sys.exc_info())
 #...0
