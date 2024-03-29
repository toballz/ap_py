#!/bin/bash

cwd=$(pwd)

if [ "$1" == "install" ];then
 echo "[!!] Installing DNAMASQ.."
 echo
 sudo apt-get install dnsmasq
 echo
 echo "[!!] Installing HOSTAPD.."
 echo
 sudo apt-get install hostapd
 echo
 echo "[!!] Installing DRIFTNET.."
 echo
 sudo apt-get install driftnet
 echo
 echo "[!!] Installing WIRESHARK.."
 echo
 sudo apt-get install wireshark
 echo
 echo "[!!] Installing DO2UNIX.."
 sudo apt-get install dos2unix
 echo
 echo "[!!] Attempt install finished."
 
 sudo rm /usr/local/bin/appy > /dev/null 2>&1
 sudo rm /usr/local/bin/appy_serv.py > /dev/null 2>&1
 sudo chmod +x ./a.py
 sudo mv a.py /usr/local/bin/appy
 sudo mv appy_serv.py /usr/local/bin/ > /dev/null 2>&1
 sudo dos2unix /usr/local/bin/appy > /dev/null 2>&1
fi


if [ "$1" == "" ];then
 echo "[install, update]"
fi
