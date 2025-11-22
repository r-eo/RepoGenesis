from flask import Blueprint, jsonify, request
from services.db_manager import execute_query, execute_insert
from services.sleep_logic import calculate_weekly_score, calculate_debt

social_bp = Blueprint('social', __name__)

@social_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    # Get all users
    users = execute_query('SELECT id, username FROM users')
    
    leaderboard = []
    for user in users:
        score = calculate_weekly_score(user['id'])
        debt = calculate_debt(user['id'])
        leaderboard.append({
            'username': user['username'],
            'score': score,
            'debt': debt
        })
    
    # Sort by score desc
    leaderboard.sort(key=lambda x: x['score'], reverse=True)
    
    return jsonify(leaderboard)

@social_bp.route('/friends/<int:user_id>', methods=['GET'])
def get_friends(user_id):
    # For this prototype, we'll just return the top 5 users from the leaderboard as "friends"
    # to populate the UI, since we don't have a real friend request system yet.
    users = execute_query('SELECT id, username FROM users WHERE id != ? LIMIT 5', (user_id,))
    
    friends = []
    for user in users:
        score = calculate_weekly_score(user['id'])
        debt = calculate_debt(user['id'])
        friends.append({
            'id': user['id'],
            'username': user['username'],
            'score': score,
            'debt': debt,
            'status': 'Online' # Mock status
        })
    
    # Sort friends by debt (ascending - lower debt is better)
    friends.sort(key=lambda x: x['debt'])
    
    return jsonify(friends)
