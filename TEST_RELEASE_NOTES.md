# Watch BLE Presence v1.1.0b1 — test release

**PRE-RELEASE for supervised testing. Do not install as an unattended HACS update.**

This is the same `watch_ble_presence` integration, not an additional integration.

## What changes

- The four Watch IRKs belong to Watch BLE Presence's **own config entry**, and are entered manually in its settings.
- Uses public Home Assistant Bluetooth cache APIs and `bluetooth-data-tools` for rotating address resolution.
- No dependency on `private_ble_device`, no active Bluetooth scan request or callback.
- Keeps the existing entity implementation and seven sensor types **unchanged**: BLE detected, last seen, detection age, RSSI, scanner, rotating address, Bluetooth name.
- Keeps the same default sampling interval (60 s) and presence timeout (300 s); existing configured values stay in options.
- Lets existing users choose an original Watch BLE Presence entity during migration, preserving the previous unique ID and normally its entity ID.

## CRITICAL — update; do NOT delete and recreate

**Do not delete Watch BLE Presence or Private BLE Device before migration.** Home Assistant may remove entity registry records when deleting an integration. Reusing a Watch display name does not guarantee the old `entity_id`.

1. Create and verify a FULL Home Assistant backup (configuration storage and custom integration files). Save all four IRKs privately; do not paste them into GitHub.
2. Record the full names of the four original Watch BLE Presence `binary_sensor` entities and the names of any automations relying on them.
3. Leave `Private BLE Device`, ESPHome proxies and Home Assistant Bluetooth enabled. Choose a maintenance window; all four Watch BLE Presence entities may temporarily go unavailable during migration.
4. Download the ZIP of branch `test` and replace **only** `/config/custom_components/watch_ble_presence/` on Home Assistant with the folder of the same name from the ZIP. Do **not** replace the `watch_ble_presence_test` folder or install another copy of the main integration.
5. Restart Home Assistant. Its existing Watch BLE Presence config entry is migrated from v1 to v2 with an empty list of Watches; this intentionally does **not** read the secret IRKs out of another integration.
6. In **Settings → Devices & services → Watch BLE Presence → Configure → Add or migrate a Watch**, enter the first Watch's name and IRK. In the **Existing Watch BLE Presence entity** dropdown choose the exact previous entity **by its complete `binary_sensor.xxx` identifier**. Avoid **New watch** when migrating existing Watches.
7. Repeat for each remaining Watch. Verify all four old entity IDs exist and still update, and check that RSSI, scanner, age and last seen are correct. Check every safety-critical automation before enabling it again.
8. Observe the four Watches with `Private BLE Device` still enabled for at least some real departures and returns.
9. After success, **disable**, do not delete, only the four Private BLE Device configuration entries. Keep Bluetooth and ESPHome scanners/proxies running. Restart Home Assistant and observe detection, scanner data and timeout for several days. Only consider removing Private BLE Device after confirmed independence.

## Rollback

If readings become unreliable, first re-enable Private BLE Device. To restore the original code **and original v1 configuration**, restore your pre-test Home Assistant backup. Simply switching Git branches or Python files does not roll back the stored v2 config entry.

## Limitations

- This pre-release was automatically tested with mocks; that is not equivalent to a field test on your exact Bluetooth proxies.
- In case you remove the old Watch BLE Presence entry before upgrading, entity ID preservation is NOT guaranteed.
- The comparison test integration under `watch_ble_presence_test` is separate and optional.
- The underlying Bluetooth scanner settings (passive or active) are managed by Home Assistant and the adapters/proxies, not changed by this integration.
- No new BLE radio scans are requested by Watch BLE Presence.

## GitHub pre-release publishing (manual)

Select **Releases → Draft a new release**, create tag `v1.1.0b1` with **target `test`**, title it `Watch BLE Presence v1.1.0b1 — TEST`, and enable **Set as a pre-release**. Paste or link this file as the release description. Do NOT mark it as the latest stable release.
