"""
Event Validator Service
Validates sleep tracking commands and enforces data integrity rules.
"""
from datetime import datetime, timedelta
from services.db_manager import execute_query

class ValidationError(Exception):
    """Custom exception for validation failures"""
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class EventValidator:
    # Maximum durations
    MAX_MANUAL_SLEEP_HOURS = 12
    MAX_AUTO_SLEEP_HOURS = 24
    MAX_NAP_MINUTES = 180  # 3 hours
    
    @staticmethod
    def validate_sleep_duration(hours, is_manual=True):
        """
        Validate sleep duration is within realistic bounds.
        
        Args:
            hours: Duration in hours
            is_manual: Whether this is a manual entry
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if hours <= 0:
            return False, "Sleep duration must be positive"
        
        if is_manual and hours > EventValidator.MAX_MANUAL_SLEEP_HOURS:
            return False, f"Manual sleep cannot exceed {EventValidator.MAX_MANUAL_SLEEP_HOURS} hours"
        
        if hours > EventValidator.MAX_AUTO_SLEEP_HOURS:
            return False, f"Sleep duration cannot exceed {EventValidator.MAX_AUTO_SLEEP_HOURS} hours"
        
        return True, None
    
    @staticmethod
    def validate_nap_duration(minutes):
        """
        Validate nap duration is within realistic bounds.
        
        Args:
            minutes: Duration in minutes
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if minutes <= 0:
            return False, "Nap duration must be positive"
        
        if minutes > EventValidator.MAX_NAP_MINUTES:
            return False, f"Nap cannot exceed {EventValidator.MAX_NAP_MINUTES} minutes (3 hours)"
        
        return True, None
    
    @staticmethod
    def check_overlap(user_id, start_time, end_time=None):
        """
        Check for overlapping sleep sessions.
        
        Args:
            user_id: User ID
            start_time: Start timestamp (ISO format)
            end_time: End timestamp (ISO format), optional
            
        Returns:
            dict: {
                'has_overlap': bool,
                'conflicts': list of conflicting sessions
            }
        """
        # Check active sessions
        active_session = execute_query(
            'SELECT * FROM active_sessions WHERE user_id = ?',
            (user_id,),
            one=True
        )
        
        if active_session:
            return {
                'has_overlap': True,
                'conflicts': [{
                    'type': 'active_session',
                    'start_time': active_session['start_time'],
                    'message': 'You have an active sleep session. Use /wakeup first.'
                }]
            }
        
        # If end_time provided, check for overlaps in sleep_logs
        if end_time:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)
            
            # Get sleep logs for the date range
            overlapping_logs = execute_query('''
                SELECT * FROM sleep_logs 
                WHERE user_id = ? 
                AND date >= ? 
                AND date <= ?
            ''', (user_id, start_dt.date().isoformat(), end_dt.date().isoformat()))
            
            if overlapping_logs:
                return {
                    'has_overlap': True,
                    'conflicts': [{
                        'type': 'existing_log',
                        'date': log['date'],
                        'hours': log['hours'],
                        'message': f"Overlaps with existing sleep log on {log['date']}"
                    } for log in overlapping_logs]
                }
        
        return {'has_overlap': False, 'conflicts': []}
    
    @staticmethod
    def validate_timeline(user_id, timestamp):
        """
        Validate timestamp is not in the future and follows logical order.
        
        Args:
            user_id: User ID
            timestamp: Timestamp to validate (ISO format)
            
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            ts = datetime.fromisoformat(timestamp)
        except ValueError:
            return False, "Invalid timestamp format"
        
        now = datetime.now()
        
        # Check if in future
        if ts > now:
            return False, "Cannot log sleep in the future"
        
        # Check if too far in past (more than 7 days)
        week_ago = now - timedelta(days=7)
        if ts < week_ago:
            return False, "Cannot log sleep more than 7 days in the past"
        
        return True, None
    
    @staticmethod
    def calculate_reliability_impact(event_type, is_auto_corrected=False, has_conflict=False):
        """
        Calculate how this event affects user reliability score.
        
        Args:
            event_type: Type of event
            is_auto_corrected: Whether this event was auto-corrected
            has_conflict: Whether this event had conflicts
            
        Returns:
            float: Impact on reliability score (-1.0 to +1.0)
        """
        if has_conflict:
            return -0.10
        
        if is_auto_corrected:
            return -0.05
        
        # Perfect manual entries get positive impact
        if event_type in ['SLEEP_START', 'SLEEP_END', 'NAP_START', 'NAP_END']:
            return +0.02
        
        if event_type == 'MANUAL_PERIOD':
            return +0.01
        
        return 0.0
    
    @staticmethod
    def validate_command(user_id, command_type, params):
        """
        Comprehensive validation for a sleep command.
        
        Args:
            user_id: User ID
            command_type: Type of command (sleep_start, sleep_end, nap, manual_log)
            params: Command parameters
            
        Returns:
            dict: {
                'valid': bool,
                'errors': list of error messages,
                'warnings': list of warning messages,
                'conflicts': dict of conflicts if any
            }
        """
        errors = []
        warnings = []
        conflicts = None
        
        if command_type == 'sleep_start' or command_type == 'nap_start':
            # Check for active sessions
            overlap_result = EventValidator.check_overlap(user_id, datetime.now().isoformat())
            if overlap_result['has_overlap']:
                conflicts = overlap_result['conflicts']
                errors.append("Cannot start new sleep session while another is active")
        
        elif command_type == 'manual_log':
            hours = params.get('hours', 0)
            valid, error = EventValidator.validate_sleep_duration(hours, is_manual=True)
            if not valid:
                errors.append(error)
        
        elif command_type == 'nap_manual':
            minutes = params.get('minutes', 0)
            valid, error = EventValidator.validate_nap_duration(minutes)
            if not valid:
                errors.append(error)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'conflicts': conflicts
        }
