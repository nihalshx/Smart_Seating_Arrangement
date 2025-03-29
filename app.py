# app.py
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify, session
import pandas as pd
import numpy as np
import random
import os
import csv
import json
from io import StringIO, BytesIO
from collections import deque, defaultdict
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import colorsys
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from datetime import datetime, timedelta
import werkzeug.utils
import uuid
import shutil
import tempfile
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# Check if running on Vercel (production)
if os.environ.get('VERCEL_REGION'):
    # Use /tmp for uploads in serverless environment
    app.config['UPLOAD_FOLDER'] = '/tmp'
    # More secure cookie settings for production
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
else:
    # Use local uploads folder from environment variable or default
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
    
# Get configuration from environment variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secure-key-here')
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_UPLOAD_SIZE_MB', 16)) * 1024 * 1024  # Default: 16MB
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=int(os.environ.get('SESSION_LIFETIME_HOURS', 1)))  # Default: 1 hour

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Department colors for visualization
DEPARTMENT_COLORS = {
    'CSE': '#FF6B6B',
    'ECE': '#4ECDC4',
    'ME': '#45B7D1',
    'CE': '#96CEB4',
    'EE': '#FFEEAD',
    'IT': '#D4A5A5',
    'AI': '#9B59B6',
    'CS': '#3498DB',
    'CSBS': '#E74C3C',
    'AIML': '#2ECC71',
    'AIDS': '#F1C40F',
    'CSCE': '#1ABC9C',
    'CIVIL': '#E67E22',
    'MECH': '#34495E',
    'EEE': '#7F8C8D',
    'CSE-AI': '#16A085',
    'CSE-DS': '#D35400',
    'CSE-CS': '#8E44AD',
    'CSE-IT': '#27AE60',
    'CSE-AIML': '#C0392B',
    'CSE-AIDS': '#F39C12',
    'CSE-CSCE': '#2980B9',
    'Computer Science': '#FF6347',
    'Engineering': '#4682B4',
    'Business': '#32CD32',
    'Arts': '#FFD700',
    'Science': '#9370DB'
}

class SeatingManager:
    def __init__(self, num_rooms, seats_per_room, department_buffer=2):
        self.num_rooms = num_rooms
        self.seats_per_room = seats_per_room
        self.department_buffer = department_buffer
        self.total_capacity = num_rooms * seats_per_room
        
    def validate_capacity(self, num_students):
        if num_students > self.total_capacity:
            raise ValueError(f"Insufficient capacity: {num_students} students vs {self.total_capacity} seats")
    
    def arrange_seating(self, students):
        rooms = defaultdict(list)
        department_history = defaultdict(lambda: deque(maxlen=self.department_buffer))
        
        students = random.sample(students, len(students))  # Shuffle
        
        for student in students:
            placed = False
            for room_num in range(1, self.num_rooms + 1):
                room_name = f'Room-{room_num}'
                if len(rooms[room_name]) < self.seats_per_room:
                    current_dept = student['Department']
                    
                    # Check department history in this room
                    if current_dept not in department_history[room_name]:
                        rooms[room_name].append(student)
                        department_history[room_name].append(current_dept)
                        placed = True
                        break
                    
            if not placed:  # Fallback placement
                for room_num in range(1, self.num_rooms + 1):
                    room_name = f'Room-{room_num}'
                    if len(rooms[room_name]) < self.seats_per_room:
                        rooms[room_name].append(student)
                        break
                        
        return rooms

def generate_sample_data(num_students):
    """Generate sample student data for testing"""
    departments = list(DEPARTMENT_COLORS.keys())[:5]  # Use first 5 departments from DEPARTMENT_COLORS
    years = [1, 2, 3, 4]
    
    data = {
        'Student_ID': [f'STU{i:03d}' for i in range(1, num_students + 1)],
        'Department': [random.choice(departments) for _ in range(num_students)],
        'Year': [random.choice(years) for _ in range(num_students)],
        'Past_Attendance': [random.uniform(0.5, 1.0) for _ in range(num_students)],
        'Attendance_Score': [random.uniform(0, 100) for _ in range(num_students)]
    }
    
    return pd.DataFrame(data)

def generate_seat_map(room_assignments, seats_per_room, seats_per_row=6):
    """Generate a visual seat map for each room"""
    seat_maps = {}
    for room, students in room_assignments.items():
        rows = []
        for i in range(0, len(students), seats_per_row):
            row = []
            for j, student in enumerate(students[i:i+seats_per_row]):
                row.append({
                    'seat_number': i + j + 1,
                    'student_id': student['Student_ID'],
                    'department': student['Department'],
                    'row': i // seats_per_row + 1,
                    'column': j + 1
                })
            rows.append(row)
        seat_maps[room] = {
            'seats': rows,
            'total_seats': len(students),
            'room_number': room.split('-')[-1]
        }
    return seat_maps

def generate_department_colors(departments):
    """Generate consistent colors for departments"""
    colors = {}
    for dept in departments:
        if dept in DEPARTMENT_COLORS:
            colors[dept] = DEPARTMENT_COLORS[dept]
            continue
            
        # Generate colors for new departments
        n = len(colors) + 1
        hue = (n * 0.618033988749895) % 1  # Golden ratio for better color distribution
        saturation = 0.7
        value = 0.8
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        # Convert to hex color
        hex_color = '#{:02x}{:02x}{:02x}'.format(
            int(rgb[0] * 255),
            int(rgb[1] * 255),
            int(rgb[2] * 255)
        )
        colors[dept] = hex_color
    
    return colors

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'csv'

def validate_csv(df):
    """Validate the CSV file structure and content"""
    required_columns = {'Student_ID', 'Department', 'Year', 'Past_Attendance'}
    
    # Check required columns
    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    
    # Check for empty values
    for col in required_columns:
        if df[col].isnull().any():
            raise ValueError(f"Column '{col}' contains empty values")
    
    # Validate data types
    if not pd.api.types.is_numeric_dtype(df['Year']):
        raise ValueError("'Year' column must contain numeric values")
    if not pd.api.types.is_numeric_dtype(df['Past_Attendance']):
        raise ValueError("'Past_Attendance' column must contain numeric values")
    
    # Validate value ranges
    if not (df['Past_Attendance'].between(0, 1).all()):
        raise ValueError("'Past_Attendance' values must be between 0 and 1")
    
    # Validate minimum number of rows
    if len(df) < 1:
        raise ValueError("CSV file must contain at least one row of data")

def predict_attendance(df):
    """Predict student attendance based on simple rules without ML
    
    Rules:
    1. Students with past attendance > 0.8 are very likely to attend (0.9 probability)
    2. Students with past attendance between 0.6-0.8 have moderate chance (0.7 probability)
    3. Students with past attendance < 0.6 have lower chance (0.5 probability)
    4. Year of study affects likelihood (seniors more likely to attend than freshmen)
    """
    # Create a copy to avoid modifying the original DataFrame
    result_df = df.copy()
    
    # Initialize attendance probability column
    result_df['Attendance_Probability'] = 0.0
    
    # Apply rule 1: Based on past attendance
    result_df.loc[result_df['Past_Attendance'] > 0.8, 'Attendance_Probability'] = 0.9
    result_df.loc[(result_df['Past_Attendance'] >= 0.6) & (result_df['Past_Attendance'] <= 0.8), 'Attendance_Probability'] = 0.7
    result_df.loc[result_df['Past_Attendance'] < 0.6, 'Attendance_Probability'] = 0.5
    
    # Apply rule 2: Year of study bonus (seniors are more likely to attend)
    # Add a small bonus for each year of study (0.02 per year)
    year_bonus = (result_df['Year'] - 1) * 0.02
    result_df['Attendance_Probability'] = result_df['Attendance_Probability'] + year_bonus
    
    # Ensure probability is between 0 and 1
    result_df['Attendance_Probability'] = result_df['Attendance_Probability'].clip(0, 1)
    
    # Predict attendance (1 = will attend, 0 = won't attend)
    # A student is predicted to attend if their probability is > 0.65
    result_df['Predicted_Attendance'] = (result_df['Attendance_Probability'] > 0.65).astype(int)
    
    return result_df

def cleanup_old_files(max_age_hours=24):
    """Clean up files older than the specified age"""
    try:
        # Skip cleanup in serverless environment
        if os.environ.get('VERCEL_REGION'):
            return
            
        current_time = datetime.now()
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            # Get file modification time
            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            # If file is older than max_age_hours, delete it
            if (current_time - file_time) > timedelta(hours=max_age_hours):
                if os.path.isfile(filepath):
                    os.remove(filepath)
    except Exception as e:
        app.logger.error(f"Error during cleanup: {str(e)}")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', message="Page not found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', message="Internal server error"), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    # Cleanup old files
    cleanup_old_files()
    
    if request.method == 'POST':
        try:
            num_rooms = int(request.form.get('num_rooms', 4))           
            seats_per_room = int(request.form.get('seats_per_room', 25))
            
            if num_rooms < 1 or seats_per_room < 1:
                raise ValueError("Invalid room configuration")
            
            if 'generate_test' in request.form:
                test_data = generate_sample_data(100)
                filename = f"sample_data_{uuid.uuid4()}.csv"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                test_data.to_csv(filepath, index=False)
                return redirect(url_for('process_seating', 
                                      filename=filename,
                                      num_rooms=num_rooms,
                                      seats_per_room=seats_per_room))
            
            if 'file' not in request.files:
                raise ValueError("No file part in the request")
            
            file = request.files['file']
            if file.filename == '':
                raise ValueError("No file selected")
            
            if not allowed_file(file.filename):
                raise ValueError("Only CSV files are allowed")
            
            # Create unique filename to prevent overwriting
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{str(uuid.uuid4())}.{file_ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Save file
            file.save(filepath)
            
            # Validate CSV content
            try:
                df = pd.read_csv(filepath)
                validate_csv(df)
            except Exception as e:
                # Clean up invalid file
                if os.path.exists(filepath):
                    os.remove(filepath)
                raise ValueError(f"Invalid CSV file: {str(e)}")
            
            # If everything is valid, redirect to process
            return redirect(url_for('process_seating',
                                  filename=unique_filename,
                                  num_rooms=num_rooms,
                                  seats_per_room=seats_per_room))
            
        except Exception as e:
            flash(str(e), 'danger')
            return render_template('index.html')
    
    return render_template('index.html')

@app.route('/process')
def process_seating():
    try:
        filename = request.args.get('filename')
        if not filename:
            raise ValueError("No filename provided")
            
        num_rooms = int(request.args.get('num_rooms', 4))
        seats_per_room = int(request.args.get('seats_per_room', 25))
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(filepath):
            raise ValueError("File not found")
        
        # Read and validate CSV
        df = pd.read_csv(filepath)
        validate_csv(df)
        
        # Use rule-based prediction instead of ML
        df = predict_attendance(df)
        
        attending_students = df[df['Predicted_Attendance'] == 1]
        
        # Seating arrangement
        manager = SeatingManager(num_rooms, seats_per_room)
        manager.validate_capacity(len(attending_students))
        room_assignments = manager.arrange_seating(
            attending_students[['Student_ID', 'Department']].to_dict('records')
        )
        
        # Generate seat maps
        seat_maps = generate_seat_map(room_assignments, seats_per_room)
        
        # Generate department colors
        departments = df['Department'].unique().tolist()
        department_colors = generate_department_colors(departments)
        
        # Generate session ID for this arrangement
        session_id = str(uuid.uuid4())
        
        # Store data in Flask session
        seating_data = {
            'rooms': room_assignments,
            'seat_maps': seat_maps,
            'total_students': len(df),
            'attending_count': len(attending_students),
            'num_rooms': num_rooms,
            'seats_per_room': seats_per_room,
            'departments': departments,
            'department_colors': department_colors,
            'attendance_probabilities': df['Attendance_Probability'].tolist(),
            'filename': filename
        }
        
        # Store in session
        session['seating_data'] = seating_data
        session['session_id'] = session_id
        
        return render_template('results.html',
                            total_students=len(df),
                            attending_count=len(attending_students),
                            seat_maps=seat_maps,
                            departments=departments,
                            department_colors=department_colors,
                            seating_data=json.dumps(seating_data),
                            num_rooms=num_rooms,
                            seats_per_room=seats_per_room,
                            attendance_probabilities=df['Attendance_Probability'].tolist())
    
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('index'))

@app.route('/process', methods=['POST'])
def process_next_file():
    try:
        num_rooms = int(request.form.get('num_rooms', 4))           
        seats_per_room = int(request.form.get('seats_per_room', 25))
        
        if num_rooms < 1 or seats_per_room < 1:
            raise ValueError("Invalid room configuration")
        
        if 'file' not in request.files:
            raise ValueError("No file part in the request")
        
        file = request.files['file']
        if file.filename == '':
            raise ValueError("No file selected")
        
        if not allowed_file(file.filename):
            raise ValueError("Only CSV files are allowed")
        
        # Create unique filename to prevent overwriting
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{str(uuid.uuid4())}.{file_ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save file
        file.save(filepath)
        
        # Validate CSV content
        try:
            df = pd.read_csv(filepath)
            validate_csv(df)
        except Exception as e:
            # Clean up invalid file
            if os.path.exists(filepath):
                os.remove(filepath)
            raise ValueError(f"Invalid CSV file: {str(e)}")
        
        # If everything is valid, redirect to process
        return redirect(url_for('process_seating',
                              filename=unique_filename,
                              num_rooms=num_rooms,
                              seats_per_room=seats_per_room))
        
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('index'))

@app.route('/download/csv')
def download_csv():
    if 'seating_data' not in session:
        flash('No seating data available. Please generate the arrangement first.', 'danger')
        return redirect(url_for('index'))
    
    try:
        # Get data from session
        seating_data = session['seating_data']
        
        # Create CSV in memory
        output = BytesIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Room', 'Seat Number', 'Student ID', 'Department'])
        
        # Write data
        for room_name, students in seating_data['rooms'].items():
            for seat_num, student in enumerate(students, 1):
                writer.writerow([
                    room_name,
                    seat_num,
                    student['Student_ID'],
                    student['Department']
                ])
        
        output.seek(0)
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'seating_arrangement_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('index'))

@app.route('/download/pdf')
def download_pdf():
    if 'seating_data' not in session:
        flash('No seating data available. Please generate the arrangement first.', 'danger')
        return redirect(url_for('index'))
    
    try:
        # Get data from session
        seating_data = session['seating_data']
        
        # Create PDF in memory
        output = BytesIO()
        doc = SimpleDocTemplate(output, pagesize=letter)
        elements = []
        
        # Create table data
        data = [['Room', 'Seat Number', 'Student ID', 'Department']]
        
        for room_name, students in seating_data['rooms'].items():
            for seat_num, student in enumerate(students, 1):
                data.append([
                    room_name,
                    str(seat_num),
                    student['Student_ID'],
                    student['Department']
                ])
        
        # Create table
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        output.seek(0)
        return send_file(
            output,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'seating_arrangement_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('index'))

@app.route('/clear-session')
def clear_session():
    # Also remove any files associated with the session
    try:
        if 'seating_data' in session and 'filename' in session['seating_data']:
            filename = session['seating_data']['filename']
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(filepath):
                os.remove(filepath)
    except Exception as e:
        app.logger.error(f"Error removing file: {str(e)}")
    
    # Clear session
    session.clear()
    return redirect(url_for('index'))

@app.route('/credits')
def credits():
    return render_template('credits.html')

@app.route('/manual')
def manual():
    return render_template('manual.html')

@app.route('/test-prediction', methods=['GET'])
def test_prediction():
    """Test endpoint to demonstrate rule-based attendance prediction"""
    # Create some sample student data
    sample_data = {
        'Student_ID': ['STU001', 'STU002', 'STU003', 'STU004', 'STU005'],
        'Department': ['CSE', 'ECE', 'ME', 'CSE', 'ECE'],
        'Year': [1, 2, 3, 4, 1],
        'Past_Attendance': [0.95, 0.75, 0.55, 0.85, 0.45]
    }
    
    # Convert to DataFrame
    df = pd.DataFrame(sample_data)
    
    # Apply prediction
    result = predict_attendance(df)
    
    # Convert to dictionary for JSON response
    prediction_result = {
        'input_data': df.to_dict(orient='records'),
        'prediction_result': result[['Student_ID', 'Department', 'Year', 
                                    'Past_Attendance', 'Attendance_Probability', 
                                    'Predicted_Attendance']].to_dict(orient='records'),
        'rules_applied': [
            'Students with past attendance > 0.8 are very likely to attend (0.9 probability)',
            'Students with past attendance between 0.6-0.8 have moderate chance (0.7 probability)',
            'Students with past attendance < 0.6 have lower chance (0.5 probability)',
            'Seniors (higher year of study) get a bonus of 0.02 per year',
            'Students with final probability > 0.65 are predicted to attend'
        ]
    }
    
    return jsonify(prediction_result)

# For Vercel serverless deployment
if __name__ == '__main__':
    # Only run the app directly when not on Vercel
    app.run(debug=True)