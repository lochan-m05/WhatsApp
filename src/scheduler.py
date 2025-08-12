"""
Scheduler for automated WhatsApp messages and reminders
"""

import schedule
import time
import json
import os
import sys
from datetime import datetime, timedelta
from threading import Thread
from loguru import logger

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import *
from src.whatsapp_automation import WhatsAppAutomation
from src.data_manager import DataManager

class MessageScheduler:
    def __init__(self):
        self.data_manager = DataManager()
        self.scheduled_jobs = []
        self.is_running = False
        self.scheduler_thread = None
        self.setup_logger()
    
    def setup_logger(self):
        """Setup logging for scheduler"""
        LOGS_DIR.mkdir(exist_ok=True)
        logger.add(
            LOGS_DIR / "scheduler.log",
            rotation="1 day",
            retention="30 days",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
        )
        logger.info("Message Scheduler initialized")
    
    def load_scheduled_jobs(self):
        """Load scheduled jobs from file"""
        jobs_file = DATA_DIR / "scheduled_jobs.json"
        try:
            if os.path.exists(jobs_file):
                with open(jobs_file, 'r') as f:
                    self.scheduled_jobs = json.load(f)
                logger.info(f"Loaded {len(self.scheduled_jobs)} scheduled jobs")
            else:
                self.scheduled_jobs = []
                logger.info("No existing scheduled jobs found")
        except Exception as e:
            logger.error(f"Failed to load scheduled jobs: {e}")
            self.scheduled_jobs = []
    
    def save_scheduled_jobs(self):
        """Save scheduled jobs to file"""
        jobs_file = DATA_DIR / "scheduled_jobs.json"
        try:
            with open(jobs_file, 'w') as f:
                json.dump(self.scheduled_jobs, f, indent=2, default=str)
            logger.info("Scheduled jobs saved")
        except Exception as e:
            logger.error(f"Failed to save scheduled jobs: {e}")
    
    def add_reminder_job(self, job_id, company, position, deadline, students, 
                        reminder_days_before=None):
        """Add a reminder job for placement deadline"""
        if reminder_days_before is None:
            reminder_days_before = REMINDER_DAYS_BEFORE
        
        deadline_date = datetime.strptime(deadline, "%Y-%m-%d")
        
        job_data = {
            "job_id": job_id,
            "type": "placement_reminder",
            "company": company,
            "position": position,
            "deadline": deadline,
            "students": students,
            "reminder_dates": [],
            "status": "active",
            "created_at": datetime.now().isoformat()
        }
        
        # Calculate reminder dates
        for days_before in reminder_days_before:
            reminder_date = deadline_date - timedelta(days=days_before)
            if reminder_date >= datetime.now():
                job_data["reminder_dates"].append({
                    "date": reminder_date.isoformat(),
                    "days_before": days_before,
                    "sent": False
                })
        
        self.scheduled_jobs.append(job_data)
        self.save_scheduled_jobs()
        logger.info(f"Added reminder job for {company} - {position}")
        return job_id
    
    def add_scheduled_message(self, job_id, students, message_template, 
                            template_vars, send_time):
        """Add a scheduled message to be sent at specific time"""
        job_data = {
            "job_id": job_id,
            "type": "scheduled_message",
            "students": students,
            "message_template": message_template,
            "template_vars": template_vars,
            "send_time": send_time,
            "status": "active",
            "sent": False,
            "created_at": datetime.now().isoformat()
        }
        
        self.scheduled_jobs.append(job_data)
        self.save_scheduled_jobs()
        logger.info(f"Added scheduled message job: {job_id}")
        return job_id
    
    def send_reminder_messages(self, job):
        """Send reminder messages for a placement opportunity"""
        try:
            logger.info(f"Sending reminder messages for job: {job['job_id']}")
            
            # Get reminder template
            reminder_template = self.data_manager.get_template("reminder")
            if not reminder_template:
                logger.error("Reminder template not found")
                return False
            
            # Calculate days remaining
            deadline_date = datetime.strptime(job['deadline'], "%Y-%m-%d")
            days_remaining = (deadline_date - datetime.now()).days
            
            # Template variables
            template_vars = {
                'company': job['company'],
                'position': job['position'],
                'last_date': job['deadline'],
                'days_remaining': days_remaining
            }
            
            # Send messages
            with WhatsAppAutomation() as wa:
                if not wa.setup_driver():
                    logger.error("Failed to setup WhatsApp driver")
                    return False
                
                if not wa.login_whatsapp():
                    logger.error("Failed to login to WhatsApp")
                    return False
                
                sent_count, failed_contacts = wa.send_bulk_messages(
                    job['students'], reminder_template, **template_vars
                )
                
                logger.info(f"Reminder messages sent: {sent_count}, Failed: {len(failed_contacts)}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to send reminder messages: {e}")
            return False
    
    def send_scheduled_message(self, job):
        """Send a scheduled message"""
        try:
            logger.info(f"Sending scheduled message for job: {job['job_id']}")
            
            with WhatsAppAutomation() as wa:
                if not wa.setup_driver():
                    logger.error("Failed to setup WhatsApp driver")
                    return False
                
                if not wa.login_whatsapp():
                    logger.error("Failed to login to WhatsApp")
                    return False
                
                sent_count, failed_contacts = wa.send_bulk_messages(
                    job['students'], 
                    job['message_template'], 
                    **job['template_vars']
                )
                
                # Mark as sent
                job['sent'] = True
                job['sent_at'] = datetime.now().isoformat()
                job['sent_count'] = sent_count
                job['failed_count'] = len(failed_contacts)
                
                self.save_scheduled_jobs()
                
                logger.info(f"Scheduled messages sent: {sent_count}, Failed: {len(failed_contacts)}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to send scheduled message: {e}")
            return False
    
    def check_reminders(self):
        """Check and send due reminder messages"""
        logger.debug("Checking for due reminders...")
        current_time = datetime.now()
        
        for job in self.scheduled_jobs:
            if job['type'] == 'placement_reminder' and job['status'] == 'active':
                for reminder in job['reminder_dates']:
                    if not reminder['sent']:
                        reminder_time = datetime.fromisoformat(reminder['date'])
                        if current_time >= reminder_time:
                            logger.info(f"Sending reminder for {job['company']} - {job['position']}")
                            if self.send_reminder_messages(job):
                                reminder['sent'] = True
                                reminder['sent_at'] = current_time.isoformat()
                                self.save_scheduled_jobs()
    
    def check_scheduled_messages(self):
        """Check and send due scheduled messages"""
        logger.debug("Checking for scheduled messages...")
        current_time = datetime.now()
        
        for job in self.scheduled_jobs:
            if (job['type'] == 'scheduled_message' and 
                job['status'] == 'active' and not job['sent']):
                
                send_time = datetime.fromisoformat(job['send_time'])
                if current_time >= send_time:
                    logger.info(f"Sending scheduled message: {job['job_id']}")
                    self.send_scheduled_message(job)
    
    def setup_schedule(self):
        """Setup the recurring schedule checks"""
        # Check for due messages every minute
        schedule.every().minute.do(self.check_reminders)
        schedule.every().minute.do(self.check_scheduled_messages)
        
        # Daily cleanup of completed jobs
        schedule.every().day.at("00:00").do(self.cleanup_old_jobs)
        
        logger.info("Schedule setup completed")
    
    def cleanup_old_jobs(self):
        """Remove completed and old jobs"""
        try:
            current_time = datetime.now()
            active_jobs = []
            
            for job in self.scheduled_jobs:
                # Keep active jobs
                if job['status'] == 'active':
                    if job['type'] == 'placement_reminder':
                        # Check if all reminders are sent
                        all_sent = all(r['sent'] for r in job['reminder_dates'])
                        if not all_sent:
                            active_jobs.append(job)
                        else:
                            logger.info(f"Removing completed reminder job: {job['job_id']}")
                    
                    elif job['type'] == 'scheduled_message':
                        if not job['sent']:
                            active_jobs.append(job)
                        else:
                            # Keep for 7 days after sending
                            sent_time = datetime.fromisoformat(job.get('sent_at', job['created_at']))
                            if (current_time - sent_time).days < 7:
                                active_jobs.append(job)
                            else:
                                logger.info(f"Removing old scheduled message job: {job['job_id']}")
            
            if len(active_jobs) != len(self.scheduled_jobs):
                self.scheduled_jobs = active_jobs
                self.save_scheduled_jobs()
                logger.info(f"Cleanup completed. Active jobs: {len(active_jobs)}")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old jobs: {e}")
    
    def start_scheduler(self):
        """Start the scheduler in a separate thread"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.load_scheduled_jobs()
        self.setup_schedule()
        self.is_running = True
        
        def run_scheduler():
            logger.info("Scheduler started")
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
            logger.info("Scheduler stopped")
        
        self.scheduler_thread = Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("Scheduler thread started")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        schedule.clear()
        logger.info("Scheduler stopped")
    
    def get_job_status(self, job_id=None):
        """Get status of scheduled jobs"""
        if job_id:
            for job in self.scheduled_jobs:
                if job['job_id'] == job_id:
                    return job
            return None
        else:
            return self.scheduled_jobs
    
    def cancel_job(self, job_id):
        """Cancel a scheduled job"""
        for job in self.scheduled_jobs:
            if job['job_id'] == job_id:
                job['status'] = 'cancelled'
                job['cancelled_at'] = datetime.now().isoformat()
                self.save_scheduled_jobs()
                logger.info(f"Job cancelled: {job_id}")
                return True
        logger.warning(f"Job not found: {job_id}")
        return False
