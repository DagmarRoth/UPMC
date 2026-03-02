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

# Create system groupings
def get_system(facility_name):
    facility_name = str(facility_name).upper()
    if 'UPMC' in facility_name:
        return 'UPMC'
    elif 'GEISINGER' in facility_name:
        return 'Geisinger'
    elif 'LEHIGH' in facility_name or 'LEHIGH VALLEY' in facility_name:
        return 'Lehigh Valley Health Network'
    elif 'WELLSPAN' in facility_name:
        return 'WellSpan'
    return None

pa_psi04['System'] = pa_psi04['Facility Name'].apply(get_system)

# Filter for only our systems of interest
pa_psi04 = pa_psi04[pa_psi04['System'].notna()]

# Calculate system averages
system_averages = pa_psi04.groupby('System')['Score'].mean()

# Get UPMC Altoona specifically
upmc_altoona = pa_psi04[pa_psi04['Facility Name'].str.contains('UPMC ALTOONA', case=False, na=False)]['Score'].values
if len(upmc_altoona) > 0:
    upmc_altoona_rate = upmc_altoona[0]
else:
    upmc_altoona_rate = None

# Create data for waffle chart
data = {
    'UPMC Altoona': upmc_altoona_rate if upmc_altoona_rate else 0,
    'UPMC System Average': system_averages.get('UPMC', 0),
    'Geisinger System': system_averages.get('Geisinger', 0),
    'Lehigh Valley Health Network': system_averages.get('Lehigh Valley Health Network', 0),
    'WellSpan System': system_averages.get('WellSpan', 0)
}

print("Death Rates Among Surgical Inpatients with Serious Treatable Complications (PA)")
print("=" * 80)
for system, rate in data.items():
    print(f"{system}: {rate:.2f}")

# Create waffle chart
fig, ax = plt.subplots(figsize=(14, 8))

systems = list(data.keys())
rates = list(data.values())

# Define colors
colors = ['#1f77b4', '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

# Create bar chart (waffle-style can be created with rectangles)
x_pos = np.arange(len(systems))
bars = ax.bar(x_pos, rates, color=colors, edgecolor='black', linewidth=1.5)

# Add value labels on bars
for i, (bar, rate) in enumerate(zip(bars, rates)):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{rate:.1f}',
            ha='center', va='bottom', fontsize=12, fontweight='bold')

# Customize the chart
ax.set_xlabel('Healthcare System', fontsize=12, fontweight='bold')
ax.set_ylabel('Death Rate (per 1,000 surgical inpatients)', fontsize=12, fontweight='bold')
ax.set_title('Death Rate Among Surgical Inpatients with Serious Treatable Complications\nPA Healthcare Systems (2024)',
             fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x_pos)
ax.set_xticklabels(systems, rotation=45, ha='right', fontsize=11)
ax.grid(axis='y', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig('/Users/dagmarrothschild/Downloads/UPMC/waffle_chart.png', dpi=300, bbox_inches='tight')
print("\nChart saved to: /Users/dagmarrothschild/Downloads/UPMC/waffle_chart.png")
plt.show()
