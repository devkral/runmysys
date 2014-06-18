#! /usr/bin/env bash


# arg1: install/remove
# arg2: method
# arg3: (install rootdir)
# arg4: (program rootdir)
# arg5: (opt): username

userid=921 #"$(id -u "$username")"
username="runmysys"
usergroups="disk,video,audio,power,kvm"
filedir="/usr/share/runmysys"
#pidfilefolder="/run/runmysys"

help()
{
  echo "$0 install/uninstall method (install rootdir) (program rootdir)"
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

installmainfile()
{
if [ "$install" = "install" ]; then
  install -D -m755 "$projdir/runmysys.py"  "$1/runmysys.py"
  #sed -i -e "s|/run/runmysys/|$rootdir/$pidfilefolder|"
elif [ "$install" = "uninstall" ]; then
  rm "$1/runmysys.py"
fi
}
# $1 shell
createuser()
{
  if [ "$install" = "install" ]; then
    groupadd -g "$userid" "$username"
    if [ "$1" = "" ]; then
      useradd -g "$userid" -r -m -u "$userid" -G "$usergroups"   "$username"
    else
      useradd -g "$userid" -r -m -u "$userid" -G "$usergroups" -s"$1"  "$username"
    fi
    
  elif [ "$install" = "uninstall" ]; then
    userdel -r "$username"
  fi
}

udevinstall()
{
  installmainfile "$rootdir/usr/bin/"
  if [ "$install" = "install" ]; then
    install -D -m755 "$projdir/launchmethods/runmysysudevhelper.sh" "$rootdir$filedir/runmysysudevhelper.sh"
    sed -i -e "s|replacebyuid|$userid|g" "$rootdir$filedir/runmysysudevhelper.sh"
    sed -i -e "s|/usr/bin/runmysys.py|$destrootdir/usr/bin/runmysys.py|g" "$rootdir$filedir/runmysysudevhelper.sh"
	install -D -m755 "$projdir/launchmethods/11-runmysys-start.rules"  "$rootdir/etc/udev/rules.d/11-runmysys-start.rules"
    sed -i -e "s|uid=921|uid=$userid|g" -e "s|/usr/share/runmysys/|$filedir|g" "$rootdir/etc/udev/rules.d/11-runmysys-start.rules"
	
  elif [ "$install" = "uninstall" ]; then
    rm -r "$rootdir$filedir"
    rm "$rootdir/etc/udev/rules.d/11-runmysys-start.rules"
  fi
	
	
}

autostartallusers()
{
  installmainfile "$rootdir/usr/bin/"
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

autostartdesktop()
{
  installmainfile "$rootdir/usr/bin/"
  if [ "$install" = "install" ]; then
    install -D -m755 "$projdir/launchmethods/lookformounted.sh" "$rootdir$filedir/lookformounted.sh"
    sed -i -e "s|/usr/bin/runmysys.py|$destrootdir/usr/bin/runmysys.py|g" "$rootdir$filedir/lookformounted.sh"
    install -D -m755 "$projdir/launchmethods/runmysysautostart.desktop"  "$rootdir/home/$username/.config/autostart/runmysysautostart.desktop"
    sed -i -e "s|/usr/share/runmysys/|$filedir|g" "$rootdir/home/$username/.config/autostart/runmysysautostart.desktop"
  elif [ "$install" = "uninstall" ]; then
    rm -r "$rootdir$filedir"
    rm "$rootdir/home/$username/.config/autostart/runmysysautostart.desktop"
  fi
}
autostartthisuser()
{
  if [ "$rootdir" = "" ]; then
    rootdir=~/".local/share/runmysys"
  fi
  installmainfile "$rootdir"
  if [ "$install" = "install" ]; then
    install -D -m755 "$projdir/launchmethods/lookformounted.sh" "$rootdir/lookformounted.sh"
    sed -i -e "s|/usr/bin/runmysys.py|$rootdir/runmysys.py|g" "$rootdir/lookformounted.sh"
    install -D -m755 "$projdir/launchmethods/runmysysautostart.desktop"  ~/".config/autostart/runmysysautostart.desktop"
    sed -i -e "s|/usr/share/runmysys/|$rootdir/|g" ~/".config/autostart/runmysysautostart.desktop"
  elif [ "$install" = "uninstall" ]; then
    rm -r "$rootdir"
    rm ~/".config/autostart/runmysysautostart.desktop"
  fi
}



userautostartshell()
{
  installmainfile "$rootdir/usr/bin/"
  if [ "$install" = "install" ]; then
    install -D -m755 "$projdir/launchmethods/lookformounted.sh" "$rootdir$filedir/lookformounted.sh"
    sed -i -e "s|/usr/bin/runmysys.py|$destrootdir/usr/bin/runmysys.py|g" "$rootdir$filedir/lookformounted.sh"
    createuser "bash"
    cat "exec $rootdir$filedir/lookformounted.sh" >> "$rootdir/home/${username}/.xinitrc"
  elif [ "$install" = "uninstall" ]; then
    rm -r "$rootdir$filedir"
  fi
}

systemd()
{
  installmainfile "$rootdir/usr/bin/"
  if [ "$install" = "install" ]; then
    install -D -m755 "$projdir/launchmethods/lookformounted.sh" "$rootdir$filedir/lookformounted.sh"
    sed -i -e "s|/usr/bin/runmysys.py|$destrootdir/usr/bin/runmysys.py|g" "$rootdir$filedir/lookformounted.sh"
    install -D -m755 "$projdir/launchmethods/runmysysd.service"  "$rootdir/etc/xdg/autostart/runmysysd.service"
    sed -i -e "s|/usr/share/runmysys/|$filedir|g" "$rootdir/etc/xdg/autostart/runmysysautostart.desktop"
  elif [ "$install" = "uninstall" ]; then
    rm -r "$rootdir$filedir"
    rm "$rootdir/etc/xdg/autostart/runmysysautostart.desktop"
  fi
}











case "$method" in
"udev")udevinstall;; #doesn't work !!!!!!
"autostartallusers")autostartallusers;;
"userautostartshell")userautostartshell;; #TODO: x environment?
"userautostartdesktop")userautostartdesktop;;
"autostartthisuser")autostartthisuser;;
"systemd")systemd;; #not implemented

"createuserb")createuser "/bin/bash";;

*) help;;
esac



