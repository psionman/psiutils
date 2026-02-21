"""Provide notifications on  Linux platforms."""
import os
import platform

if platform.system() == 'Linux' and 'XDG_CURRENT_DESKTOP' in os.environ:
    import gi
    gi.require_version('Gio', '2.0')
    gi.require_version('GioUnix', '2.0')
    gi.require_version('Notify', '0.7')
    from gi.repository import Notify


def _notify(title: str, message: str) -> None:
    if platform.system() != 'Linux' or 'XDG_CURRENT_DESKTOP' not in os.environ:
        return
    Notify.init(title)
    Notify.Notification.new(message).show()
