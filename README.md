A search provider for Gnome-Shell that adds support for searching in [pass](https://www.passwordstore.org/).

Names of passwords will show up in Gnome-Shell searches, choosing one will copy the corresponding content to the clipboard.

![Sreencapture](misc/screencapture.gif)

# Installation
## Packages

*TODO*

## Manual

Ensure that python-gobject is installed on your system (probably already the case):
```shell
$PACKAGE_MANAGER install python-gobject
```

Download or clone this repository:
```shell
git clone git@github.com:jle64/gnome-shell-pass-search-provider.git
```

Run the installation script as root:
```shell
sudo ./install.sh
```

If you need to you can change the installation paths to suit your system:
```shell
sudo SYSCONFDIR=/etc DATADIR=/usr/share LIBDIR=/usr/lib LIBEXECDIR=/usr/lib ./install.sh
```

The search provider should show up and be enabled in Gnome search preferences and be autoloaded by Gnome-Shell.
If that's not the case try closing and reopening your Gnome session.

# Environment variables

If you are configuring pass through environment variables, such as `PASSWORD_STORE_DIR`, make sure to set them in a way that will propagate to the search provider executable.
If you are on a systemd-based system, you can set them in the unit file :

```shell
systemctl --user edit org.gnome.pass.search.service
```

Add your variables like this :
```ini
[Service]
Environment=PASSWORD_STORE_DIR=/my/passwords/path
```
Then restart the service :

```shell
systemctl --user restart org.gnome.pass.search.service
```

# Compatibility

This implements the `org.gnome.Shell.SearchProvider2` D-Bus API.
I'm not sure since when this has been in Gnome nor until when it will stay.
This works fine on Gnome 3.22 and I expect it will continue to work for some time with ulterior versions.

# Troubleshooting

If this does not work for you, make sure to look to wherever Gnome and D-Bus are logging for error messages (in the journal on systemd-using systems).
