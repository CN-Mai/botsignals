class UserPreferencesManager:
    def __init__(self, db_session):
        self.db_session = db_session
        self.default_preferences = UserPreferences()
        
    async def get_user_preferences(self, user_id: int) -> UserPreferences:
        """Get user preferences or create default"""
        prefs = await self.db_session.get_preferences(user_id)
        if not prefs:
            prefs = self.default_preferences
            await self.save_user_preferences(user_id, prefs)
        return prefs
    
    async def update_preference(self, user_id: int, key: str, value: str):
        """Update a single preference"""
        prefs = await self.get_user_preferences(user_id)
        if hasattr(prefs, key):
            setattr(prefs, key, value)
            await self.save_user_preferences(user_id, prefs)
            return True
        return False