A search provider for Gnome-Shell that adds support for searching in [pass](https://www.passwordstore.org/).

Names of passwords will show up in Gnome-Shell searches, choosing one will copy the corresponding content to the clipboard.

# Installation
## Packages

*TODO*

## Manual

Ensure that python-gobject is installed on your system (probably already the case) :

`$PACKAGE_MANAGER install python-gobject`

Download or clone this repository :

`git clone git@github.com:jle64/gnome-shell-pass-search-provider.git`

Run the installation script as root :

`sudo ./install.sh`

If you need to you can change the installation paths :

`sudo SYSCONFDIR=/etc DATADIR=/usr/share LIBDIR=/usr/lib LIBEXECDIR=/usr/lib ./install.sh`

# Compatibility

This implements the `org.gnome.Shell.SearchProvider2` D-Bus API. I'm not sure since when this has been in Gnome nor until when it will stay. This works fine on Gnome 3.22 and I expect it will continue to work for some time with ulterior versions.