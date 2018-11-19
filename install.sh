#!/usr/bin/env bash
set -eu -o pipefail
cd "$(dirname "$(realpath "${0}")")"

DATADIR=${DATADIR:-/usr/share}
LIBDIR=${LIBDIR:-/usr/lib}
LIBEXECDIR=${LIBEXECDIR:-/usr/lib/}
SYSCONFDIR=${SYSCONFDIR:-/etc}
PIPARGS=${PIPARGS:-} # use --user for local install

pip install ${PIPARGS} fuzzywuzzy

install -Dm 0755 gnome-pass-search-provider.py "${LIBEXECDIR}"/gnome-pass-search-provider/gnome-pass-search-provider.py

# Search provider definition
install -Dm 0644 conf/org.gnome.Pass.SearchProvider.ini "${DATADIR}"/gnome-shell/search-providers/org.gnome.Pass.SearchProvider.ini

# Desktop file
install -Dm 0644 conf/org.gnome.Pass.SearchProvider.desktop "${DATADIR}"/applications/org.gnome.Pass.SearchProvider.desktop

# DBus configuration
install -Dm 0644 conf/org.gnome.Pass.SearchProvider.service.dbus "${DATADIR}"/dbus-1/services/org.gnome.Pass.SearchProvider.service
install -Dm 0644 conf/org.gnome.Pass.SearchProvider.service.systemd "${LIBDIR}"/systemd/user/org.gnome.Pass.SearchProvider.service
