# Daily Step Tracker Analysis

A data-driven tool to analyze your step count trends, visualize activity patterns, and receive AI-powered insights to help maintain a healthy lifestyle.

## 📋 Overview

The Daily Step Tracker Analysis System helps users understand their physical activity patterns by:
- Tracking and visualizing daily step counts over time
- Identifying active vs. inactive days through simple machine learning
- Providing personalized insights and recommendations
- Predicting future activity trends based on historical data

## ✨ Features

- **Data Management**
  - Upload step count data manually or via CSV
  - Store and manage historical step records
  - Data validation and cleaning

- **Visualization & Analytics**
  - Interactive time-series graphs of daily/weekly/monthly step counts
  - Activity heatmaps by day of week
  - Comparison with previous periods (week/month)

- **AI-Powered Insights**
  - Automatic identification of high and low activity days
  - Pattern recognition for activity habits
  - Personalized step goal recommendations
  - Weekly trend predictions

- **User Interface**
  - Clean, responsive Streamlit dashboard
  - Mobile-friendly design
  - Data export functionality

## 🛠️ Tech Stack

- **Core Technologies**
  - Python 3.9+ for all application logic
  - Streamlit for interactive web dashboard
  - ngrok for exposing local Streamlit app to the internet

- **Machine Learning & Data Analysis**
  - Scikit-Learn for predictive models
  - Pandas & NumPy for data manipulation
  - Matplotlib & Seaborn for visualization

- **Data Storage**
  - Local CSV files or SQLite database

## 🚀 Getting Started

### Prerequisites
```
python >= 3.9
pip
virtualenv (recommended)
ngrok account (free tier available)
```

### Installation

1. Clone the repository
```bash
git clone https://github.com/harigovinda-clsi/AI-ML-Daily-Step-Tracker.git
cd AI-ML-Daily-Step-Tracker
```

2. Create and activate a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run the Streamlit application
```bash
streamlit run app.py
```

5. Access the application locally
```
http://localhost:8501
```

### Exposing with ngrok

To make your Streamlit app accessible over the internet:

1. Sign up for a free ngrok account and get your authtoken
2. Install ngrok client
```bash
pip install pyngrok
```

3. Set up ngrok authentication
```bash
ngrok authtoken YOUR_AUTH_TOKEN
```

4. Run Streamlit with ngrok
```python
# Add to your app.py or create a separate run_with_ngrok.py file
from pyngrok import ngrok

# Start ngrok tunnel to expose the Streamlit app
public_url = ngrok.connect(port=8501)
print(f"Public URL: {public_url}")

# Keep your Streamlit app running
import os
os.system("streamlit run app.py")
```

5. Access your app via the ngrok public URL

## 📊 Usage Examples

### Uploading Data

Data can be uploaded in CSV format with the following structure:
```
date,steps
2025-03-01,8432
2025-03-02,10254
2025-03-03,5123
...
```

Alternatively, use the manual entry form on the Streamlit dashboard.

### Creating a New Step Entry

1. Navigate to the "Add New Data" section in the dashboard
2. Enter the date and step count
3. Click "Submit" to add the new entry
4. View updated visualizations and insights immediately

## 🧠 Machine Learning Components

The project implements basic machine learning algorithms to:
1. Classify days as "active" or "inactive" based on step count patterns
2. Detect weekly trends and seasonality in activity
3. Predict future step counts based on historical data
4. Generate personalized recommendations

## 📁 Project Structure

```
step-tracker/
├── app.py                # Main application file
├── model.py              # Machine learning model implementation
├── static/               # Static assets directory
│   └── css/              # CSS stylesheets
│       └── styles.css    # Main stylesheet
├── templates/            # HTML templates
│   ├── index.html        # Landing page template
│   └── dashboard.html    # Main dashboard template
└── uploads/              # Directory for user data uploads
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Contact

Project Maintainer - shreyasmishra001@gmail.com

Project Link: [https://github.com/harigovinda-clsi/Daily-Step-Tracker](https://github.com/harigovinda-clsi/AI-ML-Daily-Step-Tracker)
