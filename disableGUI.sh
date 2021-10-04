if [ $1 == '-e' ];then
	sudo systemctl set-default graphical.target
elif [ $1 == '-d' ];then
	sudo systemctl set-default multi-user.target
else
	echo  $1
	echo "[ -e | -d ]"
fi
