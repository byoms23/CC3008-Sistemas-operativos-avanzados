#!/bin/sh
#
# $FreeBSD: src/etc/rc.d/byOSbsd 
# 

# PROVIDE: inetd
# REQUIRE: python
# KEYWORD: shutdown

. /etc/rc.subr

name="byOS"
command="python /home/byron/CC3008-Sistemas-operativos-avanzados/webServer.py"
pidfile="/var/run/${name}.pid"

load_rc_config $name
run_rc_command $1
