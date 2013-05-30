#! /usr/bin/env bash


# arg1: install/remove
# arg2: method
# arg3: (rootdir)
# arg4: (effektive rootdir)
# arg5: (opt): username

userid=921 #"$(id -u "$username")"
username="runmysys"
filedir="/usr/share/runmysys"

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

rootdir=""
if [ "$3" != "" ]; then
  rootdir="$(realpath "$3")"
  if [ "$rootdir" = "/" ]; then
    rootdir=""
  fi
fi

destrootdir=""
if [ "$4" != "" ]; then
  destrootdir="$(realpath "$4")"
  if [ "$destrootdir" = "/" ]; then
    destrootdir=""
  fi
fi

if [ "$5" != "" ]; then
  username="$5"
fi

if [ "$install" = "useradd" ]; then
  useradd -u "$userid" "$username"
elif [ "$install" = "userdel" ]; then
  userdel "$username"
elif [ "$install" = "install" ]; then
  install -D -m755 "$projdir/runmysys.py"  "$rootdir/usr/bin/runmysys.py"
elif [ "$install" = "uninstall" ]; then
  rm "$rootdir/usr/bin/runmysys.py"
fi




udevinstall()
{
  if [ "$install" = "install" ]; then
    install -D -m755 "$projdir/launchmethods/runmysysudevhelper.sh" "$rootdir$filedir/runmysysudevhelper.sh"
    sed -i -e "s|/usr/bin/runmysys.py|$destrootdir/usr/bin/runmysys.py|g" "$rootdir$filedir/runmysysudevhelper.sh"
	install -D -m755 "$projdir/launchmethods/11-runmysys-start.rules"  "$rootdir/etc/udev/rules.d/11-runmysys-start.rules"
    sed -i -e "s|uid=921|uid=$userid|g" -e "s|/usr/share/runmysys/|$filedir|g" "$rootdir/etc/udev/rules.d/11-runmysys-start.rules"
  elif [ "$install" = "uninstall" ]; then
    rm -r "$rootdir$filedir"
    rm "$rootdir/etc/udev/rules.d/11-runmysys-start.rules"
  fi
	
	
}

autostart()
{
  if [ "$install" = "install" ]; then
    install -D -m755 "$projdir/launchmethods/lookformounted.sh" "$rootdir$filedir/lookformounted.sh"
    sed -i -e "s|/usr/bin/runmysys.py|$destrootdir/usr/bin/runmysys.py|g" "$rootdir$filedir/lookformounted.sh"
    install -D -m755 "$projdir/launchmethods/runmysysautostart.desktop"  "$rootdir/etc/xdg/autostart/runmysysautostart.desktop"
    sed -i -e "s|/usr/share/runmysys/|$filedir|g" "$rootdir/etc/xdg/autostart/runmysysautostart.desktop"
  elif [ "$install" = "uninstall" ]; then
    rm -r "$rootdir$filedir"
    rm "$rootdir/etc/xdg/autostart/runmysysautostart.desktop"
  fi
}



















case "$method" in
"udev")udevinstall;; #doesn't work !!!!!!
"autostart")autostart;;

*) help;;
esac



