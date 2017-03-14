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

# This project was based gnome-shell-search-github-repositories
# which itself was based fedmsg-notify
# Copyright (C) 2012 Red Hat, Inc.
# Author: Ralph Bean <rbean@redhat.com>
# Copyright (C) 2012 Red Hat, Inc.
# Author: Luke Macken <lmacken@redhat.com>

from subprocess import call
from os import walk, getenv
from os.path import expanduser
import re

from gi.repository import GLib

import dbus
import dbus.glib
import dbus.service

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

    _object_path = '/' + bus_name.replace('.', '/')
    __name__ = 'SearchPassService'

    def __init__(self):
        self.session_bus = dbus.SessionBus()
        bus_name = dbus.service.BusName(self.bus_name, bus=self.session_bus)
        dbus.service.Object.__init__(self, bus_name, self._object_path)
        self.password_store = getenv('PASSWORD_STORE_DIR') or \
                              expanduser('~/.password-store')

    @dbus.service.method(in_signature='sasu', **sbn)
    def ActivateResult(self, id, terms, timestamp):
        self.send_password_to_clipboard(id)

    @dbus.service.method(in_signature='as', out_signature='as', **sbn)
    def GetInitialResultSet(self, terms):
        return self.get_result_set(terms)

    @dbus.service.method(in_signature='as', out_signature='aa{sv}', **sbn)
    def GetResultMetas(self, ids):
        return [dict(id=id, name=id,) for id in ids]

    @dbus.service.method(in_signature='asas', out_signature='as', **sbn)
    def GetSubsearchResultSet(self, previous_results, new_terms):
        return self.get_result_set(new_terms)

    @dbus.service.method(in_signature='asu', terms='as', timestamp='u', **sbn)
    def LaunchSearch(self, terms, timestamp):
        # FIXME: unstable
        call(['qtpass'] + terms)

    def get_result_set(self, terms):
        names = []
        for term in terms:
            names += self.get_password_names(term)
        return set(names)

    def get_password_names(self, name):
        names = []
        for root, dirs, files in walk(self.password_store):
            dir_path = root[len(self.password_store) + 1 :]
            for file in files:
                file_path = '{0}/{1}'.format(dir_path, file)
                if re.match(r'.*{0}.*\.gpg$'.format(name),
                            file_path,
                            re.IGNORECASE):
                    names.append(file_path[:-4])
        return names

    def send_password_to_clipboard(self, name):
        call(['pass', 'show', '-c', name])

def main():
    service = SearchPassService()
    loop = GLib.MainLoop()
    loop.run()

if __name__ == '__main__':
    main()
