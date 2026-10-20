# Changelog

## 2.0.1 — Fix BLE presence timestamp attribute

Bugfix release restoring compatibility with Home Assistant presence automations.

Added the missing last_seen_before_off attribute to Watch BLE presence binary sensors.

The attribute exposes the timestamp of the last BLE advertisement when a Watch is no longer detected.

Fixed automations that rely on this timestamp to correlate Watch departures with physical events such as door, gate and lock activity.

Added regression tests covering detected, undetected and never-seen Watch states.

No changes to Bluetooth scanning, IRK resolution, presence detection logic or existing entity IDs.

No configuration changes or migration required.

## 2.0.0 — Independent Apple Watch BLE presence

Major release removing runtime dependence on `private_ble_device` and all nonpublic Home Assistant APIs.

- Watch IRKs are stored directly in the Watch BLE Presence config entry.
- Rotating BLE addresses are resolved from Home Assistant's shared Bluetooth advertisement cache with `bluetooth-data-tools`.
- Cache-only operation: no additional Bluetooth scan requests, connections or callbacks.
- Seven entities per Watch, as before: presence, last seen, age, RSSI, scanner, address, Bluetooth name.
- Add/remove Watches and adjust polling and timeout in the UI.
- Removed the one-time Private BLE Device migration wizard and entity-registry lookups.
- Existing independent v1.1/v1.2-beta installations can **upgrade in place**, preserving Watch IDs, IRKs, entity IDs and options. Internal config entry version stays at 2.
- **Breaking upgrade from original v1.0:** the direct migration is no longer supported. Original v1.0 config entries have no stored IRKs and need a new setup. Existing entity IDs are not guaranteed after deleting the original entry.
- Local brand assets already ship with the integration. Missing HACS-listing icons are a [known HACS frontend issue](https://github.com/hacs/integration/issues/5402), even though Home Assistant displays the icon correctly.

Tested on four real Watches without Private BLE Device after a Home Assistant reboot and Watch off/on transition; real-world reliability still requires longer observation.

## 1.2.0b1 — Simplification beta

Removed v1.0 migration UI and preserved existing standalone Watch identities.

## 1.1.0b1 — Standalone IRK beta

Added independent IRK storage and public Bluetooth cache resolution, with a one-time v1.0 migration flow.

## 1.0.0

- First production release.
- Prepare the integration for HACS/GitHub distribution.
- Add local Home Assistant brand assets.
- Add English and Italian custom-integration translations.
- Add translated entity names.
- Create one Home Assistant device per Private BLE Device entry.
- Add BLE presence, last-seen, age, RSSI, scanner, address and Bluetooth-name entities.
- Read the real latest advertisement timestamp from Home Assistant's Bluetooth cache.
- Add UI config flow and configurable update interval / BLE presence timeout.
- Mark the integration as a single-config-entry calculated integration.
- Add HACS and Hassfest GitHub Actions.

## 0.3.0

- Pre-release packaging for HACS/GitHub distribution.

## 0.2.0

- Initial functional prototype with UI configuration and BLE cache sampling.
