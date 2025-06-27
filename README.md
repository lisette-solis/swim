# AI Swim Workout Generator

A Flask web application that generates personalized swimming workouts using Gemini API. Choose your skill level, desired length, equipment, and experience level and let AI create custom training sessions tailored to your needs.

## Quick Start

### Prerequisites

- Python 3.8+
- At least one AI API key (Gemini recommended for free tier)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd swim
   ```

2. **Create virtual environment**
   ```bash
   conda create -n "swim_env"
   conda activate swim_env
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
  See directions below

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Open in browser**
   ```
   http://localhost:5000
   ```

## API Key Setup

### Google Gemini (Recommended - Free Tier)
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in and create an API key
3. Add to `.env`: `GEMINI_API_KEY=your_key_here`

### Environment Variables (.env file)
```bash
# Primary API key (choose one)
GEMINI_API_KEY=your_gemini_key

# Default settings
DEFAULT_LLM_PROVIDER=gemini
```

## Project Structure

```
swim-workout-generator/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (you need to create this file to store API key)
├── .gitignore           # Git ignore file
├── README.md            # This file
├── static/
│   └── images/
│       └── ocean-waves.jpg 
└── templates/
    └── index.html       
```
