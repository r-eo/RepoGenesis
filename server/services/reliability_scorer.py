"""
Reliability Scorer Service
Tracks and calculates user reliability scores based on sleep tracking behavior.
"""
from services.db_manager import execute_query, execute_insert
from datetime import datetime

class ReliabilityScorer:
    # Score adjustments
    PERFECT_ENTRY_BONUS = 0.02
    AUTO_CLOSE_PENALTY = -0.05
    CONFLICT_PENALTY = -0.10
    MANUAL_CORRECTION_PENALTY = -0.10
    CONSISTENT_PATTERN_BONUS = 0.01
    
    # Score bounds
    MIN_SCORE = 0.0
    MAX_SCORE = 1.0
    DEFAULT_SCORE = 0.75
    
    @staticmethod
    def update_score(user_id, event_type, reliability_impact=None):
        """
        Update user reliability score based on an event.
        
        Args:
            user_id: User ID
            event_type: Type of event
            reliability_impact: Pre-calculated impact (optional)
            
        Returns:
            dict: Updated reliability data
        """
        # Ensure user has reliability record
        ReliabilityScorer._ensure_reliability_record(user_id)
        
        # Calculate impact if not provided
        if reliability_impact is None:
            reliability_impact = ReliabilityScorer._calculate_impact(event_type)
        
        # Update score
        execute_query('''
            UPDATE user_reliability 
            SET score = MAX(?, MIN(?, score + ?)),
                total_events = total_events + 1,
                last_updated = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (ReliabilityScorer.MIN_SCORE, ReliabilityScorer.MAX_SCORE, reliability_impact, user_id))
        
        return ReliabilityScorer.get_user_reliability(user_id)
    
    @staticmethod
    def get_user_reliability(user_id):
        """
        Get user reliability statistics.
        
        Args:
            user_id: User ID
            
        Returns:
            dict: Reliability data
        """
        ReliabilityScorer._ensure_reliability_record(user_id)
        
        reliability = execute_query(
            'SELECT * FROM user_reliability WHERE user_id = ?',
            (user_id,),
            one=True
        )
        
        if not reliability:
            return {
                'score': ReliabilityScorer.DEFAULT_SCORE,
                'total_events': 0,
                'auto_closed_events': 0,
                'manual_corrections': 0,
                'grade': 'C',
                'description': 'New user'
            }
        
        score = reliability['score']
        grade = ReliabilityScorer._get_grade(score)
        description = ReliabilityScorer._get_description(score)
        
        return {
            'score': round(score, 2),
            'total_events': reliability['total_events'],
            'auto_closed_events': reliability['auto_closed_events'],
            'manual_corrections': reliability['manual_corrections'],
            'grade': grade,
            'description': description,
            'last_updated': reliability['last_updated']
        }
    
    @staticmethod
    def _ensure_reliability_record(user_id):
        """Ensure user has a reliability record."""
        execute_query('''
            INSERT OR IGNORE INTO user_reliability (user_id, score, total_events)
            VALUES (?, ?, ?)
        ''', (user_id, ReliabilityScorer.DEFAULT_SCORE, 0))
    
    @staticmethod
    def _calculate_impact(event_type):
        """Calculate reliability impact for event type."""
        impact_map = {
            'SLEEP_START': ReliabilityScorer.PERFECT_ENTRY_BONUS,
            'SLEEP_END': ReliabilityScorer.PERFECT_ENTRY_BONUS,
            'NAP_START': ReliabilityScorer.PERFECT_ENTRY_BONUS,
            'NAP_END': ReliabilityScorer.PERFECT_ENTRY_BONUS,
            'MANUAL_PERIOD': ReliabilityScorer.PERFECT_ENTRY_BONUS * 0.5,
            'AUTO_CLOSE': ReliabilityScorer.AUTO_CLOSE_PENALTY,
            'ERROR_CONFLICT': ReliabilityScorer.CONFLICT_PENALTY,
        }
        return impact_map.get(event_type, 0.0)
    
    @staticmethod
    def _get_grade(score):
        """Convert score to letter grade."""
        if score >= 0.90:
            return 'A+'
        elif score >= 0.85:
            return 'A'
        elif score >= 0.80:
            return 'B+'
        elif score >= 0.75:
            return 'B'
        elif score >= 0.70:
            return 'C+'
        elif score >= 0.60:
            return 'C'
        elif score >= 0.50:
            return 'D'
        else:
            return 'F'
    
    @staticmethod
    def _get_description(score):
        """Get description for score level."""
        if score >= 0.90:
            return 'Excellent - Highly reliable sleep tracking'
        elif score >= 0.80:
            return 'Good - Consistent sleep tracking'
        elif score >= 0.70:
            return 'Fair - Some inconsistencies'
        elif score >= 0.60:
            return 'Poor - Frequent auto-corrections needed'
        else:
            return 'Very Poor - Many tracking errors'
    
    @staticmethod
    def check_consistency_bonus(user_id):
        """
        Check if user deserves consistency bonus.
        Awards bonus for 7+ consecutive days of proper tracking.
        
        Args:
            user_id: User ID
            
        Returns:
            bool: Whether bonus was awarded
        """
        # Get recent events (last 7 days)
        recent_events = execute_query('''
            SELECT event_type, timestamp 
            FROM sleep_events 
            WHERE user_id = ? 
            AND timestamp >= datetime('now', '-7 days')
            ORDER BY timestamp DESC
        ''', (user_id,))
        
        # Check for consistent pattern (no AUTO_CLOSE events)
        auto_closes = [e for e in recent_events if e['event_type'] == 'AUTO_CLOSE']
        
        if len(recent_events) >= 14 and len(auto_closes) == 0:  # At least 7 sleep cycles
            # Award bonus
            execute_query('''
                UPDATE user_reliability 
                SET score = MIN(?, score + ?),
                    last_updated = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (ReliabilityScorer.MAX_SCORE, ReliabilityScorer.CONSISTENT_PATTERN_BONUS, user_id))
            return True
        
        return False
