# Watch BLE Presence

A Home Assistant custom integration for monitoring Apple Watch BLE presence using your own **Identity Resolving Keys (IRKs)**.

Independent of the official **Private BLE Device** integration. Supports multiple watches, rotating Bluetooth addresses, and Home Assistant Bluetooth proxies.

## Features

- Presence binary sensor with configurable timeout
- Last BLE detection timestamp and detection age
- RSSI, source scanner/proxy, current rotating address and Bluetooth name
- Multiple watches with individual IRKs
- Existing Home Assistant Bluetooth advertisement cache; no connections to the Watch

## Requirements

- Home Assistant 2026.3 or newer
- Bluetooth scanner or compatible ESPHome Bluetooth proxy
- Each watch's IRK (16 bytes; hex or supported base64 format)

## Installation

In HACS, add `https://github.com/paolofaz/watch-ble-presence` as a custom **Integration** repository. Install, restart Home Assistant, then add **Watch BLE Presence** under Settings → Devices & services.

Alternatively, copy `custom_components/watch_ble_presence/` into `/config/custom_components/`, restart, and add the integration.

## Configuration

Enter the first watch name and IRK in the setup flow. To add more watches, open **Watch BLE Presence → Configure → Add or migrate a Watch**.

The **Presence settings** menu controls polling (10–300 seconds, default 60) and presence timeout (60–3600 seconds, default 300). Each Watch has seven entities: BLE detected, last seen, age, RSSI, scanner, address, Bluetooth name.

## Upgrading from the original release

**This development refactor is not yet validated on a real installation. Do not install it on the production Home Assistant system before testing.**

Previous Watch BLE Presence versions did not store IRKs in their own configuration. On upgrade, you need to enter the IRK for every Watch again. The new integration does **not** read IRKs from Private BLE Device.

Take a Home Assistant backup first and keep Private BLE Device running during evaluation. For each Watch, use **Configure → Add or migrate a Watch** and select the corresponding **existing Watch BLE Presence entity** to preserve its unique ID and existing automation references. Repeat for all four Watches. See [MIGRATION.md](MIGRATION.md) for further details.

After testing detection, MAC rotation, timeout, and scanner behavior with your own equipment, Private BLE Device may be removed. Home Assistant's Bluetooth system and proxies are separate integrations.

## Development

GitHub Actions runs HACS and Hassfest checks plus unit tests using `python -m unittest discover -s tests -v`. Automated checks **cannot** establish real-world BLE presence reliability. Verify performance with physical Watches before publishing a release.

## Security

IRKs are secret key material and are stored only in Watch BLE Presence's Home Assistant config entry. Do not post IRKs to issues or logs. For critical security automation, combine BLE presence with other signals.

## Support and license

[Support the project](https://paypal.me/PaoloFazari). MIT license. Not affiliated with Apple Inc. or Home Assistant.
