#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example script for calculating biological age using reference weights.

This script demonstrates how to use the reference weights from published studies
to calculate biological age without having to fit your own model.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from kd_reference_weights import calculate_bioage_from_reference, calculate_phenoage

# Simulate a small dataset of people with different ages and biomarker values
def generate_simulated_data(n_samples=100, seed=42):
    """Generate a simulated dataset of people with biomarkers."""
    np.random.seed(seed)
    
    # Generate ages between 30 and 80
    ages = np.random.uniform(30, 80, n_samples)
    
    # Generate sex (0=male, 1=female)
    sex = np.random.binomial(1, 0.5, n_samples)
    
    # Generate biomarkers with some relationship to age and random noise
    c_reactive_protein = 0.1 + 0.01 * ages + np.random.normal(0, 0.3, n_samples)
    c_reactive_protein = np.maximum(0.1, c_reactive_protein)  # Ensure positive values
    
    glycated_hemoglobin = 5.0 + 0.02 * ages + np.random.normal(0, 0.4, n_samples)
    
    serum_albumin = 4.5 - 0.005 * ages + np.random.normal(0, 0.2, n_samples)
    
    alkaline_phosphatase = 60 + 0.5 * ages + np.random.normal(0, 15, n_samples)
    
    # Forced expiratory volume decreases with age and is higher in males
    forced_expiratory_volume = 4000 - 20 * ages + 500 * (1 - sex) + np.random.normal(0, 400, n_samples)
    
    systolic_blood_pressure = 100 + 0.7 * ages + np.random.normal(0, 10, n_samples)
    
    serum_urea_nitrogen = 10 + 0.1 * ages + np.random.normal(0, 3, n_samples)
    
    # Create a DataFrame
    data = pd.DataFrame({
        'age': ages,
        'sex': sex,
        'sex_label': ['male' if s == 0 else 'female' for s in sex],
        'c_reactive_protein': c_reactive_protein,
        'glycated_hemoglobin': glycated_hemoglobin,
        'serum_albumin': serum_albumin,
        'alkaline_phosphatase': alkaline_phosphatase,
        'forced_expiratory_volume': forced_expiratory_volume,
        'systolic_blood_pressure': systolic_blood_pressure,
        'serum_urea_nitrogen': serum_urea_nitrogen
    })
    
    # Add additional biomarkers for PhenoAge calculation
    data['creatinine'] = 0.7 + 0.005 * ages + 0.2 * (1 - sex) + np.random.normal(0, 0.15, n_samples)
    data['glucose'] = 70 + 0.5 * ages + np.random.normal(0, 10, n_samples)
    data['log_crp'] = np.log(data['c_reactive_protein'] * 10)  # Convert to mg/L and take log
    data['lymphocyte_percent'] = 35 - 0.1 * ages + np.random.normal(0, 5, n_samples)
    data['mean_cell_volume'] = 85 + 0.1 * ages + np.random.normal(0, 3, n_samples)
    data['red_cell_distribution_width'] = 12 + 0.02 * ages + np.random.normal(0, 1, n_samples)
    data['white_blood_cell_count'] = 7 + np.random.normal(0, 1.5, n_samples)
    
    return data

def calculate_biological_ages(data):
    """Calculate biological ages using different methods."""
    # Add columns for biological age calculations
    data['bioage_nhanes'] = np.nan
    data['bioage_nhanes_with_ca'] = np.nan
    data['phenoage'] = np.nan
    
    # Calculate biological ages for each person
    for i, row in data.iterrows():
        # Extract biomarkers for the KD method
        biomarkers = {
            'c_reactive_protein': row['c_reactive_protein'],
            'glycated_hemoglobin': row['glycated_hemoglobin'],
            'serum_albumin': row['serum_albumin'],
            'alkaline_phosphatase': row['alkaline_phosphatase'],
            'forced_expiratory_volume': row['forced_expiratory_volume'],
            'systolic_blood_pressure': row['systolic_blood_pressure'],
            'serum_urea_nitrogen': row['serum_urea_nitrogen']
        }
        
        # Calculate biological age without chronological age
        data.loc[i, 'bioage_nhanes'] = calculate_bioage_from_reference(
            biomarkers,
            sex=row['sex_label'],
            include_chronological_age=False
        )
        
        # Calculate biological age including chronological age
        data.loc[i, 'bioage_nhanes_with_ca'] = calculate_bioage_from_reference(
            biomarkers,
            sex=row['sex_label'],
            include_chronological_age=True,
            chronological_age=row['age']
        )
        
        # Calculate PhenoAge
        data.loc[i, 'phenoage'] = calculate_phenoage(
            albumin=row['serum_albumin'],
            creatinine=row['creatinine'],
            glucose=row['glucose'],
            log_crp=row['log_crp'],
            lymphocyte_percent=row['lymphocyte_percent'],
            mean_cell_volume=row['mean_cell_volume'],
            red_cell_distribution_width=row['red_cell_distribution_width'],
            alkaline_phosphatase=row['alkaline_phosphatase'],
            white_blood_cell_count=row['white_blood_cell_count'],
            chronological_age=row['age']
        )
    
    # Calculate aging pace (difference between biological and chronological age)
    data['aging_pace_nhanes'] = data['bioage_nhanes'] - data['age']
    data['aging_pace_nhanes_with_ca'] = data['bioage_nhanes_with_ca'] - data['age']
    data['aging_pace_phenoage'] = data['phenoage'] - data['age']
    
    return data

def plot_results(data):
    """Create visualizations of the biological age calculations."""
    # Plot 1: Biological Age vs Chronological Age
    plt.figure(figsize=(10, 8))
    
    plt.scatter(data['age'], data['bioage_nhanes'], 
                alpha=0.7, label='BioAge (NHANES)', color='blue')
    plt.scatter(data['age'], data['bioage_nhanes_with_ca'], 
                alpha=0.7, label='BioAge with CA (NHANES)', color='green')
    plt.scatter(data['age'], data['phenoage'], 
                alpha=0.7, label='PhenoAge', color='red')
    
    # Add y=x line
    min_age = min(data['age'].min(), data['bioage_nhanes'].min(), 
                 data['bioage_nhanes_with_ca'].min(), data['phenoage'].min())
    max_age = max(data['age'].max(), data['bioage_nhanes'].max(), 
                 data['bioage_nhanes_with_ca'].max(), data['phenoage'].max())
    plt.plot([min_age, max_age], [min_age, max_age], 'k--', label='y=x line')
    
    plt.xlabel('Chronological Age')
    plt.ylabel('Biological Age')
    plt.title('Biological Age vs Chronological Age')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig('bioage_comparison.png')
    
    # Plot 2: Aging Pace Distribution
    plt.figure(figsize=(10, 6))
    
    plt.hist(data['aging_pace_nhanes'], bins=20, alpha=0.5, label='NHANES')
    plt.hist(data['aging_pace_nhanes_with_ca'], bins=20, alpha=0.5, label='NHANES with CA')
    plt.hist(data['aging_pace_phenoage'], bins=20, alpha=0.5, label='PhenoAge')
    
    plt.axvline(x=0, color='k', linestyle='--')
    plt.xlabel('Aging Pace (Biological Age - Chronological Age)')
    plt.ylabel('Count')
    plt.title('Distribution of Aging Pace')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig('aging_pace_distribution.png')
    
    # Plot 3: Biomarker Relationships with Age
    biomarkers = ['c_reactive_protein', 'glycated_hemoglobin', 'serum_albumin', 
                  'alkaline_phosphatase', 'forced_expiratory_volume', 
                  'systolic_blood_pressure', 'serum_urea_nitrogen']
    
    fig, axes = plt.subplots(3, 3, figsize=(15, 12))
    axes = axes.flatten()
    
    for i, biomarker in enumerate(biomarkers):
        if i < len(axes):
            ax = axes[i]
            ax.scatter(data['age'], data[biomarker], alpha=0.6)
            ax.set_xlabel('Age')
            ax.set_ylabel(biomarker)
            ax.set_title(f'{biomarker} vs Age')
            ax.grid(True, linestyle='--', alpha=0.7)
    
    # Hide empty subplots
    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)
        
    plt.tight_layout()
    plt.savefig('biomarker_relationships.png')

def main():
    # Generate simulated data
    print("Generating simulated data...")
    data = generate_simulated_data(n_samples=100)
    
    # Calculate biological ages
    print("Calculating biological ages...")
    data = calculate_biological_ages(data)
    
    # Display summary statistics
    print("\nSummary Statistics:")
    print(data[['age', 'bioage_nhanes', 'bioage_nhanes_with_ca', 'phenoage']].describe())
    
    # Display correlations
    print("\nCorrelations with Chronological Age:")
    correlations = data[['age', 'bioage_nhanes', 'bioage_nhanes_with_ca', 'phenoage']].corr()['age']
    print(correlations)
    
    # Plot results
    print("\nCreating visualizations...")
    plot_results(data)
    
    print("\nDone! Check the output files:")
    print("- bioage_comparison.png")
    print("- aging_pace_distribution.png")
    print("- biomarker_relationships.png")
    
    # Save the data to a CSV file
    data.to_csv('simulated_bioage_data.csv', index=False)
    print("- simulated_bioage_data.csv")

if __name__ == "__main__":
    main() 