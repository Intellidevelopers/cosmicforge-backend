from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, UUID4
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta
import json
import asyncio
from uuid import uuid4

from data_integration import DataIntegrationEngine
from health_plan import HealthPlanGenerator
from health_tracker import HealthTracker
from ai_model_manager import AIModelManager
from user_preferences import UserPreferences
from database import database, health_data, health_plans, health_goals, users
from config import Config

# Set up logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Health Dashboard API", version=Config.API_VERSION)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic models for request/response
class HealthData(BaseModel):
    user_id: UUID4
    data_type: str
    value: float
    timestamp: Optional[datetime] = None

class HealthPlan(BaseModel):
    user_id: UUID4
    plan_type: str
    details: Dict[str, any]

class HealthGoal(BaseModel):
    user_id: UUID4
    goal_type: str
    target_value: float
    deadline: Optional[datetime] = None

class UserPreference(BaseModel):
    user_id: UUID4
    preferences: Dict[str, any]

# Initialize components
data_integration_engine = DataIntegrationEngine()
health_plan_generator = HealthPlanGenerator()
health_tracker = HealthTracker()
ai_model_manager = AIModelManager()
user_preferences = UserPreferences()

@app.on_event("startup")
async def startup():
    await database.connect()
    await ai_model_manager.initialize()
    await data_integration_engine.initialize()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    await data_integration_engine.close()

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user['id'])}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/dashboard/integrated-data/{user_id}")
async def get_integrated_data(user_id: UUID4, current_user: dict = Depends(get_current_user)):
    try:
        if current_user['id'] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this data")
        data = await data_integration_engine.integrate_data(user_id)
        return {"user_id": user_id, "integrated_data": data}
    except Exception as e:
        logger.error(f"Error fetching integrated data: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching integrated data")

@app.post("/api/dashboard/add-data-source")
async def add_data_source(data: HealthData, current_user: dict = Depends(get_current_user)):
    try:
        if current_user['id'] != data.user_id:
            raise HTTPException(status_code=403, detail="Not authorized to add data for this user")
        await health_tracker.update_health_data(data.user_id, data.dict())
        return {"message": "Data source added successfully"}
    except Exception as e:
        logger.error(f"Error adding data source: {str(e)}")
        raise HTTPException(status_code=500, detail="Error adding data source")

@app.get("/api/dashboard/health-plan/{user_id}")
async def get_health_plan(user_id: UUID4, current_user: dict = Depends(get_current_user)):
    try:
        if current_user['id'] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this health plan")
        user_data = await health_tracker.get_user_data(user_id)
        plan = await health_plan_generator.generate_plan(user_data)
        return {"user_id": user_id, "health_plan": plan}
    except Exception as e:
        logger.error(f"Error fetching health plan: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching health plan")

@app.post("/api/dashboard/generate-plan")
async def generate_health_plan(data: HealthPlan, current_user: dict = Depends(get_current_user)):
    try:
        if current_user['id'] != data.user_id:
            raise HTTPException(status_code=403, detail="Not authorized to generate plan for this user")
        user_data = await health_tracker.get_user_data(data.user_id)
        plan = await health_plan_generator.generate_plan(user_data)
        query = health_plans.insert().values(
            id=uuid4(),
            user_id=data.user_id,
            plan_type=data.plan_type,
            details=json.dumps(plan),
            created_at=datetime.utcnow()
        )
        await database.execute(query)
        return {"user_id": data.user_id, "health_plan": plan}
    except Exception as e:
        logger.error(f"Error generating health plan: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating health plan")

@app.put("/api/dashboard/update-plan")
async def update_health_plan(data: HealthPlan, current_user: dict = Depends(get_current_user)):
    try:
        if current_user['id'] != data.user_id:
            raise HTTPException(status_code=403, detail="Not authorized to update plan for this user")
        query = health_plans.update().where(health_plans.c.user_id == data.user_id).values(
            plan_type=data.plan_type,
            details=json.dumps(data.details),
            updated_at=datetime.utcnow()
        )
        await database.execute(query)
        return {"message": "Health plan updated successfully"}
    except Exception as e:
        logger.error(f"Error updating health plan: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating health plan")

@app.get("/api/dashboard/health-score/{user_id}")
async def get_health_score(user_id: UUID4, current_user: dict = Depends(get_current_user)):
    try:
        if current_user['id'] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this health score")
        user_data = await health_tracker.get_user_data(user_id)
        health_score = await health_tracker.calculate_health_score(user_data)
        return {"user_id": user_id, "health_score": health_score}
    except Exception as e:
        logger.error(f"Error calculating health score: {str(e)}")
        raise HTTPException(status_code=500, detail="Error calculating health score")

@app.get("/api/dashboard/progress/{user_id}")
async def get_progress(user_id: UUID4, current_user: dict = Depends(get_current_user)):
    try:
        if current_user['id'] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this progress data")
        user_data = await health_tracker.get_user_data(user_id)
        progress = await health_tracker.progress_tracker.track_progress(user_id, user_data)
        return {"user_id": user_id, "progress": progress}
    except Exception as e:
        logger.error(f"Error fetching progress: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching progress")

@app.post("/api/dashboard/set-goal")
async def set_health_goal(goal: HealthGoal, current_user: dict = Depends(get_current_user)):
    try:
        if current_user['id'] != goal.user_id:
            raise HTTPException(status_code=403, detail="Not authorized to set goal for this user")
        query = health_goals.insert().values(
            id=uuid4(),
            user_id=goal.user_id,
            goal_type=goal.goal_type,
            target_value=goal.target_value,
            deadline=goal.deadline,
            created_at=datetime.utcnow()
        )
        await database.execute(query)
        return {"message": "Health goal set successfully"}
    except Exception as e:
        logger.error(f"Error setting health goal: {str(e)}")
        raise HTTPException(status_code=500, detail="Error setting health goal")

@app.get("/api/dashboard/alerts/{user_id}")
async def get_health_alerts(user_id: UUID4, current_user: dict = Depends(get_current_user)):
    try:
        if current_user['id'] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access these alerts")
        user_data = await health_tracker.get_user_data(user_id)
        health_score = await health_tracker.calculate_health_score(user_data)
        alerts = await health_tracker.alert_system.check_alerts(user_id, user_data, health_score)
        return {"user_id": user_id, "alerts": alerts}
    except Exception as e:
        logger.error(f"Error fetching health alerts: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching health alerts")

@app.get("/api/dashboard/preferences/{user_id}")
async def get_user_preferences(user_id: UUID4, current_user: dict = Depends(get_current_user)):
    try:
        if current_user['id'] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access these preferences")
        preferences = await user_preferences.get_preferences(user_id)
        return {"user_id": user_id, "preferences": preferences}
    except Exception as e:
        logger.error(f"Error fetching user preferences: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching user preferences")

@app.put("/api/dashboard/preferences/{user_id}")
async def update_user_preferences(user_id: UUID4, preferences: UserPreference, current_user: dict = Depends(get_current_user)):
    try:
        if current_user['id'] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to update these preferences")
        await user_preferences.update_preferences(user_id, preferences.preferences)
        return {"message": "User preferences updated successfully"}
    except Exception as e:
        logger.error(f"Error updating user preferences: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating user preferences")

@app.post("/api/ai/train")
async def train_ai_models(current_user: dict = Depends(get_current_user)):
    try:
        # Check if user has admin privileges
        if not current_user.get('is_admin', False):
            raise HTTPException(status_code=403, detail="Not authorized to train AI models")
        await ai_model_manager.train_models()
        return {"message": "AI models trained successfully"}
    except Exception as e:
        logger.error(f"Error training AI models: {str(e)}")
        raise HTTPException(status_code=500, detail="Error training AI models")

@app.get("/api/ai/model-status")
async def get_ai_model_status(current_user: dict = Depends(get_current_user)):
    try:
        # Check if user has admin privileges
        if not current_user.get('is_admin', False):
            raise HTTPException(status_code=403, detail="Not authorized to view AI model status")
        status = await ai_model_manager.get_model_status()
        return {"status": status}
    except Exception as e:
        logger.error(f"Error fetching AI model status: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching AI model status")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
