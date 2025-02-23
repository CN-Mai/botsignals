class SignalDisplay:
    def format_premium_signal(self, signal_data: dict) -> str:
        return f"""
╔════ 💎 PREMIUM SIGNAL ════╗
║ {signal_data['logo']} {signal_data['pair']}
║ 
║ 💵 Price: ${signal_data['price']:,.2f}
║ 📊 Signal: {self._format_signal_strength(signal_data['signal'])}
║ 📈 Change: {self._format_change(signal_data['change'])}
║ 
║ 🎯 Entry Points:
║ • Safe: ${signal_data['entry_points']['conservative']:,.2f}
║ • Optimal: ${signal_data['entry_points']['aggressive']:,.2f}
║ 
║ 🎯 Targets:
║ • TP1: ${signal_data['targets']['tp1']:,.2f}
║ • TP2: ${signal_data['targets']['tp2']:,.2f}
║ • SL: ${signal_data['targets']['sl']:,.2f}
║ 
║ 📊 Technical Indicators:
║ • RSI: {self._format_indicator(signal_data['indicators']['rsi'])}
║ • MACD: {signal_data['indicators']['macd']}
║ • Volume: {self._format_volume(signal_data['volume'])}
║ 
║ 🎯 Confidence: {self.create_progress_bar(signal_data['confidence'])}
╚═══════════════════════════╝
"""

    def format_free_signal(self, signal_data: dict) -> str:
        return f"""
╔════ ⭐ MARKET SIGNAL ════╗
║ {signal_data['logo']} {signal_data['pair']}
║ 
║ 💵 Price: ${signal_data['price']:,.2f}
║ 📊 Signal: {self._format_signal_strength(signal_data['signal'])}
║ 📈 Change: {self._format_change(signal_data['change'])}
║ 
║ 🔒 Upgrade to Premium for:
║ • Entry & Exit points
║ • Technical Analysis
║ • AI Predictions
╚═══════════════════════════╝
"""