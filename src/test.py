import os
import re
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain

if 'OPENAI_API_KEY' not in os.environ:
    raise ValueError("Please set the OPENAI_API_KEY environment variable")

llm_resto = OpenAI(temperature=0.6)

def get_daily_plan(day):
    prompt_template_resto = PromptTemplate(
        input_variables=[
            'day', 'age', 'gender', 'weight', 'height', 'veg_or_nonveg', 
            'disease', 'region', 'allergics', 'foodtype', 'exercise_pref', 'diet_pref'
        ],
        template="""Generate a detailed one-day plan for {day}:
- Morning Meal:
  • [3 items]
- Lunch:
  • [3 items]
- Afternoon Snack:
  • [3 items]
- Dinner:
  • [3 items]
- Workout:
  • [3 items]

User Profile:
- Age: {age}
- Gender: {gender}
- Weight: {weight}
- Height: {height}
- Dietary Preference: {veg_or_nonveg}
- Health Condition: {disease}
- Region: {region}
- Allergies: {allergics}
- Preferred Food Types: {foodtype}
- Exercise Preference: {exercise_pref}
- Diet Preference: {diet_pref}"""
    )

    chain_resto = LLMChain(llm=llm_resto, prompt=prompt_template_resto)
    
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

    return chain_resto.run(input_data)

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday (Cheat Day)"]

for day in days:
    plan = get_daily_plan(day)
    print(f"Plan for {day}:\n{plan}\n")