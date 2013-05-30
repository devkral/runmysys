#! /usr/bin/env bash

# arg1: rootdir
# arg2: install/remove
# arg3: method
# arg4 (opt): username
# arg5 (opt): usrdir DON'T USE!!!!!!

userid=921 #"$(id -u "$username")"
username="lamysys"
filedir="/usr/share/lamysys"

help()
{
  echo "help"
  exit 1
}


if [ "$#" -le 3 ]; then
  help
fi

projdir="$(dirname "$0")"

rootdir="$(realpath($1))"
if [ "$rootdir" = "/" ]; then
  rootdir=""
fi

install="$2"
method="$3"
if [ "$4" != "" ]; then
  username="$4"
fi
if [ "$5" != "" ]; then
  filedir="$5"
fi

if [ "$install" = "useradd" ]; then
  useradd -u "$userid" "$username"
elif [ "$install" = "userdel" ]; then
  userdel "$username"
elif [ "$install" = "install" ]; then
  install -D -m755 "$projdir/lamysys.py"  "$rootdir/usr/bin/lamysys.py"
elif [ "$install" = "uninstall" ]; then
  rm "$rootdir/usr/bin/lamysys.py"
fi




udevinstall()
{
  if [ "$install" = "install" ]; then
    install -D -m755 "$projdir/launchmethods/lamysysudevhelper.sh" "$rootdir$filedir/lamysysudevhelper.sh"
	install -D -m755 "$projdir/launchmethods/11-lamysys-start.rules"  "$rootdir/etc/udev/rules.d/11-lamysys-start.rules"
    sed -i -e "s|uid=921|uid=$userid|" -e "s|/usr/share/lamysys/|$filedir|"
  elif [ "$install" = "uninstall" ]; then
    rm -r "$rootdir$filedir"
    rm "$rootdir/etc/udev/rules.d/11-lamysys-start.rules"
  fi
	
	
}

autostart()
{
  if [ "$install" = "install" ]; then
    
  elif [ "$install" = "uninstall" ]; then
  
  fi
}



















case "$method" in
"udev")udevinstall;;
"autostart")autostart;;

*) help;;
esac



