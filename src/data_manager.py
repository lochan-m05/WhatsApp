"""
Data management for student contacts and message templates
"""

import pandas as pd
import json
import os
import sys
from datetime import datetime, timedelta
from loguru import logger

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import *

class DataManager:
    def __init__(self):
        self.students_df = None
        self.message_templates = {}
        self.setup_directories()
    
    def setup_directories(self):
        """Create necessary directories"""
        DATA_DIR.mkdir(exist_ok=True)
        LOGS_DIR.mkdir(exist_ok=True)
    
    def create_sample_student_file(self):
        """Create a sample Excel file with student data structure"""
        sample_data = {
            'Name': [
                'John Doe', 'Jane Smith', 'Alice Johnson', 'Bob Wilson', 'Carol Brown'
            ],
            'Phone': [
                '+919876543210', '9876543211', '+919876543212', '9876543213', '+919876543214'
            ],
            'Email': [
                'john.doe@email.com', 'jane.smith@email.com', 'alice.j@email.com', 
                'bob.w@email.com', 'carol.b@email.com'
            ],
            'Course': [
                'Computer Science', 'Information Technology', 'Electronics', 
                'Mechanical', 'Computer Science'
            ],
            'Year': [4, 4, 3, 4, 3],
            'CGPA': [8.5, 9.2, 7.8, 8.0, 9.0],
            'Skills': [
                'Python, Java, React', 'JavaScript, Node.js, MongoDB', 
                'C++, Python, Machine Learning', 'Java, Spring Boot, MySQL',
                'Python, Django, PostgreSQL'
            ]
        }
        
        df = pd.DataFrame(sample_data)
        df.to_excel(STUDENTS_FILE, index=False)
        logger.info(f"Sample student file created at {STUDENTS_FILE}")
        return df
    
    def load_students(self, file_path=None):
        """Load student data from Excel file"""
        try:
            if file_path is None:
                file_path = STUDENTS_FILE
            
            if not os.path.exists(file_path):
                logger.warning(f"Student file not found at {file_path}. Creating sample file.")
                return self.create_sample_student_file()
            
            self.students_df = pd.read_excel(file_path)
            logger.info(f"Loaded {len(self.students_df)} students from {file_path}")
            return self.students_df
            
        except Exception as e:
            logger.error(f"Failed to load students: {e}")
            return None
    
    def get_students_list(self, filters=None):
        """Get list of students as dictionaries with optional filters"""
        if self.students_df is None:
            self.load_students()
        
        if self.students_df is None:
            return []
        
        df = self.students_df.copy()
        
        # Apply filters if provided
        if filters:
            for key, value in filters.items():
                if key in df.columns:
                    if isinstance(value, list):
                        df = df[df[key].isin(value)]
                    else:
                        df = df[df[key] == value]
        
        # Convert to list of dictionaries
        students = []
        for _, row in df.iterrows():
            student = {
                'name': row.get(STUDENT_COLUMNS['name'], ''),
                'phone': str(row.get(STUDENT_COLUMNS['phone'], '')),
                'email': row.get(STUDENT_COLUMNS['email'], ''),
                'course': row.get(STUDENT_COLUMNS['course'], ''),
                'year': row.get(STUDENT_COLUMNS['year'], ''),
                'cgpa': row.get(STUDENT_COLUMNS['cgpa'], ''),
                'skills': row.get(STUDENT_COLUMNS['skills'], '')
            }
            students.append(student)
        
        return students
    
    def filter_students_by_criteria(self, min_cgpa=None, courses=None, years=None, skills=None):
        """Filter students based on placement criteria"""
        filters = {}
        
        if courses:
            filters['Course'] = courses if isinstance(courses, list) else [courses]
        
        if years:
            filters['Year'] = years if isinstance(years, list) else [years]
        
        students = self.get_students_list(filters)
        
        # Apply CGPA filter
        if min_cgpa:
            students = [s for s in students if float(s.get('cgpa', 0)) >= min_cgpa]
        
        # Apply skills filter
        if skills:
            skill_list = skills if isinstance(skills, list) else [skills]
            filtered_students = []
            for student in students:
                student_skills = student.get('skills', '').lower()
                if any(skill.lower() in student_skills for skill in skill_list):
                    filtered_students.append(student)
            students = filtered_students
        
        logger.info(f"Filtered to {len(students)} students based on criteria")
        return students
    
    def load_message_templates(self):
        """Load message templates from JSON file"""
        try:
            if os.path.exists(MESSAGES_FILE):
                with open(MESSAGES_FILE, 'r') as f:
                    self.message_templates = json.load(f)
                logger.info("Message templates loaded")
            else:
                self.create_default_templates()
            return self.message_templates
        except Exception as e:
            logger.error(f"Failed to load message templates: {e}")
            return {}
    
    def create_default_templates(self):
        """Create default message templates"""
        default_templates = {
            "placement_alert": {
                "template": DEFAULT_MESSAGE_TEMPLATE,
                "description": "General placement opportunity alert"
            },
            "reminder": {
                "template": """
🔔 *Placement Reminder* 🔔

Dear {name},

This is a reminder about the placement opportunity:

*Company:* {company}
*Position:* {position}
*Application Deadline:* {last_date}

⏰ Only {days_remaining} days left to apply!

Don't miss this opportunity. Apply now!

Best regards,
Placement Cell
                """,
                "description": "Reminder message for upcoming deadlines"
            },
            "interview_schedule": {
                "template": """
📅 *Interview Scheduled* 📅

Dear {name},

Your interview has been scheduled for:

*Company:* {company}
*Position:* {position}
*Date:* {interview_date}
*Time:* {interview_time}
*Mode:* {interview_mode}
*Venue/Link:* {interview_details}

Please be prepared and join 10 minutes early.

All the best!

Placement Cell
                """,
                "description": "Interview scheduling notification"
            }
        }
        
        with open(MESSAGES_FILE, 'w') as f:
            json.dump(default_templates, f, indent=2)
        
        self.message_templates = default_templates
        logger.info("Default message templates created")
    
    def save_message_template(self, template_name, template_content, description=""):
        """Save a new message template"""
        try:
            if not self.message_templates:
                self.load_message_templates()
            
            self.message_templates[template_name] = {
                "template": template_content,
                "description": description
            }
            
            with open(MESSAGES_FILE, 'w') as f:
                json.dump(self.message_templates, f, indent=2)
            
            logger.info(f"Message template '{template_name}' saved")
            return True
        except Exception as e:
            logger.error(f"Failed to save template: {e}")
            return False
    
    def get_template(self, template_name):
        """Get a specific message template"""
        if not self.message_templates:
            self.load_message_templates()
        
        return self.message_templates.get(template_name, {}).get("template", "")
    
    def add_student(self, student_data):
        """Add a new student to the database"""
        try:
            if self.students_df is None:
                self.load_students()
            
            new_row = pd.DataFrame([student_data])
            self.students_df = pd.concat([self.students_df, new_row], ignore_index=True)
            
            # Save to file
            self.students_df.to_excel(STUDENTS_FILE, index=False)
            logger.info(f"Added new student: {student_data.get('Name', 'Unknown')}")
            return True
        except Exception as e:
            logger.error(f"Failed to add student: {e}")
            return False
    
    def update_student(self, student_id, updated_data):
        """Update existing student data"""
        try:
            if self.students_df is None:
                self.load_students()
            
            self.students_df.loc[student_id] = updated_data
            self.students_df.to_excel(STUDENTS_FILE, index=False)
            logger.info(f"Updated student at index {student_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update student: {e}")
            return False
    
    def export_filtered_students(self, students, filename):
        """Export filtered students to a new Excel file"""
        try:
            df = pd.DataFrame(students)
            export_path = DATA_DIR / filename
            df.to_excel(export_path, index=False)
            logger.info(f"Exported {len(students)} students to {export_path}")
            return export_path
        except Exception as e:
            logger.error(f"Failed to export students: {e}")
            return None
