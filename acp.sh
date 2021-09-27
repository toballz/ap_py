#!/bin/bash

cwd=$(pwd)
mbasenameEx=`basename "$0"`

if [ "$1" == "install" ];then
 sudo rm /usr/local/bin/acp
 sudo chmod +x $cwd/$mbasenameEx
 cp ./acp.sh acp
 sudo mv ./acp /usr/local/bin/

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

if [ "$1" == "update" ];then
 echo "[!!] Updating DNAMASQ.."
 echo
 sudo apt-get install dnsmasq
 echo
 echo "[!!] Updating HOSTAPD.."
 echo
 sudo apt-get install hostapd
 echo
 echo "[!!] Updating DRIFTNET.."
 echo
 sudo apt-get install driftnet
 echo
 echo "[!!] Updating WIRESHARK.."
 echo
 sudo apt-get install wireshark
 echo
 echo "[!!] Attempt update completed."
fi

ext="$(echo $mbasenameEx | cut -d'.' -f2)"

if [ "$ext" == "sh" ];then
 echo "[install, update]"
else
 python3 $cwd/a.py
fi
