#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask web application for the Questionnaire-Based Biological Age Calculator.
This provides a user-friendly web interface for filling out the questionnaire
and visualizing biological age results.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import os
import json
import io
import base64
from datetime import datetime
from questionnaire_bioage import QuestionnaireAgeCalculator

app = Flask(__name__)
app.config['SECRET_KEY'] = 'biological-age-calculator-secret-key'

# Initialize the calculator
calculator = QuestionnaireAgeCalculator()

# Custom template filters
@app.template_filter('now')
def get_now(value, format_string='%Y'):
    """Get current date/time in specified format (default: year)"""
    return datetime.now().strftime(format_string)

@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')

@app.route('/questionnaire')
def questionnaire():
    """Render the questionnaire page."""
    questions = calculator.get_questions()
    categories = calculator.get_categories()
    
    # Group questions by category for better organization
    categorized_questions = {}
    for category_id, category_name in categories.items():
        categorized_questions[category_id] = {
            'name': category_name,
            'questions': []
        }
    
    for question in questions:
        category = question['category']
        if category in categorized_questions:
            categorized_questions[category]['questions'].append(question)
    
    return render_template('questionnaire.html', 
                          categorized_questions=categorized_questions,
                          categories=categories)

@app.route('/calculate', methods=['POST'])
def calculate():
    """Process form submission and calculate biological age."""
    # Get all form data
    form_data = request.form.to_dict()
    
    # Debug info
    print(f"Form data received: {form_data}")
    
    # Convert age to float
    if 'age' in form_data:
        try:
            form_data['age'] = float(form_data['age'])
        except ValueError:
            print("Error: Age must be a number")
            return jsonify({'error': 'Age must be a number'})
    else:
        print("Error: Age is required but was not provided")
        return jsonify({'error': 'Age is required'})
    
    # Calculate biological age
    try:
        print("Calculating biological age...")
        results = calculator.calculate_biological_age(form_data)
        print(f"Results: {results}")
        
        print("Generating recommendations...")
        recommendations = calculator.generate_recommendations(results)
        
        # Generate visualizations
        print("Creating visualization...")
        fig = calculator.plot_results(results)
        
        # Convert plot to base64 for embedding in HTML
        img_data = io.BytesIO()
        fig.savefig(img_data, format='png', bbox_inches='tight')
        plt.close(fig)
        img_data.seek(0)
        plot_base64 = base64.b64encode(img_data.getvalue()).decode('utf-8')
        
        # Store results in session for results page
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        result_data = {
            'results': results,
            'recommendations': recommendations,
            'plot_base64': plot_base64,
            'timestamp': timestamp
        }
        
        # Save results to a file (optional - for history feature)
        results_dir = 'results'
        os.makedirs(results_dir, exist_ok=True)
        print(f"Saving results to {results_dir}/result_{timestamp}.json")
        with open(f'{results_dir}/result_{timestamp}.json', 'w') as f:
            # We can't directly serialize the plot, so exclude it
            serializable_data = {
                'results': results,
                'recommendations': recommendations,
                'timestamp': timestamp
            }
            json.dump(serializable_data, f)
        
        # Get categories for the results page
        categories = calculator.get_categories()
        
        print("Rendering results page...")
        # Return the results page
        return render_template('results.html', 
                              results=results,
                              recommendations=recommendations,
                              plot_base64=plot_base64,
                              categories=categories)
        
    except Exception as e:
        print(f"Error calculating biological age: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)})

@app.route('/about')
def about():
    """Render the about page with information on the method."""
    return render_template('about.html')

@app.route('/comparison')
def comparison():
    """Render the comparison page showing different lifestyle scenarios."""
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
        "Caso Base": base_responses.copy(),
        "Sueño Deficiente": {**base_responses.copy(), 'sleep': '<5'},
        "Estilo de Vida Activo": {**base_responses.copy(), 'exercise': 'very_active', 'strength_training': 'very_often', 'sedentary': '4-6'},
        "Hábitos de Salud Deficientes": {**base_responses.copy(), 'smoking': 'current_light', 'alcohol': 'heavy', 'diet': 'poor', 'exercise': 'none'},
        "Estilo de Vida Óptimo": {**base_responses.copy(), 'sleep': '7-8', 'exercise': 'very_active', 'strength_training': 'very_often', 
                             'diet': 'excellent', 'fruits_veggies': '6+', 'stress': 'low', 'happiness': 'very_happy', 
                             'social_connections': 'excellent', 'mental_activity': 'daily'}
    }
    
    # Calculate biological age for each scenario
    scenario_results = {}
    for name, responses in scenarios.items():
        scenario_results[name] = calculator.calculate_biological_age(responses)
    
    # Create comparison visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    
    # Plot biological ages
    scenario_names = list(scenario_results.keys())
    bio_ages = [scenario_results[name]['biological_age'] for name in scenario_names]
    
    bars = ax1.bar(scenario_names, bio_ages, color=['#72B7B2', '#F15854', '#60BD68', '#F17CB0', '#B276B2'])
    ax1.set_title('Edad Biológica por Escenario', fontsize=14)
    ax1.set_ylabel('Edad Biológica (años)')
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
    
    # Add values on top of bars
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                 f'{height:.1f}',
                 ha='center', va='bottom')
    
    # Plot aging pace for each scenario
    aging_paces = [scenario_results[name]['aging_pace'] for name in scenario_names]
    colors = ['#72B7B2' if pace <= 0 else '#F15854' for pace in aging_paces]
    
    bars = ax2.bar(scenario_names, aging_paces, color=colors)
    ax2.set_title('Ritmo de Envejecimiento por Escenario', fontsize=14)
    ax2.set_ylabel('Ritmo de Envejecimiento (años)')
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
    
    plt.suptitle('Impacto de Elecciones de Estilo de Vida en la Edad Biológica', fontsize=16, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    # Convert to base64 for embedding in HTML
    img_data = io.BytesIO()
    fig.savefig(img_data, format='png', bbox_inches='tight')
    plt.close(fig)
    img_data.seek(0)
    comparison_plot = base64.b64encode(img_data.getvalue()).decode('utf-8')
    
    return render_template('comparison.html', 
                          scenarios=scenarios,
                          scenario_results=scenario_results,
                          comparison_plot=comparison_plot)

# Modificación para Vercel - exportar la aplicación Flask
app.debug = False

# Solo iniciar el servidor si se ejecuta directamente (no en Vercel)
if __name__ == '__main__':
    # Make sure templates and static folders exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/img', exist_ok=True)
    
    # Start the application
    app.run(debug=True, port=5000) 