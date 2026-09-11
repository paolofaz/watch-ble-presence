# Watch BLE Presence

Repository: https://github.com/paolofaz/watch-ble-presence

A Home Assistant custom integration that exposes fast, deterministic BLE presence for Apple Watch devices already configured with Home Assistant's **Private BLE Device** integration.

Instead of relying on the comparatively long `not_home` timeout of the official device tracker, Watch BLE Presence periodically reads Home Assistant's existing in-memory Bluetooth cache and calculates when the latest advertisement matching each IRK was actually received.

It does **not** trigger additional Bluetooth scans and does **not** communicate with the Watch.

## Features

- One Home Assistant device for every configured Private BLE Device IRK.
- BLE presence binary sensor with configurable timeout.
- Last BLE detection timestamp.
- Age of the latest detection in seconds.
- RSSI diagnostic sensor.
- Bluetooth scanner/source diagnostic sensor.
- Current rotating BLE address diagnostic sensor.
- Bluetooth-advertised name diagnostic sensor.
- Configurable update interval and presence timeout from the Home Assistant UI.
- Uses all Bluetooth scanners already managed by Home Assistant, including compatible Bluetooth proxies.

## Requirements

- Home Assistant 2026.3 or newer.
- The built-in **Private BLE Device** integration configured with at least one IRK.
- Working Bluetooth scanners/proxies visible to Home Assistant.

The official Private BLE Device integration remains required because Watch BLE Presence uses its IRK configuration and address resolution logic. You can choose not to use its `device_tracker` entities in your automations.

## Installation with HACS

Until/if the repository is added to the default HACS catalog:

1. Open HACS.
2. Open **Custom repositories**.
3. Add `https://github.com/paolofaz/watch-ble-presence` as the repository URL.
4. Select **Integration** as the category.
5. Install **Watch BLE Presence**.
6. Restart Home Assistant.
7. Go to **Settings → Devices & services → Add integration**.
8. Search for **Watch BLE Presence** and add it.

## Manual installation

Copy:

```text
custom_components/watch_ble_presence/
```

into your Home Assistant configuration directory under:

```text
/config/custom_components/watch_ble_presence/
```

Restart Home Assistant and add **Watch BLE Presence** from **Settings → Devices & services**.

## Configuration

The integration has two options:

- **Update interval**: how often the integration samples Home Assistant's Bluetooth cache. Default: `60` seconds.
- **BLE presence timeout**: maximum age of the latest received advertisement before the presence binary sensor turns off. Default: `300` seconds.

For example, with an update interval of 60 seconds and a presence timeout of 180 seconds, the binary sensor normally turns off roughly 3–4 minutes after the last received advertisement.

## Entities

Each tracked watch/device gets:

| Entity | Purpose |
| --- | --- |
| BLE detected | Main presence binary sensor |
| Last BLE detection | Timestamp of the most recent BLE advertisement |
| Last detection age | Seconds since the most recent advertisement |
| RSSI | Signal strength of the latest advertisement |
| Bluetooth scanner | Scanner/proxy that supplied the latest advertisement |
| BLE address | Current rotating/private BLE address |
| Bluetooth name | Name contained in the BLE advertisement, when available |

The RSSI, scanner, address and Bluetooth-name entities are diagnostic entities.

## How it works

Home Assistant's Bluetooth stack continuously receives advertisements through its configured local adapter and Bluetooth proxies. Identical advertisements may be deduplicated before callbacks reach integrations, but Home Assistant still maintains the latest service information in its Bluetooth cache.

Watch BLE Presence reads that existing cache at the configured interval, resolves private addresses using the IRKs already managed by **Private BLE Device**, and derives the actual last-seen age from the cached advertisement timestamp.

This means the integration is sampling existing Home Assistant state, not actively polling the Watch over Bluetooth.

## Automation guidance

For security-sensitive presence logic, BLE presence is best treated as one signal rather than the sole proof that a person has left. Combining the BLE binary sensor with physical events such as a door, gate, lock or alarm state can substantially reduce false transitions.

## Compatibility note

This integration currently imports internal coordinator functionality from Home Assistant's built-in `private_ble_device` integration. That API is not guaranteed to remain stable across future Home Assistant releases. A Home Assistant update may therefore require a corresponding Watch BLE Presence update.


# 🍺 Support the Project

If you found this project useful and want to support my work, you can offer me a beer:

[![Buy Me a Beer](https://img.shields.io/badge/Buy%20Me%20a%20Beer-0070ba?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/PaoloFazari)


## Contributions
Contributions are welcome

## Trademarks

Apple and Apple Watch are trademarks of Apple Inc. This project is independent and is not affiliated with or endorsed by Apple Inc. or Home Assistant.

## License

MIT
