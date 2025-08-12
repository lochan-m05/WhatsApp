# WhatsApp Bulk Messaging System for Placement Offers

A comprehensive automated system to send bulk WhatsApp messages to students regarding placement opportunities with built-in reminder functionality.

## 🌟 Features

- **Bulk Messaging**: Send personalized placement messages to multiple students simultaneously
- **Smart Filtering**: Filter students by CGPA, course, year, skills, etc.
- **Automated Reminders**: Set automatic reminder messages before application deadlines
- **Message Templates**: Customizable message templates for different scenarios
- **Scheduling**: Schedule messages to be sent at specific times
- **Student Management**: Add, edit, and manage student database
- **Logging**: Comprehensive logging for tracking and debugging
- **CLI Interface**: Easy-to-use command-line interface
- **Excel Integration**: Import/export student data from Excel files

## 📋 Requirements

- Python 3.8 or later
- Google Chrome browser
- WhatsApp account
- Linux/macOS/Windows operating system

## 🚀 Installation

### Quick Setup

1. **Clone/Download the project**
   ```bash
   git clone <repository-url>
   cd whatsapp-placement-system
   ```

2. **Run the setup script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Activate virtual environment**
   ```bash
   source venv/bin/activate
   ```

### Manual Setup

1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Google Chrome** (if not already installed)

3. **Create necessary directories**
   ```bash
   mkdir -p data logs config
   ```

## 📊 Student Data Format

The system expects student data in Excel format with the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| Name | Student's full name | John Doe |
| Phone | Phone number with country code | +919876543210 |
| Email | Email address | john.doe@email.com |
| Course | Course/Branch | Computer Science |
| Year | Current year | 4 |
| CGPA | Current CGPA | 8.5 |
| Skills | Technical skills | Python, Java, React |

## 🎯 Usage

### 1. Send Placement Messages

Send bulk messages about a placement opportunity:

```bash
python main.py send \
    --company "TechCorp" \
    --position "Software Engineer" \
    --package "12 LPA" \
    --location "Bangalore" \
    --deadline "2024-01-15" \
    --min-cgpa 7.0 \
    --courses "Computer Science" "Information Technology" \
    --setup-reminders
```

### 2. Filter Students

Filter students based on specific criteria:

```bash
# Filter by CGPA and skills
python main.py send \
    --company "DataCorp" \
    --position "Data Scientist" \
    --package "15 LPA" \
    --location "Mumbai" \
    --deadline "2024-01-20" \
    --min-cgpa 8.0 \
    --skills "Python" "Machine Learning"

# Filter by year and course
python main.py send \
    --company "StartupXYZ" \
    --position "Full Stack Developer" \
    --package "8 LPA" \
    --location "Remote" \
    --deadline "2024-01-25" \
    --years 3 4 \
    --courses "Computer Science"
```

### 3. Manage Students

Add, list, or export student data:

```bash
# List all students
python main.py students list

# Add a new student (interactive)
python main.py students add

# Export filtered students to Excel
python main.py students export --course "Computer Science" --year 4
```

### 4. Setup Automated Reminders

Set up reminder messages for placement deadlines:

```bash
python main.py reminders \
    --company "TechCorp" \
    --position "Software Engineer" \
    --deadline "2024-01-15" \
    --reminder-days 7 3 1
```

### 5. Start the Scheduler

Start the background scheduler for automated reminders:

```bash
python main.py scheduler start
```

### 6. Check Status

View the status of scheduled jobs:

```bash
python main.py status
```

## 📝 Message Templates

### Default Templates

1. **Placement Alert**: Main placement opportunity notification
2. **Reminder**: Deadline reminder messages
3. **Interview Schedule**: Interview scheduling notifications

### Customization

You can customize message templates by editing the `data/messages.json` file or through the data manager API.

Example placement alert template:
```
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
```

## ⚙️ Configuration

Key configuration options in `config/config.py`:

- `MESSAGE_DELAY`: Delay between messages (default: 3 seconds)
- `WAIT_TIME`: Time to wait for WhatsApp elements to load
- `REMINDER_TIMES`: Times to check for reminders
- `REMINDER_DAYS_BEFORE`: Default days before deadline for reminders

## 🔄 Scheduler System

The scheduler runs in the background and:

- Checks for due reminder messages every minute
- Sends automatic reminders based on configured days before deadline
- Cleans up completed jobs daily
- Maintains logs for all operations

### Starting the Scheduler as a Service

For production use, run the scheduler as a background service:

```bash
# Using nohup
nohup python main.py scheduler start > logs/scheduler_output.log 2>&1 &

# Using screen
screen -S whatsapp-scheduler
python main.py scheduler start

# Using systemd (create service file)
sudo systemctl start whatsapp-placement-scheduler
```

## 📊 Logging

Logs are stored in the `logs/` directory:

- `logs/whatsapp_bulk.log`: Main application logs
- `logs/scheduler.log`: Scheduler-specific logs

Log files are rotated daily and kept for 7-30 days.

## 🔒 Security Considerations

1. **Phone Numbers**: Store phone numbers with country codes
2. **Rate Limiting**: Built-in delays prevent WhatsApp blocking
3. **Data Privacy**: Student data is stored locally
4. **Chrome Profile**: Separate Chrome profile for WhatsApp isolation

## 🐛 Troubleshooting

### Common Issues

1. **WhatsApp Login Issues**
   - Ensure you're scanning the QR code with the correct WhatsApp account
   - Clear Chrome cache if login fails
   - Check if WhatsApp Web is accessible

2. **Contact Not Found**
   - Verify phone numbers have country codes (+91 for India)
   - Ensure contacts exist in your WhatsApp
   - Check phone number format in Excel file

3. **Chrome Driver Issues**
   - System will auto-download correct ChromeDriver version
   - Ensure Google Chrome is installed and updated

4. **Permission Errors**
   - Run with appropriate permissions
   - Check file/directory permissions in project folder

### Debug Mode

Enable debug logging by modifying the log level in the code:
```python
logger.add(LOG_FILE, level="DEBUG")
```

## 📈 Advanced Usage

### Custom Student File

Use a custom Excel file for student data:

```bash
python main.py send \
    --student-file "/path/to/custom_students.xlsx" \
    --company "TechCorp" \
    --position "Developer" \
    --package "10 LPA" \
    --location "Delhi" \
    --deadline "2024-01-30"
```

### Headless Mode

Run without GUI (useful for servers):

```bash
python main.py send \
    --headless \
    --auto-confirm \
    --company "TechCorp" \
    --position "Developer" \
    --package "10 LPA" \
    --location "Chennai" \
    --deadline "2024-02-01"
```

### Batch Operations

Process multiple placement opportunities:

```bash
#!/bin/bash

# Multiple companies
companies=("TechCorp" "DataInc" "StartupXYZ")
positions=("Developer" "Analyst" "Engineer")
packages=("10 LPA" "12 LPA" "8 LPA")

for i in ${!companies[@]}; do
    python main.py send \
        --company "${companies[$i]}" \
        --position "${positions[$i]}" \
        --package "${packages[$i]}" \
        --location "Bangalore" \
        --deadline "2024-01-30" \
        --auto-confirm \
        --setup-reminders
done
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

- Use responsibly and in compliance with WhatsApp's Terms of Service
- Ensure you have consent from recipients before sending messages
- This tool is for educational and legitimate business purposes only
- The developers are not responsible for misuse of this system

## 🆘 Support

For support and questions:

1. Check the troubleshooting section
2. Review logs in the `logs/` directory
3. Create an issue on the repository
4. Contact the development team

## 🔮 Future Enhancements

- [ ] Web-based GUI interface
- [ ] Multiple WhatsApp account support
- [ ] Advanced analytics and reporting
- [ ] Integration with placement portals
- [ ] SMS backup messaging
- [ ] Mobile app companion
- [ ] Multi-language support

---

**Made with ❤️ for placement teams and students**
