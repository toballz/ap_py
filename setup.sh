#!/bin/bash

cwd=$(pwd)

if [ "$1" == "install" ];then
 sudo rm /usr/local/bin/acp
 sudo chmod +x ./a.py
 sudo mv a.py /usr/local/bin/acp
 dos2unix /usr/local/bin/acp
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
 echo "[!!] Attempt install finished."
fi


if [ "$1" == "" ];then
 echo "[install, update]"
fi
