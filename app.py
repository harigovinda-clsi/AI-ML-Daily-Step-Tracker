from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
import numpy as np
import os
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
from model import StepPredictor
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DATABASE'] = 'step_tracker.db'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize the ML model
step_predictor = StepPredictor()

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
    CREATE TABLE IF NOT EXISTS step_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        steps INTEGER NOT NULL,
        user_id TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    data = conn.execute('SELECT date, steps FROM step_data ORDER BY date').fetchall()
    conn.close()
    
    if not data:
        return render_template('dashboard.html', has_data=False)
    
    # Convert to DataFrame
    df = pd.DataFrame(data, columns=['date', 'steps'])
    df['date'] = pd.to_datetime(df['date'])
    
    # Generate insights
    insights = generate_insights(df)
    
    # Get predictions for the next 7 days
    last_date = df['date'].max()
    future_dates = [last_date + timedelta(days=i+1) for i in range(7)]
    predictions = step_predictor.predict(df, future_dates)
    
    # Format for the template
    chart_data = df.to_dict(orient='records')
    pred_data = [{'date': date.strftime('%Y-%m-%d'), 'steps': int(steps)} 
                 for date, steps in zip(future_dates, predictions)]
    
    return render_template('dashboard.html', 
                          chart_data=json.dumps(chart_data),
                          pred_data=json.dumps(pred_data),
                          insights=insights,
                          has_data=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    if file and file.filename.endswith('.csv'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            df = pd.read_csv(filepath)
            
            # Validate the CSV format
            required_columns = ['date', 'steps']
            if not all(col in df.columns for col in required_columns):
                return "CSV file must contain 'date' and 'steps' columns", 400
            
            # Process and store data
            conn = get_db_connection()
            for _, row in df.iterrows():
                date = row['date']
                steps = int(row['steps'])
                user_id = request.form.get('user_id', 'default_user')
                
                # Check if entry already exists
                existing = conn.execute('SELECT id FROM step_data WHERE date = ? AND user_id = ?',
                                       (date, user_id)).fetchone()
                
                if existing:
                    conn.execute('UPDATE step_data SET steps = ? WHERE date = ? AND user_id = ?',
                               (steps, date, user_id))
                else:
                    conn.execute('INSERT INTO step_data (date, steps, user_id) VALUES (?, ?, ?)',
                               (date, steps, user_id))
            
            conn.commit()
            conn.close()
            
            # Train model with new data
            all_data = get_all_step_data()
            if len(all_data) > 7:  # Need at least a week of data
                step_predictor.train(all_data)
            
            return redirect(url_for('dashboard'))
        
        except Exception as e:
            return f"Error processing file: {str(e)}", 400
    
    return "Invalid file type. Please upload a CSV file.", 400

@app.route('/manual_entry', methods=['POST'])
def manual_entry():
    try:
        date = request.form['date']
        steps = int(request.form['steps'])
        user_id = request.form.get('user_id', 'default_user')
        
        conn = get_db_connection()
        
        # Check if entry already exists
        existing = conn.execute('SELECT id FROM step_data WHERE date = ? AND user_id = ?',
                               (date, user_id)).fetchone()
        
        if existing:
            conn.execute('UPDATE step_data SET steps = ? WHERE date = ? AND user_id = ?',
                       (steps, date, user_id))
        else:
            conn.execute('INSERT INTO step_data (date, steps, user_id) VALUES (?, ?, ?)',
                       (date, steps, user_id))
        
        conn.commit()
        conn.close()
        
        # Retrain model if we have enough data
        all_data = get_all_step_data()
        if len(all_data) > 7:  # Need at least a week of data
            step_predictor.train(all_data)
        
        return redirect(url_for('dashboard'))
    
    except Exception as e:
        return f"Error adding entry: {str(e)}", 400

@app.route('/api/steps', methods=['GET'])
def get_steps():
    try:
        conn = get_db_connection()
        data = conn.execute('SELECT date, steps FROM step_data ORDER BY date').fetchall()
        conn.close()
        
        result = [{'date': row['date'], 'steps': row['steps']} for row in data]
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/insights', methods=['GET'])
def get_insights():
    try:
        data = get_all_step_data()
        if data.empty:
            return jsonify({'error': 'No data available'}), 404
        
        insights = generate_insights(data)
        return jsonify(insights)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict', methods=['GET'])
def predict_steps():
    try:
        days = int(request.args.get('days', 7))
        
        data = get_all_step_data()
        if data.empty or len(data) < 7:
            return jsonify({'error': 'Not enough data for prediction'}), 404
        
        last_date = data['date'].max()
        future_dates = [last_date + timedelta(days=i+1) for i in range(days)]
        
        predictions = step_predictor.predict(data, future_dates)
        
        result = [{'date': date.strftime('%Y-%m-%d'), 'predicted_steps': int(steps)} 
                 for date, steps in zip(future_dates, predictions)]
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_all_step_data():
    conn = get_db_connection()
    data = conn.execute('SELECT date, steps FROM step_data ORDER BY date').fetchall()
    conn.close()
    
    if not data:
        return pd.DataFrame(columns=['date', 'steps'])
    
    df = pd.DataFrame(data, columns=['date', 'steps'])
    df['date'] = pd.to_datetime(df['date'])
    return df

def generate_insights(df):
    insights = {
        'total_days': len(df),
        'avg_steps': int(df['steps'].mean()),
        'max_steps': int(df['steps'].max()),
        'max_steps_date': df.loc[df['steps'].idxmax(), 'date'].strftime('%Y-%m-%d'),
        'min_steps': int(df['steps'].min()),
        'min_steps_date': df.loc[df['steps'].idxmin(), 'date'].strftime('%Y-%m-%d'),
    }
    
    # Add day of week analysis
    df['day_of_week'] = df['date'].dt.day_name()
    day_avg = df.groupby('day_of_week')['steps'].mean().to_dict()
    
    # Find the most and least active days
    most_active_day = max(day_avg, key=day_avg.get)
    least_active_day = min(day_avg, key=day_avg.get)
    
    insights['day_averages'] = {day: int(avg) for day, avg in day_avg.items()}
    insights['most_active_day'] = most_active_day
    insights['least_active_day'] = least_active_day
    
    # Generate recommendations
    recommendations = []
    if insights['avg_steps'] < 7000:
        recommendations.append("Try to increase your daily steps to reach the recommended 10,000 steps.")
    
    if most_active_day and least_active_day:
        diff = day_avg[most_active_day] - day_avg[least_active_day]
        if diff > 3000:
            recommendations.append(f"Your activity level on {least_active_day}s is much lower than {most_active_day}s. Try to be more consistent throughout the week.")
    
    recent_trend = df.sort_values('date').tail(7)
    if len(recent_trend) == 7:
        recent_avg = recent_trend['steps'].mean()
        overall_avg = df['steps'].mean()
        
        if recent_avg < overall_avg * 0.8:
            recommendations.append("Your activity has decreased recently. Try to get back to your usual routine.")
        elif recent_avg > overall_avg * 1.2:
            recommendations.append("Great job! You've been more active than usual lately.")
    
    insights['recommendations'] = recommendations
    
    return insights

if __name__ == '__main__':
    init_db()
    app.run(debug=True)