# Sensors

The starter integration exposes a single sensor that confirms setup completed
successfully.

| Name | State | Attributes |
|---|---|---|
| Integration status | `configured` | `site_name`, `project_type` |

- **State** — always reports `configured` while the integration is set up.
- **Attributes** — `site_name` (the name entered during configuration) and
  `project_type` (`solar_farm_starter`).

This is a starter scaffold — sensor coverage will grow as the API's data is
mapped into dedicated entities. The integration identity is:

- Domain: `derril_water_solar_park`
- Platform: `sensor`