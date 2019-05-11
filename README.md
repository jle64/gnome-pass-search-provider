A search provider for GNOME Shell that adds support for searching in zx2c4/[pass](https://www.passwordstore.org/).

Names of passwords will show up in GNOME Shell searches, choosing one will copy the corresponding content to the clipboard.

![Sreencapture](misc/screencapture.gif)

# Installation
## Arch Linux
Install `gnome-pass-search-provider-git` from the AUR.

## Manual

Ensure that python>=3.5 and python-gobject are installed on your system and that pass is setup.

Install Python 3 fuzzywuzzy module.
Depending on your distribution this can be packaged as python-fuzzywuzzy, python3-fuzzywuzzy or you might need to install it with pip:
```shell
python3 -m pip install fuzzywuzzy
```

Download or clone this repository:
```shell
git clone git@github.com:jle64/gnome-shell-pass-search-provider.git
```

Run the installation script as root:
```shell
sudo ./install.sh
```

# Post-installation

Recommended : set gpg agent to use pinentry-gnome3 by adding `pinentry-program /usr/bin/pinentry-gnome3` to `~/.gnupg/gpg-agent.conf`.

If you are on Xorg, restart GNOME Shell by typing 'alt + f2' then entering 'r' as command.
If you are on Wayland, you need to close and reopen your GNOME session.

The search provider should show up and be enabled in GNOME search preferences and started on demand by GNOME Shell.

# OTP support

The [pass-otp](https://github.com/tadfisher/pass-otp) extension is supported. Searches starting with `otp` will copy the otp token to the clipboard.

# Environment variables

If you are configuring pass through environment variables, such as `PASSWORD_STORE_DIR`, make sure to set them in a way that will propagate to the search provider executable, not just in your shell.
Setting them in `~/.profile` or `~/.pam_environment` should be sufficient, but stuff in shell-specific files such as `~/.bashrc` and co will not be picked up by gnome-shell.

If your values have no effect, make sure they propagate to the script environment:
```shell
ps auxeww | grep [g]nome-pass-search-provider.py
```

# Clipboard managers

If you are using GPaste, passwords will be sent to it marked as passwords, thus ensuring they are not visible.
Otherwise they are sent to the clipboard using `pass -c` which defaults to expiration after 45 seconds.

# Compatibility

This implements the `org.gnome.Shell.SearchProvider2` D-Bus API and has been tested with GNOME Shell 3.22-3.32.

# Troubleshooting

If this does not work for you, make sure to look to wherever GNOME and D-Bus are logging for error messages (using `journalctl --user` on systemd-using systems).
Don't hesitate to open an issue.
