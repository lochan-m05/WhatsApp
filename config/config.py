"""
Configuration settings for WhatsApp Bulk Messaging System
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
SRC_DIR = BASE_DIR / "src"

# WhatsApp Web settings
WHATSAPP_WEB_URL = "https://web.whatsapp.com"
WAIT_TIME = 20  # seconds to wait for elements to load
MESSAGE_DELAY = 3  # seconds between messages to avoid being blocked

# File paths
STUDENTS_FILE = DATA_DIR / "students.xlsx"
MESSAGES_FILE = DATA_DIR / "messages.json"
LOG_FILE = LOGS_DIR / "whatsapp_bulk.log"

# Chrome driver settings
CHROME_PROFILE_PATH = os.path.expanduser("~/chrome-whatsapp-profile")
HEADLESS_MODE = False  # Set to True for headless operation

# Message templates
DEFAULT_MESSAGE_TEMPLATE = """
🎯 *Placement Opportunity Alert* 🎯

Dear {name},

We have an exciting placement opportunity that matches your profile:

*Company:* {company}
*Position:* {position}
*Package:* {package}
*Location:* {location}
*Last Date to Apply:* {last_date}

*Requirements:*
{requirements}

Please reply with "INTERESTED" if you want to apply for this position.

Best regards,
Placement Cell
"""

# Reminder settings
REMINDER_TIMES = ["09:00", "14:00", "18:00"]  # Times to send reminders (24-hour format)
REMINDER_DAYS_BEFORE = [7, 3, 1]  # Days before deadline to send reminders

# Excel column mappings
STUDENT_COLUMNS = {
    'name': 'Name',
    'phone': 'Phone',
    'email': 'Email',
    'course': 'Course',
    'year': 'Year',
    'cgpa': 'CGPA',
    'skills': 'Skills'
}
