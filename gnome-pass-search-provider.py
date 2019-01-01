#!/usr/bin/env python3
# This file is a part of gnome-pass-search-provider.
#
# gnome-pass-search-provider is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# gnome-pass-search-provider is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gnome-pass-search-provider. If not, see
# <http://www.gnu.org/licenses/>.

# Copyright (C) 2017 Jonathan Lestrelin
# Author: Jonathan Lestrelin <jonathan.lestrelin@gmail.com>

# This project was based on gnome-shell-search-github-repositories
# Copyright (C) 2012 Red Hat, Inc.
# Author: Ralph Bean <rbean@redhat.com>
# which itself was based on fedmsg-notify
# Copyright (C) 2012 Red Hat, Inc.
# Author: Luke Macken <lmacken@redhat.com>

from fuzzywuzzy import process, fuzz
from os import getenv
from os import walk
from os.path import expanduser
from os.path import join as path_join
import re
import subprocess

import dbus
import dbus.glib
import dbus.service
from gi.repository import GLib

# Convenience shorthand for declaring dbus interface methods.
# s.b.n. -> search_bus_name
search_bus_name = 'org.gnome.Shell.SearchProvider2'
sbn = dict(dbus_interface=search_bus_name)


class SearchPassService(dbus.service.Object):
    """ The pass search daemon.

    This service is started through DBus activation by calling the
    :meth:`Enable` method, and stopped with :meth:`Disable`.

    """
    bus_name = 'org.gnome.Pass.SearchProvider'

    _object_path = '/' + bus_name.replace('.', '/')

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
        pass

    def get_result_set(self, terms):
        name = ''.join(terms)
        password_list = []

        for root, dirs, files in walk(self.password_store):
            dir_path = root[len(self.password_store) + 1:]

            if dir_path.startswith('.'):
                continue

            for filename in files:
                if filename[-4:] != '.gpg':
                    continue
                path = path_join(dir_path, filename)[:-4]
                password_list.append(path)

        return [entry[0] for entry in process.extract(name,
                                                      password_list,
                                                      scorer=fuzz.partial_ratio,
                                                      limit=5)]

    def send_password_to_gpaste(self, name):
        try:
            pass_output = subprocess.check_output(
                ['pass', 'show', name],
                stderr=subprocess.STDOUT,
                text=True
            )
            password = pass_output.split('\n', 1)[0]

            self.session_bus.get_object(
                'org.gnome.GPaste.Daemon',
                '/org/gnome/GPaste'
            ).AddPassword(
                name,
                password,
                dbus_interface='org.gnome.GPaste1'
            )
            self.notify('Password {} copied to clipboard.'.format(name))

        except subprocess.CalledProcessError as error:
            self.notify('Failed to copy password!', body=error.output, error=True)

    def send_password_to_native_clipboard(self, name):
        pass_cmd = subprocess.run(['pass', 'show', '-c', name])

        if pass_cmd.returncode:
            self.notify('Failed to copy password!', error=True)
        else:
            self.notify('Password {} copied to clipboard.'.format(name))

    def send_password_to_clipboard(self, name):
        try:
            self.send_password_to_gpaste(name)
        except dbus.DBusException:
            # We couldn't join GPaste over D-Bus,
            # use pass native clipboard copy
            self.send_password_to_native_clipboard(name)

    def notify(self, message, body='', error=False):
        try:
            self.session_bus.get_object(
                'org.freedesktop.Notifications',
                '/org/freedesktop/Notifications'
            ).Notify(
                'Pass',
                0,
                '',
                message,
                body,
                '',
                {'transient': False if error else True},
                0 if error else 3000,
                dbus_interface='org.freedesktop.Notifications'
            )
        except dbus.DBusException as err:
            print('Got error {} while trying to display message {}.'.format(
                err, message))


def main():
    SearchPassService()
    GLib.MainLoop().run()


if __name__ == '__main__':
    main()
