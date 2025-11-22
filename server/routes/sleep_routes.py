from flask import Blueprint, request, jsonify
from services.db_manager import execute_insert, execute_query
from services.sleep_logic import calculate_debt, get_avatar_state, calculate_weekly_score
from services.local_data import get_random_fact, get_tip_for_state
from services.event_validator import EventValidator, ValidationError
from services.auto_healer import AutoHealer
from services.reliability_scorer import ReliabilityScorer
from datetime import datetime
import json

sleep_bp = Blueprint('sleep', __name__)

@sleep_bp.route('/log', methods=['POST'])
def log_sleep():
    data = request.json
    user_id = data.get('user_id')
    hours = data.get('hours')
    date = data.get('date', datetime.now().date().isoformat())
    
    if not user_id or hours is None:
        return jsonify({'error': 'Missing data'}), 400
    
    # Validate duration
    valid, error = EventValidator.validate_sleep_duration(hours, is_manual=True)
    if not valid:
        return jsonify({'error': error, 'error_code': 'INVALID_DURATION'}), 400
    
    # Check for overlaps
    start_time = f"{date}T00:00:00"
    end_time = f"{date}T23:59:59"
    overlap_result = EventValidator.check_overlap(user_id, start_time, end_time)
    
    if overlap_result['has_overlap']:
        return jsonify({
            'error': 'Overlap detected',
            'error_code': 'CONFLICT_DETECTED',
            'conflicts': overlap_result['conflicts']
        }), 409
    
    # Log the sleep
    execute_insert('INSERT INTO sleep_logs (user_id, date, hours) VALUES (?, ?, ?)', 
                   (user_id, date, hours))
    
    # Create event
    event_metadata = json.dumps({'manual_entry': True, 'date': date})
    reliability_impact = EventValidator.calculate_reliability_impact('MANUAL_PERIOD')
    
    execute_insert('''
        INSERT INTO sleep_events 
        (user_id, event_type, timestamp, duration_seconds, metadata, reliability_impact)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, 'MANUAL_PERIOD', datetime.now().isoformat(), int(hours * 3600), event_metadata, reliability_impact))
    
    # Update reliability
    reliability = ReliabilityScorer.update_score(user_id, 'MANUAL_PERIOD', reliability_impact)
    
    return jsonify({
        'message': 'Sleep logged successfully',
        'reliability': reliability
    }), 201

@sleep_bp.route('/start', methods=['POST'])
def start_sleep():
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID required'}), 400
    
    # Auto-close stale sessions
    auto_close_result = AutoHealer.auto_close_stale_sessions(user_id)
    
    # Check if already sleeping
    existing = execute_query('SELECT * FROM active_sessions WHERE user_id = ?', (user_id,), one=True)
    if existing:
        # Handle missing wakeup
        auto_close_info = AutoHealer.handle_missing_wakeup(user_id, datetime.now().isoformat())
        
        return jsonify({
            'message': 'Previous session auto-closed. New session started.',
            'auto_closed': auto_close_info,
            'warning': 'You forgot to use /wakeup. This affects your reliability score.'
        }), 200
    
    # Start new session
    start_time = datetime.now().isoformat()
    execute_insert('INSERT INTO active_sessions (user_id, start_time) VALUES (?, ?)', 
                   (user_id, start_time))
    
    # Create event
    event_metadata = json.dumps({'command': '/sleep'})
    reliability_impact = EventValidator.calculate_reliability_impact('SLEEP_START')
    
    execute_insert('''
        INSERT INTO sleep_events 
        (user_id, event_type, timestamp, metadata, reliability_impact)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, 'SLEEP_START', start_time, event_metadata, reliability_impact))
    
    # Update reliability
    reliability = ReliabilityScorer.update_score(user_id, 'SLEEP_START', reliability_impact)
    
    return jsonify({
        'message': 'Sleep timer started. Goodnight!',
        'start_time': start_time,
        'reliability': reliability
    }), 200

@sleep_bp.route('/end', methods=['POST'])
def end_sleep():
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID required'}), 400
        
    session = execute_query('SELECT * FROM active_sessions WHERE user_id = ?', (user_id,), one=True)
    if not session:
        return jsonify({'error': 'No active sleep session found. Use /sleep or /nap first.'}), 404
        
    start_time = datetime.fromisoformat(session['start_time'])
    end_time = datetime.now()
    duration = end_time - start_time
    hours = round(duration.total_seconds() / 3600, 2)
    
    # Validate duration
    valid, error = EventValidator.validate_sleep_duration(hours, is_manual=False)
    if not valid:
        return jsonify({'error': error, 'error_code': 'INVALID_DURATION'}), 400
    
    # Log the sleep
    execute_insert('INSERT INTO sleep_logs (user_id, date, hours) VALUES (?, ?, ?)', 
                   (user_id, end_time.date().isoformat(), hours))
    
    # Create event
    event_metadata = json.dumps({
        'command': '/wakeup',
        'start_time': session['start_time'],
        'end_time': end_time.isoformat(),
        'duration_hours': hours
    })
    reliability_impact = EventValidator.calculate_reliability_impact('SLEEP_END')
    
    execute_insert('''
        INSERT INTO sleep_events 
        (user_id, event_type, timestamp, duration_seconds, metadata, reliability_impact)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, 'SLEEP_END', end_time.isoformat(), int(duration.total_seconds()), event_metadata, reliability_impact))
    
    # Remove active session
    execute_query('DELETE FROM active_sessions WHERE user_id = ?', (user_id,))
    
    # Update reliability
    reliability = ReliabilityScorer.update_score(user_id, 'SLEEP_END', reliability_impact)
    
    # Check for consistency bonus
    ReliabilityScorer.check_consistency_bonus(user_id)
    
    return jsonify({
        'message': f'Good morning! Logged {hours} hours of sleep.',
        'hours': hours,
        'reliability': reliability
    }), 200

@sleep_bp.route('/validate', methods=['POST'])
def validate_command():
    """Pre-validate a command without executing it."""
    data = request.json
    user_id = data.get('user_id')
    command_type = data.get('command_type')
    params = data.get('params', {})
    
    if not user_id or not command_type:
        return jsonify({'error': 'Missing required fields'}), 400
    
    validation_result = EventValidator.validate_command(user_id, command_type, params)
    
    return jsonify(validation_result), 200

@sleep_bp.route('/resolve-conflict', methods=['POST'])
def resolve_conflict():
    """Handle conflict resolution."""
    data = request.json
    user_id = data.get('user_id')
    resolution = data.get('resolution')  # 'overwrite', 'merge', 'cancel'
    params = data.get('params', {})
    
    if not user_id or not resolution:
        return jsonify({'error': 'Missing required fields'}), 400
    
    result = AutoHealer.apply_correction(user_id, resolution, params)
    
    return jsonify(result), 200

@sleep_bp.route('/reliability/<int:user_id>', methods=['GET'])
def get_reliability(user_id):
    """Get user reliability score and statistics."""
    reliability = ReliabilityScorer.get_user_reliability(user_id)
    return jsonify(reliability), 200

@sleep_bp.route('/stats/<int:user_id>', methods=['GET'])
def get_stats(user_id):
    debt = calculate_debt(user_id)
    state = get_avatar_state(debt)
    score = calculate_weekly_score(user_id)
    
    fact = get_random_fact()
    tip = get_tip_for_state(state)
    
    # Check if sleeping
    is_sleeping = False
    session = execute_query('SELECT * FROM active_sessions WHERE user_id = ?', (user_id,), one=True)
    if session:
        is_sleeping = True
    
    # Get reliability
    reliability = ReliabilityScorer.get_user_reliability(user_id)
    
    return jsonify({
        'debt': debt,
        'avatar_state': state,
        'weekly_score': score,
        'fact': fact,
        'tip': tip,
        'is_sleeping': is_sleeping,
        'reliability': reliability
    })
