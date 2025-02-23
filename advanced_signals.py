import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import talib
from sklearn.ensemble import RandomForestRegressor
import joblib
from datetime import datetime, timedelta

class AdvancedSignalGenerator:
    def __init__(self, config):
        self.config = config
        self.ml_models = {}
        self.load_ml_models()
    
    def load_ml_models(self):
        """Load pre-trained ML models for each supported coin"""
        for coin in self.config.SUPPORTED_COINS:
            try:
                model_path = f"models/{coin.replace('/', '_')}_model.joblib"
                self.ml_models[coin] = joblib.load(model_path)
            except:
                self.ml_models[coin] = self._train_new_model(coin)
    
    def _train_new_model(self, symbol: str) -> RandomForestRegressor:
        """Train a new model if not existing"""
        # Get historical data
        data = self._get_historical_data(symbol)
        features = self._calculate_features(data)
        target = data['close'].pct_change().shift(-1).fillna(0)
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(features, target)
        
        # Save model
        joblib.dump(model, f"models/{symbol.replace('/', '_')}_model.joblib")
        return model
    
    def _calculate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators as features"""
        df = df.copy()
        
        # Basic indicators
        df['rsi'] = talib.RSI(df['close'])
        df['macd'], df['macd_signal'], _ = talib.MACD(df['close'])
        df['ema_9'] = talib.EMA(df['close'], timeperiod=9)
        df['ema_21'] = talib.EMA(df['close'], timeperiod=21)
        df['ema_50'] = talib.EMA(df['close'], timeperiod=50)
        df['ema_200'] = talib.EMA(df['close'], timeperiod=200)
        
        # Volume indicators
        df['obv'] = talib.OBV(df['close'], df['volume'])
        df['adx'] = talib.ADX(df['high'], df['low'], df['close'])
        
        # Volatility indicators
        df['bbands_upper'], df['bbands_middle'], df['bbands_lower'] = talib.BBANDS(df['close'])
        df['atr'] = talib.ATR(df['high'], df['low'], df['close'])
        
        # Momentum indicators
        df['mfi'] = talib.MFI(df['high'], df['low'], df['close'], df['volume'])
        df['cci'] = talib.CCI(df['high'], df['low'], df['close'])
        df['roc'] = talib.ROC(df['close'])
        
        # Custom indicators
        df['price_position'] = (df['close'] - df['bbands_lower']) / (df['bbands_upper'] - df['bbands_lower'])
        df['volume_trend'] = df['volume'] / df['volume'].rolling(20).mean()
        df['trend_strength'] = abs(df['ema_9'] - df['ema_50']) / df['atr']
        
        return df.fillna(0)
    
    async def generate_premium_signal(self, symbol: str) -> Dict:
        """Generate advanced trading signals with ML predictions"""
        try:
            # Get recent data
            data = self._get_historical_data(symbol)
            features = self._calculate_features(data)
            
            # Get ML prediction
            latest_features = features.iloc[-1:]
            prediction = self.ml_models[symbol].predict(latest_features)[0]
            
            # Calculate confidence score
            confidence = self._calculate_confidence(features.iloc[-1])
            
            # Generate signal based on multiple factors
            signal = self._generate_combined_signal(features.iloc[-1], prediction)
            
            return {
                'symbol': symbol,
                'timestamp': datetime.utcnow(),
                'price': data['close'].iloc[-1],
                'signal': signal['direction'],
                'confidence': confidence,
                'prediction': {
                    'direction': 'UP' if prediction > 0 else 'DOWN',
                    'expected_change': abs(prediction * 100),
                    'timeframe': '24h'
                },
                'indicators': {
                    'rsi': features['rsi'].iloc[-1],
                    'macd': features['macd'].iloc[-1],
                    'macd_signal': features['macd_signal'].iloc[-1],
                    'adx': features['adx'].iloc[-1],
                    'bb_position': features['price_position'].iloc[-1],
                    'trend_strength': features['trend_strength'].iloc[-1]
                },
                'risk_level': self._calculate_risk_level(features.iloc[-1]),
                'suggested_entry': self._calculate_entry_points(data, signal['direction']),
                'suggested_exit': self._calculate_exit_points(data, signal['direction'])
            }
        except Exception as e:
            logger.error(f"Error generating premium signal: {str(e)}")
            return None
    
    def _calculate_confidence(self, indicators) -> float:
        """Calculate signal confidence score"""
        confidence_factors = {
            'trend_alignment': self._check_trend_alignment(indicators),
            'volume_support': self._check_volume_support(indicators),
            'momentum': self._check_momentum(indicators),
            'risk_reward': self._check_risk_reward(indicators)
        }
        
        return sum(confidence_factors.values()) / len(confidence_factors)
    
    def _generate_combined_signal(self, indicators, ml_prediction) -> Dict:
        """Generate trading signal combining ML and technical analysis"""
        # Technical signals
        trend_signal = 1 if indicators['ema_9'] > indicators['ema_21'] else -1
        momentum_signal = 1 if indicators['rsi'] > 50 else -1
        volume_signal = 1 if indicators['volume_trend'] > 1 else -1
        
        # Combine signals with ML prediction
        combined_score = (
            0.4 * np.sign(ml_prediction) +
            0.3 * trend_signal +
            0.2 * momentum_signal +
            0.1 * volume_signal
        )
        
        return {
            'direction': 'BUY' if combined_score > 0 else 'SELL',
            'strength': abs(combined_score)
        }
    
    def _calculate_entry_points(self, data: pd.DataFrame, signal: str) -> Dict:
        """Calculate suggested entry points"""
        current_price = data['close'].iloc[-1]
        atr = talib.ATR(data['high'], data['low'], data['close']).iloc[-1]
        
        if signal == 'BUY':
            return {
                'optimal': current_price,
                'conservative': current_price - 0.5 * atr,
                'aggressive': current_price + 0.3 * atr
            }
        else:
            return {
                'optimal': current_price,
                'conservative': current_price + 0.5 * atr,
                'aggressive': current_price - 0.3 * atr
            }
    
    def _calculate_exit_points(self, data: pd.DataFrame, signal: str) -> Dict:
        """Calculate suggested exit points"""
        current_price = data['close'].iloc[-1]
        atr = talib.ATR(data['high'], data['low'], data['close']).iloc[-1]
        
        if signal == 'BUY':
            return {
                'take_profit_1': current_price + 1.5 * atr,
                'take_profit_2': current_price + 2.5 * atr,
                'stop_loss': current_price - atr
            }
        else:
            return {
                'take_profit_1': current_price - 1.5 * atr,
                'take_profit_2': current_price - 2.5 * atr,
                'stop_loss': current_price + atr
            }
    
    def _calculate_risk_level(self, indicators) -> str:
        """Calculate risk level based on market conditions"""
        risk_score = 0
        
        # Add risk based on volatility
        risk_score += self._volatility_risk(indicators)
        
        # Add risk based on trend strength
        risk_score += self._trend_risk(indicators)
        
        # Add risk based on volume
        risk_score += self._volume_risk(indicators)
        
        if risk_score < 3:
            return 'LOW'
        elif risk_score < 6:
            return 'MEDIUM'
        else:
            return 'HIGH'