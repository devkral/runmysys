#! /usr/bin/env bash


# arg1: install/remove
# arg2: method
# arg3: (rootdir)
# arg5 (opt): usrdir DON'T USE!!!!!!
# arg4 (opt): username

userid=921 #"$(id -u "$username")"
username="lamysys"
filedir="/usr/share/lamysys"

help()
{
  echo "$0 install/remove method (rootdir)"
  exit 1
}


if [ "$#" -lt 2 ]; then
  help
fi

projdir="$(dirname "$0")"



install="$1"
method="$2"
rootdir="$(realpath($3))"
if [ "$rootdir" = "/" ]; then
  rootdir=""
fi

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
    sed -i -e "s|uid=921|uid=$userid|" -e "s|/usr/share/lamysys/|$filedir|" "$rootdir/etc/udev/rules.d/11-lamysys-start.rules"
  elif [ "$install" = "uninstall" ]; then
    rm -r "$rootdir$filedir"
    rm "$rootdir/etc/udev/rules.d/11-lamysys-start.rules"
  fi
	
	
}

autostart()
{
  if [ "$install" = "install" ]; then
    install -D -m755 "$projdir/launchmethods/lookformount.sh" "$rootdir$filedir/lookformount.sh"
    install -D -m755 "$projdir/launchmethods/lamysysautostart.desktop"  "$rootdir/etc/xdg/autostart/lamysysautostart.desktop"
    sed -i -e "s|/usr/share/lamysys/|$filedir|" "$rootdir/etc/xdg/autostart/lamysysautostart.desktop"
  elif [ "$install" = "uninstall" ]; then
    rm -r "$rootdir$filedir"
    rm "$rootdir/etc/xdg/autostart/lamysysautostart.desktop"
  fi
}



















case "$method" in
"udev")udevinstall;;
"autostart")autostart;;

*) help;;
esac



