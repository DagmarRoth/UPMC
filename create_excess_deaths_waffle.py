import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the CSV file
df = pd.read_csv('/Users/dagmarrothschild/Downloads/UPMC/Complications_and_Deaths-Hospital 2024 - Complications_and_Deaths-Hospital (1).csv')

# Filter for PA hospitals and PSI_04 measure
pa_psi04 = df[(df['State'] == 'PA') & (df['Measure ID'] == 'PSI_04')].copy()

# Convert Score to numeric, handling "Not Available"
pa_psi04['Score'] = pd.to_numeric(pa_psi04['Score'], errors='coerce')

# Filter out rows with missing scores
pa_psi04 = pa_psi04[pa_psi04['Score'].notna()]

# US National Benchmark for PSI_04
# The scores appear to be per 100,000. A typical benchmark is around 117-120 per 100,000
US_BENCHMARK = 117.7

print("PA PSI_04 Data (Sample):")
print(pa_psi04[['Facility Name', 'Score']].head(5))
print(f"\nUS Benchmark: {US_BENCHMARK} per 100,000 patients")

# Create system groupings
def get_system(facility_name):
    facility_name = str(facility_name).upper()
    if 'UPMC' in facility_name:
        return 'UPMC'
    elif 'GEISINGER' in facility_name:
        return 'Geisinger'
    elif 'WELLSPAN' in facility_name:
        return 'WellSpan'
    return None

pa_psi04['System'] = pa_psi04['Facility Name'].apply(get_system)

# Filter for only our systems of interest
pa_psi04_filtered = pa_psi04[pa_psi04['System'].notna()]

print("\nFacilities by System:")
for system in pa_psi04_filtered['System'].unique():
    facilities = pa_psi04_filtered[pa_psi04_filtered['System'] == system]
    print(f"\n{system}:")
    for idx, row in facilities.iterrows():
        print(f"  {row['Facility Name']}: {row['Score']}")

# Get UPMC Altoona specifically
upmc_altoona_data = pa_psi04_filtered[pa_psi04_filtered['Facility Name'].str.contains('UPMC ALTOONA', case=False, na=False)]
if len(upmc_altoona_data) > 0:
    upmc_altoona_rate = upmc_altoona_data['Score'].values[0]
else:
    upmc_altoona_rate = None

# Calculate system averages
system_averages = pa_psi04_filtered.groupby('System')['Score'].mean()

# Calculate excess deaths per 100,000 compared to US benchmark
excess_deaths_data = {}

if upmc_altoona_rate:
    excess_deaths_data['UPMC Altoona'] = upmc_altoona_rate - US_BENCHMARK
else:
    excess_deaths_data['UPMC Altoona'] = 0

for system, rate in system_averages.items():
    excess_deaths_data[system] = rate - US_BENCHMARK

print("\n" + "="*80)
print("EXCESS DEATHS PER 100,000 PATIENTS")
print("(Compared to US National Benchmark)")
print("="*80)
for system, excess in sorted(excess_deaths_data.items(), key=lambda x: x[1], reverse=True):
    print(f"{system:.<40} {excess:+.1f}")

# Create waffle chart with excess deaths
fig, ax = plt.subplots(figsize=(14, 8))

# Sort by excess deaths descending
sorted_data = sorted(excess_deaths_data.items(), key=lambda x: x[1], reverse=True)
systems = [item[0] for item in sorted_data]
excess_values = [item[1] for item in sorted_data]

# Add US Benchmark at the bottom (with 0 excess)
systems_with_benchmark = systems + ['US Benchmark']
excess_with_benchmark = excess_values + [0]

# Colors: red for positive (worse than benchmark), gray for benchmark
colors = ['#d62728' if v > 2 else '#95a5a6' for v in excess_with_benchmark[:-1]] + ['#cccccc']

# Create horizontal bars
y_pos = np.arange(len(systems_with_benchmark))
bars = ax.barh(y_pos, excess_with_benchmark, color=colors, edgecolor='black', linewidth=1.2, height=0.65)

# Add value labels on bars
for i, (bar, excess) in enumerate(zip(bars, excess_with_benchmark)):
    width = bar.get_width()
    if width != 0:
        x_pos = width + 2 if width > 0 else width - 2
        ha = 'left' if width > 0 else 'right'
        ax.text(x_pos, bar.get_y() + bar.get_height()/2.,
                f'{excess:+.0f}',
                ha=ha, va='center', fontsize=11, fontweight='bold')
    else:
        ax.text(1, bar.get_y() + bar.get_height()/2.,
                '±0',
                ha='left', va='center', fontsize=11, fontweight='bold', color='#666666')

# Customize the chart
ax.set_yticks(y_pos)
ax.set_yticklabels(systems_with_benchmark, fontsize=11)
ax.set_xlabel('Excess Deaths per 100,000 Patients', fontsize=12, fontweight='bold')
ax.set_title('EXCESS DEATHS PER 100,000 PATIENTS\nSurgical Inpatients with Serious Treatable Complications (PA)',
             fontsize=13, fontweight='bold', pad=20, color='#d62728')
ax.axvline(x=0, color='black', linestyle='-', linewidth=2.5)
ax.grid(axis='x', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)

# Add separator line before benchmark
ax.axhline(y=len(systems)-0.5, color='#cccccc', linestyle='-', linewidth=2)

# Add a note about the benchmark
fig.text(0.5, 0.02, 'US National Benchmark = 0 | Each unit = 1 excess death per 100,000 patients',
         ha='center', fontsize=9, style='italic')

plt.tight_layout(rect=[0, 0.03, 1, 1])
plt.savefig('/Users/dagmarrothschild/Downloads/UPMC/excess_deaths_waffle.png', dpi=300, bbox_inches='tight')
print("\nChart saved to: /Users/dagmarrothschild/Downloads/UPMC/excess_deaths_waffle.png")
plt.close()
