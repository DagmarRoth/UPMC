# What's going on

This project investigates surgical mortality outcomes at UPMC hospitals following the health system's 2019 deployment of a machine learning algorithm designed to predict and prevent post-surgical complications. The analysis uses federal CMS Hospital Compare data to track the PSI-04 measure, death rate among surgical inpatients with serious but treatable complications.

I found that UPMC Altoona ranked #1 in the country for PSI-04 mortality in the most recent CMS data (2022–2024), with a rate of 259 deaths per 1,000 qualifying surgical patients, 50% above the national average. Two other UPMC hospitals (Hamot and Mercy) ranked in the top 15 nationally.


## Data Collection Process

All primary data comes from CMS Hospital Compare, downloaded from the CMS data portal. Four separate release archives were used, each representing a distinct reporting period:

| Filename | CMS Release | PSI-04 Measurement Period | Hospital Count |
|----------|-------------|---------------------------|----------------|
| hospitals_11_2023.zip | November 2023 | July 2019 – June 2021 | 1,432 reporting |
| hospitals_01_2024.zip | January 2024 | July 2020 – June 2022 | 1,609 reporting |
| hospitals_11_2025.zip | November 2025 | July 2022 – June 2024 | 1,524 reporting |
| hospitals_02_2026.zip | February 2026 | July 2022 – June 2024 | 1,524 reporting |


## Data Processing For PSI-04

For each file, records were filtered to PSI-04 only. Records with "Not Available" or blank score or denominator fields were excluded. Records with a denominator of 0 were also excluded.

### National Rate Calculation
A weighted national average rate was computed for each reporting period using all qualifying US hospitals:
```
national_rate = SUM(score/1000 * denominator) / SUM(denominator)
```

### Excess Deaths Calculation
Excess deaths for each entity were calculated as the difference between observed and expected deaths:
```
excess = SUM( (score/1000 - national_rate) * denominator )
```
For system-level entities (UPMC System Average, Geisinger System, Lehigh Valley Health Network, WellSpan System), the total excess was divided by the number of qualifying hospitals in the system for that period to produce a per-hospital average.
The PA State Average was computed as total excess across all PA hospitals divided by the number of PA hospitals reporting in that period.

### Rate Comparison (per 1,000)
For the primary visualization, raw PSI-04 rates per 1,000 were used rather than excess deaths. This allows ranking by severity of outcome per patient, independent of hospital volume.
```
rate_per_1000 = score  (already expressed per 1,000 by CMS)
```
For system averages, a volume-weighted mean was computed across all system hospitals in that period.

## Waffle/Bar Chart — Excess Deaths per 100,000 Patients
Built in Python using a waffle bar extension and a bit of help from Claude. Displays PSI-04 excess deaths per 100,000 qualifying surgical patients for UPMC Altoona, UPMC System Average, Geisinger System, WellSpan System, and US Benchmark. Each square represents one excess death per 100,000 patients.

## Range Plot — PSI-04 Rate Change Over Time (Datawrapper)

Built in Datawrapper using the Range Plot (Arrow Plot) chart type

### Key design decisions:
- Two periods only shown (not three) to avoid overlap confusion from CMS's rolling 3-year windows
- Range plot selected over grouped bar chart because it shows directional change more clearly
- Axis starts at 120 (natural minimum of the data range) rather than 0
- 2022–2024 endpoint labeled in the chart header rather than as a colored series

## Important Caveats
- PSI-04 uses CMS risk adjustment but does not account for every possible confounding variable. Patient complexity, referral patterns, and documentation practices can all influence scores.
- CMS uses overlapping 3-year measurement windows. The 2019–2021 and 2020–2022 periods share two years of data and are not independent snapshots. The primary comparison uses 2019–2021 vs 2022–2024, which do not overlap.
- Not all US hospitals report PSI-04 data to CMS. The national ranking is among the 1,524 hospitals that reported in the February 2026 release.
- This analysis establishes correlation between the algorithm's deployment and rising PSI-04 rates. It does not establish causation. UPMC has not responded to questions about the divergence.
- Dr. Aman Mahajan, the algorithm's lead architect, was interviewed on February 24, 2026.
