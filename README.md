A search provider for GNOME Shell that adds support for searching passwords in zx2c4/[pass](https://www.passwordstore.org/) or in the [rbw](https://github.com/doy/rbw) Bitwarden/Vaultwarden client.

Names of passwords will show up in GNOME Shell searches, choosing one will copy the corresponding content to the clipboard.

Can use the [GPaste](https://github.com/Keruspe/GPaste) clipboard manager, supports OTP and fields (pass only, requires GPaste).

![Sreencapture](misc/screencapture.gif)

# Installation
[![Packaging status](https://repology.org/badge/vertical-allrepos/gnome-pass-search-provider.svg)](https://repology.org/project/gnome-pass-search-provider/versions)

## Arch Linux
Install `gnome-pass-search-provider-git` from the AUR.

## Debian, Ubuntu and derivatives
If a package is available for your distribution version (see above for packaging status), just install `gnome-pass-search-provider` through APT:

```
apt install gnome-pass-search-provider
```

## Fedora

[![Copr build status](https://copr.fedorainfracloud.org/coprs/jle64/gnome-pass-search-provider/package/gnome-pass-search-provider/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/jle64/gnome-pass-search-provider/package/gnome-pass-search-provider/)

Enable the copr repo and install the package with DNF:

```
dnf copr enable jle64/gnome-pass-search-provider
dnf install gnome-pass-search-provider
```

## Manual

Ensure that python>=3.7 as well as the dbus, gobject and thefuzz (formerly fuzzywuzzy, might still be packaged under that name in your distribution) Python modules are installed. They should all be packaged under python-name or python3-name depending on your distribution.

Clone this repository and run the installation script as root:
```
git clone https://github.com/jle64/gnome-pass-search-provider.git
cd gnome-pass-search-provider
sudo ./install.sh
```

# Post-installation

Log out and reopen your GNOME session.

The search provider will be loaded automatically when doing a search.

You should see it enabled in GNOME Settings, in the Search pane. This is also where you can move it up or down in the list of results relatively to other search providers.

# Fields

To copy other values than the password in the first line from a pass file, start the search with `:NAME search...`. The field name must be a full but case insensitive match. This requires `GPaste`.

For example with a pass file like:
```
SUPERSECRETPASSWORD
user: username
pin: 123456
```

To copy the pin start the search with `:pin` and for the username with `:user`.

# OTP

The [pass-otp](https://github.com/tadfisher/pass-otp) extension is supported. Searches starting with `otp` will copy the otp token to the clipboard.

# Bitwarden/Vaultwarden

If [rbw](https://github.com/doy/rbw) is installed, it can be used instead of pass by prefixing a search with `bw`. Non prefixed searches will still go through pass if present.

# Environment variables

If you are configuring `pass` through environment variables, such as `PASSWORD_STORE_DIR`, make sure to set them in a way that will propagate to the search provider executable, not just in your shell.

Setting them in `~/.profile` (or `~/.pam_environment` if supported by your OS) should be sufficient, but stuff in shell-specific files such as `~/.bashrc` will not be picked up by gnome-shell.

If your values have no effect, make sure they propagate to the script environment. You can check this with ps:
```
ps auxeww | grep [g]nome-pass-search-provider.py
```

# Clipboard managers

If you are using GPaste, passwords will be sent to it marked as passwords, thus ensuring they are not visible.
Otherwise they are sent to the clipboard using `pass -c` which defaults to expiration after 45 seconds.

# Compatibility

This implements the `org.gnome.Shell.SearchProvider2` D-Bus API and has been tested with GNOME Shell 3.22 to 40. This uses the `org.gnome.GPaste1` or `org.gnome.GPaste2` versions of the GPaste D-Bus API to add passwords to GPaste.

# Troubleshooting

If you don't see passphrase prompts when your key is locked, it might be because GPG is not using the right pinentry program. You can force gpg-agent to use pinentry-gnome3 by adding `pinentry-program /usr/bin/pinentry-gnome3` to `~/.gnupg/gpg-agent.conf`.

If you encounter problems, make sure to look in the logs of GNOME and D-Bus. On systems that use systemd, you can do this using `journalctl --user`.

Don't hesitate to open an issue.
