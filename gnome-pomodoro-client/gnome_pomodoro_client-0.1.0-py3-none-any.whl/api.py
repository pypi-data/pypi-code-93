def get_dbus_proxy(bus):
    return bus.get("org.gnome.Pomodoro", "/org/gnome/Pomodoro")


def get_proxy_state(proxy):
    return {
        "elapsed": proxy.Elapsed,
        "is_paused": proxy.IsPaused,
        "duration": proxy.StateDuration,
        "remaining": proxy.StateDuration - proxy.Elapsed,
        "state": proxy.State,
    }
