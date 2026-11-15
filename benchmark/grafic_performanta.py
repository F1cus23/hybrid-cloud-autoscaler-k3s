import matplotlib.pyplot as plt

# Set academic style
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']

# Data setup
labels = ['Laptop\n(Baseline)', 'Proxmox Cluster\n(Local Only)', 'Hybrid System\n(Proxmox + Azure)']
times = [1434, 1185, 608]
# Professional academic palette (Grayscale friendly)
colors = ['#333333', '#666666', '#999999'] 

# Graph configuration
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(labels, times, color=colors, width=0.6, edgecolor='black', linewidth=1.5)

# Styling axes (No title inside the plot for academic papers)
ax.set_ylabel('Execution Time (Seconds)', fontsize=14)
ax.set_ylim(0, 1700)
ax.tick_params(axis='x', labelsize=12)
ax.tick_params(axis='y', labelsize=12)

# Add exact values above bars
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval + 30, f'{yval}s', 
            ha='center', va='bottom', fontsize=12)

# Add improvement percentages
laptop_time = times[0]
for i in range(1, len(bars)):
    bar = bars[i]
    improvement = ((laptop_time - times[i]) / laptop_time) * 100
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval / 2, f'-{improvement:.1f}%', 
            ha='center', va='center', fontsize=14, fontweight='bold', color='white')

# Subtle grid
ax.yaxis.grid(True, linestyle='--', alpha=0.5)
ax.set_axisbelow(True)

# Remove top and right spines for a cleaner academic look
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Save graph
plt.tight_layout()
plt.savefig('grafic_performanta.png', dpi=300)
print("Success! Academic graph saved.")