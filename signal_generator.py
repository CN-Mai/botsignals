from typing import Dict, List
import pandas as pd
import numpy as np
from datetime import datetime
import random

class EnhancedSignalGenerator:
    def __init__(self, config):
        self.config = config
        self.timeframes = {
            '1m': '1 minute',
            '3m': '3 minutes',
            '5m': '5 minutes',
            '15m': '15 minutes',
            '30m': '30 minutes',
            '1h': '1 hour',
            '2h': '2 hours',
            '4h': '4 hours',
            '6h': '6 hours',
            '12h': '12 hours',
            '1d': '1 day',
            '1w': '1 week'
        }
        
        self.crypto_logos = {
            'BTC': '₿',
            'ETH': 'Ξ',
            'BNB': 'BNB',
            'SOL': 'SOL',
            'DOGE': 'Ð',
            'SHIB': 'SHIB',
            'XRP': 'XRP',
            'ADA': 'ADA',
            'MATIC': 'MATIC',
            'DOT': 'DOT'
        }
    
    async def generate_signals(self, user_is_premium: bool, requested_timeframe: str = None) -> Dict:
        """Generate signals based on user subscription status"""
        
        if user_is_premium:
            # Premium users can choose their timeframe
            timeframes = [requested_timeframe] if requested_timeframe else list(self.timeframes.keys())
        else:
            # Free users get 3 random timeframes
            timeframes = random.sample(list(self.timeframes.keys()), 3)
        
        signals = {
            'timestamp': datetime.utcnow(),
            'timeframes': {},
            'user_type': 'Premium' if user_is_premium else 'Free'
        }
        
        for timeframe in timeframes:
            signals['timeframes'][timeframe] = await self._generate_timeframe_signals(
                timeframe,
                user_is_premium
            )
        
        return signals
    
    async def _generate_timeframe_signals(self, timeframe: str, is_premium: bool) -> Dict:
        """Generate signals for a specific timeframe"""
        signals = {
            'interval': self.timeframes[timeframe],
            'signals': []
        }
        
        # Number of coins to analyze (all for premium, 5 for free)
        coins = self.config.SUPPORTED_COINS if is_premium else self.config.SUPPORTED_COINS[:5]
        
        for coin in coins:
            symbol = coin.split('/')[0]  # Extract symbol from pair
            signal = await self._analyze_coin(coin, timeframe, is_premium)
            signal['logo'] = self.crypto_logos.get(symbol, '')  # Add crypto logo
            signals['signals'].append(signal)
        
        return signals

    async def _analyze_coin(self, coin: str, timeframe: str, is_premium: bool) -> Dict:
        """Analyze a specific coin"""
        # Simulate different analysis based on timeframe
        analysis = {
            'pair': coin,
            'price': self._generate_mock_price(coin),
            'signal': self._generate_signal_type(),
            'change': round(random.uniform(-5, 5), 2),
            'volume': round(random.uniform(1000000, 100000000), 2),
            'timestamp': datetime.utcnow()
        }
        
        if is_premium:
            analysis.update({
                'indicators': {
                    'rsi': round(random.uniform(0, 100), 2),
                    'macd': round(random.uniform(-2, 2), 3),
                    'ema_9': round(random.uniform(90, 110), 2),
                    'ema_21': round(random.uniform(90, 110), 2)
                },
                'entry_points': {
                    'conservative': round(analysis['price'] * 0.99, 2),
                    'aggressive': round(analysis['price'] * 1.01, 2)
                },
                'targets': {
                    'tp1': round(analysis['price'] * 1.05, 2),
                    'tp2': round(analysis['price'] * 1.10, 2),
                    'sl': round(analysis['price'] * 0.95, 2)
                },
                'confidence': round(random.uniform(50, 100), 2)
            })
        
        return analysis

    def _generate_mock_price(self, coin: str) -> float:
        """Generate realistic mock prices based on the coin"""
        base_prices = {
            'BTC/USDT': 88000,
            'ETH/USDT': 4900,
            'BNB/USDT': 430,
            'SOL/USDT': 190,
            'DOGE/USDT': 0.12,
            'SHIB/USDT': 0.00005,
            'XRP/USDT': 1.2,
            'ADA/USDT': 2.1,
            'MATIC/USDT': 3.4,
            'DOT/USDT': 45
        }
        
        base = base_prices.get(coin, 100)
        variation = random.uniform(-0.02, 0.02)  # 2% variation
        return round(base * (1 + variation), 8)

    def _generate_signal_type(self) -> str:
        """Generate signal type with probabilities"""
        signals = [
            ('STRONG BUY', 0.15),
            ('BUY', 0.25),
            ('NEUTRAL', 0.20),
            ('SELL', 0.25),
            ('STRONG SELL', 0.15)
        ]
        
        return random.choices(
            population=[s[0] for s in signals],
            weights=[s[1] for s in signals]
        )[0]