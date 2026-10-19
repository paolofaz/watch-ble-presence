# Watch BLE Presence v1.2.0b1 — TEST

**Beta release candidate on branch `test`**. This is not yet the stable HACS catalog release.

## Changes from v1.1 beta

- Removed v1.0 / Private BLE Device migration entrypoint and legacy entity-picker UI.
- Simplified device management: **Add a Watch**, **Remove a Watch**, **Presence settings**.
- Internal watch identity is called `watch_id`, while existing IDs remain **exactly the same stored strings**.
- Keeps configured IRKs and entity registry unique IDs for all Watches already set up using the standalone v1.1 beta.
- Cleans up Private BLE Device terminology in the Watch device model.

## Unchanged functionality

- Only reads the shared Home Assistant Bluetooth advertisement cache.
- No active-scan listener, outgoing scan request, Watch connection or new radio transmission.
- Uses each Watch's own stored IRK to resolve rotating addresses.
- Same seven Watch entities and unchanged presence, last-seen, age, RSSI, scanner, BLE address and Bluetooth name calculations.
- Same options and timeouts, including a 15-second update interval if already configured.

## Upgrading a working standalone v1.1 beta

1. Take a full Home Assistant backup.
2. **Do not delete the current Watch BLE Presence integration.** Its existing config entry contains the Watch IDs and IRKs.
3. Update the integration files from branch `test` in place; restart Home Assistant.
4. Confirm all four Watches and their original entity IDs still exist, check the states and timestamps.
5. No IRKs should need to be re-entered. No changes to Bluetooth or ESPHome proxies are required.

This beta no longer supports direct migration from v1.0 configurations that lack stored IRKs. If an earlier v1.0 install is still in use, it must be configured anew; the former migration wizard has been intentionally removed.

## Rollback

Do not rely solely on replacing Python files after changing config entries. Retain a full pre-upgrade backup and the previous beta release so you can restore both code and configuration if necessary.

## Tagging a beta manually

Create GitHub tag `v1.2.0b1` targeting **test**, label it `Watch BLE Presence v1.2.0b1 — TEST`, and check **Set as a pre-release**. Do not publish a stable v1.2 until field testing finishes.
