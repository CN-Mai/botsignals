class DisplayManager:
    def __init__(self):
        self.stats = {
            'users': {
                'free': 35000,
                'premium': 7895,
                'total': 42895
            },
            'signals_sent': 1458963,
            'successful_trades': 89745,
            'accuracy_rate': 84.3,
            'total_profit': '$127.5M'
        }
        
        self.emojis = {
            'trending_up': '📈',
            'trending_down': '📉',
            'hot': '🔥',
            'rocket': '🚀',
            'money': '💰',
            'chart': '📊',
            'premium': '💎',
            'alert': '🔔',
            'time': '⏰',
            'users': '👥',
            'crown': '👑',
            'star': '⭐',
            'lightning': '⚡',
            'target': '🎯',
            'gain': '📈',
            'loss': '📉'
        }
    
    def format_price_movement(self, price: float, change: float) -> str:
        """Format price movement with colored arrows and styling"""
        arrow = '🟢 ▲' if change > 0 else '🔴 ▼' if change < 0 else '⚪️ ▶️'
        return f"{arrow} ${price:,.2f} ({change:+.2f}%)"

    def create_progress_bar(self, value: float, max_value: float = 100) -> str:
        """Create a visual progress bar"""
        filled = int((value / max_value) * 10)
        return f"{'█' * filled}{'░' * (10 - filled)} {value:.1f}%"

    def format_volume(self, volume: float) -> str:
        """Format volume with K/M/B suffixes"""
        if volume >= 1e9:
            return f"{volume/1e9:.1f}B"
        elif volume >= 1e6:
            return f"{volume/1e6:.1f}M"
        elif volume >= 1e3:
            return f"{volume/1e3:.1f}K"
        return f"{volume:.1f}"