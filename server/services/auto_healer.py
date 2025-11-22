"""
Auto-Healer Service
Automatically corrects and heals sleep tracking data issues.
"""
from datetime import datetime, timedelta
from services.db_manager import execute_query, execute_insert
import json

class AutoHealer:
    # Threshold for stale sessions (24 hours)
    STALE_SESSION_HOURS = 24
    
    @staticmethod
    def auto_close_stale_sessions(user_id):
        """
        Auto-close sleep sessions that have been open for more than 24 hours.
        
        Args:
            user_id: User ID
            
        Returns:
            dict: {
                'closed_sessions': list of closed session details,
                'events_created': int
            }
        """
        # Find active sessions
        active_session = execute_query(
            'SELECT * FROM active_sessions WHERE user_id = ?',
            (user_id,),
            one=True
        )
        
        if not active_session:
            return {'closed_sessions': [], 'events_created': 0}
        
        start_time = datetime.fromisoformat(active_session['start_time'])
        now = datetime.now()
        duration = now - start_time
        
        # Check if stale (> 24 hours)
        if duration.total_seconds() / 3600 > AutoHealer.STALE_SESSION_HOURS:
            # Auto-close the session
            hours = round(duration.total_seconds() / 3600, 2)
            
            # Log the sleep
            execute_insert(
                'INSERT INTO sleep_logs (user_id, date, hours) VALUES (?, ?, ?)',
                (user_id, now.date().isoformat(), hours)
            )
            
            # Create AUTO_CLOSE event
            event_metadata = json.dumps({
                'reason': 'Stale session auto-closed',
                'original_start': active_session['start_time'],
                'auto_close_time': now.isoformat(),
                'duration_hours': hours
            })
            
            execute_insert('''
                INSERT INTO sleep_events 
                (user_id, event_type, timestamp, duration_seconds, metadata, reliability_impact)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, 'AUTO_CLOSE', now.isoformat(), int(duration.total_seconds()), event_metadata, -0.05))
            
            # Remove active session
            execute_query('DELETE FROM active_sessions WHERE user_id = ?', (user_id,))
            
            # Update reliability
            AutoHealer._update_reliability_for_auto_close(user_id)
            
            return {
                'closed_sessions': [{
                    'start_time': active_session['start_time'],
                    'end_time': now.isoformat(),
                    'duration_hours': hours,
                    'reason': 'Stale session (>24h)'
                }],
                'events_created': 1
            }
        
        return {'closed_sessions': [], 'events_created': 0}
    
    @staticmethod
    def handle_missing_wakeup(user_id, new_event_time):
        """
        Handle missing /wakeup by auto-closing previous session.
        
        Args:
            user_id: User ID
            new_event_time: Timestamp of new event that triggered this
            
        Returns:
            dict: Auto-close details or None
        """
        active_session = execute_query(
            'SELECT * FROM active_sessions WHERE user_id = ?',
            (user_id,),
            one=True
        )
        
        if not active_session:
            return None
        
        start_time = datetime.fromisoformat(active_session['start_time'])
        new_time = datetime.fromisoformat(new_event_time)
        duration = new_time - start_time
        hours = round(duration.total_seconds() / 3600, 2)
        
        # Log the sleep
        execute_insert(
            'INSERT INTO sleep_logs (user_id, date, hours) VALUES (?, ?, ?)',
            (user_id, new_time.date().isoformat(), hours)
        )
        
        # Create AUTO_CLOSE event
        event_metadata = json.dumps({
            'reason': 'Missing wakeup - auto-closed on new sleep command',
            'original_start': active_session['start_time'],
            'auto_close_time': new_time.isoformat(),
            'duration_hours': hours
        })
        
        execute_insert('''
            INSERT INTO sleep_events 
            (user_id, event_type, timestamp, duration_seconds, metadata, reliability_impact)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, 'AUTO_CLOSE', new_time.isoformat(), int(duration.total_seconds()), event_metadata, -0.05))
        
        # Remove active session
        execute_query('DELETE FROM active_sessions WHERE user_id = ?', (user_id,))
        
        # Update reliability
        AutoHealer._update_reliability_for_auto_close(user_id)
        
        return {
            'auto_closed': True,
            'start_time': active_session['start_time'],
            'end_time': new_time.isoformat(),
            'duration_hours': hours,
            'reason': 'Missing wakeup'
        }
    
    @staticmethod
    def suggest_correction(conflict_data):
        """
        Suggest correction options for conflicts.
        
        Args:
            conflict_data: Conflict information
            
        Returns:
            dict: Suggested correction options
        """
        return {
            'options': [
                {
                    'action': 'overwrite',
                    'description': 'Replace existing session with new one',
                    'impact': 'Previous session will be deleted'
                },
                {
                    'action': 'merge',
                    'description': 'Combine both sessions into one',
                    'impact': 'Total duration will be summed'
                },
                {
                    'action': 'cancel',
                    'description': 'Cancel new session, keep existing',
                    'impact': 'No changes will be made'
                }
            ],
            'recommended': 'cancel'  # Default safe option
        }
    
    @staticmethod
    def apply_correction(user_id, correction_type, params):
        """
        Apply a correction based on user choice.
        
        Args:
            user_id: User ID
            correction_type: Type of correction (overwrite, merge, cancel)
            params: Correction parameters
            
        Returns:
            dict: Result of correction
        """
        if correction_type == 'overwrite':
            # Delete existing session and create new one
            execute_query('DELETE FROM active_sessions WHERE user_id = ?', (user_id,))
            execute_insert(
                'INSERT INTO active_sessions (user_id, start_time) VALUES (?, ?)',
                (user_id, params['new_start_time'])
            )
            
            # Log manual correction
            AutoHealer._log_manual_correction(user_id, 'overwrite')
            
            return {'success': True, 'action': 'overwrite'}
        
        elif correction_type == 'cancel':
            return {'success': True, 'action': 'cancel', 'message': 'Kept existing session'}
        
        return {'success': False, 'error': 'Unknown correction type'}
    
    @staticmethod
    def _update_reliability_for_auto_close(user_id):
        """Update user reliability score for auto-close event."""
        execute_query('''
            UPDATE user_reliability 
            SET auto_closed_events = auto_closed_events + 1,
                score = MAX(0.0, score - 0.05),
                last_updated = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (user_id,))
    
    @staticmethod
    def _log_manual_correction(user_id, correction_type):
        """Log manual correction to reliability."""
        execute_query('''
            UPDATE user_reliability 
            SET manual_corrections = manual_corrections + 1,
                score = MAX(0.0, score - 0.10),
                last_updated = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (user_id,))
