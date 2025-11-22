from services.db_manager import execute_query
from datetime import datetime, timedelta

IDEAL_SLEEP = 8.0

def get_aggregated_logs(user_id, days=7):
    today = datetime.now().date()
    start_date = today - timedelta(days=days)
    
    # Get all logs for the period
    logs = execute_query('''
        SELECT date, hours FROM sleep_logs 
        WHERE user_id = ? AND date >= ?
    ''', (user_id, start_date.isoformat()))
    
    # Aggregate hours by date
    daily_sleep = {}
    for row in logs:
        date_str = row['date']
        hours = row['hours']
        if date_str in daily_sleep:
            daily_sleep[date_str] += hours
        else:
            daily_sleep[date_str] = hours
            
    return daily_sleep

def calculate_debt(user_id):
    # Calculate debt over the last 7 days
    daily_sleep = get_aggregated_logs(user_id, days=7)
    
    total_slept = sum(daily_sleep.values())
    days_tracked = len(daily_sleep)
    
    if days_tracked == 0:
        return 0.0
        
    # Debt = (Days Tracked * Ideal) - Total Slept
    debt = (days_tracked * IDEAL_SLEEP) - total_slept
    return round(debt, 1)

def get_avatar_state(debt):
    if debt <= 0:
        return "glowing"
    elif debt < 5:
        return "neutral"
    else:
        return "grumpy"

def calculate_weekly_score(user_id):
    # Simple scoring: 10 pts per hour, +50 bonus if daily total >= 8 hours
    daily_sleep = get_aggregated_logs(user_id, days=7)
    
    score = 0
    for date_str, total_hours in daily_sleep.items():
        # Base points: 10 per hour
        score += int(total_hours * 10)
        
        # Bonus points for hitting daily target
        if total_hours >= IDEAL_SLEEP:
            score += 50
            
    return score
