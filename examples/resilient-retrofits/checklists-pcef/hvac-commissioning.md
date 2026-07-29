# Commissioning Diagnostics
key: hvac_commissioning
applies: hvac
auto: commission
qa: true
type: record
order: 20

- HP Airflow (CFM)
- CFM/ton (target 350-400)
- Supply static pressure (in. WG)
- Return static upstream of filter (in. WG)
- Return static downstream of filter (in. WG)
- Pressure pan test — avg < 1.5, no single > 2 (Q60)
- Room pressurization — no room > 3 Pa (Q62)
