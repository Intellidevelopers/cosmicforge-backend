import logging
from typing import Dict, Any, List
from databases import Database
from sqlalchemy import Table, Column, Integer, String, JSON, DateTime, MetaData, select, insert, update, delete
from datetime import datetime
import json
import uuid
from fastapi import HTTPException
import asyncio
from aiocache import cached
from aiocache.serializers import JsonSerializer

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database setup
from database import database, user_preferences, user_preferences_history

class UserPreferences:
    def __init__(self):
        self.default_preferences = {
            "dashboard_layout": "default",
            "data_sources": ["wearables", "ehr", "lab_results"],
            "notification_settings": {
                "email": True,
                "sms": False,
                "push": True
            },
            "privacy_settings": {
                "share_data_with_doctors": True,
                "share_anonymized_data_for_research": False
            },
            "health_goals": [],
            "preferred_units": {
                "weight": "kg",
                "height": "cm",
                "temperature": "celsius"
            },
            "language": "en"
        }

    @cached(ttl=300, key_builder=lambda f, self, user_id: f'user_preferences:{user_id}', serializer=JsonSerializer())
    async def get_preferences(self, user_id: int) -> Dict[str, Any]:
        try:
            query = select([user_preferences]).where(user_preferences.c.user_id == user_id)
            result = await database.fetch_one(query)
            if result:
                return json.loads(result['preferences'])
            else:
                return self.default_preferences
        except Exception as e:
            logger.error(f"Error fetching user preferences: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch user preferences")

    async def update_preferences(self, user_id: int, new_preferences: Dict[str, Any]):
        try:
            async with database.transaction():
                current_preferences = await self.get_preferences(user_id)
                updated_preferences = self.merge_preferences(current_preferences, new_preferences)
                validated_preferences = self.validate_preferences(updated_preferences)

                # Store current preferences in history
                history_query = insert(user_preferences_history).values(
                    user_id=user_id,
                    preferences=json.dumps(current_preferences),
                    timestamp=datetime.utcnow()
                )
                await database.execute(history_query)

                # Update current preferences
                query = update(user_preferences).where(user_preferences.c.user_id == user_id).values(
                    preferences=json.dumps(validated_preferences),
                    last_updated=datetime.utcnow()
                )
                result = await database.execute(query)

                if result == 0:
                    # If no rows were updated, insert new preferences
                    query = insert(user_preferences).values(
                        user_id=user_id,
                        preferences=json.dumps(validated_preferences),
                        last_updated=datetime.utcnow()
                    )
                    await database.execute(query)

            logger.info(f"Updated preferences for user {user_id}")
            await self.invalidate_cache(user_id)
        except Exception as e:
            logger.error(f"Error updating user preferences: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to update user preferences")

    def merge_preferences(self, current: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        merged = current.copy()
        for key, value in new.items():
            if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                merged[key] = self.merge_preferences(merged[key], value)
            else:
                merged[key] = value
        return merged

    def validate_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        validated = {}
        for key, value in preferences.items():
            if key in self.default_preferences:
                if isinstance(self.default_preferences[key], dict):
                    validated[key] = self.validate_preferences(value)
                elif isinstance(self.default_preferences[key], list):
                    validated[key] = [item for item in value if isinstance(item, type(self.default_preferences[key][0]))] if value else []
                else:
                    validated[key] = value if isinstance(value, type(self.default_preferences[key])) else self.default_preferences[key]
        return validated

    async def get_dashboard_layout(self, user_id: int) -> str:
        preferences = await self.get_preferences(user_id)
        return preferences.get('dashboard_layout', 'default')

    async def update_dashboard_layout(self, user_id: int, layout: str):
        await self.update_preferences(user_id, {'dashboard_layout': layout})

    async def get_data_sources(self, user_id: int) -> List[str]:
        preferences = await self.get_preferences(user_id)
        return preferences.get('data_sources', self.default_preferences['data_sources'])

    async def update_data_sources(self, user_id: int, data_sources: List[str]):
        await self.update_preferences(user_id, {'data_sources': data_sources})

    async def get_notification_settings(self, user_id: int) -> Dict[str, bool]:
        preferences = await self.get_preferences(user_id)
        return preferences.get('notification_settings', self.default_preferences['notification_settings'])

    async def update_notification_settings(self, user_id: int, settings: Dict[str, bool]):
        await self.update_preferences(user_id, {'notification_settings': settings})

    async def get_privacy_settings(self, user_id: int) -> Dict[str, bool]:
        preferences = await self.get_preferences(user_id)
        return preferences.get('privacy_settings', self.default_preferences['privacy_settings'])

    async def update_privacy_settings(self, user_id: int, settings: Dict[str, bool]):
        await self.update_preferences(user_id, {'privacy_settings': settings})

    async def get_health_goals(self, user_id: int) -> List[Dict[str, Any]]:
        preferences = await self.get_preferences(user_id)
        return preferences.get('health_goals', [])

    async def add_health_goal(self, user_id: int, goal: Dict[str, Any]):
        goal['id'] = str(uuid.uuid4())
        goal['created_at'] = datetime.utcnow().isoformat()
        preferences = await self.get_preferences(user_id)
        health_goals = preferences.get('health_goals', [])
        health_goals.append(goal)
        await self.update_preferences(user_id, {'health_goals': health_goals})

    async def remove_health_goal(self, user_id: int, goal_id: str):
        preferences = await self.get_preferences(user_id)
        health_goals = preferences.get('health_goals', [])
        health_goals = [goal for goal in health_goals if goal.get('id') != goal_id]
        await self.update_preferences(user_id, {'health_goals': health_goals})

    async def get_preferred_units(self, user_id: int) -> Dict[str, str]:
        preferences = await self.get_preferences(user_id)
        return preferences.get('preferred_units', self.default_preferences['preferred_units'])

    async def update_preferred_units(self, user_id: int, units: Dict[str, str]):
        await self.update_preferences(user_id, {'preferred_units': units})

    async def get_language(self, user_id: int) -> str:
        preferences = await self.get_preferences(user_id)
        return preferences.get('language', self.default_preferences['language'])

    async def update_language(self, user_id: int, language: str):
        await self.update_preferences(user_id, {'language': language})

    async def reset_preferences(self, user_id: int):
        try:
            async with database.transaction():
                # Store current preferences in history before deleting
                current_preferences = await self.get_preferences(user_id)
                history_query = insert(user_preferences_history).values(
                    user_id=user_id,
                    preferences=json.dumps(current_preferences),
                    timestamp=datetime.utcnow()
                )
                await database.execute(history_query)

                # Delete current preferences
                query = delete(user_preferences).where(user_preferences.c.user_id == user_id)
                await database.execute(query)

            logger.info(f"Reset preferences for user {user_id}")
            await self.invalidate_cache(user_id)
        except Exception as e:
            logger.error(f"Error resetting user preferences: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to reset user preferences")

    async def get_preferences_history(self, user_id: int) -> List[Dict[str, Any]]:
        try:
            query = select([user_preferences_history]).where(user_preferences_history.c.user_id == user_id).order_by(user_preferences_history.c.timestamp.desc())
            results = await database.fetch_all(query)
            return [{"preferences": json.loads(row['preferences']), "timestamp": row['timestamp']} for row in results]
        except Exception as e:
            logger.error(f"Error fetching user preferences history: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch user preferences history")

    async def invalidate_cache(self, user_id: int):
        cache_key = f'user_preferences:{user_id}'
        await asyncio.get_event_loop().run_in_executor(None, self.get_preferences.invalidate, cache_key)

# Initialize UserPreferences
user_preferences_manager = UserPreferences()

# Startup and shutdown events
async def startup_event():
    await database.connect()

async def shutdown_event():
    await database.disconnect()
