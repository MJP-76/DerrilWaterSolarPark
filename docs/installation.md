# Installation

## HACS (recommended)

1. In HACS, add this repository as a custom repository (category: **Integration**):
   `https://github.com/MJP-76/DerrilWaterSolarPark`
2. Search for "Derril Water Solar Park" in HACS and install it.
3. Restart Home Assistant.
4. Go to **Settings > Devices & Services > Add Integration**, search for
   "Derril Water Solar Park", and enter your Derril Water Solar Park API key
   and site name.

## Manual

1. Copy `custom_components/derril_water_solar_park/` into your Home Assistant
   `config/custom_components/` directory.
2. Restart Home Assistant.
3. Go to **Settings > Devices & Services > Add Integration**, search for
   "Derril Water Solar Park", and enter your API key and site name.

## Configuration flow

The config flow asks for:

- **API key** — your personal Derril Water Solar Park dashboard API key.
- **Site name** — a label for the site, used in your entities.

!!! tip "Getting an API key"

    Your personal API key is available from the Derril Water Solar Park
    dashboard — this integration reads the dashboard's public API endpoints
    with it, so a valid key is required before data can be pulled.