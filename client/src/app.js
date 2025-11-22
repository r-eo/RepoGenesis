import React, { useState, useEffect } from 'react';
import { registerUser, loginUser, logSleep, getStats, getFriends, startSleep, endSleep } from './sleepApi';
import './index.css';
import Clock from 'react-live-clock';

// Helper for Pomodoro Countdown
const CountdownTimer = ({ minutes = 25, onComplete }) => {
    const [timeLeft, setTimeLeft] = useState(minutes * 60);

    useEffect(() => {
        if (timeLeft <= 0) {
            onComplete?.();
            return;
        }
        const timer = setInterval(() => {
            setTimeLeft(prev => prev - 1);
        }, 1000);
        return () => clearInterval(timer);
    }, [timeLeft, onComplete]);

    const m = Math.floor(timeLeft / 60);
    const s = timeLeft % 60;
    return (
        <div style={{ fontSize: '3rem', fontFamily: 'monospace', fontWeight: 'bold', color: 'var(--danger)' }}>
            {String(m).padStart(2, '0')}:{String(s).padStart(2, '0')}
        </div>
    );
};

// ... (inside Dashboard component)

// ... (keep existing state)

// ... (keep existing handleCommand, but update Pomodoro to not use setTimeout for logic if we use the component for visual, 
// actually we can keep the timeout for the system message but use the component for display)

// ... (inside return JSX, replace avatar-container content)

{/* Center: Avatar or Clock */ }
<main className="main-content">
    <div className="card avatar-container" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '300px' }}>
        {focusMode ? (
            <>
                <div style={{ fontSize: '5rem', marginBottom: '20px' }}>🍅</div>
                <CountdownTimer minutes={25} onComplete={() => {
                    setFocusMode(false);
                    showMessage("Pomodoro complete! Take a break. ☕", 'success');
                }} />
                <h2 style={{ margin: '20px 0 0' }}>Focusing...</h2>
            </>
        ) : stats.is_sleeping ? (
            <>
                <div style={{ fontSize: '4rem', color: 'var(--primary)', fontFamily: 'monospace', fontWeight: 'bold' }}>
                    <Clock format={'HH:mm:ss'} ticking={true} timezone={Intl.DateTimeFormat().resolvedOptions().timeZone} />
                </div>
                <div style={{ fontSize: '3rem', marginTop: '20px' }}>💤</div>
                <h2 style={{ margin: '20px 0 0' }}>Sleeping...</h2>
            </>
        ) : (
            <>
                <svg className={`avatar-svg ${stats.avatar_state}`} viewBox="0 0 100 100" style={{ maxWidth: '200px' }}>
                    <circle cx="50" cy="50" r="45" fill="var(--bg-body)" stroke="var(--primary)" strokeWidth="2" />
                    <circle cx="35" cy="40" r="5" fill="var(--text-main)" />
                    <circle cx="65" cy="40" r="5" fill="var(--text-main)" />
                    {stats.avatar_state === 'grumpy' ? (
                        <path d="M 30 70 Q 50 60 70 70" stroke="var(--text-main)" strokeWidth="3" fill="none" />
                    ) : (
                        <path d="M 30 60 Q 50 80 70 60" stroke="var(--text-main)" strokeWidth="3" fill="none" />
                    )}
                </svg>
                <h2 style={{ margin: 0 }}>Level {Math.floor(stats.weekly_score / 100) + 1}</h2>
                <p style={{ color: 'var(--text-muted)' }}>Keep sleeping well to level up!</p>
            </>
        )}
    </div>
</main>

// --- Theme Management ---
const useTheme = () => {
    const [theme, setTheme] = useState(localStorage.getItem('theme') || 'light');

    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }, [theme]);

    const toggleTheme = () => {
        setTheme(prev => prev === 'light' ? 'dark' : 'light');
    };

    return { theme, toggleTheme };
};

// --- Components ---

const LoginScreen = ({ onLogin }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [isRegistering, setIsRegistering] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e) => {
        if (e) e.preventDefault(); // Prevent form reload

        if (!username || !password) {
            alert('Please enter both username and password');
            return;
        }

        setIsLoading(true);
        try {
            let user;
            if (isRegistering) {
                user = await registerUser(username, password);
            } else {
                user = await loginUser(username, password);
            }
            onLogin(user);
        } catch (e) {
            console.error('Auth error:', e);
            console.error('Error response:', e.response?.data);
            alert(`Authentication failed: ${e.response?.data?.error || e.message || 'Unknown error'}`);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="card auth-container">
            <div className="auth-header">
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--primary)', marginBottom: '16px' }}>Sleep Quest</div>
                <h1 style={{ fontSize: '1.5rem', fontWeight: '400', margin: '0', color: 'var(--text-main)' }}>
                    {isRegistering ? 'Create your account' : 'Sign in'}
                </h1>
                <p style={{ fontSize: '1rem', margin: '8px 0 0', color: 'var(--text-main)' }}>
                    to continue to Sleep Quest
                </p>
            </div>
            <form className="auth-form" onSubmit={handleSubmit}>
                <div className="input-group">
                    <input
                        type="text"
                        placeholder="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        className="google-input"
                        disabled={isLoading}
                    />
                </div>
                <div className="input-group">
                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="google-input"
                        disabled={isLoading}
                    />
                </div>

                <div className="auth-actions" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '30px' }}>
                    <button
                        type="button"
                        className="btn btn-text"
                        onClick={() => setIsRegistering(!isRegistering)}
                        style={{ color: 'var(--primary)', fontWeight: '600', padding: '0' }}
                        disabled={isLoading}
                    >
                        {isRegistering ? 'Sign in instead' : 'Create account'}
                    </button>
                    <button
                        type="submit"
                        className="btn btn-primary"
                        style={{ padding: '10px 24px', borderRadius: '4px', minWidth: '80px' }}
                        disabled={isLoading}
                    >
                        {isLoading ? '...' : (isRegistering ? 'Sign up' : 'Next')}
                    </button>
                </div>
            </form>
        </div>
    );
};

const Dashboard = ({ user, onLogout, toggleTheme, theme }) => {
    const [stats, setStats] = useState(null);
    const [friends, setFriends] = useState([]);
    const [sleepInput, setSleepInput] = useState('');
    const [systemMessage, setSystemMessage] = useState(null);

    const [focusMode, setFocusMode] = useState(false);

    useEffect(() => {
        const loadData = async () => {
            const s = await getStats(user.id);
            setStats(s);
            const f = await getFriends(user.id);
            setFriends(f);
        };
        loadData();
    }, [user.id]);

    const showMessage = (text, type = 'info') => {
        setSystemMessage({ text, type });
        // Auto-hide after 5 seconds
        setTimeout(() => setSystemMessage(null), 5000);
    };

    const handleCommand = async () => {
        if (!sleepInput) return;

        const cleanInput = sleepInput.toLowerCase().trim();

        try {
            if (cleanInput === '/sleep') {
                const res = await startSleep(user.id);
                showMessage(res.message, 'success');
                const s = await getStats(user.id);
                setStats(s);
                setSleepInput('');
            } else if (cleanInput === '/wakeup') {
                const res = await endSleep(user.id);
                showMessage(res.message, 'success');
                const s = await getStats(user.id);
                setStats(s);
                setSleepInput('');
            } else if (cleanInput === '/nap') {
                // Start dynamic nap session
                const res = await startSleep(user.id);
                showMessage("Nap started! 💤 Type /wakeup when you wake up.", 'success');
                const s = await getStats(user.id);
                setStats(s);
                setSleepInput('');
            } else if (cleanInput === '/pomodoro') {
                setFocusMode(true);
                showMessage("Pomodoro started! 🍅 Focus for 25 minutes.", 'success');
                setSleepInput('');
                // Auto-turn off after 25 mins (optional visual cue)
                setTimeout(() => {
                    setFocusMode(false);
                    showMessage("Pomodoro complete! Take a break. ☕", 'success');
                }, 25 * 60 * 1000);
            } else if (cleanInput === '/break') {
                setFocusMode(false);
                showMessage("Focus mode ended.", 'info');
                setSleepInput('');
            } else if (cleanInput.startsWith('/nap ')) {
                // Manual log: /nap [minutes]
                const parts = cleanInput.split(' ');
                const mins = parts.length > 1 ? parseFloat(parts[1]) : 20;
                const hours = mins / 60;
                await logSleep(user.id, hours);
                const s = await getStats(user.id);
                setStats(s);
                setSleepInput('');
                showMessage(`Power Nap Logged: ${mins} minutes. +Generosity Bonus!`, 'success');
            } else if (cleanInput === '/motivate') {
                const quotes = [
                    "Sleep is the best meditation.",
                    "A good laugh and a long sleep are the best cures in the doctor's book.",
                    "Your future depends on your dreams, so go to sleep.",
                    "Rest is not idleness."
                ];
                const randomQuote = quotes[Math.floor(Math.random() * quotes.length)];
                showMessage(`Oracle says: "${randomQuote}"`, 'info');
                setSleepInput('');
            } else {
                const hours = parseFloat(cleanInput.replace('/sleep', '').trim());
                if (!isNaN(hours) && hours > 0 && hours <= 24) {
                    await logSleep(user.id, hours);
                    const s = await getStats(user.id);
                    setStats(s);
                    setSleepInput('');
                    showMessage(`Logged ${hours} hours.`, 'success');
                } else {
                    showMessage('Invalid command. Try /sleep, /wakeup, /nap 20, /pomodoro, /motivate', 'error');
                }
            }
        } catch (e) {
            showMessage(e.response?.data?.message || 'Command failed.', 'error');
        }
    };

    if (!stats) return <div>Loading...</div>;

    return (
        <div className="dashboard-layout">
            {/* System Message Toast */}
            {systemMessage && (
                <div className={`system-message ${systemMessage.type}`}>
                    {systemMessage.type === 'success' ? '✅ ' : systemMessage.type === 'error' ? '❌ ' : 'ℹ️ '}
                    {systemMessage.text}
                </div>
            )}

            {/* Header */}
            <header className="dash-header">
                <div className="brand-logo">Sleep Quest</div>
                <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
                    <div style={{ fontSize: '1.2rem', fontFamily: 'monospace', fontWeight: 'bold', color: 'var(--text-main)' }}>
                        <Clock format={'HH:mm:ss'} ticking={true} timezone={Intl.DateTimeFormat().resolvedOptions().timeZone} />
                    </div>
                    <button className="theme-toggle" onClick={toggleTheme} title="Toggle Theme">
                        {theme === 'light' ? '🌙' : '☀️'}
                    </button>
                    {stats.reliability && (
                        <div
                            className={`reliability-badge grade-${stats.reliability.grade.toLowerCase().replace('+', 'plus')}`}
                            title={`Reliability: ${stats.reliability.description}\nScore: ${stats.reliability.score}`}
                        >
                            {stats.reliability.grade}
                        </div>
                    )}
                    <span>{user.username}</span>
                    <button className="btn btn-outline" onClick={onLogout} style={{ padding: '5px 10px', fontSize: '0.8rem' }}>Logout</button>
                </div>
            </header>

            {/* Left Sidebar: Stats */}
            <aside className="sidebar-left">
                <div className="card flex-grow">
                    <h3 style={{ marginTop: 0, color: 'var(--primary)' }}>Daily Stats</h3>
                    <div className="stat-row">
                        <span className="stat-label">Sleep Debt</span>
                        <span className="stat-value" style={{ color: stats.debt > 0 ? 'var(--danger)' : 'var(--success)' }}>
                            {stats.debt} hrs
                        </span>
                    </div>
                    <div className="stat-row">
                        <span className="stat-label">Weekly XP</span>
                        <span className="stat-value">{stats.weekly_score}</span>
                    </div>
                    <div className="stat-row">
                        <span className="stat-label">Status</span>
                        <span className="stat-value" style={{ textTransform: 'capitalize' }}>
                            {focusMode ? 'Focusing 🍅' : (stats.is_sleeping ? 'Sleeping 💤' : stats.avatar_state)}
                        </span>
                    </div>
                </div>

                <div className="card" style={{ background: 'var(--bg-input)', border: 'none' }}>
                    <h4 style={{ margin: '0 0 10px 0', fontSize: '0.9rem' }}>Motivation</h4>
                    <p style={{ margin: 0, fontSize: '0.9rem', fontStyle: 'italic', color: 'var(--text-muted)' }}>
                        "{stats.tip}"
                    </p>
                </div>
            </aside>

            {/* Center: Avatar or Clock */}
            <main className="main-content">
                <div className="card avatar-container" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '300px' }}>
                    {focusMode ? (
                        <>
                            <div style={{ fontSize: '5rem', marginBottom: '20px' }}>🍅</div>
                            <CountdownTimer minutes={25} onComplete={() => {
                                setFocusMode(false);
                                showMessage("Pomodoro complete! Take a break. ☕", 'success');
                            }} />
                            <h2 style={{ margin: '20px 0 0' }}>Focusing...</h2>
                        </>
                    ) : stats.is_sleeping ? (
                        <>
                            <div style={{ fontSize: '4rem', color: 'var(--primary)', fontFamily: 'monospace', fontWeight: 'bold' }}>
                                <Clock format={'HH:mm:ss'} ticking={true} timezone={Intl.DateTimeFormat().resolvedOptions().timeZone} />
                            </div>
                            <div style={{ fontSize: '3rem', marginTop: '20px' }}>💤</div>
                            <h2 style={{ margin: '20px 0 0' }}>Sleeping...</h2>
                        </>
                    ) : (
                        <>
                            <svg className={`avatar-svg ${stats.avatar_state}`} viewBox="0 0 100 100" style={{ maxWidth: '200px' }}>
                                <circle cx="50" cy="50" r="45" fill="var(--bg-body)" stroke="var(--primary)" strokeWidth="2" />
                                <circle cx="35" cy="40" r="5" fill="var(--text-main)" />
                                <circle cx="65" cy="40" r="5" fill="var(--text-main)" />
                                {stats.avatar_state === 'grumpy' ? (
                                    <path d="M 30 70 Q 50 60 70 70" stroke="var(--text-main)" strokeWidth="3" fill="none" />
                                ) : (
                                    <path d="M 30 60 Q 50 80 70 60" stroke="var(--text-main)" strokeWidth="3" fill="none" />
                                )}
                            </svg>
                            <h2 style={{ margin: 0 }}>Level {Math.floor(stats.weekly_score / 100) + 1}</h2>
                            <p style={{ color: 'var(--text-muted)' }}>Keep sleeping well to level up!</p>
                        </>
                    )}
                </div>
            </main>

            {/* Right Sidebar: Friends */}
            <aside className="sidebar-right">
                <div className="card" style={{ height: '100%' }}>
                    <h3 style={{ marginTop: 0, color: 'var(--primary)' }}>Debt Leaderboard</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                        {friends.map((friend, index) => (
                            <div key={friend.id} className="friend-item">
                                <div className="friend-avatar">{index + 1}</div>
                                <div style={{ flex: 1 }}>
                                    <div style={{ fontWeight: 600 }}>{friend.username}</div>
                                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                                        Debt: <span style={{ color: friend.debt > 0 ? 'var(--danger)' : 'var(--success)' }}>{friend.debt} hrs</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                        {friends.length === 0 && <div style={{ color: 'var(--text-muted)' }}>No friends yet.</div>}
                    </div>
                </div>
            </aside>

            {/* Bottom: Command Bar */}
            <div className="command-bar-container" style={{ gridColumn: '1 / -1', gridRow: '3 / 4', marginTop: '20px' }}>
                <div className="command-bar">
                    <input
                        type="text"
                        placeholder="Enter command (/sleep, /wakeup, /nap 20) or hours..."
                        value={sleepInput}
                        onChange={(e) => setSleepInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleCommand()}
                        style={{ flex: 1 }}
                    />
                    <button className="btn btn-primary" onClick={handleCommand}>Execute</button>
                </div>
            </div>
        </div>
    );
};

function App() {
    const [user, setUser] = useState(null);
    const { theme, toggleTheme } = useTheme();

    return (
        <>
            {!user ? (
                <LoginScreen onLogin={setUser} />
            ) : (
                <Dashboard user={user} onLogout={() => setUser(null)} toggleTheme={toggleTheme} theme={theme} />
            )}
        </>
    );
}

export default App;
