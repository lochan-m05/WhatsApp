#!/usr/bin/env python3
"""
Simple Web Interface for WhatsApp Bulk Messaging System
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.whatsapp_automation import WhatsAppAutomation
from src.data_manager import DataManager
from src.scheduler import MessageScheduler
from config.config import *

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

# Initialize components
dm = DataManager()
scheduler = MessageScheduler()

@app.route('/')
def index():
    """Main dashboard"""
    # Get basic stats
    students = dm.get_students_list()
    jobs = scheduler.get_job_status()
    
    stats = {
        'total_students': len(students),
        'active_jobs': len([j for j in jobs if j.get('status') == 'active']),
        'completed_jobs': len([j for j in jobs if j.get('status') != 'active']),
        'recent_jobs': jobs[-5:] if jobs else []
    }
    
    return render_template('index.html', stats=stats)

@app.route('/students')
def students():
    """Student management page"""
    students_list = dm.get_students_list()
    return render_template('students.html', students=students_list)

@app.route('/send_message')
def send_message_form():
    """Send message form"""
    students = dm.get_students_list()
    
    # Get unique courses and years for filters
    courses = list(set(s['course'] for s in students if s['course']))
    years = list(set(s['year'] for s in students if s['year']))
    
    return render_template('send_message.html', courses=courses, years=years)

@app.route('/send_message', methods=['POST'])
def send_message_post():
    """Process send message form"""
    try:
        # Get form data
        company = request.form['company']
        position = request.form['position']
        package = request.form['package']
        location = request.form['location']
        deadline = request.form['deadline']
        requirements = request.form.get('requirements', 'As per job description')
        
        # Get filters
        min_cgpa = float(request.form['min_cgpa']) if request.form.get('min_cgpa') else None
        courses = request.form.getlist('courses') if request.form.getlist('courses') else None
        years = [int(y) for y in request.form.getlist('years')] if request.form.getlist('years') else None
        skills = request.form['skills'].split(',') if request.form.get('skills') else None
        
        setup_reminders = 'setup_reminders' in request.form
        
        # Filter students
        filtered_students = dm.filter_students_by_criteria(
            min_cgpa=min_cgpa,
            courses=courses,
            years=years,
            skills=skills
        )
        
        if not filtered_students:
            flash('No students match the specified criteria!', 'error')
            return redirect(url_for('send_message_form'))
        
        # Store job data for processing
        job_data = {
            'company': company,
            'position': position,
            'package': package,
            'location': location,
            'deadline': deadline,
            'requirements': requirements,
            'students': filtered_students,
            'setup_reminders': setup_reminders,
            'created_at': datetime.now().isoformat()
        }
        
        # Save to temp file for processing
        temp_file = DATA_DIR / f"temp_job_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(temp_file, 'w') as f:
            json.dump(job_data, f, indent=2, default=str)
        
        flash(f'Message job created for {len(filtered_students)} students! Check status page.', 'success')
        return redirect(url_for('status'))
        
    except Exception as e:
        flash(f'Error creating message job: {str(e)}', 'error')
        return redirect(url_for('send_message_form'))

@app.route('/status')
def status():
    """Status page showing scheduled jobs"""
    jobs = scheduler.get_job_status()
    return render_template('status.html', jobs=jobs)

@app.route('/scheduler')
def scheduler_page():
    """Scheduler management page"""
    is_running = scheduler.is_running
    jobs = scheduler.get_job_status()
    return render_template('scheduler.html', is_running=is_running, jobs=jobs)

@app.route('/start_scheduler', methods=['POST'])
def start_scheduler():
    """Start the scheduler"""
    try:
        scheduler.start_scheduler()
        flash('Scheduler started successfully!', 'success')
    except Exception as e:
        flash(f'Error starting scheduler: {str(e)}', 'error')
    return redirect(url_for('scheduler_page'))

@app.route('/stop_scheduler', methods=['POST'])
def stop_scheduler():
    """Stop the scheduler"""
    try:
        scheduler.stop_scheduler()
        flash('Scheduler stopped successfully!', 'success')
    except Exception as e:
        flash(f'Error stopping scheduler: {str(e)}', 'error')
    return redirect(url_for('scheduler_page'))

@app.route('/api/students')
def api_students():
    """API endpoint for students data"""
    students = dm.get_students_list()
    return jsonify(students)

@app.route('/api/jobs')
def api_jobs():
    """API endpoint for jobs status"""
    jobs = scheduler.get_job_status()
    return jsonify(jobs)

# Create templates directory and basic templates
def create_templates():
    """Create basic HTML templates"""
    templates_dir = Path(__file__).parent / "templates"
    templates_dir.mkdir(exist_ok=True)
    
    # Base template
    base_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}WhatsApp Placement System{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('index') }}">
                <i class="fab fa-whatsapp"></i> Placement System
            </a>
            <div class="navbar-nav">
                <a class="nav-link" href="{{ url_for('index') }}">Dashboard</a>
                <a class="nav-link" href="{{ url_for('students') }}">Students</a>
                <a class="nav-link" href="{{ url_for('send_message_form') }}">Send Message</a>
                <a class="nav-link" href="{{ url_for('status') }}">Status</a>
                <a class="nav-link" href="{{ url_for('scheduler_page') }}">Scheduler</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }} alert-dismissible">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''
    
    # Index template
    index_html = '''{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-md-3">
        <div class="card text-white bg-primary">
            <div class="card-body">
                <div class="d-flex align-items-center">
                    <div class="flex-grow-1">
                        <h4 class="card-title">{{ stats.total_students }}</h4>
                        <p class="card-text">Total Students</p>
                    </div>
                    <i class="fas fa-users fa-2x"></i>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-white bg-success">
            <div class="card-body">
                <div class="d-flex align-items-center">
                    <div class="flex-grow-1">
                        <h4 class="card-title">{{ stats.active_jobs }}</h4>
                        <p class="card-text">Active Jobs</p>
                    </div>
                    <i class="fas fa-clock fa-2x"></i>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-white bg-info">
            <div class="card-body">
                <div class="d-flex align-items-center">
                    <div class="flex-grow-1">
                        <h4 class="card-title">{{ stats.completed_jobs }}</h4>
                        <p class="card-text">Completed Jobs</p>
                    </div>
                    <i class="fas fa-check-circle fa-2x"></i>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-white bg-warning">
            <div class="card-body text-center">
                <a href="{{ url_for('send_message_form') }}" class="btn btn-light btn-lg">
                    <i class="fas fa-paper-plane"></i> Send Message
                </a>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-md-12">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-history"></i> Recent Jobs</h5>
            </div>
            <div class="card-body">
                {% if stats.recent_jobs %}
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Job ID</th>
                                    <th>Type</th>
                                    <th>Company</th>
                                    <th>Status</th>
                                    <th>Created</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for job in stats.recent_jobs %}
                                <tr>
                                    <td>{{ job.job_id }}</td>
                                    <td>{{ job.type }}</td>
                                    <td>{{ job.get('company', 'N/A') }}</td>
                                    <td>
                                        <span class="badge bg-{{ 'success' if job.status == 'active' else 'secondary' }}">
                                            {{ job.status }}
                                        </span>
                                    </td>
                                    <td>{{ job.created_at[:19] }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                {% else %}
                    <p class="text-muted">No jobs found</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    # Save templates
    with open(templates_dir / "base.html", "w") as f:
        f.write(base_html)
    
    with open(templates_dir / "index.html", "w") as f:
        f.write(index_html)
    
    # Simple send message form
    send_form_html = '''{% extends "base.html" %}

{% block content %}
<div class="card">
    <div class="card-header">
        <h5><i class="fas fa-paper-plane"></i> Send Placement Message</h5>
    </div>
    <div class="card-body">
        <form method="POST">
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label">Company Name *</label>
                        <input type="text" class="form-control" name="company" required>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label">Position *</label>
                        <input type="text" class="form-control" name="position" required>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label">Package *</label>
                        <input type="text" class="form-control" name="package" placeholder="e.g., 12 LPA" required>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label">Location *</label>
                        <input type="text" class="form-control" name="location" required>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label">Application Deadline *</label>
                        <input type="date" class="form-control" name="deadline" required>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label">Minimum CGPA</label>
                        <input type="number" class="form-control" name="min_cgpa" step="0.1" min="0" max="10">
                    </div>
                </div>
            </div>
            <div class="mb-3">
                <label class="form-label">Requirements</label>
                <textarea class="form-control" name="requirements" rows="3" placeholder="Job requirements..."></textarea>
            </div>
            <div class="mb-3">
                <label class="form-label">Skills (comma-separated)</label>
                <input type="text" class="form-control" name="skills" placeholder="Python, Java, React">
            </div>
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label">Courses</label>
                        <select class="form-control" name="courses" multiple>
                            {% for course in courses %}
                            <option value="{{ course }}">{{ course }}</option>
                            {% endfor %}
                        </select>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label">Years</label>
                        <select class="form-control" name="years" multiple>
                            {% for year in years %}
                            <option value="{{ year }}">{{ year }}</option>
                            {% endfor %}
                        </select>
                    </div>
                </div>
            </div>
            <div class="mb-3">
                <div class="form-check">
                    <input type="checkbox" class="form-check-input" name="setup_reminders" checked>
                    <label class="form-check-label">Setup automatic reminders</label>
                </div>
            </div>
            <button type="submit" class="btn btn-primary">
                <i class="fas fa-paper-plane"></i> Create Message Job
            </button>
        </form>
    </div>
</div>
{% endblock %}'''
    
    with open(templates_dir / "send_message.html", "w") as f:
        f.write(send_form_html)

if __name__ == '__main__':
    # Create templates
    create_templates()
    
    # Add Flask to requirements
    print("🌐 Starting Web Interface...")
    print("📝 Note: Install Flask if not already installed: pip install flask")
    print("🔗 Web interface will be available at: http://localhost:8000")
    
    app.run(debug=True, host='0.0.0.0', port=8000)
