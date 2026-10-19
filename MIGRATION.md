# Beta-test migration for the four existing Watches

The beta test code is on GitHub branch `test`, with version `1.1.0b1`.

**Keep your existing Watch BLE Presence configuration entry. Do not delete it before upgrading.** Reusing a name alone does not preserve entity IDs. The migrated configuration selects the **old entity identifier** for each Watch. The sensor and entity classes remain unchanged from `main`.

## Before starting

- Make and verify a complete Home Assistant backup. Reverting Python alone will NOT restore an already migrated configuration entry.
- Keep all four Private BLE Device entries enabled until the new integration is configured and successfully tested.
- Have all four IRKs ready **privately**.
- Record the four old `binary_sensor` IDs and any important automations.
- Choose a maintenance window: Watch BLE Presence entities may be temporarily unavailable after upgrade and until all four keys are re-entered.

## Upgrade the original integration (do not delete it)

1. Install beta `v1.1.0b1` from GitHub release or copy **only** the folder `custom_components/watch_ble_presence/` from branch `test` over the matching existing folder.
2. Restart Home Assistant. The old v1 configuration becomes v2 without borrowing another integration's IRKs. The device list starts empty until your IRKs are configured.
3. Open Settings → Devices & services → **Watch BLE Presence** → **Configure** → **Add or migrate a Watch**.
4. Paste the IRK, set the name, then **choose the matching old Watch BLE Presence binary sensor from the drop-down** by its full `binary_sensor.xxx` entity ID. Do not select `New watch` for an existing Watch.
5. Repeat for the other three Watches. Verify presence, last seen, age, RSSI, scanner, address and Bluetooth name. Confirm all four original entity IDs still match and that automations are correctly attached.
6. Leave Private BLE Device enabled initially; verify entry and exit events.

## Independence test

When all four Watch BLE Presence sensors behave correctly, **disable**, do not delete, the four Private BLE Device entries under Settings → Devices & services. **Do not turn off Bluetooth or your ESPHome Bluetooth proxies.** Restart Home Assistant and test over several days.

The new integration only reads Home Assistant's existing Bluetooth advertisement cache and **does not register a BLE listener or request active scanning**. Adapters/proxies are controlled independently by Home Assistant and their own firmware/settings.

## Rollback

If sensor detection fails, re-enable Private BLE Device first. If the test version is not usable, restore the full pre-upgrade Home Assistant backup (both config entries and integration files); do not rely on changing `main`, `legacy`, or `test` to revert the stored v2 config entry.

**Do not delete either integration until you're satisfied with the full independence test.**
