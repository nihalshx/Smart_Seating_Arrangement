# app.py
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify, session
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
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

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'your-secure-key-here'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)  # Set session timeout

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
        'Attended': [random.choice([0, 1]) for _ in range(num_students)]
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
    required_columns = {'Student_ID', 'Department', 'Year', 'Past_Attendance', 'Attended'}
    
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
    if not pd.api.types.is_numeric_dtype(df['Attended']):
        raise ValueError("'Attended' column must contain numeric values")
    
    # Validate value ranges
    if not (df['Past_Attendance'].between(0, 1).all()):
        raise ValueError("'Past_Attendance' values must be between 0 and 1")
    if not (df['Attended'].isin([0, 1]).all()):
        raise ValueError("'Attended' values must be 0 or 1")
    
    # Validate minimum number of rows
    if len(df) < 1:
        raise ValueError("CSV file must contain at least one row of data")

def cleanup_old_files(max_age_hours=24):
    """Clean up files older than the specified age"""
    try:
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
        
        # Machine learning pipeline
        le = LabelEncoder()
        df['Dept_Encoded'] = le.fit_transform(df['Department'])
        
        X_train, X_test, y_train, y_test = train_test_split(
            df[['Dept_Encoded', 'Year', 'Past_Attendance']], 
            df['Attended'], 
            test_size=0.2, 
            random_state=42
        )
        
        model = LogisticRegression()
        model.fit(X_train, y_train)
        
        # Extract probability for class 1 (will attend)
        probabilities = model.predict_proba(df[['Dept_Encoded', 'Year', 'Past_Attendance']])
        df['Attendance_Probability'] = probabilities[:, 1]  # Get probability of class 1
        df['Predicted_Attendance'] = model.predict(df[['Dept_Encoded', 'Year', 'Past_Attendance']])
        
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

if __name__ == '__main__':
    app.run(debug=True)