"""Web interface for BalanceBuddy health and fitness planner."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(env_path)

# Add parent directory to Python path for imports
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import google.generativeai as genai
from pydantic import BaseModel
import uvicorn

from config import GOOGLE_API_KEY, API_HOST, API_PORT

app = FastAPI(title="BalanceBuddy Web Interface")
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))
app.mount("/static", StaticFiles(directory=str(Path(__file__).resolve().parent / "static")), name="static")

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# Print available models
for m in genai.list_models():
    print(f"Found model: {m.name}")

model = genai.GenerativeModel('gemini-2.0-flash')

class UserPreferences(BaseModel):
    age: int
    gender: str
    weight: float
    height: float
    veg_or_nonveg: str
    disease: str = ""
    region: str
    allergics: str = ""
    foodtype: str
    exercise_pref: str
    diet_pref: str

def get_daily_plan(day: str, preferences: UserPreferences) -> str:
    """Generate a daily plan based on user preferences."""
    try:
        prompt = f"""Generate a detailed one-day plan for {day}, considering these preferences:
        Age: {preferences.age}, Gender: {preferences.gender}
        Weight: {preferences.weight}kg, Height: {preferences.height}m
        Diet: {preferences.veg_or_nonveg}
        Health Conditions: {preferences.disease}
        Region: {preferences.region}
        Allergies: {preferences.allergics}
        Food Types: {preferences.foodtype}
        Exercise: {preferences.exercise_pref}
        Diet Goals: {preferences.diet_pref}

        Format the plan with HTML tags as follows:

        <h2>Morning Meal</h2>
        <ul>
        <li>[Healthy breakfast option 1]</li>
        <li>[Healthy breakfast option 2]</li>
        <li>[Healthy breakfast option 3]</li>
        </ul>

        <h2>Lunch</h2>
        <ul>
        <li>[Nutritious lunch option 1]</li>
        <li>[Nutritious lunch option 2]</li>
        <li>[Nutritious lunch option 3]</li>
        </ul>

        <h2>Afternoon Snack</h2>
        <ul>
        <li>[Healthy snack option 1]</li>
        <li>[Healthy snack option 2]</li>
        <li>[Healthy snack option 3]</li>
        </ul>

        <h2>Dinner</h2>
        <ul>
        <li>[Balanced dinner option 1]</li>
        <li>[Balanced dinner option 2]</li>
        <li>[Balanced dinner option 3]</li>
        </ul>

        <h2>Workout Plan</h2>
        <ul>
        <li>[Exercise activity 1 with duration/intensity]</li>
        <li>[Exercise activity 2 with duration/intensity]</li>
        <li>[Exercise activity 3 with duration/intensity]</li>
        </ul>

        Make sure all recommendations are appropriate for the user's preferences, health conditions, and dietary restrictions.
        Keep descriptions concise but informative, including portion sizes for meals and duration/intensity for exercises."""

        print(f"Sending prompt to Gemini: {prompt[:100]}...")
        response = model.generate_content(prompt)
        print(f"Received response from Gemini: {response}")
        result = response.text
        print(f"Extracted text: {result[:100]}...")
        return result
    except Exception as e:
        print(f"Error with Gemini: {str(e)}")
        return f"Error generating plan: {str(e)}"

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/plan", response_class=HTMLResponse)
async def create_plan(
    request: Request,
    day: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    weight: float = Form(...),
    height: float = Form(...),
    veg_or_nonveg: str = Form(...),
    disease: str = Form(""),
    region: str = Form(...),
    allergics: str = Form(""),
    foodtype: str = Form(...),
    exercise_pref: str = Form(...),
    diet_pref: str = Form(...)
):
    preferences = UserPreferences(
        age=age,
        gender=gender,
        weight=weight,
        height=height,
        veg_or_nonveg=veg_or_nonveg,
        disease=disease,
        region=region,
        allergics=allergics,
        foodtype=foodtype,
        exercise_pref=exercise_pref,
        diet_pref=diet_pref
    )
    
    plan = get_daily_plan(day, preferences)
    return templates.TemplateResponse(
        "day_plan.html",
        {"request": request, "plan": plan, "day": day, "preferences": preferences}
    )

if __name__ == "__main__":
    uvicorn.run(app, host=API_HOST, port=API_PORT, reload=True)
