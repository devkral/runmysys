#! /usr/bin/env bash

mountlookdir="/run/media/$(whoami)" #$(id -u)"

tempwalker=""
countwalker="0"
alreadywalked=""
countwalked="0"

for ((; ;))
do
  if [ -d "$mountlookdir" ]; then
    tempwalker="$(ls "$mountlookdir")"
    countwalker="$(echo "$tempwalker" | wc -w)"
    countwalked="$(echo "$alreadywalked" | wc -w)"
    if [ "$countwalked" -ne "$countwalker"  ]; then
      if [ "$countwalked" -lt "$countwalker" ]; then
        for dirobject in $tempwalker
        do
          if [ -d "$mountlookdir/${dirobject}" ]; then
            /usr/bin/lamysys.py "start" "$mountlookdir/${dirobject}/lamysys.ini"
          fi
        done
      else
        for dirobject in $alreadywalked
        do
          if ! echo "$countwalked" | grep -n "$dirobject" && [ -d "$mountlookdir/${dirobject}" ]; then
            /usr/bin/lamysys.py "stop" "$mountlookdir/${dirobject}/lamysys.ini"
          fi
        done
      fi
      alreadywalked="$tempwalker"
    fi
  fi
  sleep 4
done