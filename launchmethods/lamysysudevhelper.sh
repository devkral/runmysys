#! /usr/bin/env bash

if [ "$#" != "2" ]; then
  echo "Warning: don't use if you haven't read the sourcecode of this program"
  echo "usage: $0 action path"
  exit 1
fi


DISPLAY=:0 /usr/bin/lamysys.py "$1" "$2/lamysys.ini"  #doesn't work because I don't find anything about this

/bin/umount "$2" 2> /dev/null
/bin/rmdir "$2" 2> /dev/null