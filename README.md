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

**Important:** If you are already using the independent v1.1 or v1.2 beta with configured Watches, upgrade the integration **in place**, without removing its config entry. All existing Watch IDs, IRKs, entity IDs and options are retained. Home Assistant's internal config-entry schema remains version 2; the integration release is v2.0.0.

**Breaking change in v2.0:** The old Private BLE Device migration wizard was removed. Direct upgrades from the original v1.0 entry (which did not store IRKs) are unsupported; back up your configuration, remove the old v1.0 integration entry and set up v2.0 with your own IRKs. Reusing the old Watch name alone does **not** guarantee the same entity ID. Existing independent v1.1/v1.2-beta entries keep their configured Watch IDs and entity IDs.

## Development and testing

The `main` branch tracks stable releases; `test` is used for development and evaluation; `legacy` preserves the original code. GitHub Actions runs HACS validation, Hassfest and unit tests using:

```sh
python -m unittest discover -s tests -v
```

Automated checks do not guarantee Bluetooth presence behavior in every environment. Evaluate live advertisements, rotating addresses, scanner names and departure/arrival transitions before deploying safety-critical automations.

## Integration icon in HACS

Home Assistant 2026.3+ supports locally bundled brand assets. Watch BLE Presence includes `brand/icon.png`, `brand/logo.png`, high-resolution and dark-mode variants in its integration folder. They show correctly in Settings → Devices & services.

Some HACS frontends still display **"icon not available"** for custom integrations because they fetch an older public icon CDN instead of Home Assistant's local brand endpoint. This is a [known HACS frontend issue](https://github.com/hacs/integration/issues/5402), not a missing icon file in this repository. It does not affect the integration or BLE detection.

## Privacy and security

IRKs are secret identity keys stored in the integration's own Home Assistant config entry. Do not share them in GitHub issues, screenshots or support chats. Avoid relying on BLE presence alone for security-critical actions.

## Support and license

[Support the project](https://paypal.me/PaoloFazari). MIT License. This project is not affiliated with Apple Inc. or Home Assistant.
