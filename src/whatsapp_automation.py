"""
WhatsApp Web automation for bulk messaging
"""

import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from loguru import logger
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import *

class WhatsAppAutomation:
    def __init__(self, headless=False):
        self.driver = None
        self.wait = None
        self.headless = headless
        self.setup_logger()
        
    def setup_logger(self):
        """Setup logging configuration"""
        LOGS_DIR.mkdir(exist_ok=True)
        logger.add(
            LOG_FILE,
            rotation="1 day",
            retention="7 days",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
        )
        logger.info("WhatsApp Automation initialized")
    
    def setup_driver(self):
        """Setup Chrome WebDriver with WhatsApp profile"""
        try:
            chrome_options = Options()
            
            # Create profile directory if it doesn't exist
            os.makedirs(CHROME_PROFILE_PATH, exist_ok=True)
            
            # Chrome options
            chrome_options.add_argument(f"--user-data-dir={CHROME_PROFILE_PATH}")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-first-run")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # Setup ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, WAIT_TIME)
            
            logger.info("Chrome WebDriver initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {e}")
            return False
    
    def login_whatsapp(self):
        """Open WhatsApp Web and wait for login"""
        try:
            self.driver.get(WHATSAPP_WEB_URL)
            logger.info("Navigated to WhatsApp Web")
            
            # Wait for either QR code or chat list (if already logged in)
            try:
                # Try to find QR code (means not logged in)
                qr_code = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='qr-code']")))
                logger.info("QR code found. Please scan QR code to login to WhatsApp Web")
                
                # Wait for login completion (QR code disappears)
                WebDriverWait(self.driver, 60).until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, "[data-testid='qr-code']"))
                )
                logger.info("Login successful")
                
            except TimeoutException:
                # QR code not found, might already be logged in
                try:
                    # Check if chat list is visible
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='chat-list']")))
                    logger.info("Already logged in to WhatsApp Web")
                except TimeoutException:
                    logger.error("Unable to determine login status")
                    return False
            
            # Wait for chat interface to fully load
            time.sleep(5)
            return True
            
        except Exception as e:
            logger.error(f"Failed to login to WhatsApp: {e}")
            return False
    
    def search_contact(self, phone_number):
        """Search for a contact by phone number"""
        try:
            # Clean phone number (remove spaces, hyphens, etc.)
            clean_phone = ''.join(filter(str.isdigit, phone_number))
            if not clean_phone.startswith('+'):
                clean_phone = '+91' + clean_phone  # Default to India (+91)
            
            # Click on search box
            search_box = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='search-input']"))
            )
            search_box.clear()
            search_box.send_keys(clean_phone)
            
            time.sleep(2)
            
            # Click on the first search result
            try:
                first_result = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='cell-frame-container']"))
                )
                first_result.click()
                time.sleep(2)
                return True
            except TimeoutException:
                logger.warning(f"Contact not found for phone number: {phone_number}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to search contact {phone_number}: {e}")
            return False
    
    def send_message(self, message):
        """Send a message to the currently selected chat"""
        try:
            # Find message input box
            message_box = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='conversation-compose-box-input']"))
            )
            
            # Clear and type message
            message_box.clear()
            
            # Split message into lines and send
            lines = message.split('\n')
            for i, line in enumerate(lines):
                message_box.send_keys(line)
                if i < len(lines) - 1:
                    # Send Shift+Enter for new line
                    message_box.send_keys(u'\ue008' + u'\ue007')  # Shift + Enter
            
            time.sleep(1)
            
            # Send message
            send_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='send']")
            send_button.click()
            
            time.sleep(MESSAGE_DELAY)
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def send_bulk_messages(self, contacts, message_template, **template_vars):
        """Send bulk messages to multiple contacts"""
        sent_count = 0
        failed_contacts = []
        
        logger.info(f"Starting bulk message sending to {len(contacts)} contacts")
        
        for i, contact in enumerate(contacts, 1):
            try:
                name = contact.get('name', 'Student')
                phone = contact.get('phone', '')
                
                if not phone:
                    logger.warning(f"No phone number for {name}, skipping")
                    failed_contacts.append({'name': name, 'phone': phone, 'reason': 'No phone number'})
                    continue
                
                logger.info(f"Sending message {i}/{len(contacts)} to {name} ({phone})")
                
                # Search and select contact
                if not self.search_contact(phone):
                    failed_contacts.append({'name': name, 'phone': phone, 'reason': 'Contact not found'})
                    continue
                
                # Personalize message
                personalized_message = message_template.format(
                    name=name,
                    **template_vars,
                    **contact
                )
                
                # Send message
                if self.send_message(personalized_message):
                    sent_count += 1
                    logger.info(f"✅ Message sent to {name}")
                else:
                    failed_contacts.append({'name': name, 'phone': phone, 'reason': 'Failed to send'})
                
                # Clear search to prepare for next contact
                search_box = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='search-input']")
                search_box.clear()
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error sending message to {name}: {e}")
                failed_contacts.append({'name': name, 'phone': phone, 'reason': str(e)})
        
        logger.info(f"Bulk messaging completed. Sent: {sent_count}, Failed: {len(failed_contacts)}")
        return sent_count, failed_contacts
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
