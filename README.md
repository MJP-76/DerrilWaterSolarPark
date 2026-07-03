# Kirk Hill Wind Farm SCADA Simulator

A Home Assistant custom component that simulates a small SCADA-monitored wind farm: a farm-level control hub plus a configurable number of individual turbines, each with realistic wind/power/health dynamics and randomised fault injection. No external API or network access is required - everything runs locally inside Home Assistant.

If you like my work:
<br><a href="https://www.buymeacoffee.com/mjp76" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>
<br>Use my [Octopus.Energy 🐙](https://share.octopus.energy/iron-moose-196) referral code. You get £50 credit for joining and I get £50 credit.

## Features
- Local SCADA simulation - no API key or network calls needed
- Farm-level sensors: power, wind speed, capacity factor, farm state, active fault count
- Farm alarm binary sensor (on when degraded/critical)
- Per-turbine sensors: power, wind speed, health, state
- Per-turbine fault binary sensor
- Configurable turbine count and simulation tick interval, both at setup and via Options
- Services to inject faults, reset turbines, and override wind speed for testing/demo purposes
- Ready-to-import Lovelace SCADA dashboard

## Installation
<br>[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

1. Add this repository to HACS (Custom Repositories)
2. Install "Kirk Hill Wind SCADA Simulator"
3. Restart Home Assistant
4. Add the integration via Settings -> Devices & Services -> Add Integration -> "Kirk Hill Wind Farm"
5. Enter a site name, turbine count, and simulation tick interval

Turbine count and tick interval can be changed later from the integration's **Configure** (Options) menu.

## Sensors

Farm hub device:
- Power output (MW)
- Wind speed (m/s)
- Farm state (normal / degraded / critical)
- Active faults
- Capacity factor (%)
- Alarm (binary sensor)

Per turbine device (`Turbine T1` ... `Turbine TN`):
- Power output (MW)
- Wind speed (m/s)
- Health (%)
- State (normal / fault)
- Fault (binary sensor)

## Services

| Service | Description |
| --- | --- |
| `kirkhill_wind.inject_fault` | Force a specific turbine into a fault state |
| `kirkhill_wind.reset_turbine` | Reset a specific turbine back to healthy operation |
| `kirkhill_wind.set_wind_speed` | Override the simulated global wind speed (0-25 m/s) |

## Dashboard

A ready-made Lovelace dashboard is provided at [`dashboards/kirkhill_wind_scada.yaml`](dashboards/kirkhill_wind_scada.yaml) with a farm overview (glance + history graph + turbine tile grid) and a per-turbine detail view.

To use it:
1. Go to **Settings -> Dashboards -> Add Dashboard -> New dashboard from scratch**.
2. Open the new dashboard, choose **Edit Dashboard -> ... -> Raw configuration editor**.
3. Paste the contents of `dashboards/kirkhill_wind_scada.yaml`.
4. If you changed the default site name or turbine count, update the entity IDs in the YAML to match.

## License

MIT
