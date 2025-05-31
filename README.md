<div style="display:none;" class="badges">

![Build Status](https://github.com/konikvranik/pyCEC/workflows/Tests/badge.svg)
![PyPi Version](https://img.shields.io/pypi/v/pyCEC)
![Issue Count](https://img.shields.io/github/issues-raw/konikvranik/pyCEC)
![Coverage Status](https://img.shields.io/coveralls/github/konikvranik/pyCEC)

</div>

# `pyCEC` – Python HDMI-CEC Bridge for Kodi & Home Assistant

The purpose of this project is:

🔹 to provide an object-based API to [libcec](https://github.com/Pulse-Eight/libcec)  
  for the [`hdmi_cec`](https://www.home-assistant.io/integrations/hdmi_cec/) module in **Home Assistant** ([primary goal](https://github.com/konikvranik/pyCEC/projects/1))  
🔹 to offer a TCP ⇄ HDMI bridge to control CEC devices over network  
  ([secondary goal](https://github.com/konikvranik/pyCEC/projects/2))

---

## ✨ Features

🔌 Send commands to your TV or AV receiver  
🖥️ Monitor HDMI power and input status  
🏠 Integrate with Home Assistant automations  
🎮 Control devices using Kodi remote or custom scripts  
💻 Simple command-line interface (CLI)  
🐍 Python API for custom scripting  
📺 Kodi integration (via bundled plugin)

---

## 📦 Installation

```bash
pip install pyCEC
```

> ⚠️ **libcec must be installed** for direct-mode usage.  
> Do **not** run `pip install cec` – it will fail. Instead, [compile libcec](https://github.com/Pulse-Eight/libcec#supported-platforms) for your OS.

### On Debian/Ubuntu:

```bash
sudo apt install libcec-dev cec-utils
```

If you're using a **Python virtualenv**, make sure it can access system Python modules with:

```bash
python3 -m venv venv --system-site-packages
```

> 💡 **Note:** When using `pyCEC` in *network mode* (TCP client), `libcec` is **not required**.

---

## 🚀 Running the Server

You can launch the server bridge with:

```bash
python3 -m pycec
```

This binds to TCP port `9526` on all interfaces.

Then:

- connect from a remote `pyCEC` client using `TcpAdapter`
- or use [Netcat](https://www.wikiwand.com/en/Netcat) to manually send CEC commands:

```bash
echo '10:04' | nc YOUR_IP 9526
```

---

## 🏠 Home Assistant Integration (Multiple TVs via Telnet)

You can integrate `pyCEC` into Home Assistant via `telnet` platform, for example:

```yaml
switch:
  - platform: telnet
    switches:
      some_device_id:
        name: "Some Device Name"
        resource: 192.168.1.123
        port: 9526
        command_on: '10:04'
        command_off: '10:36'
        command_state: '10:8f'
        value_template: '{{ value == "01:90:00" }}'
        timeout: 1
```

This allows you to switch devices on/off or query their state.

---

## 🤝 Contributing

Contributions are welcome!  
Feel free to [open an issue](https://github.com/konikvranik/pyCEC/issues) or [create a pull request](https://github.com/konikvranik/pyCEC/pulls).

---

## 📜 License

MIT License – see [LICENSE](./LICENSE).

> Made with ❤️ by [@konikvranik](https://github.com/konikvranik)