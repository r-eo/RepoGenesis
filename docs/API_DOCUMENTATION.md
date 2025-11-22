# Sleep Quest API Documentation

## Base URL
```
http://localhost:5000/api
```

---

## Table of Contents
1. [Authentication](#authentication)
2. [Sleep Tracking](#sleep-tracking)
3. [Social Features](#social-features)
4. [Reliability System](#reliability-system)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)

---

## Authentication

### Register User
Create a new user account.

**Endpoint:** `POST /auth/register`

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "username": "johndoe"
}
```

**Errors:**
- `400 Bad Request` - Missing username or password
- `409 Conflict` - Username already exists

---

### Login User
Authenticate an existing user.

**Endpoint:** `POST /auth/login`

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "johndoe"
}
```

**Errors:**
- `400 Bad Request` - Missing credentials
- `401 Unauthorized` - Invalid username or password

---

## Sleep Tracking

### Start Sleep Session
Begin tracking a sleep session.

**Endpoint:** `POST /sleep/start`

**Request Body:**
```json
{
  "user_id": 1
}
```

**Response (200 OK):**
```json
{
  "message": "Sleep timer started. Goodnight!",
  "start_time": "2025-11-22T06:00:00+05:30",
  "reliability": {
    "score": 0.77,
    "grade": "B",
    "description": "Good - Consistent sleep tracking",
    "total_events": 10,
    "auto_closed_events": 0,
    "manual_corrections": 0
  }
}
```

**Auto-Healing:**
If a previous session exists:
```json
{
  "message": "Previous session auto-closed. New session started.",
  "auto_closed": {
    "start_time": "2025-11-21T22:00:00+05:30",
    "end_time": "2025-11-22T06:00:00+05:30",
    "duration_hours": 8.0,
    "reason": "Missing wakeup"
  },
  "warning": "You forgot to use /wakeup. This affects your reliability score."
}
```

**Errors:**
- `400 Bad Request` - Missing user_id

---

### End Sleep Session
End the current sleep session and log sleep.

**Endpoint:** `POST /sleep/end`

**Request Body:**
```json
{
  "user_id": 1
}
```

**Response (200 OK):**
```json
{
  "message": "Good morning! Logged 7.5 hours of sleep.",
  "hours": 7.5,
  "reliability": {
    "score": 0.79,
    "grade": "B",
    "description": "Good - Consistent sleep tracking"
  }
}
```

**Errors:**
- `400 Bad Request` - Missing user_id or invalid duration
- `404 Not Found` - No active sleep session

**Validation:**
- Maximum duration: 24 hours
- Auto-closes if > 24 hours

---

### Log Manual Sleep
Manually log sleep hours for a specific date.

**Endpoint:** `POST /sleep/log`

**Request Body:**
```json
{
  "user_id": 1,
  "hours": 8.0,
  "date": "2025-11-22"  // Optional, defaults to today
}
```

**Response (201 Created):**
```json
{
  "message": "Sleep logged successfully",
  "reliability": {
    "score": 0.76,
    "grade": "B+"
  }
}
```

**Validation Rules:**
- `hours` must be > 0
- `hours` must be ≤ 12 (manual limit)
- Cannot overlap with existing logs

**Errors:**
- `400 Bad Request` - Invalid duration or missing data
- `409 Conflict` - Overlap detected

**Conflict Response (409):**
```json
{
  "error": "Overlap detected",
  "error_code": "CONFLICT_DETECTED",
  "conflicts": [
    {
      "type": "existing_log",
      "date": "2025-11-22",
      "hours": 7.5,
      "message": "Overlaps with existing sleep log on 2025-11-22"
    }
  ]
}
```

---

### Get User Stats
Retrieve comprehensive sleep statistics for a user.

**Endpoint:** `GET /sleep/stats/<user_id>`

**Response (200 OK):**
```json
{
  "debt": 2.5,
  "avatar_state": "neutral",
  "weekly_score": 85,
  "fact": "Adults need 7-9 hours of sleep per night.",
  "tip": "Try going to bed at the same time every night.",
  "is_sleeping": false,
  "reliability": {
    "score": 0.77,
    "grade": "B",
    "description": "Good - Consistent sleep tracking",
    "total_events": 15,
    "auto_closed_events": 1,
    "manual_corrections": 0,
    "last_updated": "2025-11-22T06:00:00"
  }
}
```

**Fields:**
- `debt` (float): Hours of sleep debt (positive = behind, negative = ahead)
- `avatar_state` (string): "glowing", "neutral", or "grumpy"
- `weekly_score` (int): XP score for the week (0-100)
- `fact` (string): Random sleep fact
- `tip` (string): Personalized tip based on avatar state
- `is_sleeping` (boolean): Whether user has an active session
- `reliability` (object): Reliability score details

---

### Validate Command
Pre-validate a sleep command without executing it.

**Endpoint:** `POST /sleep/validate`

**Request Body:**
```json
{
  "user_id": 1,
  "command_type": "manual_log",  // or "sleep_start", "nap_manual"
  "params": {
    "hours": 15  // Example: invalid duration
  }
}
```

**Response (200 OK):**
```json
{
  "valid": false,
  "errors": [
    "Manual sleep cannot exceed 12 hours"
  ],
  "warnings": [],
  "conflicts": null
}
```

**Command Types:**
- `sleep_start` - Starting a sleep session
- `sleep_end` - Ending a sleep session
- `nap_start` - Starting a nap
- `nap_manual` - Manual nap log
- `manual_log` - Manual sleep log

---

### Resolve Conflict
Handle sleep log conflicts (overlaps).

**Endpoint:** `POST /sleep/resolve-conflict`

**Request Body:**
```json
{
  "user_id": 1,
  "resolution": "overwrite",  // or "merge", "cancel"
  "params": {
    "new_start_time": "2025-11-22T22:00:00+05:30"
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "action": "overwrite"
}
```

**Resolution Options:**
- `overwrite` - Replace existing session with new one
- `merge` - Combine both sessions (future feature)
- `cancel` - Keep existing, discard new

---

### Get Reliability Score
Get detailed reliability statistics for a user.

**Endpoint:** `GET /sleep/reliability/<user_id>`

**Response (200 OK):**
```json
{
  "score": 0.77,
  "total_events": 20,
  "auto_closed_events": 2,
  "manual_corrections": 0,
  "grade": "B",
  "description": "Good - Consistent sleep tracking",
  "last_updated": "2025-11-22T06:00:00"
}
```

---

## Social Features

### Get Friends List
Retrieve user's friends with their sleep debt (leaderboard).

**Endpoint:** `GET /social/friends/<user_id>`

**Response (200 OK):**
```json
[
  {
    "id": 2,
    "username": "alice",
    "debt": -1.5,
    "avatar_state": "glowing"
  },
  {
    "id": 3,
    "username": "bob",
    "debt": 2.0,
    "avatar_state": "neutral"
  },
  {
    "id": 1,
    "username": "johndoe",
    "debt": 4.5,
    "avatar_state": "grumpy"
  }
]
```

**Sorting:** Friends are sorted by debt (ascending), so best sleepers appear first.

---

## Reliability System

### Event Types
The system tracks these event types:

| Event Type | Description | Reliability Impact |
|------------|-------------|--------------------|
| `SLEEP_START` | Started sleep session | +0.02 |
| `SLEEP_END` | Ended sleep session | +0.02 |
| `NAP_START` | Started nap | +0.02 |
| `NAP_END` | Ended nap | +0.02 |
| `MANUAL_PERIOD` | Manual sleep log | +0.01 |
| `AUTO_CLOSE` | Auto-closed session | -0.05 |
| `ERROR_CONFLICT` | Conflict detected | -0.10 |

### Reliability Calculation
```python
# Starting score
score = 0.75

# Perfect sleep cycle
score += 0.02  # /sleep
score += 0.02  # /wakeup
# New score: 0.79

# Forgot wakeup (auto-closed)
score -= 0.05
# New score: 0.74

# Bounds
score = max(0.0, min(1.0, score))
```

---

## Error Handling

### Standard Error Response
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE"  // Optional
}
```

### HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful request |
| 201 | Created | Resource created (e.g., sleep log) |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Invalid credentials |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Data conflict (e.g., overlap) |
| 500 | Internal Server Error | Server-side error |

### Error Codes

| Code | Description |
|------|-------------|
| `INVALID_DURATION` | Sleep duration outside valid range |
| `CONFLICT_DETECTED` | Overlapping sleep sessions |
| `NO_ACTIVE_SESSION` | No sleep session to end |
| `MISSING_DATA` | Required fields missing |

---

## Rate Limiting

**Current Status:** No rate limiting implemented

**Recommended for Production:**
- 100 requests per minute per user
- 1000 requests per hour per IP
- Implement using Flask-Limiter

---

## Data Models

### User
```typescript
interface User {
  id: number;
  username: string;
  password: string;  // Hashed
  timezone?: string;  // Future feature
}
```

### Sleep Log
```typescript
interface SleepLog {
  id: number;
  user_id: number;
  date: string;  // ISO date (YYYY-MM-DD)
  hours: number;
}
```

### Active Session
```typescript
interface ActiveSession {
  user_id: number;
  start_time: string;  // ISO 8601 timestamp
}
```

### Sleep Event
```typescript
interface SleepEvent {
  id: number;
  user_id: number;
  event_type: 'SLEEP_START' | 'SLEEP_END' | 'NAP_START' | 'NAP_END' | 'MANUAL_PERIOD' | 'AUTO_CLOSE';
  timestamp: string;  // ISO 8601
  duration_seconds?: number;
  metadata?: string;  // JSON
  reliability_impact: number;
  created_at: string;
}
```

### User Reliability
```typescript
interface UserReliability {
  user_id: number;
  score: number;  // 0.0 - 1.0
  total_events: number;
  auto_closed_events: number;
  manual_corrections: number;
  last_updated: string;
}
```

---

## Example Workflows

### Complete Sleep Cycle
```javascript
// 1. Start sleep
POST /api/sleep/start
{
  "user_id": 1
}

// 2. Wait (user sleeps)...

// 3. End sleep
POST /api/sleep/end
{
  "user_id": 1
}

// 4. Check stats
GET /api/sleep/stats/1
```

### Manual Sleep Log
```javascript
// 1. Validate first (optional)
POST /api/sleep/validate
{
  "user_id": 1,
  "command_type": "manual_log",
  "params": { "hours": 8 }
}

// 2. If valid, log sleep
POST /api/sleep/log
{
  "user_id": 1,
  "hours": 8,
  "date": "2025-11-22"
}
```

### Handle Conflict
```javascript
// 1. Attempt to log sleep
POST /api/sleep/log
{
  "user_id": 1,
  "hours": 8,
  "date": "2025-11-22"
}

// 2. Receive conflict error (409)
{
  "error": "Overlap detected",
  "conflicts": [...]
}

// 3. Resolve conflict
POST /api/sleep/resolve-conflict
{
  "user_id": 1,
  "resolution": "cancel"
}
```

---

## Testing with cURL

### Register
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'
```

### Start Sleep
```bash
curl -X POST http://localhost:5000/api/sleep/start \
  -H "Content-Type: application/json" \
  -d '{"user_id":1}'
```

### Get Stats
```bash
curl http://localhost:5000/api/sleep/stats/1
```

---

## Changelog

### Version 2.0 (Current)
- ✅ Event-based validation system
- ✅ Auto-healing for stale sessions
- ✅ Reliability scoring (A-F grades)
- ✅ Conflict detection and resolution
- ✅ Enhanced error messages

### Version 1.0
- Basic sleep logging
- Manual sleep tracking
- Simple debt calculation
- Friend leaderboard

---

**API Version:** 2.0  
**Last Updated:** 2025-11-22  
**Base URL:** `http://localhost:5000/api`
