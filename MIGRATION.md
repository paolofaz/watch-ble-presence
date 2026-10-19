# Development branch: standalone IRKs

**Do not install this branch on your active Home Assistant yet.** The existing Watch BLE Presence config has no IRKs; after upgrading its sensors will be unavailable until each IRK is added again.

The refactor reads only IRKs stored in its own configuration, not from Private BLE Device. It registers its own active Bluetooth listener and polls Home Assistant's existing advertisement cache.

## Migration checklist

1. Save a Home Assistant backup and record the four Watch BLE Presence entity IDs.
2. Keep Private BLE Device and your Bluetooth proxies enabled while testing.
3. Open Watch BLE Presence > Configure > Add or migrate a Watch.
4. Enter the name and IRK of each Watch. Select the correct existing Watch BLE Presence entity from the selection field to preserve its registry identifier.
5. Repeat for the remaining Watches, then confirm old sensor entity IDs and automations are still intact.
6. Compare entry/exit transitions, timeouts, rotating addresses, scanners and RSSI over several days.
7. Consider removing Private BLE Device **only after** the independent detection has been confirmed.

Do not post real IRKs publicly, including in GitHub issues or PR screenshots. The key remains in your Home Assistant config entry.

## Limitations

This is still work in progress. Unit tests do not establish real scanner/proxy performance, nor does preserving unique IDs guarantee the entire migration will be seamless. No release should be published until testing on a real Home Assistant instance passes.
