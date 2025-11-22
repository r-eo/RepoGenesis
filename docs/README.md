# Sleep Quest Documentation

Welcome to the Sleep Quest documentation! This directory contains comprehensive guides for users, developers, and system administrators.

---

## 📚 Documentation Index

### For Users
- **[User Guide](./USER_GUIDE.md)** - Complete guide to using Sleep Quest
  - Getting started
  - Commands reference
  - Understanding stats
  - Reliability system
  - Troubleshooting

### For Developers
- **[API Documentation](./API_DOCUMENTATION.md)** - Complete API reference
  - Authentication endpoints
  - Sleep tracking endpoints
  - Social features
  - Error handling
  - Data models
  - Example workflows

### For Deployment
- **[Deployment Guide](./DEPLOYMENT_GUIDE.md)** - Production deployment instructions
  - Local development setup
  - Traditional server deployment
  - Docker deployment
  - Cloud platform deployment
  - Environment configuration
  - Monitoring & maintenance

---

## Quick Start

### For Users
1. Read the [User Guide](./USER_GUIDE.md#getting-started)
2. Create an account
3. Start with `/sleep` command
4. Check your reliability badge!

### For Developers
1. Read the [API Documentation](./API_DOCUMENTATION.md)
2. Test endpoints with cURL or Postman
3. Review data models and error codes
4. Build your integration

### For Deployment
1. Follow the [Deployment Guide](./DEPLOYMENT_GUIDE.md#local-development-setup) for local setup
2. Choose deployment option (Traditional/Docker/Cloud)
3. Configure environment variables
4. Deploy and monitor

---

## System Architecture

```
┌─────────────────┐
│   React Client  │  (Port 3000)
│   (Frontend)    │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│   Flask API     │  (Port 5000)
│   (Backend)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SQLite/DB      │
│  (Database)     │
└─────────────────┘
```

---

## Key Features

### ✅ Implemented
- Event-based validation system
- Auto-healing for stale sessions
- Reliability scoring (A-F grades)
- Conflict detection and resolution
- Discord-style commands
- Real-time status updates
- Social leaderboard

### 🔄 Planned
- Sleep streaks with badges
- Enhanced sleep debt analysis
- Timezone handling
- Anomaly detection
- Mobile app support

---

## Technology Stack

### Frontend
- React 18.2.0
- Axios 1.4.0
- Modern CSS (Flexbox/Grid)

### Backend
- Python 3.8+
- Flask 2.3.0
- Flask-CORS 4.0.0
- Werkzeug 2.3.0

### Database
- SQLite (development)
- PostgreSQL (production recommended)

---

## Support & Contributing

### Getting Help
1. Check the [User Guide](./USER_GUIDE.md#troubleshooting)
2. Review [API Documentation](./API_DOCUMENTATION.md#error-handling)
3. Check [Deployment Guide](./DEPLOYMENT_GUIDE.md#troubleshooting)
4. Open an issue on GitHub

### Contributing
1. Fork the repository
2. Create a feature branch
3. Follow code style guidelines
4. Write tests
5. Submit pull request

---

## Version History

### v2.0 (Current) - Enhanced Validation System
- Event-based architecture
- Reliability scoring
- Auto-healing mechanisms
- Improved error handling

### v1.0 - Initial Release
- Basic sleep tracking
- Manual logging
- Simple debt calculation
- Friend leaderboard

---

## License

MIT License - See LICENSE file for details

---

## Contact

- **GitHub:** [github.com/yourusername/sleep-quest](https://github.com/yourusername/sleep-quest)
- **Issues:** [github.com/yourusername/sleep-quest/issues](https://github.com/yourusername/sleep-quest/issues)
- **Email:** support@sleepquest.app

---

**Last Updated:** 2025-11-22  
**Documentation Version:** 2.0
