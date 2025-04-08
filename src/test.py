import os
import re
os.environ['OPENAI_API_KEY'] = 'sk-proj-m7DsICl5VTRESDnng3sDT3BlbkFJ3CM7HsreTRZURjQXwyRz' # apenai

from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain

llm_resto = OpenAI(temperature=0.6)

def get_daily_plan(day):
    prompt_template_resto = PromptTemplate(
        input_variables=[
            'age', 'gender', 'weight', 'height', 'veg_or_nonveg', 
            'disease', 'region', 'allergics', 'foodtype', 'exercise_pref', 'diet_pref'
        ],
        template=f"""Please generate a detailed one-day plan for {{day}}. The plan should include meals and workouts formatted as follows:
        - Morning Meal: [3 bullet points]
        - Lunch: [3 bullet points]
        - Afternoon Snack: [3 bullet points]
        - Dinner: [3 bullet points]
        - Workout: [3 bullet points]
        Keep it short and do not add anything extra other than these points also limit each to 3 bullet points.
        
        Consider the following details for the plan:
        - Age: {{age}}
        - Gender: {{gender}}
        - Weight: {{weight}}
        - Height: {{height}}
        - Dietary Preference: {{veg_or_nonveg}}
        - Health Condition: {{disease}}
        - Region: {{region}}
        - Allergies: {{allergics}}
        - Preferred Food Types: {{foodtype}}
        - Exercise Preference: {{exercise_pref}}
        - Diet Preference: {{diet_pref}}
        """
    )

    chain_resto = LLMChain(llm=llm_resto, prompt=prompt_template_resto)

    # Define the input dictionary with additional user preferences
    input_data = {
        'day': day,
        'age': 30,
        'gender': 'female',
        'weight': 140,
        'height': 5.6,
        'veg_or_nonveg': 'veg',
        'disease': 'hypertension',
        'region': 'India',
        'allergics': 'Peanut',
        'foodtype': 'Whole grains',
        'exercise_pref': 'Yoga, Light Cardio',
        'diet_pref': 'Low Sodium'
    }

    results = chain_resto.run(input_data)
    return results

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday (Cheat Day)"]

for day in days:
    plan = get_daily_plan(day)
    print(f"Plan for {day}:\n{plan}\n")