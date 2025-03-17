/**
 * Main JavaScript for Biological Age Calculator Web App
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize tooltip
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Questionnaire form validation and progress tracking
    const questionnaireForm = document.getElementById('questionnaire-form');
    if (questionnaireForm) {
        const progressBar = document.getElementById('questionnaire-progress');
        const totalQuestions = document.querySelectorAll('.question-card').length;
        const submitButton = document.getElementById('submit-questionnaire');
        
        // Function to update progress bar
        function updateProgress() {
            const answeredQuestions = getAnsweredQuestionsCount();
            const progressPercentage = Math.round((answeredQuestions / totalQuestions) * 100);
            
            progressBar.style.width = progressPercentage + '%';
            progressBar.setAttribute('aria-valuenow', progressPercentage);
            progressBar.textContent = progressPercentage + '%';
            
            // Enable/disable submit button based on completion
            if (answeredQuestions === totalQuestions) {
                submitButton.disabled = false;
                submitButton.classList.remove('btn-secondary');
                submitButton.classList.add('btn-primary');
            } else {
                submitButton.disabled = true;
                submitButton.classList.remove('btn-primary');
                submitButton.classList.add('btn-secondary');
            }
        }
        
        // Function to count answered questions
        function getAnsweredQuestionsCount() {
            let count = 0;
            const questionCards = document.querySelectorAll('.question-card');
            
            questionCards.forEach(card => {
                const questionId = card.getAttribute('data-question-id');
                const inputType = card.getAttribute('data-input-type');
                
                if (inputType === 'number') {
                    const input = card.querySelector('input[name="' + questionId + '"]');
                    if (input && input.value) {
                        count++;
                    }
                } else if (inputType === 'choice') {
                    const checkedInput = card.querySelector('input[name="' + questionId + '"]:checked');
                    if (checkedInput) {
                        count++;
                    }
                }
            });
            
            console.log(`Preguntas respondidas: ${count} de ${totalQuestions}`);
            return count;
        }
        
        // Add change event listeners to all inputs
        const allInputs = questionnaireForm.querySelectorAll('input');
        allInputs.forEach(input => {
            input.addEventListener('change', updateProgress);
        });
        
        // Initialize progress on page load
        updateProgress();
        
        // Smooth scroll to next question after answering
        const radioInputs = questionnaireForm.querySelectorAll('input[type="radio"]');
        radioInputs.forEach(radio => {
            radio.addEventListener('change', function() {
                const currentCard = this.closest('.question-card');
                const nextCard = currentCard.nextElementSibling;
                
                if (nextCard && nextCard.classList.contains('question-card')) {
                    setTimeout(() => {
                        nextCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }, 300);
                }
            });
        });
        
        // Form submission handling
        questionnaireForm.addEventListener('submit', function(e) {
            console.log('Iniciando envío del formulario');
            
            // Check if all questions are answered
            const answeredQuestions = getAnsweredQuestionsCount();
            if (answeredQuestions < totalQuestions) {
                e.preventDefault();
                alert(`Por favor responde todas las preguntas. Has respondido ${answeredQuestions} de ${totalQuestions} preguntas.`);
                return;
            }
            
            console.log('Todas las preguntas respondidas, procediendo con el envío');
            
            // Show loading indicator
            const loadingOverlay = document.getElementById('loading-overlay');
            if (loadingOverlay) {
                loadingOverlay.classList.remove('d-none');
                console.log('Indicador de carga mostrado');
            } else {
                console.log('Elemento de indicador de carga no encontrado');
            }
        });
    }
    
    // Results page animations
    const resultsContainer = document.getElementById('results-container');
    if (resultsContainer) {
        // Add animation class to elements sequentially
        const animatedElements = document.querySelectorAll('.animate-on-load');
        animatedElements.forEach((element, index) => {
            setTimeout(() => {
                element.classList.add('animate-fade-in');
            }, 100 * index);
        });
    }
    
    // Category breakdown visualization
    const categoryBars = document.querySelectorAll('.category-bar');
    if (categoryBars.length > 0) {
        categoryBars.forEach(bar => {
            const value = parseFloat(bar.getAttribute('data-value'));
            const maxValue = 5; // Maximum possible impact (positive or negative)
            
            // Calculate width based on value
            // Center point (0 impact) should be at 50%
            const percentage = 50 + (value / maxValue * 50);
            bar.style.width = percentage + '%';
            
            // Set color based on value
            if (value <= -2) {
                bar.classList.add('bg-success');
            } else if (value < 0) {
                bar.classList.add('bg-info');
            } else if (value < 2) {
                bar.classList.add('bg-warning');
            } else {
                bar.classList.add('bg-danger');
            }
        });
    }
    
    // Print results functionality
    const printResultsBtn = document.getElementById('print-results');
    if (printResultsBtn) {
        printResultsBtn.addEventListener('click', function() {
            window.print();
        });
    }
    
    // BMI Calculator helper (if included on the form)
    const heightInput = document.getElementById('height-input');
    const weightInput = document.getElementById('weight-input');
    const bmiResult = document.getElementById('bmi-result');
    
    if (heightInput && weightInput && bmiResult) {
        function calculateBMI() {
            const height = parseFloat(heightInput.value) / 100; // cm to meters
            const weight = parseFloat(weightInput.value);
            
            if (height > 0 && weight > 0) {
                const bmi = weight / (height * height);
                bmiResult.textContent = bmi.toFixed(1);
                
                // Find the radio button that corresponds to the calculated BMI and select it
                let bmiValue = '';
                if (bmi < 18.5) {
                    bmiValue = 'underweight';
                } else if (bmi < 25) {
                    bmiValue = 'normal';
                } else if (bmi < 30) {
                    bmiValue = 'overweight';
                } else if (bmi < 35) {
                    bmiValue = 'obese_1';
                } else if (bmi < 40) {
                    bmiValue = 'obese_2';
                } else {
                    bmiValue = 'obese_3';
                }
                
                // Select the appropriate radio button
                const radioBmiOption = document.querySelector(`input[name="bmi"][value="${bmiValue}"]`);
                if (radioBmiOption) {
                    radioBmiOption.checked = true;
                    
                    // Trigger change event to update form progress
                    const event = new Event('change');
                    radioBmiOption.dispatchEvent(event);
                }
            }
        }
        
        heightInput.addEventListener('input', calculateBMI);
        weightInput.addEventListener('input', calculateBMI);
    }
    
    // Comparison page tabs
    const comparisonTabs = document.querySelectorAll('#comparison-tabs .nav-link');
    if (comparisonTabs.length > 0) {
        comparisonTabs.forEach(tab => {
            tab.addEventListener('click', function(e) {
                e.preventDefault();
                const target = this.getAttribute('data-bs-target');
                
                // Update active tab
                comparisonTabs.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                
                // Show target content
                const tabContents = document.querySelectorAll('.comparison-tab-content');
                tabContents.forEach(content => {
                    content.classList.add('d-none');
                });
                document.querySelector(target).classList.remove('d-none');
            });
        });
    }
}); 