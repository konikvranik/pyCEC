![Build Status](https://github.com/konikvranik/pyCEC/workflows/Tests/badge.svg)
![PyPi Version](https://img.shields.io/pypi/v/pyCEC)
![Issue Count](https://img.shields.io/github/issues-raw/konikvranik/pyCEC)
![Coverage Status](https://img.shields.io/coveralls/github/konikvranik/pyCEC)

# pyCEC – Python HDMI-CEC bridge for Kodi and Home Assistant

**pyCEC** is a lightweight Python bridge for controlling HDMI devices over the [CEC (Consumer Electronics Control)](https://en.wikipedia.org/wiki/Consumer_Electronics_Control) protocol. It is designed to act as a glue between media software like **Kodi** and smart home systems like **Home Assistant**. But it can serve as a python binding to the C++ [**libcec**](https://libcec.pulse-eight.com/) library too.

Additionally, it provides a TCP server that proxies CEC commands from the network to the local CEC adapter and the Kodi plugin that acts the same way, but uses Kodi's CEC API instead of direct calls to the libcec.

To send commands over a network you can use bundled commandline client, [netcat](https://en.wikipedia.org/wiki/Netcat) or configure the pyCEC library in your code to connect to the _pyCEC_ server instead of the local CEC adapter.

---

## 🚀 Features

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

You must also have [`libcec`](https://libcec.pulse-eight.com/) installed on your system.

### On Ubuntu/Debian:

```bash
sudo apt install libcec-dev cec-utils
```

or follow the [official installation instructions](https://github.com/Pulse-Eight/libcec#supported-platforms).

---

## 🧪 Quick Start

```bash
pythom -m pycec -h
```

This will start the module and provide a list of options.

---

## 🧠 Use Cases

- Turn on your TV when Kodi starts playing
- Power off AV receiver when system suspends
- Control TV or Amplifier remotely
- Create Home Assistant automations triggered by HDMI input changes
- Use IR remote to control Kodi via CEC passthrough

---

## 📘 Documentation

- [Getting Started](#)
- [Command Line Reference](#)
- [Integration with Kodi](#)
- [MQTT Setup](#)
- [Home Assistant Example Automations](#)

*(Links coming soon)*

---

## 🧩 Related Projects

- [Kodi](https://kodi.tv/)
- [Home Assistant](https://www.home-assistant.io/)
- [libCEC](https://libcec.pulse-eight.com/)
- [cec-client](https://github.com/Pulse-Eight/libcec)

---

## 🤝 Contributing

Pull requests and issues are welcome! Whether you found a bug, have a feature request, or want to contribute code — feel free to participate.

👉 [GitHub Repository](https://github.com/konikvranik/pyCEC)

---

## 📜 License

MIT License. See [LICENSE](https://github.com/konikvranik/pyCEC/blob/main/LICENSE) for details.

---

> Made with ❤️ by [konikvranik](https://github.com/konikvranik)
