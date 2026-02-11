import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load the dataset using pandas
df = pd.read_csv('All_Diets.csv')

# 2. Clean the data: convert columns to numeric and fill missing values with column means
for col in ['Protein(g)', 'Carbs(g)', 'Fat(g)']:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df[['Protein(g)', 'Carbs(g)', 'Fat(g)']] = df[['Protein(g)', 'Carbs(g)', 'Fat(g)']].fillna(df[['Protein(g)', 'Carbs(g)', 'Fat(g)']].mean())

# 3. Calculate average macronutrient content for each diet type
avg_macros = df.groupby('Diet_type')[['Protein(g)', 'Carbs(g)', 'Fat(g)']].mean()
print("\nAverage macronutrient content by diet type:")
print(avg_macros)

# 4. Top 5 protein-rich recipes for each diet type
top_protein = df.sort_values('Protein(g)', ascending=False).groupby('Diet_type').head(5)
print("\nTop 5 protein-rich recipes for each diet type:")
for diet in top_protein['Diet_type'].unique():
    print(f"\nDiet: {diet}")
    print(top_protein[top_protein['Diet_type'] == diet][['Recipe_name', 'Protein(g)', 'Cuisine_type']])

# 5. Diet type with the highest average protein content
highest_protein_diet = avg_macros['Protein(g)'].idxmax()
print(f"\nDiet type with the highest average protein: {highest_protein_diet}")

# 6. Most common cuisine for each diet type
common_cuisines = df.groupby('Diet_type')['Cuisine_type'].agg(lambda x: x.value_counts().idxmax())
print("\nMost common cuisine for each diet type:")
print(common_cuisines)

# 7. Add new metrics: protein-to-carbs and carbs-to-fat ratios
df['Protein_to_Carbs_ratio'] = df['Protein(g)'] / df['Carbs(g)']
df['Carbs_to_Fat_ratio'] = df['Carbs(g)'] / df['Fat(g)']

# 8. Visualizations

# Bar chart: Average macronutrients by diet type
plt.figure(figsize=(10,6))
avg_macros.plot(kind='bar')
plt.title('Average Macronutrient Content by Diet Type')
plt.ylabel('Grams')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('avg_macronutrients_by_diet_type.png')
plt.show()

# Heatmap: Correlation between macronutrients and diet types
plt.figure(figsize=(8,6))
sns.heatmap(avg_macros, annot=True, cmap='YlGnBu')
plt.title('Heatmap of Average Macronutrients by Diet Type')
plt.tight_layout()
plt.savefig('heatmap_macronutrients_by_diet_type.png')
plt.show()

# Scatter plot: Top 5 protein-rich recipes for each diet type
plt.figure(figsize=(10,6))
sns.scatterplot(data=top_protein, x='Diet_type', y='Protein(g)', hue='Cuisine_type', style='Cuisine_type', s=100)
plt.title('Top 5 Protein-rich Recipes per Diet Type')
plt.ylabel('Protein (g)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('top5_protein_recipes_scatter.png')
plt.show()

# Save processed data for reference
df.to_csv('All_Diets_processed.csv', index=False)

print("\nAnalysis complete. Plots saved as PNG files. You can use these images in your report or take screenshots with date/time visible.")

