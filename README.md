# Watch BLE Presence

A Home Assistant custom integration for monitoring Apple Watch presence using each Watch's own **Identity Resolving Key (IRK)**. No Private BLE Device integration required.

## How it works

Watch BLE Presence **only reads the Bluetooth advertisement cache** maintained by Home Assistant. It does not initiate Bluetooth scans, register active-scan listeners, connect to the Watch or change ESPHome proxy behavior. The actual scanning modes of Bluetooth adapters and proxies are controlled by their respective integrations.

The integration resolves rotating BLE addresses with `bluetooth-data-tools` and exposes the newest cached advertisement for each configured IRK.

## Features

Each Watch has seven entities, preserving the same names and entity keys as Watch BLE Presence v1.0:

- BLE detected (binary sensor)
- Last BLE detection (timestamp)
- Last detection age (seconds)
- RSSI (dBm)
- Bluetooth scanner/proxy
- BLE address
- Bluetooth name

Presence timeout and polling interval are configurable. Defaults are 300 seconds for presence timeout and 60 seconds for polling; polling can be set as low as 10 seconds.

## Requirements

- Home Assistant 2026.3 or newer
- Working Home Assistant Bluetooth integration and a Bluetooth adapter or ESPHome Bluetooth proxy
- One valid 16-byte IRK per Apple Watch, entered in Home Assistant as 32 hexadecimal digits or the supported base64 encoding

## Installation

Install Watch BLE Presence as a HACS custom repository integration, or copy `custom_components/watch_ble_presence/` into `/config/custom_components/watch_ble_presence/`. Restart Home Assistant and add **Watch BLE Presence** in Settings → Devices & services.

Enter the first Watch's name and IRK during setup. Use **Configure → Add a Watch** for additional watches, or **Configure → Remove a Watch** to remove a device. **Presence settings** changes the timeout and update interval.

**Important:** If you are already using the independent v1.1 beta with configured Watches, upgrade the integration **in place**, without removing its config entry. All existing Watch IDs, IRKs, entity IDs and options are retained. Home Assistant keeps the internal entry schema at version 2; the application release is v1.2.

This streamlined v1.2 line **does not contain the old Private BLE Device migration workflow**. Starting from the original pre-IRK v1.0 requires setting up Watch BLE Presence afresh; the former migration UI is not available.

## Development and testing

The `test` branch tracks the v1.2 beta. GitHub Actions runs HACS validation, Hassfest and unit tests using:

```sh
python -m unittest discover -s tests -v
```

Automated checks do not guarantee Bluetooth presence behavior in every environment. Evaluate live advertisements, rotating addresses, scanner names and departure/arrival transitions before deploying safety-critical automations.

## Privacy and security

IRKs are secret identity keys stored in the integration's own Home Assistant config entry. Do not share them in GitHub issues, screenshots or support chats. Avoid relying on BLE presence alone for security-critical actions.

## Support and license

[Support the project](https://paypal.me/PaoloFazari). MIT License. This project is not affiliated with Apple Inc. or Home Assistant.
