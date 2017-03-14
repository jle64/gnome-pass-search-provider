#!/usr/bin/env bash
set -eu -o pipefail
cd "$(dirname "$(realpath "${0}")")"

DATADIR='/usr/share'
LIBDIR='/usr/lib'
LIBEXECDIR='/usr/lib/'
SYSCONFDIR='/etc'

install -Dm 0755 daemon.py "${LIBEXECDIR}"/gnome-shell-search-pass/daemon.py

# Search provider definition
install -Dm 0644 conf/org.gnome.pass.search.ini "${DATADIR}"/gnome-shell/search-providers/org.gnome.pass.search.ini

# Desktop file
install -Dm 0644 conf/org.gnome.pass.search.desktop "${DATADIR}"/applications/org.gnome.pass.search.desktop

# DBus configuration
install -Dm 0644 conf/org.gnome.pass.search.service.dbus "${DATADIR}"/dbus-1/services/org.gnome.pass.search.service
install -Dm 0644 conf/org.gnome.pass.search.conf "${SYSCONFDIR}"/dbus-1/system.d/org.gnome.pass.search.conf
install -Dm 0644 conf/org.gnome.pass.search.service.systemd "${LIBDIR}"/systemd/user/org.gnome.pass.search.service
