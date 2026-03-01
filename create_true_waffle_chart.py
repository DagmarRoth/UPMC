import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Read the CSV file
df = pd.read_csv('/Users/dagmarrothschild/Downloads/UPMC/Complications_and_Deaths-Hospital 2024 - Complications_and_Deaths-Hospital (1).csv')

# Filter for PA hospitals and PSI_04 measure
pa_psi04 = df[(df['State'] == 'PA') & (df['Measure ID'] == 'PSI_04')].copy()

# Convert Score to numeric, handling "Not Available"
pa_psi04['Score'] = pd.to_numeric(pa_psi04['Score'], errors='coerce')
pa_psi04 = pa_psi04[pa_psi04['Score'].notna()]

# US National Benchmark
US_BENCHMARK = 117.7

# Create system groupings (without Lehigh Valley)
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
pa_psi04_filtered = pa_psi04[pa_psi04['System'].notna()]

# Get UPMC Altoona specifically
upmc_altoona_data = pa_psi04_filtered[pa_psi04_filtered['Facility Name'].str.contains('UPMC ALTOONA', case=False, na=False)]
upmc_altoona_rate = upmc_altoona_data['Score'].values[0] if len(upmc_altoona_data) > 0 else 0

# Calculate system averages
system_averages = pa_psi04_filtered.groupby('System')['Score'].mean()

# Calculate excess deaths per 100,000
excess_deaths_data = {
    'UPMC Altoona': upmc_altoona_rate - US_BENCHMARK,
    'UPMC System Average': system_averages.get('UPMC', 0) - US_BENCHMARK,
    'Geisinger System': system_averages.get('Geisinger', 0) - US_BENCHMARK,
    'WellSpan System': system_averages.get('WellSpan', 0) - US_BENCHMARK,
}

# Sort by value descending
excess_deaths_data = dict(sorted(excess_deaths_data.items(), key=lambda x: x[1], reverse=True))

print("Excess Deaths per 100,000 Patients:")
for system, excess in excess_deaths_data.items():
    print(f"  {system}: {excess:+.1f}")

# Create waffle chart with improved design
fig = plt.figure(figsize=(14, 8))
ax = fig.add_subplot(111)

# Determine grid size
max_excess = max([v for k, v in excess_deaths_data.items() if v > 0])
cols = 20  # Number of columns in waffle
rows = int(np.ceil(max_excess / cols))

# Spacing parameters
y_start = len(excess_deaths_data) - 1
row_height = rows + 1.5
label_x = -1.2

for idx, (system, excess) in enumerate(excess_deaths_data.items()):
    y_pos = y_start - (idx * row_height)
    num_squares = int(np.ceil(excess)) if excess > 0 else 0

    # Draw squares for this system
    square_count = 0
    for row in range(rows):
        for col in range(cols):
            x = col
            y = y_pos - row

            if square_count < num_squares:
                # Red square for actual excess
                rect = patches.Rectangle((x, y), 0.92, 0.92,
                                        linewidth=0.8, edgecolor='#c0392b',
                                        facecolor='#d62728', zorder=2)
                ax.add_patch(rect)
                square_count += 1
            else:
                # Light gray square for remaining space
                rect = patches.Rectangle((x, y), 0.92, 0.92,
                                        linewidth=0.8, edgecolor='#e5e5e5',
                                        facecolor='#f5f5f5', zorder=1)
                ax.add_patch(rect)

    # Add label and value
    label_text = system
    value_text = f"{excess:+.0f}"
    ax.text(label_x, y_pos - rows/2 + 0.2, label_text,
            fontsize=13, fontweight='600', ha='right', va='center')
    ax.text(cols + 0.5, y_pos - rows/2 + 0.2, value_text,
            fontsize=13, fontweight='700', ha='left', va='center',
            color='#c0392b')

# Configure axes
ax.set_xlim(label_x - 0.3, cols + 2)
ax.set_ylim(y_start - (len(excess_deaths_data) * row_height) - 1, y_start + 1)
ax.set_aspect('equal')
ax.axis('off')

# Title and subtitle - centered on axis, not figure
center_x = (label_x - 0.3 + cols + 2) / 2  # Center of xlim
ax.text(center_x, y_start + 4.2, 'EXCESS DEATHS PER 100,000 PATIENTS',
        ha='center', fontsize=18, fontweight='bold', color='#1a1a1a')
ax.text(center_x, y_start + 2.2, 'Surgical Inpatients with Serious Treatable Complications',
        ha='center', fontsize=12, style='italic', color='#666')

# Footer note
fig.text(0.5, 0.015, 'Each ■ = 1 excess death per 100,000 patients',
         ha='center', fontsize=10, style='italic', color='#999', transform=fig.transFigure)

plt.tight_layout(rect=[0, 0.05, 1, 0.80])
plt.savefig('/Users/dagmarrothschild/Downloads/UPMC/excess_deaths_waffle_grid.png',
            dpi=300, bbox_inches='tight', facecolor='#faf9f7', edgecolor='none')
print("\nWaffle chart saved to: /Users/dagmarrothschild/Downloads/UPMC/excess_deaths_waffle_grid.png")
plt.close()
