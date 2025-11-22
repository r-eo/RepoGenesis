# Sleep Quest - User Guide

## Welcome to Sleep Quest! 🌙

Sleep Quest is a gamified sleep tracking application that helps you maintain healthy sleep habits through Discord-style commands, reliability scoring, and social features.

---

## Table of Contents
1. [Getting Started](#getting-started)
2. [Commands Reference](#commands-reference)
3. [Understanding Your Stats](#understanding-your-stats)
4. [Reliability System](#reliability-system)
5. [Social Features](#social-features)
6. [Tips & Best Practices](#tips--best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Creating Your Account

1. Navigate to the Sleep Quest application
2. Click **"Create account"**
3. Enter your desired username and password
4. Click **"Sign up"**
5. You'll be logged in automatically with a default reliability score of **B (0.75)**

### Your Dashboard

Once logged in, you'll see three main sections:

**Left Sidebar - Daily Stats:**
- Sleep Debt (hours behind/ahead)
- Weekly XP Score
- Current Status (Awake/Sleeping)

**Center - Avatar:**
- Your sleep avatar changes based on your sleep debt
- 😊 **Glowing** (debt ≤ 0): Well-rested
- 😐 **Neutral** (0 < debt ≤ 3): Slightly tired
- 😫 **Grumpy** (debt > 3): Sleep deprived

**Right Sidebar - Social:**
- Debt Leaderboard (compare with friends)
- Motivation tips based on your state

---

## Commands Reference

All commands are entered in the command bar at the bottom of the dashboard.

### Sleep Tracking Commands

#### `/sleep`
**Purpose:** Start a sleep session timer  
**Usage:** Type `/sleep` and click Execute  
**What Happens:**
- Starts tracking your sleep time
- Status changes to "Sleeping 💤"
- Creates a `SLEEP_START` event
- Adds +0.02 to reliability score

**Example:**
```
> /sleep
✅ Sleep timer started. Goodnight!
```

#### `/wakeup`
**Purpose:** End your sleep session  
**Usage:** Type `/wakeup` and click Execute  
**What Happens:**
- Calculates total sleep duration
- Logs sleep to your history
- Updates sleep debt
- Adds +0.02 to reliability score
- Status returns to "Awake"

**Example:**
```
> /wakeup
✅ Good morning! Logged 7.5 hours of sleep.
```

#### `/sleep <hours>`
**Purpose:** Manually log sleep hours  
**Usage:** Type `/sleep 8` (for 8 hours)  
**Validation:**
- Maximum: 12 hours
- Minimum: Must be positive
- Cannot overlap with existing logs

**Example:**
```
> /sleep 8
✅ Logged 8 hours.
```

#### `/nap`
**Purpose:** Start a nap timer  
**Usage:** Type `/nap` and click Execute  
**What Happens:**
- Similar to `/sleep` but for short rest periods
- Use `/wakeup` to end the nap
- Nap duration is added to daily sleep total

**Example:**
```
> /nap
✅ Nap timer started.
```

#### `/nap <minutes>`
**Purpose:** Manually log a nap  
**Usage:** Type `/nap 30` (for 30 minutes)  
**Validation:**
- Maximum: 180 minutes (3 hours)
- Minimum: Must be positive

**Example:**
```
> /nap 20
✅ Logged 20-minute nap.
```

#### `/motivate`
**Purpose:** Get a random sleep tip  
**Usage:** Type `/motivate` and click Execute  
**What Happens:**
- Displays a personalized tip based on your avatar state
- Tips are tailored to help improve your sleep

**Example:**
```
> /motivate
ℹ️ Try going to bed at the same time every night!
```

---

## Understanding Your Stats

### Sleep Debt
**What It Is:** The difference between your ideal sleep (8 hours/night) and actual sleep over the last 7 days.

**Calculation:**
```
Sleep Debt = (8 hours × 7 days) - (Your Total Sleep)
```

**Interpretation:**
- **Negative debt** (e.g., -2h): You're ahead! Well done! 😊
- **0-3 hours**: Slightly behind, manageable 😐
- **>3 hours**: Significantly sleep deprived 😫

### Weekly XP Score
**What It Is:** A score based on your sleep consistency over the past 7 days.

**How It's Calculated:**
- Perfect sleep (8h/night): 100 XP per day
- Less sleep: Proportionally lower XP
- Negative debt: Bonus XP

**Example:**
- 7 days × 8 hours = 56 hours total
- If you slept 50 hours: ~89 XP

### Status Indicator
Shows your current state:
- **Awake** - Normal state
- **Sleeping 💤** - Active sleep/nap session

---

## Reliability System

### What Is Reliability?
Your reliability score measures how accurately and consistently you track your sleep. It's displayed as a **colored badge** next to your username.

### Scoring System

**Starting Score:** 0.75 (B grade)

**How to Improve (+):**
- Complete sleep cycles properly: +0.02 per event
- Use `/sleep` and `/wakeup` correctly: +0.02 each
- Manual logs: +0.01
- 7+ days without auto-corrections: +0.01 bonus

**Penalties (-):**
- Forgot `/wakeup` (auto-closed): -0.05
- Overlapping sessions: -0.10
- Invalid entries: -0.10

### Grade Scale

| Grade | Score Range | Color | Meaning |
|-------|-------------|-------|---------|
| **A+** | 0.90 - 1.00 | 🟢 Green | Excellent - Highly reliable |
| **A** | 0.85 - 0.89 | 🟢 Green | Excellent |
| **B+** | 0.80 - 0.84 | 🔵 Blue | Good |
| **B** | 0.75 - 0.79 | 🔵 Blue | Good - Consistent |
| **C+** | 0.70 - 0.74 | 🟠 Orange | Fair |
| **C** | 0.60 - 0.69 | 🟠 Orange | Fair - Some inconsistencies |
| **D** | 0.50 - 0.59 | 🔴 Red | Poor |
| **F** | 0.00 - 0.49 | 🔴 Red | Very Poor |

**Hover over your badge** to see detailed stats:
- Current score
- Total events logged
- Auto-closed sessions
- Manual corrections

---

## Social Features

### Debt Leaderboard
Compare your sleep debt with friends:
- Lower debt = Better ranking
- Negative debt (surplus) ranks highest
- Updates in real-time

**How to Add Friends:**
(Feature coming soon - currently shows mock data)

---

## Tips & Best Practices

### For Best Results

1. **Use `/sleep` and `/wakeup`** instead of manual logging
   - More accurate
   - Better reliability score
   - Automatic duration calculation

2. **Don't Forget `/wakeup`**
   - Sessions auto-close after 24 hours
   - Penalty to reliability score
   - May lose accurate sleep data

3. **Log Sleep Daily**
   - Keeps debt calculation accurate
   - Maintains consistency bonus
   - Better avatar state

4. **Avoid Overlapping Logs**
   - System will detect conflicts
   - You'll need to resolve manually
   - Penalty to reliability score

### Common Mistakes to Avoid

❌ **Logging unrealistic sleep** (e.g., 15 hours)
- System rejects manual logs > 12 hours
- Auto-sleep sessions max 24 hours

❌ **Starting new sleep without ending previous**
- Previous session auto-closes
- Reliability penalty applied

❌ **Logging sleep in the future**
- System validates timestamps
- Only past/present allowed

---

## Troubleshooting

### "Authentication failed" on signup
**Solution:** 
- Ensure backend server is running
- Check CORS settings
- Try refreshing the page

### "No active sleep session" when using `/wakeup`
**Cause:** You haven't used `/sleep` or `/nap` first  
**Solution:** Use `/sleep` to start a session before `/wakeup`

### "Overlap detected" error
**Cause:** You're trying to log sleep for a date that already has a log  
**Solution:** 
- Check your existing logs
- Use a different date
- Delete conflicting log (if incorrect)

### Reliability score decreased
**Cause:** Auto-correction or conflict occurred  
**Solution:**
- Review your recent commands
- Use `/sleep` and `/wakeup` properly
- Avoid forgetting to wake up

### Avatar not changing
**Cause:** Sleep debt hasn't crossed threshold  
**Thresholds:**
- Glowing: debt ≤ 0
- Neutral: 0 < debt ≤ 3
- Grumpy: debt > 3

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Enter` in command bar | Execute command |
| `Esc` | Clear command bar |

---

## Privacy & Data

- Your sleep data is stored locally in the application database
- Passwords are hashed using Werkzeug security
- No data is shared with third parties
- You can request data deletion by contacting support

---

## Need Help?

If you encounter issues not covered in this guide:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review the [Commands Reference](#commands-reference)
3. Contact support with:
   - Your username
   - Description of the issue
   - Screenshot (if applicable)

---

**Happy Sleeping! 🌙✨**

*Version 2.0 - Enhanced Validation System*
