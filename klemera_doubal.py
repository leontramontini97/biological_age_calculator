#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Implementation of the Klemera-Doubal (KD) method for calculating biological age.

Reference:
Klemera P, Doubal S. A new approach to the concept and computation of biological age.
Mech Ageing Dev. 2006;127(3):240-248. doi:10.1016/j.mad.2005.10.004
"""

import numpy as np
from scipy import stats
from typing import List, Tuple, Dict, Optional, Union
import pandas as pd
import matplotlib.pyplot as plt


class KlemeraDoubal:
    """
    Class implementing the Klemera-Doubal method for calculating biological age.
    """
    
    def __init__(self, chronological_age_col: str = 'age'):
        """
        Initialize the KD biological age calculator.
        
        Parameters:
        -----------
        chronological_age_col : str, default='age'
            Column name for chronological age in the dataset
        """
        self.chronological_age_col = chronological_age_col
        self.biomarkers = []
        self.fitted = False
        self.params = {}
        self.s_BA = None
        
    def fit(self, 
            data: pd.DataFrame, 
            biomarkers: List[str],
            verbose: bool = False) -> None:
        """
        Fit the KD model to training data.
        
        Parameters:
        -----------
        data : pd.DataFrame
            Training data containing biomarkers and chronological age
        biomarkers : List[str]
            List of column names for biomarkers to be used
        verbose : bool, default=False
            Whether to print detailed information during fitting
        """
        if self.chronological_age_col not in data.columns:
            raise ValueError(f"Chronological age column '{self.chronological_age_col}' not found in data")
            
        for biomarker in biomarkers:
            if biomarker not in data.columns:
                raise ValueError(f"Biomarker '{biomarker}' not found in data")
        
        self.biomarkers = biomarkers
        chronological_age = data[self.chronological_age_col].values
        
        # Calculate parameters for each biomarker
        self.params = {}
        for biomarker in self.biomarkers:
            biomarker_values = data[biomarker].values
            
            # Simple linear regression x_i = q_i + k_i * CA + e_i
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                chronological_age, biomarker_values
            )
            
            # Calculate residual standard error (s_i)
            residuals = biomarker_values - (intercept + slope * chronological_age)
            s_i = np.sqrt(np.sum(residuals**2) / (len(residuals) - 2))
            
            # Store parameters
            self.params[biomarker] = {
                'k_i': slope,  # slope
                'q_i': intercept,  # intercept
                's_i': s_i,  # residual standard error
                'r2': r_value**2,  # coefficient of determination
                'corr': r_value,  # correlation coefficient
                'p_value': p_value,  # p-value for the regression
                'std_err': std_err  # standard error of the estimate
            }
            
            if verbose:
                print(f"Biomarker: {biomarker}")
                print(f"  Slope (k_i): {slope:.4f}")
                print(f"  Intercept (q_i): {intercept:.4f}")
                print(f"  Residual std error (s_i): {s_i:.4f}")
                print(f"  R-squared: {r_value**2:.4f}")
                print(f"  p-value: {p_value:.4e}")
                print("-----")
        
        # Calculate s_BA (standard deviation of the biological age)
        k_i_squared_over_s_i_squared_sum = sum([
            (self.params[biomarker]['k_i']**2) / (self.params[biomarker]['s_i']**2)
            for biomarker in self.biomarkers
        ])
        
        self.s_BA = 1 / np.sqrt(k_i_squared_over_s_i_squared_sum)
        
        if verbose:
            print(f"Standard deviation of biological age (s_BA): {self.s_BA:.4f}")
        
        self.fitted = True
    
    def predict(self, data: pd.DataFrame, include_chronological: bool = False) -> np.ndarray:
        """
        Calculate biological age using the KD method.
        
        Parameters:
        -----------
        data : pd.DataFrame
            Data containing biomarkers for prediction
        include_chronological : bool, default=False
            Whether to include chronological age in the calculation
            
        Returns:
        --------
        np.ndarray
            Biological age estimates for each sample
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before prediction")
        
        # Check if all biomarkers are present
        missing_biomarkers = [b for b in self.biomarkers if b not in data.columns]
        if missing_biomarkers:
            raise ValueError(f"Missing biomarkers in data: {missing_biomarkers}")
        
        n_samples = len(data)
        biological_ages = np.zeros(n_samples)
        
        for i in range(n_samples):
            sample = data.iloc[i]
            
            # Calculate terms for the weighted average
            numerator_sum = 0
            denominator_sum = 0
            
            for biomarker in self.biomarkers:
                k_i = self.params[biomarker]['k_i']
                q_i = self.params[biomarker]['q_i']
                s_i = self.params[biomarker]['s_i']
                
                x_i = sample[biomarker]
                
                # Calculate the terms for the weighted average
                weight = (k_i**2) / (s_i**2)
                ba_estimate = (x_i - q_i) / k_i
                
                numerator_sum += weight * ba_estimate
                denominator_sum += weight
            
            # Include chronological age in calculation if requested
            if include_chronological and self.chronological_age_col in data.columns:
                ca = sample[self.chronological_age_col]
                s_CA = self.s_BA  # Assuming s_CA = s_BA following the paper
                
                weight_ca = 1 / (s_CA**2)
                numerator_sum += weight_ca * ca
                denominator_sum += weight_ca
            
            # Calculate the biological age
            biological_ages[i] = numerator_sum / denominator_sum
        
        return biological_ages
    
    def plot_biomarker_relationships(self, data: pd.DataFrame, figsize=(15, 10)):
        """
        Plot the relationship between each biomarker and chronological age.
        
        Parameters:
        -----------
        data : pd.DataFrame
            Data containing biomarkers and chronological age
        figsize : tuple, default=(15, 10)
            Size of the figure
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before plotting")
            
        if self.chronological_age_col not in data.columns:
            raise ValueError(f"Chronological age column '{self.chronological_age_col}' not found in data")
        
        # Calculate number of rows and columns for subplots
        n_biomarkers = len(self.biomarkers)
        n_cols = min(3, n_biomarkers)
        n_rows = int(np.ceil(n_biomarkers / n_cols))
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        if n_rows == 1 and n_cols == 1:
            axes = np.array([axes])
        axes = axes.flatten()
        
        for i, biomarker in enumerate(self.biomarkers):
            ax = axes[i]
            
            # Extract parameters
            k_i = self.params[biomarker]['k_i']
            q_i = self.params[biomarker]['q_i']
            r2 = self.params[biomarker]['r2']
            
            # Plot data points
            ax.scatter(data[self.chronological_age_col], data[biomarker], alpha=0.5)
            
            # Plot regression line
            x_range = np.array([data[self.chronological_age_col].min(), data[self.chronological_age_col].max()])
            y_range = q_i + k_i * x_range
            ax.plot(x_range, y_range, 'r-', linewidth=2)
            
            # Add labels and title
            ax.set_xlabel('Chronological Age')
            ax.set_ylabel(biomarker)
            ax.set_title(f"{biomarker} vs Age (R² = {r2:.3f})")
            ax.grid(True, linestyle='--', alpha=0.7)
        
        # Hide empty subplots
        for j in range(i + 1, len(axes)):
            axes[j].set_visible(False)
            
        plt.tight_layout()
        return fig, axes
    
    def plot_biological_vs_chronological(self, data: pd.DataFrame, biological_ages=None, figsize=(10, 8)):
        """
        Plot biological age against chronological age.
        
        Parameters:
        -----------
        data : pd.DataFrame
            Data containing biomarkers and chronological age
        biological_ages : np.ndarray, optional
            Pre-calculated biological ages. If None, they will be calculated.
        figsize : tuple, default=(10, 8)
            Size of the figure
        """
        if self.chronological_age_col not in data.columns:
            raise ValueError(f"Chronological age column '{self.chronological_age_col}' not found in data")
            
        if biological_ages is None:
            biological_ages = self.predict(data)
            
        chronological_ages = data[self.chronological_age_col].values
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot the points
        ax.scatter(chronological_ages, biological_ages, alpha=0.6)
        
        # Plot y=x line
        min_age = min(chronological_ages.min(), biological_ages.min())
        max_age = max(chronological_ages.max(), biological_ages.max())
        ax.plot([min_age, max_age], [min_age, max_age], 'r--', label='y=x')
        
        # Calculate and plot regression line
        slope, intercept, r_value, p_value, _ = stats.linregress(chronological_ages, biological_ages)
        x_range = np.array([min_age, max_age])
        y_range = intercept + slope * x_range
        ax.plot(x_range, y_range, 'g-', 
                label=f'Regression line (R² = {r_value**2:.3f})')
        
        # Calculate and show the correlation
        correlation = np.corrcoef(chronological_ages, biological_ages)[0, 1]
        
        # Add labels and title
        ax.set_xlabel('Chronological Age')
        ax.set_ylabel('Biological Age (KD method)')
        ax.set_title(f'Biological Age vs Chronological Age\nCorrelation: {correlation:.3f}')
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()
        
        plt.tight_layout()
        return fig, ax
    
    def get_summary(self) -> pd.DataFrame:
        """
        Get a summary of the model parameters.
        
        Returns:
        --------
        pd.DataFrame
            Summary of the model parameters for each biomarker
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before getting summary")
            
        summary_data = []
        for biomarker in self.biomarkers:
            params = self.params[biomarker]
            summary_data.append({
                'Biomarker': biomarker,
                'Slope (k_i)': params['k_i'],
                'Intercept (q_i)': params['q_i'],
                'Std Error (s_i)': params['s_i'],
                'R-squared': params['r2'],
                'Correlation': params['corr'],
                'p-value': params['p_value']
            })
            
        summary_df = pd.DataFrame(summary_data)
        return summary_df


def example():
    """Example usage of the KD method with simulated data."""
    # Generate simulated data
    np.random.seed(42)
    n_samples = 200
    
    # True parameters
    true_age = np.random.uniform(20, 80, n_samples)
    
    # Biomarkers with different relationships to age
    biomarker1 = 50 + 0.5 * true_age + np.random.normal(0, 5, n_samples)  # Increasing with age
    biomarker2 = 120 - 0.3 * true_age + np.random.normal(0, 8, n_samples)  # Decreasing with age
    biomarker3 = 30 + 0.8 * true_age + np.random.normal(0, 10, n_samples)  # Stronger increase with age
    biomarker4 = 70 + 0.1 * true_age + np.random.normal(0, 3, n_samples)  # Weak increase with age
    
    # Create a DataFrame
    data = pd.DataFrame({
        'age': true_age,
        'biomarker1': biomarker1,
        'biomarker2': biomarker2,
        'biomarker3': biomarker3,
        'biomarker4': biomarker4
    })
    
    # Split data into training and testing sets
    from sklearn.model_selection import train_test_split
    train_data, test_data = train_test_split(data, test_size=0.3, random_state=42)
    
    # Initialize and fit the KD model
    kd = KlemeraDoubal(chronological_age_col='age')
    kd.fit(train_data, 
           biomarkers=['biomarker1', 'biomarker2', 'biomarker3', 'biomarker4'],
           verbose=True)
    
    # Get model summary
    summary = kd.get_summary()
    print("\nModel Summary:")
    print(summary)
    
    # Calculate biological ages
    bio_ages = kd.predict(test_data)
    
    # Calculate biological ages including chronological age
    bio_ages_with_ca = kd.predict(test_data, include_chronological=True)
    
    # Plot results
    plt.figure(figsize=(10, 6))
    plt.scatter(test_data['age'], bio_ages, alpha=0.7, label='Bio Age (biomarkers only)')
    plt.scatter(test_data['age'], bio_ages_with_ca, alpha=0.7, label='Bio Age (with chronological)')
    plt.plot([20, 80], [20, 80], 'k--', label='y=x line')
    plt.xlabel('Chronological Age')
    plt.ylabel('Biological Age')
    plt.title('Comparison of Biological Age Calculations')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig('bio_age_comparison.png')
    
    # Plot biomarker relationships
    kd.plot_biomarker_relationships(train_data)
    plt.savefig('biomarker_relationships.png')
    
    # Plot biological vs chronological age
    kd.plot_biological_vs_chronological(test_data, bio_ages)
    plt.savefig('bio_vs_chrono_age.png')
    
    print("\nCalculation completed. Check the output files:")
    print("- bio_age_comparison.png")
    print("- biomarker_relationships.png")
    print("- bio_vs_chrono_age.png")
    
    return kd, train_data, test_data


if __name__ == "__main__":
    example() 