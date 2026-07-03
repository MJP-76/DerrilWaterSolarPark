# Kirk Hill Wind Farm Integration

A Home Assistant custom component that reads live data from the Kirk Hill Wind Farm API.

It pulls current data for both OpenAPI scopes:
- `owner` (your ownership share)
- `site` (whole-site values)

If you like my work:
<br><a href="https://www.buymeacoffee.com/mjp76" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>
<br>Use my [Octopus.Energy 🐙](https://share.octopus.energy/iron-moose-196) referral code. You get £50 credit for joining and I get £50 credit.

## Features
- Live API polling (`cloud_polling` integration)
- Farm-level owner/site scoped sensors for:
  - power
  - capacity factor
- Farm-level physical sensors (scope-independent):
  - wind speed
  - active turbines
  - inactive turbines
  - alarm binary sensor
- Per-turbine sensors:
  - power (`owner` + `site`)
  - capacity factor (`owner` + `site`)
  - wind speed
  - state text
  - active binary sensor
- Config flow with API key validation
- Optional custom base URL (advanced)
- Configurable polling interval via Options
- Ready-to-import Lovelace dashboard YAML

## Installation
<br>[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

1. Add this repository to HACS (Custom Repositories)
2. Install "Kirk Hill Wind Farm"
3. Restart Home Assistant
4. Add the integration via Settings -> Devices & Services -> Add Integration -> "Kirk Hill Wind Farm"
5. Enter your API key, site name, and (optionally) a custom base URL

Polling interval can be changed later from the integration's **Configure** (Options) menu.

## Sensors

Farm hub device:
- Power (owner) [kW]
- Power (site) [kW]
- Capacity factor (owner) [%]
- Capacity factor (site) [%]
- Wind speed [m/s]
- Active turbines
- Inactive turbines
- Alarm (binary sensor)

Per turbine device (`Turbine T1` ... `Turbine T8`):
- Power (owner) [kW]
- Power (site) [kW]
- Capacity factor (owner) [%]
- Capacity factor (site) [%]
- Wind speed (m/s)
- State text
- Active (binary sensor)

## Dashboard

A ready-made Lovelace dashboard is provided at [`dashboards/kirkhill_wind_scada.yaml`](dashboards/kirkhill_wind_scada.yaml) with:
- owner vs site farm metrics
- farm wind and turbine availability
- per-turbine owner/site power and capacity sensors

To use it:
1. Go to **Settings -> Dashboards -> Add Dashboard -> New dashboard from scratch**.
2. Open the new dashboard, choose **Edit Dashboard -> ... -> Raw configuration editor**.
3. Paste the contents of `dashboards/kirkhill_wind_scada.yaml`.
4. If your entity IDs differ from the defaults, update the YAML entity IDs to match your instance.

## License

MIT
