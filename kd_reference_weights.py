#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reference weights for the Klemera-Doubal method for calculating biological age.

This file contains published reference values from various studies that used
the Klemera-Doubal method to calculate biological age. These weights can be used
directly without having to fit your own model if your biomarkers match the ones
in the referenced studies.

Main sources:
1. Levine ME. "Modeling the rate of senescence: can estimated biological age predict 
   mortality more accurately than chronological age?" J Gerontol A Biol Sci Med Sci. 2013
2. Levine ME, et al. "An epigenetic biomarker of aging for lifespan and healthspan." 
   Aging (Albany NY). 2018
"""

import numpy as np
from typing import Dict, List, Tuple

# NHANES III reference weights from Levine's 2013 study
# These were used in the "KDM2" algorithm which performed best in mortality prediction
# 
# The biomarkers used in this study were:
# - C-reactive protein (mg/dL)
# - Glycated hemoglobin (%)
# - Serum albumin (g/dL)
# - Serum alkaline phosphatase (U/L)
# - Forced expiratory volume (mL)
# - Systolic blood pressure (mmHg)
# - Serum urea nitrogen (mg/dL)

NHANES_III_MALE_WEIGHTS = {
    # Biomarker: (k_i, q_i, s_i)
    # where k_i is the slope, q_i is the intercept, s_i is the residual standard error
    'c_reactive_protein': (0.0939, 0.1333, 0.9431),  # C-reactive protein (mg/dL)
    'glycated_hemoglobin': (0.0106, 5.2771, 0.5674),  # Glycated hemoglobin (%)
    'serum_albumin': (-0.0076, 4.3103, 0.3023),  # Serum albumin (g/dL)
    'alkaline_phosphatase': (0.4152, 65.3099, 19.8032),  # Serum alkaline phosphatase (U/L)
    'forced_expiratory_volume': (-41.7970, 4029.7070, 780.4862),  # Forced expiratory volume (mL)
    'systolic_blood_pressure': (0.5336, 101.7092, 14.4056),  # Systolic blood pressure (mmHg)
    'serum_urea_nitrogen': (0.0714, 12.1833, 3.9244),  # Serum urea nitrogen (mg/dL)
}

NHANES_III_FEMALE_WEIGHTS = {
    # Biomarker: (k_i, q_i, s_i)
    'c_reactive_protein': (0.0929, 0.2022, 0.9802),  # C-reactive protein (mg/dL)
    'glycated_hemoglobin': (0.0058, 5.2997, 0.5284),  # Glycated hemoglobin (%)
    'serum_albumin': (-0.0058, 4.2031, 0.2793),  # Serum albumin (g/dL)
    'alkaline_phosphatase': (0.3716, 65.1039, 19.4999),  # Serum alkaline phosphatase (U/L)
    'forced_expiratory_volume': (-25.0337, 2731.7228, 546.7556),  # Forced expiratory volume (mL)
    'systolic_blood_pressure': (0.6808, 97.3992, 17.1402),  # Systolic blood pressure (mmHg)
    'serum_urea_nitrogen': (0.0786, 10.9897, 3.7234),  # Serum urea nitrogen (mg/dL)
}

# Reference values for standard deviation of biological age
NHANES_III_S_BA = {
    'male': 8.91,
    'female': 7.21
}

# PhenoAge reference weights from Levine's 2018 study
# This is a modified Klemera-Doubal method that's been validated extensively
# and is called PhenoAge.
#
# The biomarkers used in this model are:
# - albumin (g/dL)
# - creatinine (mg/dL)
# - glucose (mg/dL)
# - log(C-reactive protein) (mg/L)
# - lymphocyte percent (%)
# - mean cell volume (fL)
# - red blood cell distribution width (%)
# - alkaline phosphatase (U/L)
# - white blood cell count (1000 cells/uL)
# - age (years)

PHENOAGE_WEIGHTS = {
    # Weights derived from Gompertz proportional hazards model
    'albumin': -0.0336,  # g/dL
    'creatinine': 0.0095,  # mg/dL
    'glucose': 0.1953,  # mg/dL
    'log_c_reactive_protein': 0.0954,  # log(mg/L)
    'lymphocyte_percent': -0.0120,  # %
    'mean_cell_volume': 0.0268,  # fL
    'red_cell_distribution_width': 0.3306,  # %
    'alkaline_phosphatase': 0.00188,  # U/L
    'white_blood_cell_count': 0.0554,  # 1000 cells/uL
    'chronological_age': 0.0804,  # years
    
    # Intercept from the model
    'intercept': -19.9067
}

def calculate_phenoage(
    albumin: float,  # g/dL
    creatinine: float,  # mg/dL
    glucose: float,  # mg/dL
    log_crp: float,  # log(mg/L)
    lymphocyte_percent: float,  # %
    mean_cell_volume: float,  # fL
    red_cell_distribution_width: float,  # %
    alkaline_phosphatase: float,  # U/L
    white_blood_cell_count: float,  # 1000 cells/uL
    chronological_age: float  # years
) -> float:
    """
    Calculate PhenoAge using the reference weights from Levine's 2018 study.
    
    This implements the PhenoAge algorithm which was derived using a modified 
    Klemera-Doubal approach by Morgan Levine et al.
    
    Parameters:
    -----------
    albumin: float
        Albumin level in g/dL
    creatinine: float
        Creatinine level in mg/dL
    glucose: float
        Glucose level in mg/dL
    log_crp: float
        Natural log of C-reactive protein in mg/L
    lymphocyte_percent: float
        Lymphocyte percent (%)
    mean_cell_volume: float
        Mean cell volume in fL
    red_cell_distribution_width: float
        Red cell distribution width (%)
    alkaline_phosphatase: float
        Alkaline phosphatase in U/L
    white_blood_cell_count: float
        White blood cell count in 1000 cells/uL
    chronological_age: float
        Chronological age in years
        
    Returns:
    --------
    float:
        Calculated PhenoAge in years
    """
    # Calculate linear predictor
    xb = (
        PHENOAGE_WEIGHTS['albumin'] * albumin +
        PHENOAGE_WEIGHTS['creatinine'] * creatinine +
        PHENOAGE_WEIGHTS['glucose'] * glucose +
        PHENOAGE_WEIGHTS['log_c_reactive_protein'] * log_crp +
        PHENOAGE_WEIGHTS['lymphocyte_percent'] * lymphocyte_percent +
        PHENOAGE_WEIGHTS['mean_cell_volume'] * mean_cell_volume +
        PHENOAGE_WEIGHTS['red_cell_distribution_width'] * red_cell_distribution_width +
        PHENOAGE_WEIGHTS['alkaline_phosphatase'] * alkaline_phosphatase +
        PHENOAGE_WEIGHTS['white_blood_cell_count'] * white_blood_cell_count +
        PHENOAGE_WEIGHTS['chronological_age'] * chronological_age +
        PHENOAGE_WEIGHTS['intercept']
    )
    
    # Convert to mortality risk
    mortality_risk = 1 - np.exp(-np.exp(xb))
    
    # Convert mortality risk to phenoage
    phenoage = 141.50225 + np.log(-0.00553 * np.log(1 - mortality_risk)) / 0.090165
    
    return phenoage

def calculate_bioage_from_reference(
    biomarker_values: Dict[str, float],
    sex: str = 'male',
    include_chronological_age: bool = False,
    chronological_age: float = None
) -> float:
    """
    Calculate biological age using the reference weights from NHANES III study.
    
    Parameters:
    -----------
    biomarker_values: Dict[str, float]
        Dictionary with biomarker names and their values
    sex: str
        'male' or 'female'
    include_chronological_age: bool
        Whether to include chronological age in the calculation
    chronological_age: float
        Chronological age in years (required if include_chronological_age is True)
        
    Returns:
    --------
    float:
        Calculated biological age in years
    """
    if sex.lower() not in ['male', 'female']:
        raise ValueError("Sex must be either 'male' or 'female'")
    
    if include_chronological_age and chronological_age is None:
        raise ValueError("Chronological age must be provided if include_chronological_age is True")
    
    # Select the appropriate weights
    if sex.lower() == 'male':
        weights = NHANES_III_MALE_WEIGHTS
        s_BA = NHANES_III_S_BA['male']
    else:
        weights = NHANES_III_FEMALE_WEIGHTS
        s_BA = NHANES_III_S_BA['female']
    
    # Calculate terms for the weighted average
    numerator_sum = 0
    denominator_sum = 0
    
    for biomarker, value in biomarker_values.items():
        if biomarker not in weights:
            raise ValueError(f"Biomarker '{biomarker}' not found in reference weights for {sex}")
        
        k_i, q_i, s_i = weights[biomarker]
        
        # Calculate the terms for the weighted average
        weight = (k_i**2) / (s_i**2)
        ba_estimate = (value - q_i) / k_i
        
        numerator_sum += weight * ba_estimate
        denominator_sum += weight
    
    # Include chronological age in calculation if requested
    if include_chronological_age:
        s_CA = s_BA  # Assuming s_CA = s_BA following the paper
        
        weight_ca = 1 / (s_CA**2)
        numerator_sum += weight_ca * chronological_age
        denominator_sum += weight_ca
    
    # Calculate the biological age
    biological_age = numerator_sum / denominator_sum
    
    return biological_age


# Example usage:
if __name__ == "__main__":
    # Example values for a hypothetical 50-year-old male
    example_biomarkers = {
        'c_reactive_protein': 0.5,  # mg/dL
        'glycated_hemoglobin': 5.7,  # %
        'serum_albumin': 4.0,  # g/dL
        'alkaline_phosphatase': 80,  # U/L
        'forced_expiratory_volume': 3000,  # mL
        'systolic_blood_pressure': 130,  # mmHg
        'serum_urea_nitrogen': 15  # mg/dL
    }
    
    # Calculate biological age
    bioage = calculate_bioage_from_reference(
        example_biomarkers, 
        sex='male',
        include_chronological_age=True,
        chronological_age=50
    )
    
    print(f"Calculated Biological Age: {bioage:.2f} years")
    
    # Example PhenoAge calculation
    phenoage = calculate_phenoage(
        albumin=4.0,  # g/dL
        creatinine=0.9,  # mg/dL
        glucose=90,  # mg/dL
        log_crp=np.log(1.5),  # log(mg/L)
        lymphocyte_percent=30,  # %
        mean_cell_volume=90,  # fL
        red_cell_distribution_width=13,  # %
        alkaline_phosphatase=80,  # U/L
        white_blood_cell_count=6.0,  # 1000 cells/uL
        chronological_age=50  # years
    )
    
    print(f"Calculated PhenoAge: {phenoage:.2f} years") 