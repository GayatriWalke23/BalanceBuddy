from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")
# Mount a static directory
app.mount("/static", StaticFiles(directory="static"), name="static")


os.environ['OPENAI_API_KEY'] = 'sk-proj-m7DsICl5VTRESDnng3sDT3BlbkFJ3CM7HsreTRZURjQXwyRz'  # Use your actual API key
llm_resto = OpenAI(temperature=0.8)

def get_daily_plan(day, age, gender, weight, height, veg_or_nonveg, disease, region, allergics, foodtype, exercise_pref, diet_pref):
    prompt_template_resto = PromptTemplate(
        input_variables=[
            'day', 'age', 'gender', 'weight', 'height', 'veg_or_nonveg', 
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
    input_data = {
        'day': day,
        'age': age,
        'gender': gender,
        'weight': weight,
        'height': height,
        'veg_or_nonveg': veg_or_nonveg,
        'disease': disease,
        'region': region,
        'allergics': allergics,
        'foodtype': foodtype,
        'exercise_pref': exercise_pref,
        'diet_pref': diet_pref
    }
    results = chain_resto.run(input_data)
    return results

@app.get("/{day}", response_class=HTMLResponse)
def read_day(request: Request, day: str):
    plan = get_daily_plan(day, 30, 'female', 140, 5.6, 'veg', 'hypertension', 'India', 'Peanut', 'Whole grains', 'Yoga, Light Cardio', 'Low Sodium')
    return templates.TemplateResponse("day_plan.html", {"request": request, "plan": plan, "day": day})

@app.get("/")
def website_launch():
    return FileResponse("templates/index.html")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
