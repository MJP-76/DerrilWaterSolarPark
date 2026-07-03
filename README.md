# Kirk Hill Wind Farm Integration

A Home Assistant custom component that reads live data from the Kirk Hill Wind Farm API.

<p align="center">
  <a href="https://www.home-assistant.io/" target="_blank" rel="noopener noreferrer">
    <img src="https://cdn.simpleicons.org/homeassistant/41BDF5" alt="Home Assistant" height="40">
  </a>
  <a href="https://github.com/MJP-76/KirkHillWindFarm" target="_blank" rel="noopener noreferrer">
    <img src="https://cdn.simpleicons.org/github" alt="GitHub" height="40">
  </a>
  <a href="https://github.com/features/copilot" target="_blank" rel="noopener noreferrer">
    <img src="https://cdn.simpleicons.org/githubcopilot" alt="GitHub Copilot" height="40">
  </a>
</p>

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
  - generation by timeframe: yesterday, today, week, month, ytd, year, alltime
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
- Auto-generated Lovelace dashboard tab created during integration setup
- Dashboard includes turbine map and coordinate list (lat/lon from API)
- Dashboard YAML file is still included for manual import/customization

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
- Generation (yesterday) [kWh] for owner and site
- Generation (today) [kWh] for owner and site
- Generation (week) [kWh] for owner and site
- Generation (month) [kWh] for owner and site
- Generation (ytd) [kWh] for owner and site
- Generation (year) [kWh] for owner and site
- Generation (alltime) [kWh] for owner and site
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

When you add the integration, it auto-creates a Lovelace dashboard tab (`kirk-hill-wind-dashboard`) in the sidebar.

The generated dashboard includes:
- owner vs site farm metrics
- farm wind and turbine availability
- per-turbine owner/site power and capacity sensors
- turbine map
- turbine latitude/longitude attribute list

For manual import or customization, a dashboard YAML is also provided at [`dashboards/kirkhill_wind_scada.yaml`](dashboards/kirkhill_wind_scada.yaml).

## License

MIT
