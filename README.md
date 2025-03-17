# Klemera-Doubal Biological Age Calculator

This repository contains a Python implementation of the Klemera-Doubal (KD) method for calculating biological age based on biomarkers. The KD method is considered one of the most accurate statistical approaches for biological age estimation.

## Background

The Klemera-Doubal method was proposed in a 2006 paper:

> Klemera P, Doubal S. A new approach to the concept and computation of biological age. Mech Ageing Dev. 2006;127(3):240-248. doi:10.1016/j.mad.2005.10.004

It uses multiple biomarkers that correlate with chronological age to create a more accurate estimation of biological age. The method works by:

1. Establishing linear regression relationships between each biomarker and chronological age
2. Computing biological age as a weighted average of biomarker-specific age estimates
3. Optionally incorporating chronological age into the calculation 

Compared to other methods like multiple linear regression, the KD method has several advantages:
- Better theoretical foundation
- More accurate and reliable biological age estimates
- Better correlation with mortality and morbidity

## Installation

1. Clone this repository
2. Install dependencies:
```
pip install -r requirements.txt
```

## Usage

### Basic Example

```python
from klemera_doubal import KlemeraDoubal
import pandas as pd

# Load your data (must have chronological age and biomarker columns)
data = pd.read_csv("your_data.csv")

# Split data into training and testing sets (optional)
from sklearn.model_selection import train_test_split
train_data, test_data = train_test_split(data, test_size=0.3, random_state=42)

# Initialize KD calculator (specify your chronological age column)
kd = KlemeraDoubal(chronological_age_col='age')

# Fit the model on training data
kd.fit(train_data, 
       biomarkers=['biomarker1', 'biomarker2', 'biomarker3', 'biomarker4'],
       verbose=True)

# Get a summary of the model parameters
summary = kd.get_summary()
print(summary)

# Calculate biological ages for test data
biological_ages = kd.predict(test_data)

# Calculate biological ages including chronological age in the estimation
biological_ages_with_ca = kd.predict(test_data, include_chronological=True)

# Plot relationships between biomarkers and chronological age
kd.plot_biomarker_relationships(data)

# Plot biological age vs chronological age
kd.plot_biological_vs_chronological(test_data, biological_ages)
```

### Using the Included Example

The module includes an example with simulated data that you can run directly:

```
python klemera_doubal.py
```

This will:
1. Generate simulated data with biomarkers related to age
2. Fit the KD model
3. Calculate biological ages
4. Create visualizations saved as PNG files

## Input Data Format

Your data should be in a pandas DataFrame format with:
- A column for chronological age
- Columns for each biomarker you want to include

Biomarkers should have some relationship with chronological age (either positive or negative correlation).

## Interpreting Results

- Biological age above chronological age suggests accelerated aging
- Biological age below chronological age suggests slower aging
- The difference between biological and chronological age (BA-CA) is sometimes called the "aging pace"

## Customization

The implementation allows you to:
- Specify which biomarkers to include
- Choose whether to include chronological age in the calculation
- Customize visualization parameters

## License

This implementation is provided for research and educational purposes.

## Citation

If you use this implementation in your research, please cite the original Klemera-Doubal paper:

Klemera P, Doubal S. A new approach to the concept and computation of biological age. Mech Ageing Dev. 2006;127(3):240-248. doi:10.1016/j.mad.2005.10.004 