#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Questionnaire-Based Biological Age Calculator

This module provides a questionnaire-based approach to estimating biological age
without requiring laboratory biomarker values. It's based on lifestyle, health, 
and behavioral factors that have been associated with longevity and aging in 
scientific literature.

While not as precise as biomarker-based methods like Klemera-Doubal, this approach
can provide a rough estimate of biological age and aging pace based on self-reported
information.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class QuestionnaireAgeCalculator:
    """
    A class to calculate biological age based on questionnaire responses.
    
    This calculator is based on lifestyle, behavioral, and health factors
    that have been associated with accelerated or decelerated aging in 
    scientific literature.
    """
    
    def __init__(self):
        """Initialize the calculator with question weights and categories."""
        # Categories of questions
        self.categories = {
            'personal': 'Características Personales',
            'physical': 'Actividad Física y Forma',
            'nutrition': 'Nutrición y Dieta',
            'medical': 'Salud Médica',
            'lifestyle': 'Hábitos de Vida',
            'psychology': 'Bienestar Psicológico',
            'social': 'Conexiones Sociales'
        }
        
        # Define questions, options, and their weights
        self.questions = [
            {
                'id': 'age',
                'text': '¿Cuál es tu edad cronológica?',
                'type': 'number',
                'min': 18,
                'max': 120,
                'category': 'personal',
                'impact': 0  # No impact on biological age calculation, just reference
            },
            {
                'id': 'sex',
                'text': '¿Cuál es tu sexo biológico?',
                'type': 'choice',
                'options': [
                    {'text': 'Masculino', 'value': 'male', 'impact': 0},  # Reference
                    {'text': 'Femenino', 'value': 'female', 'impact': -2}  # Women tend to live longer on average
                ],
                'category': 'personal'
            },
            {
                'id': 'sleep',
                'text': '¿Cuántas horas de sueño obtienes normalmente por noche?',
                'type': 'choice',
                'options': [
                    {'text': 'Menos de 5 horas', 'value': '<5', 'impact': 4},
                    {'text': '5-6 horas', 'value': '5-6', 'impact': 2},
                    {'text': '7-8 horas', 'value': '7-8', 'impact': -1},
                    {'text': 'Más de 8 horas', 'value': '>8', 'impact': 1}
                ],
                'category': 'lifestyle'
            },
            {
                'id': 'smoking',
                'text': '¿Fumas productos de tabaco?',
                'type': 'choice',
                'options': [
                    {'text': 'Nunca he fumado', 'value': 'never', 'impact': -1},
                    {'text': 'Ex-fumador (dejé hace más de 10 años)', 'value': 'former_10plus', 'impact': 0},
                    {'text': 'Ex-fumador (dejé hace 5-10 años)', 'value': 'former_5_10', 'impact': 1},
                    {'text': 'Ex-fumador (dejé hace 1-5 años)', 'value': 'former_1_5', 'impact': 2},
                    {'text': 'Ex-fumador (dejé hace menos de 1 año)', 'value': 'former_recent', 'impact': 3},
                    {'text': 'Fumador actual (menos de 10 cigarrillos/día)', 'value': 'current_light', 'impact': 4},
                    {'text': 'Fumador actual (10 o más cigarrillos/día)', 'value': 'current_heavy', 'impact': 6}
                ],
                'category': 'lifestyle'
            },
            {
                'id': 'alcohol',
                'text': '¿Cuánto alcohol consumes habitualmente?',
                'type': 'choice',
                'options': [
                    {'text': 'Nada', 'value': 'none', 'impact': 0},
                    {'text': 'Ligero (1-2 bebidas/semana)', 'value': 'light', 'impact': -0.5},
                    {'text': 'Moderado (3-7 bebidas/semana)', 'value': 'moderate', 'impact': 0},
                    {'text': 'Alto (8-14 bebidas/semana)', 'value': 'heavy', 'impact': 2},
                    {'text': 'Muy alto (15+ bebidas/semana)', 'value': 'very_heavy', 'impact': 4}
                ],
                'category': 'lifestyle'
            },
            {
                'id': 'exercise',
                'text': '¿Cuánta actividad física moderada a vigorosa realizas por semana?',
                'type': 'choice',
                'options': [
                    {'text': 'Nada o muy poco (menos de 30 minutos)', 'value': 'none', 'impact': 4},
                    {'text': 'Ligera (30-90 minutos)', 'value': 'light', 'impact': 2},
                    {'text': 'Moderada (90-150 minutos)', 'value': 'moderate', 'impact': 0},
                    {'text': 'Activa (150-300 minutos)', 'value': 'active', 'impact': -1},
                    {'text': 'Muy activa (300+ minutos)', 'value': 'very_active', 'impact': -2}
                ],
                'category': 'physical'
            },
            {
                'id': 'strength_training',
                'text': '¿Con qué frecuencia realizas ejercicios de fuerza?',
                'type': 'choice',
                'options': [
                    {'text': 'Nunca', 'value': 'never', 'impact': 2},
                    {'text': 'Raramente (algunas veces al mes)', 'value': 'rarely', 'impact': 1},
                    {'text': 'A veces (una vez por semana)', 'value': 'sometimes', 'impact': 0},
                    {'text': 'A menudo (2-3 veces por semana)', 'value': 'often', 'impact': -1},
                    {'text': 'Muy a menudo (4+ veces por semana)', 'value': 'very_often', 'impact': -2}
                ],
                'category': 'physical'
            },
            {
                'id': 'diet',
                'text': '¿Cómo describirías tu dieta?',
                'type': 'choice',
                'options': [
                    {'text': 'Pobre (alta en alimentos procesados, azúcar y grasas no saludables)', 'value': 'poor', 'impact': 3},
                    {'text': 'Regular (mezcla de alimentos saludables y no saludables)', 'value': 'fair', 'impact': 1},
                    {'text': 'Buena (principalmente alimentos integrales con algunos procesados)', 'value': 'good', 'impact': 0},
                    {'text': 'Excelente (alimentos integrales, enfocada en plantas, mínimos procesados)', 'value': 'excellent', 'impact': -2}
                ],
                'category': 'nutrition'
            },
            {
                'id': 'fruits_veggies',
                'text': '¿Cuántas porciones de frutas y verduras comes diariamente?',
                'type': 'choice',
                'options': [
                    {'text': '0-1 porciones', 'value': '0-1', 'impact': 2},
                    {'text': '2-3 porciones', 'value': '2-3', 'impact': 1},
                    {'text': '4-5 porciones', 'value': '4-5', 'impact': -1},
                    {'text': '6+ porciones', 'value': '6+', 'impact': -2}
                ],
                'category': 'nutrition'
            },
            {
                'id': 'bmi',
                'text': '¿Cuál es tu rango de IMC?',
                'type': 'choice',
                'options': [
                    {'text': 'Bajo peso (IMC menor a 18.5)', 'value': 'underweight', 'impact': 1},
                    {'text': 'Peso normal (IMC 18.5-24.9)', 'value': 'normal', 'impact': -1},
                    {'text': 'Sobrepeso (IMC 25-29.9)', 'value': 'overweight', 'impact': 1},
                    {'text': 'Obesidad Clase I (IMC 30-34.9)', 'value': 'obese_1', 'impact': 2},
                    {'text': 'Obesidad Clase II (IMC 35-39.9)', 'value': 'obese_2', 'impact': 3},
                    {'text': 'Obesidad Clase III (IMC 40 o mayor)', 'value': 'obese_3', 'impact': 4}
                ],
                'category': 'physical'
            },
            {
                'id': 'chronic_conditions',
                'text': '¿Cuántas condiciones crónicas de salud tienes? (ej., diabetes, hipertensión, enfermedad cardíaca)',
                'type': 'choice',
                'options': [
                    {'text': 'Ninguna', 'value': '0', 'impact': -1},
                    {'text': '1 condición', 'value': '1', 'impact': 1},
                    {'text': '2 condiciones', 'value': '2', 'impact': 2},
                    {'text': '3 condiciones', 'value': '3', 'impact': 3},
                    {'text': '4+ condiciones', 'value': '4+', 'impact': 5}
                ],
                'category': 'medical'
            },
            {
                'id': 'medications',
                'text': '¿Cuántos medicamentos con receta tomas regularmente?',
                'type': 'choice',
                'options': [
                    {'text': 'Ninguno', 'value': '0', 'impact': -1},
                    {'text': '1 medicamento', 'value': '1', 'impact': 0},
                    {'text': '2-3 medicamentos', 'value': '2-3', 'impact': 1},
                    {'text': '4-5 medicamentos', 'value': '4-5', 'impact': 2},
                    {'text': '6+ medicamentos', 'value': '6+', 'impact': 3}
                ],
                'category': 'medical'
            },
            {
                'id': 'blood_pressure',
                'text': '¿Cuál es el estado de tu presión arterial?',
                'type': 'choice',
                'options': [
                    {'text': 'Normal (sistólica <120 y diastólica <80)', 'value': 'normal', 'impact': -1},
                    {'text': 'Elevada (sistólica 120-129 y diastólica <80)', 'value': 'elevated', 'impact': 0},
                    {'text': 'Hipertensión Etapa 1 (sistólica 130-139 o diastólica 80-89)', 'value': 'stage1', 'impact': 1},
                    {'text': 'Hipertensión Etapa 2 (sistólica 140+ o diastólica 90+)', 'value': 'stage2', 'impact': 2},
                    {'text': 'No lo sé', 'value': 'unknown', 'impact': 0.5}
                ],
                'category': 'medical'
            },
            {
                'id': 'stress',
                'text': '¿Cómo calificarías tu nivel de estrés habitual?',
                'type': 'choice',
                'options': [
                    {'text': 'Muy bajo', 'value': 'very_low', 'impact': -2},
                    {'text': 'Bajo', 'value': 'low', 'impact': -1},
                    {'text': 'Moderado', 'value': 'moderate', 'impact': 0},
                    {'text': 'Alto', 'value': 'high', 'impact': 2},
                    {'text': 'Muy alto', 'value': 'very_high', 'impact': 4}
                ],
                'category': 'psychology'
            },
            {
                'id': 'happiness',
                'text': '¿Cómo calificarías tu felicidad general o satisfacción con la vida?',
                'type': 'choice',
                'options': [
                    {'text': 'Muy infeliz', 'value': 'very_unhappy', 'impact': 3},
                    {'text': 'Infeliz', 'value': 'unhappy', 'impact': 2},
                    {'text': 'Neutral', 'value': 'neutral', 'impact': 0},
                    {'text': 'Feliz', 'value': 'happy', 'impact': -1},
                    {'text': 'Muy feliz', 'value': 'very_happy', 'impact': -2}
                ],
                'category': 'psychology'
            },
            {
                'id': 'social_connections',
                'text': '¿Cómo calificarías tus conexiones sociales y red de apoyo?',
                'type': 'choice',
                'options': [
                    {'text': 'Muy pobre (aislado, pocas o ninguna relación cercana)', 'value': 'very_poor', 'impact': 3},
                    {'text': 'Pobre (interacciones sociales limitadas)', 'value': 'poor', 'impact': 2},
                    {'text': 'Promedio (algunas relaciones cercanas)', 'value': 'average', 'impact': 0},
                    {'text': 'Buena (múltiples relaciones cercanas, interacción social regular)', 'value': 'good', 'impact': -1},
                    {'text': 'Excelente (red de apoyo fuerte, muchas relaciones cercanas)', 'value': 'excellent', 'impact': -2}
                ],
                'category': 'social'
            },
            {
                'id': 'education',
                'text': '¿Cuál es tu nivel más alto de educación?',
                'type': 'choice',
                'options': [
                    {'text': 'Menos que bachillerato', 'value': 'less_than_high_school', 'impact': 1},
                    {'text': 'Graduado de bachillerato', 'value': 'high_school', 'impact': 0.5},
                    {'text': 'Algunos estudios universitarios o grado asociado', 'value': 'some_college', 'impact': 0},
                    {'text': 'Licenciatura', 'value': 'bachelors', 'impact': -0.5},
                    {'text': 'Maestría o doctorado', 'value': 'graduate', 'impact': -1}
                ],
                'category': 'personal'
            },
            {
                'id': 'mental_activity',
                'text': '¿Con qué frecuencia participas en actividades mentalmente estimulantes (lectura, puzzles, aprender nuevas habilidades)?',
                'type': 'choice',
                'options': [
                    {'text': 'Raramente o nunca', 'value': 'rarely', 'impact': 2},
                    {'text': 'Ocasionalmente (algunas veces al mes)', 'value': 'occasionally', 'impact': 1},
                    {'text': 'Semanalmente', 'value': 'weekly', 'impact': 0},
                    {'text': 'Varias veces a la semana', 'value': 'several_weekly', 'impact': -1},
                    {'text': 'Diariamente', 'value': 'daily', 'impact': -2}
                ],
                'category': 'lifestyle'
            },
            {
                'id': 'sedentary',
                'text': '¿Cuántas horas al día pasas normalmente sentado?',
                'type': 'choice',
                'options': [
                    {'text': 'Menos de 4 horas', 'value': '<4', 'impact': -2},
                    {'text': '4-6 horas', 'value': '4-6', 'impact': -1},
                    {'text': '7-9 horas', 'value': '7-9', 'impact': 0},
                    {'text': '10-12 horas', 'value': '10-12', 'impact': 1},
                    {'text': 'Más de 12 horas', 'value': '>12', 'impact': 2}
                ],
                'category': 'physical'
            },
            {
                'id': 'longevity_family',
                'text': '¿Tienes antecedentes familiares de longevidad (múltiples parientes que viven más allá de los 85 años)?',
                'type': 'choice',
                'options': [
                    {'text': 'Sí, muchos parientes vivieron/viven más de 85 años', 'value': 'strong', 'impact': -2},
                    {'text': 'Sí, algunos parientes vivieron/viven más de 85 años', 'value': 'moderate', 'impact': -1},
                    {'text': 'No hay un patrón particular de longevidad', 'value': 'average', 'impact': 0},
                    {'text': 'No, la mayoría de mis parientes fallecieron antes de los 75 años', 'value': 'below_average', 'impact': 1},
                    {'text': 'No lo sé', 'value': 'unknown', 'impact': 0}
                ],
                'category': 'personal'
            }
        ]
    
    def get_questions(self):
        """Return the list of questions for the questionnaire."""
        return self.questions
    
    def get_categories(self):
        """Return the categories of questions."""
        return self.categories
    
    def calculate_biological_age(self, responses):
        """
        Calculate biological age based on questionnaire responses.
        
        Parameters:
        -----------
        responses : dict
            Dictionary with question IDs as keys and selected option values as values
            
        Returns:
        --------
        dict
            Dictionary containing biological age estimate and category breakdowns
        """
        if 'age' not in responses:
            raise ValueError("Chronological age is required")
        
        chronological_age = float(responses['age'])
        if chronological_age < 18:
            raise ValueError("This calculator is designed for adults 18 and older")
        
        # Calculate the total impact from all responses
        total_impact = 0
        category_impacts = {category: 0 for category in self.categories}
        category_counts = {category: 0 for category in self.categories}
        
        for question in self.questions:
            question_id = question['id']
            if question_id == 'age':
                continue  # Skip the age question in impact calculation
                
            if question_id not in responses:
                continue  # Skip questions without responses
                
            response_value = responses[question_id]
            impact = 0
            
            # Find the selected option and its impact
            if question['type'] == 'choice':
                for option in question['options']:
                    if option['value'] == response_value:
                        impact = option['impact']
                        break
            
            # Add to total and category impacts
            total_impact += impact
            category = question['category']
            category_impacts[category] += impact
            category_counts[category] += 1
        
        # Calculate the average impact per answered question
        answered_questions = sum(category_counts.values())
        if answered_questions == 0:
            return {"error": "No questions were answered"}
        
        # Calculate normalized category scores (convert to percentage of contribution)
        category_scores = {}
        for category in self.categories:
            if category_counts[category] > 0:
                avg_impact = category_impacts[category] / category_counts[category]
                category_scores[category] = avg_impact
            else:
                category_scores[category] = 0
        
        # Calculate biological age
        # We use a formula that adjusts chronological age based on the total impact:
        # - Positive impact adds to chronological age (accelerated aging)
        # - Negative impact subtracts from chronological age (decelerated aging)
        scaling_factor = 0.8  # Controls how much the impacts affect the biological age
        biological_age = chronological_age + (total_impact * scaling_factor)
        
        # Cap biological age to reasonable limits
        biological_age = max(18, min(120, biological_age))
        
        # Calculate aging pace (biological age vs chronological age)
        aging_pace = biological_age - chronological_age
        
        # Determine qualitative rating based on aging pace
        if aging_pace <= -8:
            qualitative_rating = "Significativamente más joven que la edad cronológica"
        elif aging_pace <= -4:
            qualitative_rating = "Moderadamente más joven que la edad cronológica"
        elif aging_pace <= -1:
            qualitative_rating = "Ligeramente más joven que la edad cronológica"
        elif aging_pace < 1:
            qualitative_rating = "Aproximadamente igual a la edad cronológica"
        elif aging_pace < 4:
            qualitative_rating = "Ligeramente mayor que la edad cronológica"
        elif aging_pace < 8:
            qualitative_rating = "Moderadamente mayor que la edad cronológica"
        else:
            qualitative_rating = "Significativamente mayor que la edad cronológica"
        
        return {
            "chronological_age": chronological_age,
            "biological_age": round(biological_age, 1),
            "aging_pace": round(aging_pace, 1),
            "qualitative_rating": qualitative_rating,
            "category_scores": category_scores,
            "total_impact": total_impact
        }
    
    def generate_recommendations(self, results):
        """
        Generate personalized recommendations based on questionnaire results.
        
        Parameters:
        -----------
        results : dict
            Results from calculate_biological_age method
            
        Returns:
        --------
        dict
            Dictionary containing personalized recommendations
        """
        category_scores = results['category_scores']
        recommendations = []
        
        # Sort categories by impact (highest positive impact first)
        sorted_categories = sorted(
            category_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Generate recommendations for the top 3 categories with positive impact
        top_categories = [cat for cat, score in sorted_categories if score > 0][:3]
        
        for category in top_categories:
            if category == 'physical':
                recommendations.append({
                    "category": self.categories[category],
                    "suggestions": [
                        "Intenta realizar al menos 150 minutos de actividad aeróbica de intensidad moderada por semana",
                        "Incorpora ejercicios de fortalecimiento muscular al menos dos veces por semana",
                        "Reduce el tiempo sedentario tomando descansos para ponerte de pie o caminar cada hora",
                        "Considera actividades que mejoren el equilibrio y la flexibilidad, como yoga o tai chi",
                        "Comienza poco a poco si actualmente eres inactivo - incluso 10 minutos de actividad son beneficiosos"
                    ]
                })
            elif category == 'nutrition':
                recommendations.append({
                    "category": self.categories[category],
                    "suggestions": [
                        "Aumenta el consumo de frutas y verduras a al menos 5 porciones diarias",
                        "Elige granos integrales en lugar de granos refinados",
                        "Limita los alimentos procesados, azúcares añadidos y grasas poco saludables",
                        "Mantente hidratado bebiendo suficiente agua a lo largo del día",
                        "Considera un patrón de dieta mediterránea o DASH, que se han asociado con mayor longevidad"
                    ]
                })
            elif category == 'lifestyle':
                recommendations.append({
                    "category": self.categories[category],
                    "suggestions": [
                        "Prioriza el sueño buscando 7-8 horas de sueño de calidad cada noche",
                        "Si fumas, busca ayuda para dejarlo - los beneficios comienzan en cuestión de horas",
                        "Limita el consumo de alcohol a niveles moderados o menos",
                        "Participa en actividades mentalmente estimulantes a diario",
                        "Establece una rutina regular para dormir, comer y realizar actividad física"
                    ]
                })
            elif category == 'psychology':
                recommendations.append({
                    "category": self.categories[category],
                    "suggestions": [
                        "Practica técnicas de manejo del estrés como meditación, respiración profunda o mindfulness",
                        "Busca ayuda profesional si experimentas estado de ánimo bajo o ansiedad persistente",
                        "Dedica tiempo a actividades que te brinden alegría y satisfacción",
                        "Practica la gratitud anotando regularmente cosas que aprecias",
                        "Establece metas realistas y celebra los logros, por pequeños que sean"
                    ]
                })
            elif category == 'medical':
                recommendations.append({
                    "category": self.categories[category],
                    "suggestions": [
                        "Programa chequeos regulares con profesionales de la salud",
                        "Sigue los planes de tratamiento para cualquier condición de salud existente",
                        "Monitorea tu presión arterial regularmente",
                        "Mantente al día con las evaluaciones de salud recomendadas",
                        "Consulta con tu médico formas de optimizar tu régimen de medicamentos si corresponde"
                    ]
                })
            elif category == 'social':
                recommendations.append({
                    "category": self.categories[category],
                    "suggestions": [
                        "Fortalece las relaciones existentes a través del contacto regular",
                        "Únete a clubes, clases u oportunidades de voluntariado para conocer gente nueva",
                        "Considera herramientas digitales para mantenerte conectado con amigos y familiares distantes",
                        "Equilibra la soledad con la interacción social según tus necesidades personales",
                        "Busca comunidades de apoyo alineadas con tus intereses o valores"
                    ]
                })
        
        # If there aren't any categories with positive impact, provide general recommendations
        if not recommendations:
            recommendations.append({
                "category": "Bienestar General",
                "suggestions": [
                    "Continúa con tus hábitos saludables mientras buscas nuevas formas de optimizar tu bienestar",
                    "Comparte tu conocimiento y hábitos con otros que podrían beneficiarse",
                    "Mantente informado sobre los avances en la ciencia de la longevidad",
                    "Considera reevaluar periódicamente tu edad biológica para rastrear cambios a lo largo del tiempo",
                    "Concéntrate en mantener el equilibrio que has logrado en diferentes dominios de la salud"
                ]
            })
        
        return {
            "recommendations": recommendations,
            "general_note": "Estas recomendaciones se basan en tus respuestas al cuestionario y deben considerarse en consulta con profesionales de la salud. No pretenden reemplazar el consejo médico profesional."
        }
    
    def plot_results(self, results):
        """
        Create visualizations of the biological age calculation results.
        
        Parameters:
        -----------
        results : dict
            Results from calculate_biological_age method
            
        Returns:
        --------
        matplotlib.figure.Figure
            Figure containing the visualizations
        """
        fig = plt.figure(figsize=(15, 10))
        
        # 1. Age comparison plot
        ax1 = plt.subplot2grid((2, 2), (0, 0))
        ages = [results['chronological_age'], results['biological_age']]
        bars = ax1.bar(['Edad Cronológica', 'Edad Biológica'], ages, color=['#72B7B2', '#F15854'])
        ax1.set_title('Comparación de Edad', fontsize=14)
        ax1.set_ylabel('Edad (años)')
        ax1.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Add values on top of bars
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                     f'{height:.1f}',
                     ha='center', va='bottom')
        
        # 2. Category impact plot
        ax2 = plt.subplot2grid((2, 2), (0, 1))
        categories = list(self.categories.values())
        impacts = [results['category_scores'].get(cat_id, 0) for cat_id in self.categories.keys()]
        
        # Color bars based on impact (negative=good, positive=bad)
        colors = ['#72B7B2' if impact <= 0 else '#F15854' for impact in impacts]
        
        y_pos = np.arange(len(categories))
        ax2.barh(y_pos, impacts, color=colors)
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(categories)
        ax2.set_xlabel('Puntuación de Impacto (negativo es mejor)')
        ax2.set_title('Impactos por Categoría', fontsize=14)
        ax2.grid(axis='x', linestyle='--', alpha=0.7)
        ax2.axvline(x=0, color='k', linestyle='-', alpha=0.3)
        
        # 3. Aging pace interpretation
        ax3 = plt.subplot2grid((2, 2), (1, 0), colspan=2)
        ax3.axis('off')
        pace = results['aging_pace']
        
        # Create a horizontal gauge chart
        gauge_min = -15
        gauge_max = 15
        gauge_width = gauge_max - gauge_min
        
        # Background gauge (gray)
        ax3.barh(0, gauge_width, left=gauge_min, height=0.5, color='#EEEEEE')
        
        # Colored sections
        sections = [
            (gauge_min, -8, '#009900'),  # Dark green: Significantly younger
            (-8, -4, '#66CC00'),         # Light green: Moderately younger
            (-4, -1, '#99FF66'),         # Very light green: Slightly younger
            (-1, 1, '#FFFF66'),          # Yellow: Approximately equal
            (1, 4, '#FFCC66'),           # Light orange: Slightly older
            (4, 8, '#FF9933'),           # Orange: Moderately older
            (8, gauge_max, '#FF5050')    # Red: Significantly older
        ]
        
        for start, end, color in sections:
            width = end - start
            ax3.barh(0, width, left=start, height=0.5, color=color)
        
        # Pace marker (black triangle)
        marker_y = [0, 0.5, 0]
        marker_x = [pace, pace+0.8, pace-0.8]
        ax3.fill(marker_x, marker_y, 'black')
        
        # Add text annotations for the scale
        ax3.text(gauge_min, -0.5, 'Significativamente Más Joven', ha='left', va='top', fontsize=10)
        ax3.text(0, -0.5, 'Igual', ha='center', va='top', fontsize=10)
        ax3.text(gauge_max, -0.5, 'Significativamente Mayor', ha='right', va='top', fontsize=10)
        
        # Add value and interpretation
        ax3.text(0, 1.2, f'Ritmo de Envejecimiento: {pace:+.1f} años', ha='center', va='bottom', fontsize=14, fontweight='bold')
        ax3.text(0, 0.8, results['qualitative_rating'], ha='center', va='bottom', fontsize=12)
        
        # Set gauge limits
        ax3.set_xlim(gauge_min - 2, gauge_max + 2)
        ax3.set_ylim(-1, 2)
        
        # Add overall title
        plt.suptitle('Resultados de la Evaluación de Edad Biológica', fontsize=16, fontweight='bold')
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        return fig

def main():
    """
    Example usage of the QuestionnaireAgeCalculator.
    """
    calculator = QuestionnaireAgeCalculator()
    
    # Example responses
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
    
    # Print results
    print(f"Chronological Age: {results['chronological_age']}")
    print(f"Biological Age: {results['biological_age']}")
    print(f"Aging Pace: {results['aging_pace']} years")
    print(f"Assessment: {results['qualitative_rating']}")
    print("\nCategory Impacts:")
    for category_id, impact in results['category_scores'].items():
        category_name = calculator.categories[category_id]
        print(f"  {category_name}: {impact:.2f}")
    
    # Generate and print recommendations
    recommendations = calculator.generate_recommendations(results)
    print("\nRecommendations:")
    for rec in recommendations['recommendations']:
        print(f"\n{rec['category']}:")
        for i, suggestion in enumerate(rec['suggestions'], 1):
            print(f"  {i}. {suggestion}")
    
    # Create and save visualizations
    fig = calculator.plot_results(results)
    plt.savefig('biological_age_results.png')
    print("\nResults visualization saved as 'biological_age_results.png'")
    
    plt.close(fig)

if __name__ == "__main__":
    main() 