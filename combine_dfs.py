import pandas as pd

CBS_data = pd.read_csv('CBS_data.csv')
HF04_data = pd.read_csv('res.csv')

org_lvl = [
    'Organisation unit',
    "National",
    "District",
    "Council",
    "Chiefdom",
    "Clinic",
    'CHW',
    'nufVxEfy3Ps.REPORTING_RATE',
    'nufVxEfy3Ps.REPORTING_RATE_ON_TIME',
    'nufVxEfy3Ps.ACTUAL_REPORTS',
    'nufVxEfy3Ps.ACTUAL_REPORTS_ON_TIME',
    'nufVxEfy3Ps.EXPECTED_REPORTS'
]

meged_df = pd.merge(
    CBS_data,
    HF04_data[org_lvl],
    on='Organisation unit',
    how='left'
)

meged_df.to_csv('merged.csv')