# XParky Tracker
## Experience Points (XP) Tracking System for Data and ML Cadets

XParkyTracker is a Streamlit-based web application designed to track and manage experience points (XP) for Data and Machine Learning Cadets participating in Google Developer Group On Campus PUP's learning programs.

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Development](#development)

## Overview
XParkyTracker simplifies the process of tracking learner progress and achievements in the Data and ML learning path. The application helps mentors and organizers monitor cadet progress through various activities, certifications, and projects.

### Key Objectives
- Track cadet progress through learning milestones
- Monitor completion of certifications and badges
- Calculate and manage experience points
- Provide insights into learning progress
- Facilitate assessment of learning achievements

## Features

### XP Tracking
- **Certificate Tracking**: Record and validate completed certificates
- **Badge Management**: Track earned badges from learning platforms
- **Project Submissions**: Monitor and grade project submissions
- **Point Calculation**: Automated XP calculation based on achievements
- **Progress Dashboard**: Visual representation of cadet progress

### Administrative Features
- **Achievement Verification**: Validate submitted certificates and badges
- **Points Configuration**: Customize point values for different achievements
- **Progress Reports**: Generate individual and group progress reports

## Technology Stack
- **Frontend & Backend**: Streamlit
- **Programming Language**: Python 3.9
- **Data Processing**: Pandas 
- **Development Environment**: Dev Container support
- **Version Control**: Git

## Project Structure
```
XParkyTracker/
├── .devcontainer/       # Development container configuration
├── .streamlit/          # Streamlit configuration
├── assets/             # Static assets and resources
├── src/                # Source code directory
│   ├── __init__.py
│   ├── points.py       # XP calculation logic
│   ├── validators.py   # Certificate/badge validation
│   └── utils.py        # Utility functions
├── app.py              # Main Streamlit application
└── requirements.txt    # Python dependencies
```

## Installation

### Prerequisites
- Python 3.9
- Git
- Google Cloud credentials (for Google Sheets integration)

### Local Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/username/XParkyTracker.git
   cd XParkyTracker
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure Google Sheets credentials:
   - Reach out to me for credentials

## Usage

### Starting the Application
```bash
streamlit run app.py
```

### For Cadets
1. Submit certificates and badges through the interface
2. View current XP status
3. Track progress towards learning goals
4. Access performance insights

### For Administrators
1. Verify submitted achievements
2. Monitor cadet progress
3. Generate progress reports
4. Manage point configurations

## Development

### Point System Configuration
Points are awarded for different achievements:
- Certificates: 100
- Badges: 100
- Projects: 150
- Attendance/Answers Eval Forms: 200

### Adding New Features
1. Create feature branch
2. Implement functionality
3. Add appropriate tests
4. Submit pull request

### Code Style Guidelines
- Follow PEP 8
- Include docstrings
- Comment complex logic
- Use type hints

## Configuration

### Streamlit Settings
Configure in `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#..."
backgroundColor = "#..."
secondaryBackgroundColor = "#..."
textColor = "#..."
```

### Google Sheets Integration
Required environment variables:
```
GOOGLE_SHEETS_CREDENTIALS=...
SPREADSHEET_ID=...
```

## Contributing
1. Fork repository
2. Create feature branch
3. Implement changes
4. Submit pull request

## Support
For support:
- Create GitHub issue
- Contact GDG On Campus PUP organizers
- Reach out to project maintainers

---

**Note**: This documentation is maintained by the GDG On Campus PUP Data and ML track team. For questions about the learning program itself, please contact the GDG organizers directly.
