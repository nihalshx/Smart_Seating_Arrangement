from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import os
import json
import csv
from io import StringIO, BytesIO
from collections import deque, defaultdict
from datetime import datetime, timedelta
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Ensure all response headers are secure
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# Error handling for production
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return render_template('error.html', message="An unexpected error occurred"), 500

# Serverless-friendly configuration
app.config.update(
    SECRET_KEY=os.environ.get('FLASK_SECRET_KEY', 'your-secure-random-key'),
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1),
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

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
        
        # Simulate shuffling students instead of using random.sample
        # This avoids importing random module
        students_copy = students.copy()
        for i in range(len(students_copy)):
            j = (i * 7919) % len(students_copy)  # Use prime number for pseudo-random shuffle
            students_copy[i], students_copy[j] = students_copy[j], students_copy[i]
        
        for student in students_copy:
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
        
        # Generate a simple hash-based color if not in predefined colors
        hash_code = sum(ord(c) for c in dept)
        r = (hash_code * 123) % 255
        g = (hash_code * 456) % 255
        b = (hash_code * 789) % 255
        colors[dept] = f'#{r:02x}{g:02x}{b:02x}'
    
    return colors

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', message="Page not found"), 404

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/demo', methods=['GET', 'POST'])
def demo():
    # Mock data for demo purposes
    mock_depts = ['CSE', 'ECE', 'ME', 'CE', 'EE']
    mock_students = []
    
    # Generate 50 mock students
    for i in range(1, 51):
        student_id = f'STU{i:03d}'
        dept = mock_depts[i % len(mock_depts)]
        mock_students.append({
            'Student_ID': student_id,
            'Department': dept
        })
    
    num_rooms = 2
    seats_per_room = 30
    
    # Use seating manager to arrange students
    manager = SeatingManager(num_rooms, seats_per_room)
    room_assignments = manager.arrange_seating(mock_students)
    
    # Generate seat maps
    seat_maps = generate_seat_map(room_assignments, seats_per_room)
    
    # Generate department colors
    department_colors = generate_department_colors(mock_depts)
    
    # Store data in Flask session
    seating_data = {
        'rooms': room_assignments,
        'seat_maps': seat_maps,
        'total_students': len(mock_students),
        'attending_count': len(mock_students),
        'num_rooms': num_rooms,
        'seats_per_room': seats_per_room,
        'departments': mock_depts,
        'department_colors': department_colors,
        'attendance_probabilities': [0.8] * len(mock_students)
    }
    
    session['seating_data'] = seating_data
    session['session_id'] = str(uuid.uuid4())
    
    return render_template('results.html',
                        total_students=len(mock_students),
                        attending_count=len(mock_students),
                        seat_maps=seat_maps,
                        departments=mock_depts,
                        department_colors=department_colors,
                        seating_data=json.dumps(seating_data),
                        num_rooms=num_rooms,
                        seats_per_room=seats_per_room,
                        attendance_probabilities=[0.8] * len(mock_students))

@app.route('/credits')
def credits():
    return render_template('credits.html')

@app.route('/manual')
def manual():
    return render_template('manual.html')

if __name__ == '__main__':
    app.run(debug=True) 