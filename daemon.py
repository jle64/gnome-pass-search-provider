#!/usr/bin/env python3
# This file is a part of gnome-shell-search-pass.
#
# gnome-shell-search-pass is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# gnome-shell-search-passs is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with search-pass.  If not, see
# <http://www.gnu.org/licenses/>.

# Copyright (C) 2017 Jonathan Lestrelin
# Author: Jonathan Lestrelin <jonathan.lestrelin@gmail.com>

# This project was based on a fork from gnome-shell-search-github-repositories
# which itself was based on a fork from fedmsg-notify
# Copyright (C) 2012 Red Hat, Inc.
# Author: Ralph Bean <rbean@redhat.com>
# Copyright (C) 2012 Red Hat, Inc.
# Author: Luke Macken <lmacken@redhat.com>

import dbus
import dbus.glib
import dbus.service

from gi.repository import Gio, GLib

config_tool = "gnome-shell-search-pass-config"

# Convenience shorthand for declaring dbus interface methods.
# s.b.n. -> search_bus_name
search_bus_name = 'org.gnome.Shell.SearchProvider2'
sbn = dict(dbus_interface=search_bus_name)


class SearchPassService(dbus.service.Object):
    """ The pass search daemon.

    This service is started through DBus activation by calling the
    :meth:`Enable` method, and stopped with :meth:`Disable`.

    """
    bus_name = 'org.gnome.pass.search'
    enabled = False

    _search_cache = {}
    _request_cache = {}

    _object_path = '/%s' % bus_name.replace('.', '/')
    __name__ = "SearchPassService"

    def __init__(self):
        self.settings = Gio.Settings.new(self.bus_name)
        if not self.settings.get_boolean('enabled'):
            return

        self.session_bus = dbus.SessionBus()
        bus_name = dbus.service.BusName(self.bus_name, bus=self.session_bus)
        dbus.service.Object.__init__(self, bus_name, self._object_path)
        self.enabled = True

    @dbus.service.method(in_signature='s', **sbn)
    def ActivateResult(self, search_id):
        print(search_id)

    @dbus.service.method(in_signature='as', out_signature='as', **sbn)
    def GetInitialResultSet(self, terms):
        for term in terms:
            print(term)
        return []

    @dbus.service.method(in_signature='as', out_signature='aa{sv}', **sbn)
    def GetResultMetas(self, ids):
        print(ids)
        return [dict(
            id=id,
            name=id.split(":")[0].split('/')[-1],
        ) for id in ids]

    @dbus.service.method(in_signature='asas', out_signature='as', **sbn)
    def GetSubsearchResultSet(self, previous_results, new_terms):
        print(previous_results + new_terms)
        return []

def main():
    service = SearchPassService()
    loop = GLib.MainLoop()
    loop.run()

if __name__ == '__main__':
    main()
