from typing import Dict, Optional
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from rate_limit import RateLimiter
from encryption import EncryptionManager

class SecurityManager:
    def __init__(self, config):
        self.config = config
        self.rate_limiter = RateLimiter()
        self.encryption_manager = EncryptionManager()
    
    async def authenticate_user(self, user_id: int, api_key: str) -> bool:
        """Authenticate user with API key"""
        try:
            if not self.rate_limiter.check_rate_limit(user_id, 'auth'):
                raise ValueError("Rate limit exceeded")
            
            stored_key = await self._get_stored_api_key(user_id)
            return self._verify_api_key(api_key, stored_key)
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def generate_session_token(self, user_id: int) -> str:
        """Generate JWT session token"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'jti': secrets.token_hex(16)
        }
        
        return jwt.encode(payload, self.config.JWT_SECRET, algorithm='HS256')
    
    def verify_session_token(self, token: str) -> Optional[Dict]:
        """Verify JWT session token"""
        try:
            payload = jwt.decode(token, self.config.JWT_SECRET, algorithms=['HS256'])
            if not self.rate_limiter.check_rate_limit(payload['user_id'], 'session'):
                raise ValueError("Session rate limit exceeded")
            return payload
        except:
            return None
    
    def encrypt_sensitive_data(self, data: Dict) -> Dict:
        """Encrypt sensitive user data"""
        return self.encryption_manager.encrypt_data(data)
    
    def decrypt_sensitive_data(self, encrypted_data: Dict) -> Dict:
        """Decrypt sensitive user data"""
        return self.encryption_manager.decrypt_data(encrypted_data)