# Publishing checklist

Repository: `https://github.com/paolofaz/watch-ble-presence`

Before publishing v1.0.0:

1. Push the contents of this folder to the repository root.
2. Set a short repository description and add topics such as `home-assistant`, `hacs`, `bluetooth`, `ble`, `apple-watch`, and `presence-detection`.
3. Ensure GitHub Issues are enabled.
4. Confirm both GitHub Actions (HACS and Hassfest) pass.
5. Create the GitHub release/tag `v1.0.0`.
6. Test installation through HACS as a custom repository.

The manifest is already configured for `@paolofaz`, including documentation and issue tracker URLs.

The integration contains its brand assets locally under:

```text
custom_components/watch_ble_presence/brand/
```
