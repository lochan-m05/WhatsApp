#!/usr/bin/env python3
"""
WhatsApp Bulk Messaging System - Demo Script
This script demonstrates the basic functionality of the system
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.data_manager import DataManager
from src.scheduler import MessageScheduler

def demo_data_management():
    """Demonstrate data management features"""
    print("📊 Data Management Demo")
    print("=" * 40)
    
    dm = DataManager()
    
    # Load students (will create sample file if not exists)
    print("📥 Loading student data...")
    students = dm.load_students()
    
    if students is not None:
        print(f"✅ Loaded {len(students)} students")
        
        # Show first few students
        student_list = dm.get_students_list()
        print("\n👥 Sample Students:")
        for i, student in enumerate(student_list[:3], 1):
            print(f"{i}. {student['name']} - {student['course']} - CGPA: {student['cgpa']}")
    
    # Demonstrate filtering
    print("\n🔍 Filtering Examples:")
    
    # Filter by CGPA
    high_cgpa_students = dm.filter_students_by_criteria(min_cgpa=8.0)
    print(f"Students with CGPA >= 8.0: {len(high_cgpa_students)}")
    
    # Filter by course
    cs_students = dm.filter_students_by_criteria(courses=["Computer Science"])
    print(f"Computer Science students: {len(cs_students)}")
    
    # Filter by skills
    python_students = dm.filter_students_by_criteria(skills=["Python"])
    print(f"Students with Python skills: {len(python_students)}")
    
    # Multiple filters
    filtered = dm.filter_students_by_criteria(
        min_cgpa=7.5,
        courses=["Computer Science", "Information Technology"],
        skills=["Python", "Java"]
    )
    print(f"CS/IT students with CGPA >= 7.5 and Python/Java skills: {len(filtered)}")

def demo_message_templates():
    """Demonstrate message template management"""
    print("\n📝 Message Templates Demo")
    print("=" * 40)
    
    dm = DataManager()
    
    # Load templates
    templates = dm.load_message_templates()
    
    print("Available templates:")
    for name, template_data in templates.items():
        print(f"- {name}: {template_data['description']}")
    
    # Show a sample template
    placement_template = dm.get_template("placement_alert")
    if placement_template:
        print(f"\n📄 Sample Placement Alert Template:")
        print("-" * 40)
        sample_message = placement_template.format(
            name="John Doe",
            company="TechCorp",
            position="Software Engineer",
            package="12 LPA",
            location="Bangalore",
            last_date="2024-01-15",
            requirements="Python, Java, React"
        )
        print(sample_message[:200] + "..." if len(sample_message) > 200 else sample_message)

def demo_scheduler():
    """Demonstrate scheduler functionality"""
    print("\n⏰ Scheduler Demo")
    print("=" * 40)
    
    scheduler = MessageScheduler()
    dm = DataManager()
    
    # Get some students for demo
    students = dm.get_students_list()[:2]  # Just 2 students for demo
    
    if students:
        # Create a demo reminder job
        future_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        
        job_id = scheduler.add_reminder_job(
            job_id=f"demo_job_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            company="DemoTech",
            position="Developer",
            deadline=future_date,
            students=students,
            reminder_days_before=[7, 3, 1]
        )
        
        print(f"✅ Created demo reminder job: {job_id}")
        print(f"📅 Deadline: {future_date}")
        print(f"👥 Students: {len(students)}")
        print("🔔 Reminders scheduled for: 7, 3, 1 days before deadline")
        
        # Show job status
        job_status = scheduler.get_job_status(job_id)
        if job_status:
            print(f"\n📊 Job Status:")
            print(f"- Status: {job_status['status']}")
            print(f"- Reminder dates: {len(job_status['reminder_dates'])}")
            for i, reminder in enumerate(job_status['reminder_dates'], 1):
                print(f"  {i}. {reminder['date'][:10]} ({reminder['days_before']} days before)")
    
    else:
        print("❌ No students available for demo")

def demo_cli_examples():
    """Show CLI usage examples"""
    print("\n💻 CLI Usage Examples")
    print("=" * 40)
    
    examples = [
        {
            "description": "Send messages to all CS students with CGPA >= 8.0",
            "command": """python main.py send \\
    --company "TechCorp" \\
    --position "Software Engineer" \\
    --package "12 LPA" \\
    --location "Bangalore" \\
    --deadline "2024-01-15" \\
    --min-cgpa 8.0 \\
    --courses "Computer Science" \\
    --setup-reminders"""
        },
        {
            "description": "Filter by skills and years",
            "command": """python main.py send \\
    --company "DataInc" \\
    --position "Data Scientist" \\
    --package "15 LPA" \\
    --location "Mumbai" \\
    --deadline "2024-01-20" \\
    --skills "Python" "Machine Learning" \\
    --years 3 4"""
        },
        {
            "description": "Start the scheduler for automatic reminders",
            "command": "python main.py scheduler start"
        },
        {
            "description": "Check status of all jobs",
            "command": "python main.py status"
        },
        {
            "description": "List all students",
            "command": "python main.py students list"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['description']}:")
        print("   " + example['command'].replace("\n", "\n   "))

def main():
    """Run all demos"""
    print("🎯 WhatsApp Bulk Messaging System - Demo")
    print("=" * 50)
    print()
    
    try:
        demo_data_management()
        demo_message_templates()
        demo_scheduler()
        demo_cli_examples()
        
        print("\n" + "=" * 50)
        print("✅ Demo completed successfully!")
        print("\n🚀 Next Steps:")
        print("1. Run: python main.py --help (for full CLI help)")
        print("2. Run: python web_interface.py (for web interface)")
        print("3. Start scheduler: python main.py scheduler start")
        print("4. Check README.md for detailed documentation")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
