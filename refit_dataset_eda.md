# REFIT Appliance Power Summary

Per-appliance summary statistics derived from the [REFIT Electrical Load Measurements dataset](https://pureportal.strath.ac.uk/en/datasets/refit-electrical-load-measurements) (Murray et al., 2015), covering 20 UK households (House 1–21, House 14 excluded) monitored at ~8-second resolution between September 2013 and July 2015.

Each household has 1 whole-house aggregate circuit plus 9 Individual Appliance Monitors (IAMs), for 200 rows total (20 houses × 10 channels).

## File

`appliance_summary.csv` — 200 rows, 8 columns.

| Column | Type | Description |
|---|---|---|
| `house` | int | House ID (1–21, skipping 14) |
| `appliance` | string | Appliance label as given in the REFIT documentation (e.g. `Fridge`, `Washing Machine`). `???` indicates an appliance whose identity was not recorded by the original study. |
| `category` | string | Appliance normalized into a common category so the same appliance type can be compared across houses (e.g. `Fridge`, `Fridge-Freezer`, `Freezer`, `Washing Machine`, `Washer Dryer`, `Tumble Dryer`, `Dishwasher`, `Television/Site`, `Computer/Site`, `Microwave`, `Kettle`, `Toaster`, `Hi-Fi`, `Electric Heater`, `Other`, `Unknown`, `Aggregate`). |
| `is_agg` | bool | `True` for the whole-house aggregate channel, `False` for individual appliances. |
| `mean` | float | Mean power draw in watts (W) over the full monitoring period. |
| `std` | float | Standard deviation of power draw, in watts. |
| `max` | float | Maximum recorded power draw, in watts. |
| `pct_on` | float | Percentage of readings where the appliance drew more than 10W ("on-time"). |

## Data cleaning applied

- Raw REFIT readings occasionally contain implausible sensor-glitch spikes (up to ~65,000W). Before computing statistics, appliance-channel readings were capped at **4,000W** and the whole-house aggregate channel at **20,000W**.
- Missing sensor readings (literal `NaN` in the source data — e.g. 3 channels in House 12 that were never recorded) are excluded from mean/std/max/pct_on rather than treated as zero. These appear as `NaN` in this summary.

## Source

Values were computed from the raw REFIT CSV files (`House1.csv` … `House21.csv`), which record `UNIX_TIMESTAMP, Aggregate, Appliance1, ..., Appliance9` at ~8-second intervals, with a sensor-to-appliance mapping specific to each house (documented in the original REFIT README).

## Citation

Murray, D., Liao, J., Stankovic, L., Stankovic, V., Hauxwell-Baldwin, R., Wilson, C., Coleman, M., Kane, T., & Firth, S. (2015). *A data management platform for personalised real-time energy feedback*. Proceedings of the 8th International Conference on Energy Efficiency in Domestic Appliances and Lighting.
