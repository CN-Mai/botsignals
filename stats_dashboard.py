class StatsDashboard:
    def generate_dashboard(self) -> str:
        return f"""
╔════ 📊 BOT STATISTICS ════╗
║ 
║ 👥 Total Users: 42,895
║ ├─⭐ Free: 35,000
║ └─💎 Premium: 7,895
║ 
║ 📈 Performance:
║ • Signals Sent: 1,458,963
║ • Successful Trades: 89,745
║ • Accuracy Rate: 84.3%
║ • Total Profit: $127.5M
║ 
║ 🏆 Today's Best Signals:
║ 1. BTC/USDT +12.3%
║ 2. SOL/USDT +8.7%
║ 3. ETH/USDT +6.9%
║ 
╚═══════════════════════════╝
"""