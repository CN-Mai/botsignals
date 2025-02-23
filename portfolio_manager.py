from typing import Dict, List
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from decimal import Decimal

class PortfolioManager:
    def __init__(self, db_session, config):
        self.db_session = db_session
        self.config = config
        self.risk_manager = RiskManager()
    
    async def get_portfolio_summary(self, user_id: int) -> Dict:
        """Get user's portfolio summary"""
        portfolio = self.db_session.query(Portfolio).filter_by(user_id=user_id).first()
        
        if not portfolio:
            return self._generate_empty_portfolio()
        
        positions = self.db_session.query(Position).filter_by(portfolio_id=portfolio.id).all()
        trades = self.db_session.query(Trade).filter_by(portfolio_id=portfolio.id).all()
        
        return {
            'total_value': self._calculate_total_value(positions),
            'pnl': self._calculate_total_pnl(positions),
            'performance': self._calculate_performance_metrics(trades),
            'positions': self._format_positions(positions),
            'risk_metrics': self.risk_manager.calculate_risk_metrics(positions),
            'suggestions': await self._generate_portfolio_suggestions(positions)
        }
    
    async def add_position(self, user_id: int, position_data: Dict) -> Dict:
        """Add new position to portfolio"""
        try:
            portfolio = self._get_or_create_portfolio(user_id)
            
            # Validate position against risk management rules
            if not self.risk_manager.validate_new_position(portfolio, position_data):
                raise ValueError("Position exceeds risk management limits")
            
            position = Position(
                portfolio_id=portfolio.id,
                symbol=position_data['symbol'],
                entry_price=position_data['entry_price'],
                quantity=position_data['quantity'],
                side=position_data['side'],
                entry_time=datetime.utcnow()
            )
            
            self.db_session.add(position)
            self.db_session.commit()
            
            return {'status': 'success', 'position_id': position.id}
            
        except Exception as e:
            self.db_session.rollback()
            raise e
    
    async def close_position(self, position_id: int, exit_data: Dict) -> Dict:
        """Close an existing position"""
        try:
            position = self.db_session.query(Position).get(position_id)
            if not position:
                raise ValueError("Position not found")
            
            trade = Trade(
                portfolio_id=position.portfolio_id,
                symbol=position.symbol,
                entry_price=position.entry_price,
                exit_price=exit_data['exit_price'],
                quantity=position.quantity,
                side=position.side,
                entry_time=position.entry_time,
                exit_time=datetime.utcnow(),
                pnl=self._calculate_trade_pnl(position, exit_data['exit_price'])
            )
            
            self.db_session.add(trade)
            self.db_session.delete(position)
            self.db_session.commit()
            
            return {
                'status': 'success',
                'trade_summary': self._format_trade(trade)
            }
            
        except Exception as e:
            self.db_session.rollback()
            raise e
    
    def _calculate_trade_pnl(self, position: Position, exit_price: float) -> float:
        """Calculate PnL for a trade"""
        if position.side == 'BUY':
            return (exit_price - position.entry_price) * position.quantity
        else:
            return (position.entry_price - exit_price) * position.quantity
    
    async def _generate_portfolio_suggestions(self, positions: List[Position]) -> Dict:
        """Generate portfolio optimization suggestions"""
        return {
            'rebalancing': self._get_rebalancing_suggestions(positions),
            'risk_management': self.risk_manager.get_risk_suggestions(positions),
            'diversification': self._get_diversification_suggestions(positions)
        }