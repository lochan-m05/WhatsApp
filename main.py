#!/usr/bin/env python3
"""
WhatsApp Bulk Messaging System for Placement Offers
Main CLI Application
"""

import argparse
import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.whatsapp_automation import WhatsAppAutomation
from src.data_manager import DataManager
from src.scheduler import MessageScheduler
from config.config import *

def send_placement_messages(args):
    """Send placement opportunity messages to students"""
    print("🎯 Sending Placement Messages...")
    
    # Initialize data manager
    dm = DataManager()
    
    # Load students
    if args.student_file:
        students = dm.load_students(args.student_file)
    else:
        students = dm.load_students()
    
    if students is None:
        print("❌ Failed to load student data")
        return
    
    # Apply filters
    filtered_students = dm.filter_students_by_criteria(
        min_cgpa=args.min_cgpa,
        courses=args.courses,
        years=args.years,
        skills=args.skills
    )
    
    if not filtered_students:
        print("❌ No students match the criteria")
        return
    
    print(f"📊 Found {len(filtered_students)} students matching criteria")
    
    # Get template
    template = dm.get_template("placement_alert")
    if not template:
        print("❌ Placement alert template not found")
        return
    
    # Template variables
    template_vars = {
        'company': args.company,
        'position': args.position,
        'package': args.package,
        'location': args.location,
        'last_date': args.deadline,
        'requirements': args.requirements or "As per job description"
    }
    
    # Confirm before sending
    print(f"\n📋 Message Details:")
    print(f"Company: {args.company}")
    print(f"Position: {args.position}")
    print(f"Package: {args.package}")
    print(f"Location: {args.location}")
    print(f"Deadline: {args.deadline}")
    print(f"Recipients: {len(filtered_students)} students")
    
    if not args.auto_confirm:
        confirm = input("\n🤔 Do you want to proceed? (y/N): ")
        if confirm.lower() != 'y':
            print("❌ Cancelled by user")
            return
    
    # Send messages
    with WhatsAppAutomation(headless=args.headless) as wa:
        if not wa.setup_driver():
            print("❌ Failed to setup WhatsApp driver")
            return
        
        print("\n🔗 Please scan QR code if prompted...")
        if not wa.login_whatsapp():
            print("❌ Failed to login to WhatsApp")
            return
        
        print("📤 Sending messages...")
        sent_count, failed_contacts = wa.send_bulk_messages(
            filtered_students, template, **template_vars
        )
        
        print(f"\n✅ Messaging completed!")
        print(f"📊 Messages sent: {sent_count}")
        print(f"❌ Failed: {len(failed_contacts)}")
        
        if failed_contacts:
            print(f"\nFailed contacts:")
            for contact in failed_contacts:
                print(f"  - {contact['name']} ({contact['phone']}): {contact['reason']}")
    
    # Setup reminders if requested
    if args.setup_reminders and args.deadline:
        scheduler = MessageScheduler()
        job_id = f"placement_{args.company}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        scheduler.add_reminder_job(
            job_id=job_id,
            company=args.company,
            position=args.position,
            deadline=args.deadline,
            students=filtered_students
        )
        
        print(f"\n🔔 Reminders scheduled with job ID: {job_id}")

def setup_reminders(args):
    """Setup reminder messages for placement deadline"""
    print("🔔 Setting up Reminders...")
    
    scheduler = MessageScheduler()
    dm = DataManager()
    
    # Load students
    students = dm.get_students_list()
    if args.student_filter:
        # Apply any filters here if needed
        pass
    
    job_id = f"reminder_{args.company}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    scheduler.add_reminder_job(
        job_id=job_id,
        company=args.company,
        position=args.position,
        deadline=args.deadline,
        students=students,
        reminder_days_before=args.reminder_days
    )
    
    print(f"✅ Reminders scheduled with job ID: {job_id}")
    print(f"📅 Deadline: {args.deadline}")
    print(f"🔔 Reminder days before: {args.reminder_days}")

def start_scheduler(args):
    """Start the message scheduler daemon"""
    print("🚀 Starting Message Scheduler...")
    
    scheduler = MessageScheduler()
    
    try:
        scheduler.start_scheduler()
        print("✅ Scheduler started successfully!")
        print("📝 Logs are available in: logs/scheduler.log")
        print("⏹️  Press Ctrl+C to stop the scheduler")
        
        # Keep the main thread alive
        import signal
        import time
        
        def signal_handler(sig, frame):
            print("\n🛑 Stopping scheduler...")
            scheduler.stop_scheduler()
            print("✅ Scheduler stopped")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping scheduler...")
        scheduler.stop_scheduler()
        print("✅ Scheduler stopped")

def show_status(args):
    """Show status of scheduled jobs"""
    print("📊 Scheduler Status...")
    
    scheduler = MessageScheduler()
    scheduler.load_scheduled_jobs()
    
    jobs = scheduler.get_job_status()
    
    if not jobs:
        print("📭 No scheduled jobs found")
        return
    
    print(f"\n📋 Total Jobs: {len(jobs)}")
    
    for job in jobs:
        print(f"\n🆔 Job ID: {job['job_id']}")
        print(f"📝 Type: {job['type']}")
        print(f"📊 Status: {job['status']}")
        print(f"📅 Created: {job['created_at']}")
        
        if job['type'] == 'placement_reminder':
            print(f"🏢 Company: {job['company']}")
            print(f"💼 Position: {job['position']}")
            print(f"⏰ Deadline: {job['deadline']}")
            print(f"👥 Students: {len(job['students'])}")
            
            sent_reminders = sum(1 for r in job['reminder_dates'] if r['sent'])
            total_reminders = len(job['reminder_dates'])
            print(f"🔔 Reminders: {sent_reminders}/{total_reminders} sent")
        
        elif job['type'] == 'scheduled_message':
            print(f"📅 Send Time: {job['send_time']}")
            print(f"👥 Students: {len(job['students'])}")
            print(f"📤 Sent: {'Yes' if job['sent'] else 'No'}")

def manage_students(args):
    """Manage student database"""
    dm = DataManager()
    
    if args.action == 'list':
        students = dm.get_students_list()
        print(f"👥 Total Students: {len(students)}")
        
        for i, student in enumerate(students, 1):
            print(f"\n{i}. {student['name']}")
            print(f"   📞 Phone: {student['phone']}")
            print(f"   📧 Email: {student['email']}")
            print(f"   🎓 Course: {student['course']} (Year {student['year']})")
            print(f"   📊 CGPA: {student['cgpa']}")
    
    elif args.action == 'add':
        student_data = {
            'Name': input("Enter name: "),
            'Phone': input("Enter phone number (with country code): "),
            'Email': input("Enter email: "),
            'Course': input("Enter course: "),
            'Year': int(input("Enter year: ")),
            'CGPA': float(input("Enter CGPA: ")),
            'Skills': input("Enter skills (comma-separated): ")
        }
        
        if dm.add_student(student_data):
            print("✅ Student added successfully!")
        else:
            print("❌ Failed to add student")
    
    elif args.action == 'export':
        filters = {}
        if args.course:
            filters['Course'] = args.course
        if args.year:
            filters['Year'] = args.year
        
        students = dm.get_students_list(filters)
        filename = f"filtered_students_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        if dm.export_filtered_students(students, filename):
            print(f"✅ Exported {len(students)} students to {filename}")
        else:
            print("❌ Failed to export students")

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="WhatsApp Bulk Messaging System for Placement Offers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py send --company "TechCorp" --position "Software Engineer" --package "12 LPA" --location "Bangalore" --deadline "2024-01-15"
  python main.py scheduler start
  python main.py status
  python main.py students list
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Send messages command
    send_parser = subparsers.add_parser('send', help='Send placement messages')
    send_parser.add_argument('--company', required=True, help='Company name')
    send_parser.add_argument('--position', required=True, help='Job position')
    send_parser.add_argument('--package', required=True, help='Salary package')
    send_parser.add_argument('--location', required=True, help='Job location')
    send_parser.add_argument('--deadline', required=True, help='Application deadline (YYYY-MM-DD)')
    send_parser.add_argument('--requirements', help='Job requirements')
    send_parser.add_argument('--min-cgpa', type=float, help='Minimum CGPA filter')
    send_parser.add_argument('--courses', nargs='+', help='Course filter')
    send_parser.add_argument('--years', type=int, nargs='+', help='Year filter')
    send_parser.add_argument('--skills', nargs='+', help='Skills filter')
    send_parser.add_argument('--student-file', help='Custom student Excel file')
    send_parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    send_parser.add_argument('--setup-reminders', action='store_true', help='Setup automatic reminders')
    send_parser.add_argument('--auto-confirm', action='store_true', help='Skip confirmation prompt')
    
    # Scheduler commands
    scheduler_parser = subparsers.add_parser('scheduler', help='Scheduler operations')
    scheduler_subparsers = scheduler_parser.add_subparsers(dest='scheduler_action')
    
    start_scheduler_parser = scheduler_subparsers.add_parser('start', help='Start the scheduler')
    
    # Reminders command
    reminder_parser = subparsers.add_parser('reminders', help='Setup reminders')
    reminder_parser.add_argument('--company', required=True, help='Company name')
    reminder_parser.add_argument('--position', required=True, help='Job position')
    reminder_parser.add_argument('--deadline', required=True, help='Application deadline (YYYY-MM-DD)')
    reminder_parser.add_argument('--reminder-days', type=int, nargs='+', default=[7, 3, 1],
                               help='Days before deadline to send reminders')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show scheduler status')
    
    # Students management
    students_parser = subparsers.add_parser('students', help='Manage students database')
    students_parser.add_argument('action', choices=['list', 'add', 'export'], help='Action to perform')
    students_parser.add_argument('--course', help='Filter by course (for export)')
    students_parser.add_argument('--year', type=int, help='Filter by year (for export)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'send':
            send_placement_messages(args)
        elif args.command == 'scheduler':
            if args.scheduler_action == 'start':
                start_scheduler(args)
            else:
                scheduler_parser.print_help()
        elif args.command == 'reminders':
            setup_reminders(args)
        elif args.command == 'status':
            show_status(args)
        elif args.command == 'students':
            manage_students(args)
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
