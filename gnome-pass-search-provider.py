#!/usr/bin/python3
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
import re
import subprocess
from os import getenv
from os import walk
from os.path import expanduser
from os.path import join as path_join

import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

try:
    from thefuzz import fuzz
    from thefuzz import process
except ModuleNotFoundError:
    from fuzzywuzzy import fuzz
    from fuzzywuzzy import process
from gi.repository import GLib

# Convenience shorthand for declaring dbus interface methods.
# s.b.n. -> search_bus_name
search_bus_name = "org.gnome.Shell.SearchProvider2"
sbn = dict(dbus_interface=search_bus_name)


class SearchPassService(dbus.service.Object):
    """The pass search daemon.

    This service is started through DBus activation by calling the
    :meth:`Enable` method, and stopped with :meth:`Disable`.

    """

    bus_name = "org.gnome.Pass.SearchProvider"
    _object_path = "/" + bus_name.replace(".", "/")

    def __init__(self):
        self.session_bus = dbus.SessionBus()
        bus_name = dbus.service.BusName(self.bus_name, bus=self.session_bus)
        dbus.service.Object.__init__(self, bus_name, self._object_path)
        self.password_store = getenv("PASSWORD_STORE_DIR") or expanduser(
            "~/.password-store"
        )
        self.password_executable = getenv("PASSWORD_EXECUTABLE") or "pass"
        self.password_mode = getenv("PASSWORD_MODE") or "pass"
        self.clipboard_executable = getenv("CLIPBOARD_EXECUTABLE") or "wl-copy"
        self.disable_notifications = (
            getenv("DISABLE_NOTIFICATIONS", "false").lower() == "true"
        )
        # For checking if the database is unlocked yet:
        self.database_unlocked = True

    @dbus.service.method(in_signature="sasu", **sbn)
    def ActivateResult(self, id, terms, timestamp):
        if self.database_unlocked:
            self.send_password_to_clipboard(id)
        else:
            self.unlock_database()

    @dbus.service.method(in_signature="as", out_signature="as", **sbn)
    def GetInitialResultSet(self, terms):
        if self.password_mode == "bw":
            return self.get_bw_result_set(terms)
        else:
            return self.get_pass_result_set(terms)

    @dbus.service.method(in_signature="as", out_signature="aa{sv}", **sbn)
    def GetResultMetas(self, ids):
        return [
            dict(
                id=id,
                name=id[1:] if id.startswith(":") else id,
                gicon="dialog-password",
            )
            for id in ids
        ]

    @dbus.service.method(in_signature="asas", out_signature="as", **sbn)
    def GetSubsearchResultSet(self, previous_results, new_terms):
        if self.password_mode == "bw":
            return self.get_bw_result_set(new_terms)
        else:
            return self.get_pass_result_set(new_terms)

    @dbus.service.method(in_signature="asu", terms="as", timestamp="u", **sbn)
    def LaunchSearch(self, terms, timestamp):
        pass

    def unlock_database(self):
        if self.password_mode == "bw":
            subprocess.run([self.password_executable, "unlock"])

    def get_bw_result_set(self, terms):
        self.database_unlocked = not bool(subprocess.run(
            [self.password_executable, "unlocked"]
            ).returncode)

        if not self.database_unlocked:
            results = [f"Unlock {self.password_executable}"]

        else:
            if terms[0].startswith(":"):
                field = terms[0][1:]
                terms = terms[1:]
            else:
                field = None
            name = "".join(terms)

            password_list = subprocess.check_output(
                [self.password_executable, "list"], universal_newlines=True
            ).split("\n")[:-1]

            results = [
                e[0]
                for e in process.extract(
                    name, password_list, limit=5, scorer=fuzz.partial_ratio
                )
            ]
            if field is not None:
                results = [f":{field} {r}" for r in results]
        
        return results

    def get_pass_result_set(self, terms):
        if terms[0] == "otp":
            field = terms[0]
        elif terms[0].startswith(":"):
            field = terms[0][1:]
            terms = terms[1:]
        else:
            field = None

        name = "".join(terms)
        password_list = []
        for root, dirs, files in walk(self.password_store):
            dir_path = root[len(self.password_store) + 1 :]

            if dir_path.startswith("."):
                continue

            for filename in files:
                if filename[-4:] != ".gpg":
                    continue
                path = path_join(dir_path, filename)[:-4]
                password_list.append(path)

        results = [
            e[0]
            for e in process.extract(
                name, password_list, limit=5, scorer=fuzz.partial_ratio
            )
        ]
        if field == "otp":
            results = [f"otp {r}" for r in results]
        elif field is not None:
            results = [f":{field} {r}" for r in results]
        return results

    def get_value_from_output(self, output, field=None):
        if field is not None:
            match = re.search(
                rf"^{field}:\s*(?P<value>.+?)$", output, flags=re.I | re.M
            )
            if match:
                value = match.group("value")
            else:
                raise RuntimeError(f"The field {field} was not found in the password entry.")
        else:
            value = output.split("\n", 1)[0]
        return value

    def send_password_to_gpaste(self, base_args, name, field=None):
        gpaste = self.session_bus.get_object(
            "org.gnome.GPaste.Daemon", "/org/gnome/GPaste"
        )

        output = subprocess.check_output(base_args + [name], universal_newlines=True)
        value = self.get_value_from_output(output, field)
        try:
            gpaste.AddPassword(name, value, dbus_interface="org.gnome.GPaste1")
        except dbus.DBusException:
            gpaste.AddPassword(name, value, dbus_interface="org.gnome.GPaste2")

    def send_password_to_native_clipboard(self, base_args, name, field=None):
        if self.password_mode == "bw":
            output = subprocess.check_output(base_args + [name], universal_newlines=True)
            value = self.get_value_from_output(output, field)
            p1 = subprocess.run(self.clipboard_executable, input=value, text=True)
            if p1.returncode:
                raise RuntimeError(
                    f"Error while running copying to clipboard: got return code: {p1.returncode}."
                )
        else:
            if field is not None:
                raise RuntimeError("This feature requires GPaste.")
            result = subprocess.run(base_args + ["-c", name])
            if result.returncode:
                raise RuntimeError(
                    f"Error while running pass: got return code: {result.returncode}."
                )

    def send_password_to_clipboard(self, name):
        if name.startswith(":"):
            field, name = name.split(" ", 1)
            field = field[1:]
        else:
            field = None

        if self.password_mode == "bw":
            base_args = [self.password_executable, "get", "--full"]
        elif name.startswith("otp "):
            base_args = [self.password_executable, "otp", "code"]
            name = name[4:]
            field = None
        else:
            base_args = [self.password_executable, "show"]

        try:
            try:
                self.send_password_to_gpaste(base_args, name, field)
            except dbus.DBusException:
                # We couldn't join GPaste over D-Bus, use native clipboard
                self.send_password_to_native_clipboard(base_args, name, field)
            if "otp" in base_args:
                self.notify("Copied OTP password to clipboard:", body=f"<b>{name}</b>")
            elif field is not None:
                self.notify(
                    f"Copied field {field} to clipboard:", body=f"<b>{name}</b>"
                )
            else:
                self.notify("Copied password to clipboard:", body=f"<b>{name}</b>")
        except (subprocess.CalledProcessError, FileNotFoundError, RuntimeError) as e:
            self.notify("Failed to copy password or field!", body=str(e), error=True)

    def notify(self, message, body="", error=False):
        if not error and self.disable_notifications:
            return
        try:
            self.session_bus.get_object(
                "org.freedesktop.Notifications", "/org/freedesktop/Notifications"
            ).Notify(
                "Pass",
                0,
                "dialog-password",
                message,
                body,
                "",
                {"transient": False if error else True},
                0 if error else 3000,
                dbus_interface="org.freedesktop.Notifications",
            )
        except dbus.DBusException as err:
            print(f"Error {err} while trying to display {message}.")


if __name__ == "__main__":
    DBusGMainLoop(set_as_default=True)
    SearchPassService()
    GLib.MainLoop().run()
