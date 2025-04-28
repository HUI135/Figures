import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
from PIL import Image

plt.rcParams["font.family"] = "Arial"

# Your DataFrame
# data1 = pd.read_csv('your_data.csv')

data1["HR"] = data1["aHR"].str.extract(r'(\d+\.\d{1,3})').astype(float)
data1[["CI_lower", "CI_upper"]] = data1["aHR"].str.extract(r'\[(\d+\.\d{1,3}),\s?(\d+\.\d{1,3})\]').astype(float)
data1.loc[data1["aHR"] == "1 [Reference]", "HR"] = 1

rows_with_space = []
for idx in range(len(data1)):
    if idx < 70:
        rows_with_space.append(data1.iloc[idx])
        if (idx + 1) % 5 == 0:
            empty_row = pd.Series([np.nan] * data1.shape[1], index=data1.columns)
            rows_with_space.append(empty_row)

data1_sorted_reversed = pd.DataFrame(rows_with_space).iloc[::-1].reset_index(drop=True).iloc[1:, :]

fig, ax = plt.subplots(figsize=(40.5, 10.5))

color_map = {
    '≥ 60': ('#6F4C85', '#6F4C85'),
    '45-59': ('#2C7FA7', '#2C7FA7'),
    '30-44': ('#009E73', '#009E73'),
    '15-29': ('#CB7530', '#CB7530'),
    '< 15 or dialysis': ('#D3415F', '#D3415F')
}

for i, row in data1_sorted_reversed.iterrows():
    if pd.notnull(row["outcome_category"]):
        ci_color, scatter_color = color_map[row["outcome_category"]]
        if pd.notnull(row["HR"]):
            if pd.notnull(row["CI_lower"]) and pd.notnull(row["CI_upper"]):
                ax.plot([row["CI_lower"], row["CI_upper"]], [i, i], color=ci_color, linewidth=2)
                ax.scatter(row["CI_lower"], i, color=ci_color, s=100, marker='|', zorder=3)
                ax.scatter(row["CI_upper"], i, color=ci_color, s=100, marker='|', zorder=3)
            ax.scatter(row["HR"], i, color=scatter_color, s=40, marker='s')

ax.hlines(y=0, xmin=0.5, xmax=9, color='#808080', linewidth=1)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)

ax.xaxis.set_ticks_position('bottom')
ax.spines['bottom'].set_position(('axes', 0.03))

ax.set_xticks([0.5, 1, 3, 5, 7, 9])
ax.set_xticklabels(["0.5", "1", "3", "5", "7", "9"])
ax.tick_params(axis='x', pad=-10, length=0)

for x in [0.5, 1, 3, 5, 7, 9]:
    ax.vlines(x, ymin=-0.25, ymax=0.25, color='#808080', linewidth=1)

ax.set_xlim([-7, 13.2])
ax.set_xlabel("Adjusted Hazard Ratio", fontsize=13, x=0.55, labelpad=5)
ax.set_title("Cause-specific mortality according to outcome category", fontsize=18, x=0.47, y=1.00, fontweight='bold')

ax.annotate(" 21.4 ", xy=(9, 44.1), xytext=(7.5, 44.1),
            fontsize=12, color='#CB7530', ha='left', va='center', fontweight='bold',
            arrowprops=dict(arrowstyle="->", color='#CB7530', linewidth=1.5))

ax.annotate(" 28.9 ", xy=(9, 43.1), xytext=(7.5, 43.1),
            fontsize=12, color='#D3415F', ha='left', va='center', fontweight='bold',
            arrowprops=dict(arrowstyle="->", color='#D3415F', linewidth=1.5))

italic_font = font_manager.FontProperties(style='italic', weight='bold')

header_y_position = len(data1_sorted_reversed) + 1.7
ax.text(-5.8, header_y_position, "Outcome", va='center', fontsize=15.5, ha='center', fontweight='bold')
ax.text(-1.65, header_y_position, "Outcome category", va='center', fontsize=15.5, ha='center', fontweight='bold')
ax.text(11.2, header_y_position, "aHR [95% C.I]", va='center', fontsize=15.5, ha='center', fontweight='bold')

for i, row in data1_sorted_reversed.iterrows():
    if i > 0:
        ax.text(-5.9, i-2, f"{row['Outcome'] if pd.notnull(row['Outcome']) else ''}", va='center', fontsize=14, ha='center', fontweight='bold')
        ax.text(-2.8, i, f"{row['outcome_category'] if pd.notnull(row['outcome_category']) else ''}", va='center', fontsize=13.5, ha='left')
        if pd.notnull(row["aHR"]):
            HR_text = row["aHR"].replace(", ", "–")
            ax.text(9.8, i, HR_text+" ", va='center', fontsize=13.5, ha='left')

ax.axvline(x=-3.5, linestyle='--', color='lightgrey', ymin=0.05, ymax=0.985, linewidth=0.5)
ax.axvline(x=0.2, linestyle='--', color='lightgrey', ymin=0.05, ymax=0.985, linewidth=0.5)
ax.axvline(x=9.3, linestyle='--', color='lightgrey', ymin=0.05, ymax=0.985, linewidth=0.5)
ax.axvline(x=1, linestyle='--', color='grey', ymin=0.05, ymax=0.985, linewidth=0.5)

plt.tight_layout()
plt.subplots_adjust(left=0.25, right=0.5, top=1.5, bottom=0.1)

# Save
png_path = os.path.join("outputs", "1_0_Cause_forest_plot_0417.png")
tiff_path = os.path.join("outputs", "1_0_Cause_forest_plot_0417.tiff")

fig.savefig(png_path, dpi=600, format="png", bbox_inches='tight')
with Image.open(png_path) as img:
    img.save(tiff_path, format="TIFF", dpi=(600, 600))

plt.show()
