import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
from PIL import Image

plt.rcParams["font.family"] = "Arial"

# Your DataFrame
# data2 = pd.read_csv('your_data.csv')

for group_name in data2['Group'].dropna().unique():
    subset = data2[data2['Group'] == group_name].copy().reset_index(drop=True)

    subset['HR'] = subset['aHR'].str.extract(r'(\d+\.\d{1,3})').astype(float)
    subset[['CI_lower', 'CI_upper']] = subset['aHR'].str.extract(r'\[(\d+\.\d{1,3}),\s?(\d+\.\d{1,3})\]').astype(float)
    subset.loc[subset['aHR'].str.contains('Reference', na=False), 'HR'] = 1

    rows_with_space = []
    for idx in range(len(subset)):
        rows_with_space.append(subset.iloc[idx])
        if (idx + 1) % 5 == 0:
            empty_row = pd.Series([np.nan] * subset.shape[1], index=subset.columns)
            rows_with_space.append(empty_row)

    subset_plot = pd.DataFrame(rows_with_space).iloc[::-1].reset_index(drop=True).iloc[1:, :]

    valid_data = subset_plot.dropna(subset=['CI_lower', 'CI_upper'])
    if not valid_data.empty:
        x_min = valid_data['CI_lower'].min()
        x_max = valid_data['CI_upper'].max()

    x_max = min(x_max, 10)
    x_range = x_max - x_min
    x_min = x_min - 0.1 * x_range
    x_max = x_max + 0.1 * x_range

    fig, ax = plt.subplots(figsize=(11, 15.25))

    color_map = {
        '≥ 60': ('#6F4C85', '#6F4C85'),
        '45-59': ('#2C7FA7', '#2C7FA7'),
        '30-44': ('#009E73', '#009E73'),
        '15-29': ('#CB7530', '#CB7530'),
        '< 15 or dialysis': ('#D3415F', '#D3415F')
    }

    for i, row in subset_plot.iterrows():
        if pd.notnull(row["outcome_category"]):
            ci_color, scatter_color = color_map.get(row["outcome_category"], ('black', 'black'))
            if pd.notnull(row["HR"]):
                if pd.notnull(row["CI_lower"]) and pd.notnull(row["CI_upper"]):
                    ax.plot([row["CI_lower"], row["CI_upper"]], [i, i], color=ci_color, linewidth=2)
                    ax.scatter(row["CI_lower"], i, color=ci_color, s=100, marker='|', zorder=3)
                    ax.scatter(row["CI_upper"], i, color=ci_color, s=100, marker='|', zorder=3)
                ax.scatter(row["HR"], i, color=scatter_color, s=40, marker='s')

    ax.hlines(y=0, xmin=x_min-0.001*x_range, xmax=x_max+0.02*x_range, color='#808080', linewidth=1)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    ax.set_yticks([])
    ax.set_yticklabels([])

    x_ticks = np.linspace(x_min-0.001*x_range, x_max+0.02*x_range, 5)
    x_tick_labels = [f"{x:.1f}" for x in x_ticks]
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_tick_labels)
    ax.tick_params(axis='x', pad=-40, length=0)

    for x in x_ticks:
        ax.vlines(x, ymin=-0.25, ymax=0.25, color='#808080', linewidth=1)

    # Background sections
    for start in range(0, len(subset_plot), 12):
        ax.fill_betweenx(y=[start, start+6], x1=x_min-1.3*x_range, x2=x_max+1.4*x_range, color='lightgrey', alpha=0.2)

    ax.set_xlim([x_min-1.3*x_range-0.1, x_max+1.4*x_range+0.1])
    ax.set_xlabel("Adjusted Hazard Ratio", fontsize=12, x=0.5, labelpad=-20)
    ax.set_title(f"Subgroup-specific {group_name} according to outcome category", fontsize=16, x=0.5, y=1.01, fontweight='bold')

    italic_font = font_manager.FontProperties(style='italic', weight='bold')
    header_y_position = len(subset_plot) + 2.5

    subgroup_x = x_min - 1.05 * x_range
    outcome_category_x = x_min - 0.45 * x_range
    ahr_x = x_max + 0.45 * x_range
    p_x = x_max + 0.84 * x_range
    p_inter_x = x_max + 0.9 * x_range

    ax.text(subgroup_x, header_y_position, "Subgroup", va='center', fontsize=14, ha='center', fontweight='bold')
    ax.text(outcome_category_x, header_y_position, "Outcome category", va='center', fontsize=14, ha='center', fontweight='bold')
    ax.text(ahr_x, header_y_position, "aHR [95% C.I]", va='center', fontsize=14, ha='center', fontweight='bold')
    ax.text(p_x, header_y_position, "P", va='center', fontsize=13.5, ha='center', fontproperties=italic_font)
    ax.text(p_inter_x, header_y_position, "for interaction", va='center', fontsize=14, ha='left', fontweight='bold')

    current_subgroup = None
    for i, row in subset_plot.iterrows():
        if pd.notnull(row["Subgroup"]) and row["Subgroup"] != current_subgroup:
            ax.text(subgroup_x, i-2, f"{row['Subgroup']}", va='center', fontsize=13, ha='center', fontweight='bold')
            current_subgroup = row["Subgroup"]
        if pd.notnull(row["outcome_category"]):
            ax.text(x_min - 0.65*x_range, i, f"{row['outcome_category']}", va='center', fontsize=13, ha='left')
        if pd.notnull(row["aHR"]):
            HR_text = row["aHR"].replace(", ", "–")
            ax.text(x_max + 0.2*x_range, i, HR_text, va='center', fontsize=13, ha='left')
        if pd.notnull(row.get("p for inter")):
            ax.text(x_max + 1.1*x_range, i, f"{row['p for inter']}", va='center', fontsize=13.5, ha='center')

    plt.tight_layout()
    plt.subplots_adjust(left=0.08, right=0.9, top=1.05, bottom=0.1)

    png_path = os.path.join("outputs", f"{group_name}_forest_plot_0417.png".replace(' ', '_'))
    tiff_path = os.path.join("outputs", f"{group_name}_forest_plot_0417.tiff".replace(' ', '_'))

    fig.savefig(png_path, dpi=600, format="png", bbox_inches='tight')
    with Image.open(png_path) as img:
        img.save(tiff_path, format="TIFF", dpi=(600, 600))

    plt.show()
