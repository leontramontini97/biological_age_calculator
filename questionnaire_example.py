#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example script for using the questionnaire-based biological age calculator.
This file demonstrates how to use the QuestionnaireAgeCalculator with example data,
interactive mode, and custom visualization of results.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from questionnaire_bioage import QuestionnaireAgeCalculator

def run_example_case():
    """Run the calculator with a predefined example case."""
    print("=== Running Biological Age Calculator with Example Data ===\n")
    
    # Initialize the calculator
    calculator = QuestionnaireAgeCalculator()
    
    # Example responses for a 45-year-old male with mostly healthy habits
    responses = {
        'age': 45,
        'sex': 'male',
        'sleep': '7-8',
        'smoking': 'never',
        'alcohol': 'moderate',
        'exercise': 'moderate',
        'strength_training': 'sometimes',
        'diet': 'good',
        'fruits_veggies': '2-3',
        'bmi': 'normal',
        'chronic_conditions': '0',
        'medications': '0',
        'blood_pressure': 'normal',
        'stress': 'moderate',
        'happiness': 'happy',
        'social_connections': 'good',
        'education': 'bachelors',
        'mental_activity': 'several_weekly',
        'sedentary': '7-9',
        'longevity_family': 'moderate'
    }
    
    # Calculate biological age
    results = calculator.calculate_biological_age(responses)
    
    # Generate recommendations
    recommendations = calculator.generate_recommendations(results)
    
    # Display results
    print_results(results, recommendations)
    
    # Create and save visualizations
    fig = calculator.plot_results(results)
    plt.savefig('example_bioage_results.png')
    print("\nResults visualization saved as 'example_bioage_results.png'")
    plt.close(fig)
    
    return results

def print_results(results, recommendations):
    """Print formatted results and recommendations."""
    print("\n" + "="*50)
    print(f"BIOLOGICAL AGE ASSESSMENT RESULTS")
    print("="*50)
    
    print(f"\nChronological Age: {results['chronological_age']} years")
    print(f"Biological Age:    {results['biological_age']} years")
    print(f"Aging Pace:        {results['aging_pace']:+.1f} years")
    print(f"\nAssessment: {results['qualitative_rating']}")
    
    print("\n" + "-"*50)
    print("CATEGORY BREAKDOWN")
    print("-"*50)
    
    # Sort categories by impact (worst to best)
    sorted_scores = sorted(
        results['category_scores'].items(), 
        key=lambda x: x[1], 
        reverse=True
    )
    
    calculator = QuestionnaireAgeCalculator()
    for category_id, impact in sorted_scores:
        category_name = calculator.categories[category_id]
        impact_str = f"{impact:+.2f}"
        
        # Add visual indicators
        if impact > 1:
            indicator = "⚠️ Needs improvement"
        elif impact > 0:
            indicator = "⚠️ Slight concern"
        elif impact > -1:
            indicator = "✓ Adequate"
        else:
            indicator = "✓✓ Excellent"
            
        print(f"{category_name:25} {impact_str:>8}  {indicator}")
    
    print("\n" + "-"*50)
    print("TOP RECOMMENDATIONS")
    print("-"*50)
    
    for i, rec in enumerate(recommendations['recommendations'], 1):
        print(f"\n{i}. {rec['category']}:")
        for j, suggestion in enumerate(rec['suggestions'], 1):
            print(f"   {j}. {suggestion}")
    
    print("\n" + "-"*50)
    print("DISCLAIMER: This assessment is for informational purposes only and should not")
    print("be considered medical advice. Consult with healthcare professionals for")
    print("personalized recommendations about your health.")
    print("-"*50)

def run_interactive_mode():
    """Run the calculator in interactive mode, asking the user for responses."""
    print("=== Interactive Biological Age Calculator ===\n")
    print("Please answer the following questions to calculate your biological age.")
    print("This will provide an estimate based on your lifestyle and health factors.\n")
    
    calculator = QuestionnaireAgeCalculator()
    questions = calculator.get_questions()
    
    responses = {}
    
    for question in questions:
        print(f"\n{question['text']}")
        
        if question['type'] == 'number':
            while True:
                try:
                    value = float(input("Enter a number: "))
                    if value < question['min'] or value > question['max']:
                        print(f"Please enter a value between {question['min']} and {question['max']}.")
                        continue
                    responses[question['id']] = value
                    break
                except ValueError:
                    print("Please enter a valid number.")
        
        elif question['type'] == 'choice':
            # Display options
            for i, option in enumerate(question['options'], 1):
                print(f"  {i}. {option['text']}")
            
            # Get valid input
            while True:
                try:
                    choice = int(input("Enter the number of your choice: "))
                    if 1 <= choice <= len(question['options']):
                        responses[question['id']] = question['options'][choice-1]['value']
                        break
                    else:
                        print(f"Please enter a number between 1 and {len(question['options'])}.")
                except ValueError:
                    print("Please enter a valid number.")
    
    # Calculate and display results
    results = calculator.calculate_biological_age(responses)
    recommendations = calculator.generate_recommendations(results)
    print_results(results, recommendations)
    
    # Create and save visualizations
    fig = calculator.plot_results(results)
    plt.savefig('my_bioage_results.png')
    print("\nResults visualization saved as 'my_bioage_results.png'")
    plt.close(fig)
    
    return results

def compare_scenarios():
    """Compare biological age across different lifestyle scenarios."""
    calculator = QuestionnaireAgeCalculator()
    
    # Base case - 45-year-old with average lifestyle
    base_responses = {
        'age': 45,
        'sex': 'male',
        'sleep': '7-8',
        'smoking': 'never',
        'alcohol': 'moderate',
        'exercise': 'moderate',
        'strength_training': 'sometimes',
        'diet': 'good',
        'fruits_veggies': '2-3',
        'bmi': 'normal',
        'chronic_conditions': '0',
        'medications': '0',
        'blood_pressure': 'normal',
        'stress': 'moderate',
        'happiness': 'happy',
        'social_connections': 'good',
        'education': 'bachelors',
        'mental_activity': 'several_weekly',
        'sedentary': '7-9',
        'longevity_family': 'moderate'
    }
    
    # Scenarios to compare
    scenarios = {
        "Base Case": base_responses.copy(),
        "Poor Sleep": {**base_responses.copy(), 'sleep': '<5'},
        "Active Lifestyle": {**base_responses.copy(), 'exercise': 'very_active', 'strength_training': 'very_often', 'sedentary': '4-6'},
        "Poor Health Habits": {**base_responses.copy(), 'smoking': 'current_light', 'alcohol': 'heavy', 'diet': 'poor', 'exercise': 'none'},
        "Optimal Lifestyle": {**base_responses.copy(), 'sleep': '7-8', 'exercise': 'very_active', 'strength_training': 'very_often', 
                             'diet': 'excellent', 'fruits_veggies': '6+', 'stress': 'low', 'happiness': 'very_happy', 
                             'social_connections': 'excellent', 'mental_activity': 'daily'}
    }
    
    # Calculate biological age for each scenario
    results = {}
    for name, responses in scenarios.items():
        results[name] = calculator.calculate_biological_age(responses)
    
    # Create comparison visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
    
    # Plot biological ages
    scenario_names = list(results.keys())
    bio_ages = [results[name]['biological_age'] for name in scenario_names]
    
    bars = ax1.bar(scenario_names, bio_ages, color=['#72B7B2', '#F15854', '#60BD68', '#F17CB0', '#B276B2'])
    ax1.set_title('Biological Age by Scenario', fontsize=14)
    ax1.set_ylabel('Biological Age (years)')
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
    
    # Add values on top of bars
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                 f'{height:.1f}',
                 ha='center', va='bottom')
    
    # Plot aging pace for each scenario
    aging_paces = [results[name]['aging_pace'] for name in scenario_names]
    colors = ['#72B7B2' if pace <= 0 else '#F15854' for pace in aging_paces]
    
    bars = ax2.bar(scenario_names, aging_paces, color=colors)
    ax2.set_title('Aging Pace by Scenario', fontsize=14)
    ax2.set_ylabel('Aging Pace (years difference from chronological age)')
    ax2.grid(axis='y', linestyle='--', alpha=0.7)
    ax2.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
    
    # Add values on top of bars
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., 
                 height + 0.5 if height >= 0 else height - 1.5,
                 f'{height:+.1f}',
                 ha='center', va='bottom' if height >= 0 else 'top')
    
    plt.suptitle('Biological Age Comparison Across Different Lifestyle Scenarios', fontsize=16, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    plt.savefig('bioage_comparison.png')
    print("\nScenario comparison saved as 'bioage_comparison.png'")
    
    # Print summary table
    print("\n" + "="*80)
    print(f"{'Scenario':<20} {'Chronological Age':<20} {'Biological Age':<20} {'Aging Pace':<20}")
    print("="*80)
    
    for name in scenario_names:
        chrono = results[name]['chronological_age']
        bio = results[name]['biological_age']
        pace = results[name]['aging_pace']
        print(f"{name:<20} {chrono:<20.1f} {bio:<20.1f} {pace:+<20.1f}")
    
    print("="*80)
    print("\nThis comparison shows how different lifestyle choices can significantly impact biological age.")
    print("Even with the same chronological age, biological age can vary by several years based on health habits.")

def main():
    """Main function to run the example script."""
    print("Questionnaire-Based Biological Age Calculator Example")
    print("="*50)
    print("\nThis script demonstrates different ways to use the biological age calculator:")
    print("1. Run with example data")
    print("2. Run in interactive mode (answer questions yourself)")
    print("3. Compare different lifestyle scenarios")
    print("4. Exit")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (1-4): "))
            if choice == 1:
                run_example_case()
            elif choice == 2:
                run_interactive_mode()
            elif choice == 3:
                compare_scenarios()
            elif choice == 4:
                print("\nExiting program.")
                sys.exit(0)
            else:
                print("Please enter a number between 1 and 4.")
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\nExiting program.")
            sys.exit(0)
        
        input("\nPress Enter to return to the main menu...")
        print("\n" + "="*50)

if __name__ == "__main__":
    main() 