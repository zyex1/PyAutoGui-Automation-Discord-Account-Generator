import sys
import os
import json
 
import time
import random
import string
import tempfile
import shutil
import re
import hashlib
import hmac
 
import asyncio
from datetime import datetime, timezone
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QTextEdit, QSpinBox, QCheckBox,
    QGroupBox, QGridLayout, QProgressBar, QFrame,
    QScrollArea, QMessageBox, QDialog, QDialogButtonBox, QSplitter,
    QFileDialog, QComboBox, QSplashScreen
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer,
    QRect, QSize
)
from PyQt6.QtGui import (
    QFont, QIcon, QColor, QPainter, 
    QLinearGradient, QBrush, QPen, QTextCursor, QMouseEvent
)
import multiprocessing
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import requests
import httpx
import zendriver as uc
import psutil
from notifypy import Notify
 
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Robust resource resolver for PyInstaller onefile and dev mode
def resource_path(relative_path: str) -> str:
    try:
        base_path = getattr(sys, '_MEIPASS', None)
        if base_path:
            return os.path.join(base_path, relative_path)
    except Exception:
        pass
    return os.path.join(os.path.abspath('.'), relative_path)

# Get approximate user location (city, country) with a short HTTP call
def resolve_user_location() -> str | None:
    try:
        resp = requests.get('https://ipapi.co/json/', timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            city = data.get('city', 'Unknown')
            country = data.get('country_name', 'Unknown')
            return f"{city}, {country}"
    except Exception:
        return None
    return None

# MongoDB Authentication System
MONGO_URI = "mongodb://blur:zyex1@node-jigsromeo.endercloud.host:5047/"
MONGO_DB_NAME = "test"
MONGO_COLLECTION_NAME = "authusers"
TOOL_NAME = "accgen"  # enforce tool-specific keys

class ModernButton(QPushButton):
    def __init__(self, text, primary=False, icon_text=None):
        super().__init__(text)
        self.primary = primary
        self.icon_text = icon_text
        self.setFixedHeight(35)
        self.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.apply_style()

    def apply_style(self):
        if self.primary:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 rgba(220, 38, 38, 0.8), stop:0.5 rgba(239, 68, 68, 0.8), stop:1 rgba(248, 113, 113, 0.8));
                    color: white;
                    border: 1px solid rgba(220, 38, 38, 0.6);
                    border-radius: 15px;
                    font-weight: bold;
                    padding: 12px 24px;
                    text-align: center;

                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 rgba(239, 68, 68, 0.9), stop:0.5 rgba(248, 113, 113, 0.9), stop:1 rgba(252, 165, 165, 0.9));
                    border-color: rgba(239, 68, 68, 0.8);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 rgba(185, 28, 28, 0.9), stop:0.5 rgba(220, 38, 38, 0.9), stop:1 rgba(239, 68, 68, 0.9));
                    border-color: rgba(185, 28, 28, 0.8);
                }
                QPushButton:disabled {
                    background: rgba(55, 65, 81, 0.6);
                    color: #9ca3af;
    
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 rgba(75, 85, 99, 0.7), stop:1 rgba(55, 65, 81, 0.7));
                    color: #ffffff;
                    border: 2px solid rgba(107, 114, 128, 0.6);
                    border-radius: 12px;
                    padding: 8px 16px;
                    font-weight: 600;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 rgba(220, 38, 38, 0.8), stop:1 rgba(75, 85, 99, 0.8));
                    border-color: rgba(239, 68, 68, 0.8);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 rgba(55, 65, 81, 0.9), stop:1 rgba(31, 41, 55, 0.9));
                    border-color: rgba(220, 38, 38, 0.8);
                }
                QPushButton:disabled {
                    background: rgba(31, 41, 55, 0.6);
                    color: #6b7280;
                    border-color: rgba(55, 65, 81, 0.6);
                }
            """)

class ModernLineEdit(QLineEdit):
    def __init__(self, placeholder=""):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setFixedHeight(36)
        self.setFont(QFont("Segoe UI", 11))
        self.setStyleSheet("""
            QLineEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 rgba(55, 65, 81, 0.8), stop:1 rgba(31, 41, 55, 0.8));
                color: #ffffff;
                border: 2px solid rgba(107, 114, 128, 0.6);
                border-radius: 15px;
                padding: 12px 20px;
                font-size: 11px;
                selection-background-color: rgba(220, 38, 38, 0.3);
            }
            QLineEdit:focus {
                border-color: rgba(220, 38, 38, 0.8);
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 rgba(75, 85, 99, 0.9), stop:1 rgba(55, 65, 81, 0.9));
            }
            QLineEdit:hover {
                border-color: rgba(220, 38, 38, 0.6);
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 rgba(75, 85, 99, 0.9), stop:1 rgba(55, 65, 81, 0.9));
            }
            QLineEdit::placeholder {
                color: #d1d5db;
                font-style: italic;
            }
        """)

class ModernSpinBox(QSpinBox):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(36)
        self.setFont(QFont("Segoe UI", 11))
        self.setStyleSheet("""
            QSpinBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 rgba(75, 85, 99, 0.7), stop:1 rgba(55, 65, 81, 0.7));
                color: #ffffff;
                border: 2px solid rgba(107, 114, 128, 0.6);
                border-radius: 15px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 600;
                selection-background-color: rgba(220, 38, 38, 0.3);
            }
            QSpinBox:focus {
                border-color: rgba(220, 38, 38, 0.8);
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 rgba(220, 38, 38, 0.8), stop:1 rgba(75, 85, 99, 0.8));
            }
            QSpinBox:hover {
                border-color: rgba(220, 38, 38, 0.8);
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 rgba(220, 38, 38, 0.8), stop:1 rgba(75, 85, 99, 0.8));
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 0px;
                height: 0px;
                border: none;
                background: transparent;
            }
            QSpinBox::up-arrow, QSpinBox::down-arrow {
                width: 0px;
                height: 0px;
                border: none;
            }
        """)

class KeyAuth:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.is_connected = False
    
    def connect_to_mongodb(self):
        try:
            self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client[MONGO_DB_NAME]
            self.collection = self.db[MONGO_COLLECTION_NAME]
            self.is_connected = True
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            return False
        except Exception as e:
            return False
    
    def verify_key(self, key):
        if not self.is_connected or self.collection is None:
            return False
        
        try:
            current_time = datetime.now(timezone.utc)
            user = self.collection.find_one({
                "tool": TOOL_NAME,
                "key": key,
                "expiresAt": {"$gt": current_time}
            })
            
            if user:
                return True, user
            else:
                return False, None
        except Exception as e:
            return False, None
    
    def disconnect(self):
        if self.client:
            self.client.close()
            self.is_connected = False

class AuthDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Authentication Required")
        self.setFixedSize(600, 360)
        self.setModal(True)
        self.authenticated = False
        self.auth_system = KeyAuth()
        self.user_data = None
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
        self.setup_ui()
        self.apply_modern_theme()

    def setup_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Centering wrapper
        wrapper = QWidget()
        wrap_layout = QVBoxLayout(wrapper)
        wrap_layout.setContentsMargins(30, 30, 30, 30)
        wrap_layout.setSpacing(0)
        wrap_layout.addStretch()

        # Auth card
        card = QFrame()
        card.setObjectName("authCard")
        card.setStyleSheet("""
            #authCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(30, 15, 15, 0.95), stop:1 rgba(50, 20, 20, 0.95));
                border: 2px solid rgba(220, 38, 38, 0.8);
                border-radius: 14px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 18, 22, 18)
        card_layout.setSpacing(12)
        
        # Title
        title = QLabel("Enter License Key")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff; font-weight: bold;")
        card_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("A valid license key is required to use this application")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: #e5e7eb; font-weight: 500;")
        card_layout.addWidget(subtitle)

        # Input
        self.key_input = ModernLineEdit("Enter your license key...")
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.returnPressed.connect(self.authenticate)
        self.key_input.setStyleSheet(self.key_input.styleSheet() + "\nQLineEdit{border:2px solid #6d28d9;}")
        card_layout.addWidget(self.key_input)
        
        # Status (small, grey)
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setMinimumHeight(22)
        self.status_label.setStyleSheet("color: #ffffff; padding: 4px; font-weight: 500; background: rgba(0,0,0,0.3); border-radius: 4px;")
        card_layout.addWidget(self.status_label)

        # Button row
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.authenticate_btn = ModernButton("Authenticate", primary=True)
        self.authenticate_btn.clicked.connect(self.authenticate)
        btn_row.addWidget(self.authenticate_btn)
        btn_row.addStretch()
        card_layout.addLayout(btn_row)

        wrap_layout.addWidget(card, 0, Qt.AlignmentFlag.AlignHCenter)
        wrap_layout.addStretch()

        root.addWidget(wrapper)
        self.setLayout(root)

    def apply_modern_theme(self):
        self.setStyleSheet("""
            QDialog { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(0, 0, 0, 0.8), stop:1 rgba(20, 0, 0, 0.8)); 
            }
            QLabel { color: #ffffff; background: transparent; }
        """)

    def authenticate(self):
        key = self.key_input.text().strip()
        if not key:
            self.status_label.setText("Please enter a license key")
            return
        self.authenticate_btn.setEnabled(False)
        self.authenticate_btn.setText("Verifying...")
        self.status_label.setText("Connecting to authentication server...")
        QTimer.singleShot(100, lambda: self.complete_auth(key))

    def complete_auth(self, key: str):
        try:
            if not self.auth_system.connect_to_mongodb():
                self.status_label.setText("Cannot connect to server. Check internet connection.")
                self.authenticate_btn.setEnabled(True)
                self.authenticate_btn.setText("Authenticate")
                return
            
            self.status_label.setText("Verifying license key...")
            QApplication.processEvents()
            
            result = self.auth_system.verify_key(key)
            if isinstance(result, tuple):
                is_valid, user_data = result
            else:
                is_valid, user_data = False, None
            
            if is_valid and user_data:
                self.authenticated = True
                self.user_data = user_data
                username = user_data.get('name', 'User')
                self.status_label.setText(f"Welcome, {username}! Authentication successful.")
                self.update_user_stats(user_data)
                try:
                    expires_at = user_data['expiresAt']
                    if expires_at.tzinfo is None:
                        expires_at = expires_at.replace(tzinfo=timezone.utc)
                    current_time = datetime.now(timezone.utc)
                    time_remaining = expires_at - current_time
                    days_remaining = time_remaining.days
                    hours_remaining = time_remaining.seconds // 3600
                    if days_remaining > 0:
                        expiry_text = f"Access expires in {days_remaining} days, {hours_remaining} hours"
                    else:
                        expiry_text = f"Access expires in {hours_remaining} hours"
                    QTimer.singleShot(1500, lambda: self.show_expiry_info(expiry_text))
                except Exception:
                    pass
                self.auth_system.disconnect()
                QTimer.singleShot(3000, self.accept)
            else:
                self.status_label.setText("Invalid or expired license key. Please try again.")
                self.authenticate_btn.setEnabled(True)
                self.authenticate_btn.setText("Authenticate")
                self.key_input.clear()
                self.key_input.setFocus()
                self.auth_system.disconnect()
        except Exception as e:
            self.status_label.setText(f"Authentication error: {str(e)}")
            self.authenticate_btn.setEnabled(True)
            self.authenticate_btn.setText("Authenticate")
            self.auth_system.disconnect()
    
    def show_expiry_info(self, expiry_text: str):
        self.status_label.setText(expiry_text)

    def update_user_stats(self, user_data: dict):
        # Stats are hidden in the new design; this is a safe no-op
        pass
    
    def get_user_location(self):
        try:
            response = requests.get('https://ipapi.co/json/', timeout=5)
            if response.status_code == 200:
                data = response.json()
                city = data.get('city', 'Unknown')
                country = data.get('country_name', 'Unknown')
                return f"{city}, {country}"
        except Exception:
            return None
        return None

class LogWidget(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 10))
        doc = self.document()
        if doc:
            doc.setMaximumBlockCount(1000)
        self.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #1e293b, stop:1 #0f172a);
                color: #ffffff;
                border: 2px solid #475569;
                border-radius: 15px;
                padding: 15px;
                selection-background-color: rgba(99, 102, 241, 0.3);
                selection-color: #ffffff;
                font-family: 'Consolas', 'Monaco', monospace;
            }
            QScrollBar:vertical {
                background: #334155;
                width: 14px;
                border-radius: 7px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #64748b;
                border-radius: 7px;
                min-height: 25px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: #6366f1;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar:horizontal {
                background: #334155;
                height: 14px;
                border-radius: 7px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #64748b;
                border-radius: 7px;
                min-width: 25px;
                margin: 2px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #6366f1;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
                width: 0px;
            }
            QScrollBar::corner {
                background: #334155;
                border: none;
            }
        """)

    def add_log(self, level, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        colors = {
            "INFO": "#60a5fa",
            "SUCCESS": "#34d399", 
            "WARNING": "#fbbf24",
            "ERROR": "#f87171",
            "DEBUG": "#a855f7"
        }
        
        color = colors.get(level, "#ffffff")
        
        log_entry = f'<span style="color: #94a3b8;">[{timestamp}]</span> '
        log_entry += f'<span style="color: {color}; font-weight: bold;">[{level}]</span> '
        log_entry += f'<span style="color: #ffffff;">{message}</span><br>'
        
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(log_entry)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

class ModernSplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__()
        self.setFixedSize(400, 220)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
    def paintEvent(self, a0):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background with subtle red gradient
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(30, 15, 15, 200))
        gradient.setColorAt(1, QColor(50, 20, 20, 200))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 25, 25)
        
        # Brand text with subtle red gradient
        text_gradient = QLinearGradient(0, 0, self.width(), 0)
        text_gradient.setColorAt(0, QColor(180, 60, 60))
        text_gradient.setColorAt(0.5, QColor(200, 80, 80))
        text_gradient.setColorAt(1, QColor(220, 100, 100))
        painter.setPen(QPen(QBrush(text_gradient), 1))
        font = QFont('Segoe UI', 32, QFont.Weight.ExtraBold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "BLUR TOOLZ")
        
        # Subtitle
        painter.setPen(QColor(254, 202, 202, 200))
        font = QFont('Segoe UI', 12)
        painter.setFont(font)
        subtitle_rect = QRect(0, self.height() - 60, self.width(), 30)
        painter.drawText(subtitle_rect, Qt.AlignmentFlag.AlignCenter, "Discord Account Creator")
        
        # Developer
        painter.setPen(QColor(239, 68, 68, 200))
        font = QFont('Segoe UI', 10)
        painter.setFont(font)
        dev_rect = QRect(0, self.height() - 35, self.width(), 25)
        painter.drawText(dev_rect, Qt.AlignmentFlag.AlignCenter, "developed by @zyex.1z")

# Discord Account Generation Constants
months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

class AccountGeneratorThread(QThread):
    log_signal = pyqtSignal(str, str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal()
    
    def __init__(self, account_count, config):
        super().__init__()
        self.account_count = account_count
        self.config = config
        self.should_stop = False
        
    def run(self):
        try:
            self.log_signal.emit("INFO", f"Starting generation of {self.account_count} accounts")
            
            for run_count in range(1, self.account_count + 1):
                if self.should_stop:
                    self.log_signal.emit("WARNING", "Generation stopped by user")
                    break
                    
                self.log_signal.emit("INFO", f"Creating account #{run_count}")
                
                try:
                    asyncio.run(self.create_real_discord_account(run_count))
                    
                    self.progress_signal.emit(run_count)
                    self.log_signal.emit("SUCCESS", f"Account #{run_count} created successfully")
                    
                    if not self.should_stop and run_count < self.account_count and self.config.get("check_ratelimit", True):
                        try:
                            wait_time = self.account_ratelimit()
                            max_wait = int(self.config.get("ratelimit_max_wait", 20))
                            original_wait = wait_time
                            if wait_time > max_wait:
                                wait_time = max_wait
                                self.log_signal.emit("WARNING", f"Retry-After was {original_wait}s; capping to {max_wait}s")
                            if wait_time > 1:
                                self.log_signal.emit("WARNING", f"Rate limited — waiting {wait_time} seconds...")
                                self.send_notification("Blur Toolz", f"Ratelimited for {wait_time} seconds!")
                                for i in range(wait_time):
                                    if self.should_stop:
                                        break
                                    self.log_signal.emit("DEBUG", f"Waiting {wait_time - i} more seconds...")
                                    time.sleep(1)
                        except Exception as e:
                            self.log_signal.emit("ERROR", f"Failed to check rate limit: {e}")
                    
                except Exception as e:
                    self.log_signal.emit("ERROR", f"Failed to create account #{run_count}: {str(e)}")
            
            if not self.should_stop:
                self.log_signal.emit("SUCCESS", f"All {self.account_count} accounts generated successfully!")
            
        except Exception as e:
            self.log_signal.emit("ERROR", f"Generation thread error: {str(e)}")
        finally:
            self.finished_signal.emit()

    def generate_random_name(self):
        return ''.join(random.choices(string.ascii_letters, k=8))

    def generate_real_name(self):
        first_names = [
            "Liam","Noah","Oliver","Elijah","James","Benjamin","Lucas","Henry","Alexander","Mason",
            "Michael","Ethan","Daniel","Jacob","Logan","Jackson","Levi","Sebastian","Mateo","Jack",
            "Owen","Theodore","Aiden","Samuel","Joseph","John","David","Wyatt","Matthew","Luke",
            "Julian","Dylan","Isaac","Anthony","Grayson","Andrew","Thomas","Leo","Jaxon","Christopher",
            "Ezra","Hudson","Charles","Maverick","Josiah","Isaiah","Andrew","Ryan","Nathan","Adrian"
        ]
        last_names = [
            "Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Rodriguez","Martinez",
            "Hernandez","Lopez","Gonzalez","Wilson","Anderson","Thomas","Taylor","Moore","Jackson","Martin",
            "Lee","Perez","Thompson","White","Harris","Sanchez","Clark","Ramirez","Lewis","Robinson",
            "Walker","Young","Allen","King","Wright","Scott","Torres","Nguyen","Hill","Flores",
            "Green","Adams","Nelson","Baker","Hall","Rivera","Campbell","Mitchell","Carter","Roberts"
        ]
        return f"{random.choice(first_names)} {random.choice(last_names)}"


    def account_ratelimit(self, email=None, nam=None):
        try:
            headers = {
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.5",
                "Content-Type": "application/json",
                "DNT": "1",
                "Host": "discord.com",
                "Origin": "https://discord.com",
                "Referer": "https://discord.com/register",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Sec-GPC": "1",
                "TE": "trailers",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
                "X-Debug-Options": "bugReporterEnabled",
                "X-Discord-Locale": "en-US",
                "X-Discord-Timezone": "Asia/Calcutta",
            }
            mailbaba = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10))
            email = mailbaba + "@gmail.com"
            nam = self.generate_random_name()
            paassword = "$BlurTUSiCE2169#"
            data = {
                'email': email,
                'password': paassword,
                'date_of_birth': "2000-09-20",
                'username': email,
                'global_name': nam,
                'consent': True,
                'captcha_service': 'hcaptcha',
                'captcha_key': None,
                'invite': None,
                'promotional_email_opt_in': False,
                'gift_code_sku_id': None
            }
            req = requests.post('https://discord.com/api/v9/auth/register', json=data, headers=headers)
            try:
                resp_data = req.json()
            except Exception:
                return 1
            if req.status_code == 429 or 'retry_after' in resp_data:
                limit = resp_data.get('retry_after', 1)
                return int(float(limit)) + 1 if limit else 1
            else:
                return 1
        except Exception as e:
            self.log_signal.emit("ERROR", f"Account ratelimit check failed: {e}")
            return 1

    def create_inbox(self):
        scrambled = "4O)QqiTV+(U+?Vi]qe|6..Xe"
        
        def get_secret_key():
            return ''.join([chr(ord(c) - 2) for c in scrambled])
        
        def sign_payload(payload: dict, secret: str):
            message = json.dumps(payload, separators=(',', ':')).encode()
            key = secret.encode()
            return hmac.new(key, message, hashlib.sha256).hexdigest()
        
        def get_random_fr_ip():
            return f"90.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
        
        timestamp = int(time.time() * 1000)
        domain = self.config.get("mail_domain", "termwave.in")
        api_url = self.config.get("mail_api", "https://api.incognitomail.co/")
        
        payload = {
            "ts": timestamp,
            "domain": domain
        }
        key = get_secret_key()
        payload["key"] = sign_payload(payload, key)
        
        fake_ip = get_random_fr_ip()
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "fr-FR,fr;q=0.9",
            "X-Forwarded-For": fake_ip,
            "X-Real-IP": fake_ip,
            "Via": fake_ip
        }
        
        response = httpx.post(f"{api_url}/inbox/v2/create", json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data["id"], data["token"]
        else:
            raise Exception("Inbox creation failed")

    def poll_for_discord_verification(self, inbox_id, inbox_token):
        scrambled = "4O)QqiTV+(U+?Vi]qe|6..Xe"
        
        def get_secret_key():
            return ''.join([chr(ord(c) - 2) for c in scrambled])
        
        def sign_payload(payload: dict, secret: str):
            message = json.dumps(payload, separators=(',', ':')).encode()
            key = secret.encode()
            return hmac.new(key, message, hashlib.sha256).hexdigest()
        
        secret = get_secret_key()
        api_url = self.config.get("mail_api", "https://api.incognitomail.co/")
        
        for _ in range(500):
            if self.should_stop:
                return None
            
            ts = int(time.time() * 1000)
            payload = {
                "inboxId": inbox_id,
                "inboxToken": inbox_token,
                "ts": ts
            }
            payload["key"] = sign_payload(payload, secret)
            headers = {"Content-Type": "application/json"}
            
            try:
                response = requests.post(f"{api_url}/inbox/v1/list", json=payload, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items")
                    if items:
                        message_url = items[0].get("messageURL")
                        if message_url:
                            email_data = requests.get(message_url, timeout=10).json()
                            subject = email_data.get("subject", "")
                            if "Verify" in subject:
                                content = email_data.get("text", "") + email_data.get("html", "")
                                match = re.search(r'https:\/\/click\.discord\.com[^\s"\'\'<>\\\\]+', content)
                                if match:
                                    link = match.group(0).split("\n")[0].strip()
                                    return link
            except:
                pass
            time.sleep(1)
        return None

    def send_notification(self, title, message):
        if not self.config.get("notify", False):
            return
        try:
            notification = Notify()
            notification.application_name = "Blur Toolz"
            notification.title = title
            notification.message = message
            icon_path = self.config.get("notification_icon")
            if icon_path and os.path.isfile(icon_path):
                notification.icon = icon_path
            notification.send()
        except Exception as e:
            self.log_signal.emit("ERROR", f"Notification error: {e}")

    def close_chrome(self, profile_dir):
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'chrome' in proc.info['name'].lower():
                    cmd = ' '.join(proc.info['cmdline']).lower()
                    if profile_dir.lower() in cmd:
                        proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        shutil.rmtree(profile_dir, ignore_errors=True)

    async def slow_type(self, element, text, delay=0.03):
        for char in text:
            if self.should_stop:
                return
            await element.send_keys(char)
            await asyncio.sleep(delay)

    async def click_dropdown_option(self, tab, expected_text):
        # Try multiple selectors and approaches for dropdown options
        js = f"""
            (() => {{
                // Try different selectors for dropdown options
                const selectors = [
                    'div[class*="option"]',
                    'div[class*="Option"]',
                    'div[role="option"]',
                    'div[class*="menu"] div',
                    'div[class*="Menu"] div',
                    'div[class*="item"]',
                    'div[class*="Item"]',
                    '[data-value]',
                    'li[role="option"]',
                    'div[class*="select"] div'
                ];
                
                for (const selector of selectors) {{
                    const options = document.querySelectorAll(selector);
                    for (const opt of options) {{
                        if (opt.innerText && opt.innerText.trim().toLowerCase() === "{expected_text.lower()}") {{
                            opt.click();
                            return true;
                        }}
                    }}
                }}
                
                // Fallback: try to find by partial match
                for (const selector of selectors) {{
                    const options = document.querySelectorAll(selector);
                    for (const opt of options) {{
                        if (opt.innerText && opt.innerText.trim().toLowerCase().includes("{expected_text.lower()}")) {{
                            opt.click();
                            return true;
                        }}
                    }}
                }}
                
                return false;
            }})()
        """
        result = await tab.evaluate(js)
        return result

    async def fill_dropdown_with_keyboard(self, element, value):
        """Alternative method using keyboard navigation for dropdowns"""
        try:
            # Clear the field first
            await element.clear()
            await asyncio.sleep(0.1)
            
            # Type the value
            await self.slow_type(element, value, delay=0.05)
            await asyncio.sleep(0.2)
            
            # Try pressing Enter to select
            await element.send_keys('\n')
            await asyncio.sleep(0.2)
            
            # Try pressing Tab to move to next field
            await element.send_keys('\t')
            await asyncio.sleep(0.2)
            
            return True
        except Exception as e:
            self.log_signal.emit("WARNING", f"Keyboard dropdown fill failed: {e}")
            return False

    async def create_real_discord_account(self, account_number):
        temp_profile_dir = tempfile.mkdtemp(prefix="chrome-profile-")
        driver = None
        
        try:
            self.log_signal.emit("DEBUG", f"Account #{account_number}: Initializing browser session")
            
            # More comprehensive browser options for Windows
            browser_options = {
                "user_data_dir": temp_profile_dir,
                "no_sandbox": True,
                "disable_web_security": True,
                "disable_features": "VizDisplayCompositor",
                "disable_gpu": True,
                "disable_dev_shm_usage": True,
                "disable_extensions": True,
                "disable_plugins": True,
                "disable_images": True,
                "disable_background_timer_throttling": True,
                "disable_backgrounding_occluded_windows": True,
                "disable_renderer_backgrounding": True,
                "window_size": "1280,720",
                "headless": False,  # Set to True if you want headless mode
                "args": [
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--no-zygote"
                ]
            }
            
            driver = await uc.start(options=browser_options)
            
            # Test browser connection
            self.log_signal.emit("DEBUG", f"Account #{account_number}: Browser started successfully")
            tab = await driver.get("https://discord.com/register")
            
            self.log_signal.emit("DEBUG", f"Account #{account_number}: Creating temporary email")
            inbox_id, inbox_token = self.create_inbox()
            await tab.wait_for_ready_state('complete')
            
            self.log_signal.emit("INFO", f"Account #{account_number}: Using email {inbox_id}")
            
            username = self.generate_random_name()
            global_name = self.generate_real_name()
            
            # Fill email input
            self.log_signal.emit("DEBUG", f"Account #{account_number}: Filling registration form")
            email_input = await tab.select('input[name="email"]', timeout=120_000)
            if email_input:
                await self.slow_type(email_input, inbox_id, delay=0.025)
                await asyncio.sleep(0.15)
            else:
                raise Exception("Email input not found")

            # Fill global name
            global_name_input = await tab.select('input[name="global_name"]', timeout=120_000)
            if global_name_input:
                await self.slow_type(global_name_input, global_name, delay=0.025)
                await asyncio.sleep(0.15)
            else:
                raise Exception("Global name input not found")

            # Fill username
            username_input = await tab.select('input[name="username"]', timeout=120_000)
            if username_input:
                await self.slow_type(username_input, username, delay=0.025)
                await asyncio.sleep(0.15)
            else:
                raise Exception("Username input not found")

            # Fill password
            password_input = await tab.select('input[name="password"]', timeout=120_000)
            if password_input:
                await self.slow_type(password_input, inbox_token, delay=0.025)
                await asyncio.sleep(0.15)
            else:
                raise Exception("Password input not found")

            # Fill birth month
            self.log_signal.emit("DEBUG", f"Account #{account_number}: Filling birth month")
            month = random.choice(months)
            month_selectors = ['#react-select-2-input', 'input[placeholder*="month" i]', 'input[aria-label*="month" i]', 'select[name*="month" i]']
            month_input = None
            for selector in month_selectors:
                try:
                    month_input = await tab.select(selector, timeout=5000)
                    if month_input:
                        break
                except:
                    continue
            
            if month_input:
                await month_input.click()
                await asyncio.sleep(0.2)
                success = await self.click_dropdown_option(tab, month)
                if not success:
                    # Try keyboard method as fallback
                    success = await self.fill_dropdown_with_keyboard(month_input, month)
                await asyncio.sleep(0.3)
            else:
                raise Exception("Month input not found")

            # Fill birth day
            self.log_signal.emit("DEBUG", f"Account #{account_number}: Filling birth day")
            day = f"{random.randint(1, 28)}"
            day_selectors = ['#react-select-3-input', 'input[placeholder*="day" i]', 'input[aria-label*="day" i]', 'select[name*="day" i]']
            day_input = None
            for selector in day_selectors:
                try:
                    day_input = await tab.select(selector, timeout=5000)
                    if day_input:
                        break
                except:
                    continue
            
            if day_input:
                await day_input.click()
                await asyncio.sleep(0.2)
                success = await self.click_dropdown_option(tab, day)
                if not success:
                    # Try keyboard method as fallback
                    success = await self.fill_dropdown_with_keyboard(day_input, day)
                await asyncio.sleep(0.3)
            else:
                raise Exception("Day input not found")

            # Fill birth year
            self.log_signal.emit("DEBUG", f"Account #{account_number}: Filling birth year")
            year = f"{random.randint(1995, 2005)}"
            year_selectors = ['#react-select-4-input', 'input[placeholder*="year" i]', 'input[aria-label*="year" i]', 'select[name*="year" i]']
            year_input = None
            for selector in year_selectors:
                try:
                    year_input = await tab.select(selector, timeout=5000)
                    if year_input:
                        break
                except:
                    continue
            
            if year_input:
                await year_input.click()
                await asyncio.sleep(0.2)
                success = await self.click_dropdown_option(tab, year)
                if not success:
                    # Try keyboard method as fallback
                    success = await self.fill_dropdown_with_keyboard(year_input, year)
                await asyncio.sleep(0.3)
            else:
                raise Exception("Year input not found")

            # Submit form
            submit_button = await tab.select('button[type="submit"]', timeout=120_000)
            if submit_button:
                await asyncio.sleep(0.3)
                await submit_button.mouse_click()
                self.log_signal.emit("INFO", f"Account #{account_number}: Registration form submitted")
            else:
                raise Exception("Submit button not found")

            # Wait for CAPTCHA solving
            self.log_signal.emit("WARNING", f"Account #{account_number}: Please solve CAPTCHA manually!")
            self.send_notification("Blur Toolz", "Please solve the CAPTCHA!")
            
            for attempt in range(300):
                if self.should_stop:
                    return
                try:
                    current_url = await tab.evaluate("window.location.href")
                    if current_url and "discord.com/channels/@me" in str(current_url):
                        self.log_signal.emit("SUCCESS", f"Account #{account_number}: CAPTCHA solved successfully!")
                        break
                except Exception:
                    pass
                await asyncio.sleep(1)
            else:
                raise Exception("CAPTCHA not solved or redirect failed")

            # Poll for verification email
            self.log_signal.emit("DEBUG", f"Account #{account_number}: Waiting for verification email")
            verify_url = self.poll_for_discord_verification(inbox_id, inbox_token)
            
            if not verify_url:
                raise Exception("Could not find verification link in email")
                
            self.log_signal.emit("INFO", f"Account #{account_number}: Email verification link fetched!")
            
            # Open verification link
            await tab.evaluate(f'''
                (() => {{
                    window.open("{verify_url}", "_blank");
                    return "ok";
                }})()
            ''')

            # Wait for email verification
            tabs = driver.tabs
            verify_tab = tabs[-1]
            
            for attempt in range(60):
                if self.should_stop:
                    return
                try:
                    page_text = await verify_tab.evaluate('''
                        (() => {{
                            return document.body.innerText || "NO_TEXT_FOUND";
                        }})()
                    ''')
                    if page_text and "email verified" in str(page_text).lower():
                        self.log_signal.emit("SUCCESS", f"Account #{account_number}: Email verified successfully!")
                        break
                except Exception:
                    pass
                await asyncio.sleep(1)
            else:
                raise Exception("Email verification not detected in time")

            # Auto-close browser after email verification
            self.log_signal.emit("INFO", f"Account #{account_number}: Email verified! Closing browser and continuing...")
            await asyncio.sleep(2)  # Brief pause before closing

            # Extract token
            try:
                session = requests.Session()
                payload = {
                    'login': inbox_id,
                    'password': inbox_token,
                }
                headers = {
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                    'Origin': 'https://discord.com',
                    'Referer': 'https://discord.com/login'
                }
                response = session.post('https://discord.com/api/v9/auth/login', json=payload, headers=headers)
                
                if response.status_code == 200:
                    response_data = response.json()
                    if 'token' in response_data:
                        token = response_data['token']
                        with open('tokens.txt', 'a', encoding='utf-8') as f:
                            f.write(f'{inbox_id}:{inbox_token}:{token}\n')
                            f.flush()
                            os.fsync(f.fileno())
                        self.log_signal.emit("SUCCESS", f"Account #{account_number}: Token extracted {token[:25]}***")
                    else:
                        self.log_signal.emit("WARNING", f"Account #{account_number}: No token in response")
                else:
                    self.log_signal.emit("WARNING", f"Account #{account_number}: Failed to login for token extraction")
            except Exception as e:
                self.log_signal.emit("WARNING", f"Account #{account_number}: Error extracting token: {e}")

        except Exception as e:
            self.log_signal.emit("ERROR", f"Account #{account_number}: {str(e)}")
            raise
        finally:
            try:
                if driver:
                    await driver.stop()
            except Exception as e:
                self.log_signal.emit("WARNING", f"Account #{account_number}: Failed to stop browser: {e}")
            
            try:
                self.close_chrome(temp_profile_dir)
            except Exception as e:
                self.log_signal.emit("WARNING", f"Account #{account_number}: Failed to cleanup: {e}")
    
    def stop(self):
        self.should_stop = True

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blur Toolz - Discord Account Creator")
        self.setFixedSize(1000, 600)
        self.center_window()
        
        # Use native window frame (remove custom header)
        # self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.title_bar_height = 0
        self.drag_position = None
        
        try:
            icon_candidate = resource_path("data/pack.ico")
            if os.path.exists(icon_candidate):
                self.setWindowIcon(QIcon(icon_candidate))
        except Exception:
            pass
        
        self.config = {
            "check_ratelimit": True,
            "notify": True,
            "notification_icon": "data/pack.ico",
            "mail_api": "https://api.incognitomail.co/",
            "mail_domain": "termwave.in",
            "save_tokens": True,
            "ratelimit_max_wait": 20
        }
        
        self.user_data = None
        self.setup_ui()
        self.apply_modern_theme()
        self.load_config()
        self.update_ui_from_config()
        self.generation_thread = None
        self.hide()
        self.is_authenticated = False

        
        # Countdown timer for expiry
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.countdown_timer.start(1000)  # Update every second
        
    
    def create_title_bar(self):
        # No custom title bar anymore
        return QWidget()
    
    def mousePressEvent(self, a0: QMouseEvent | None):
        pass
    
    def mouseMoveEvent(self, a0: QMouseEvent | None):
        pass

    def update_ui_from_config(self):
        """Update UI elements based on loaded configuration"""
        if hasattr(self, 'ratelimit_check'):
            self.ratelimit_check.setChecked(self.config.get("check_ratelimit", True))
        if hasattr(self, 'notify_check'):
            self.notify_check.setChecked(self.config.get("notify", True))
        if hasattr(self, 'ratelimit_cap_input'):
            try:
                self.ratelimit_cap_input.setValue(int(self.config.get("ratelimit_max_wait", 20)))
            except Exception:
                self.ratelimit_cap_input.setValue(20)
        if hasattr(self, 'log_widget') and self.log_widget:
            self.log_widget.add_log("INFO", "UI updated with configuration settings")

    def load_config(self):
        """Load configuration from config.json"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                self.config.update(loaded_config)
            if hasattr(self, 'log_widget') and self.log_widget:
                self.log_widget.add_log("INFO", "Configuration loaded successfully")
        except Exception as e:
            if hasattr(self, 'log_widget') and self.log_widget:
                self.log_widget.add_log("WARNING", f"Failed to load configuration, using defaults: {str(e)}")
    
    def save_config(self):
        """Save current configuration to config.json"""
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            if hasattr(self, 'log_widget'):
                self.log_widget.add_log("WARNING", f"Failed to save configuration: {str(e)}")

    def center_window(self):
        primary_screen = QApplication.primaryScreen()
        if primary_screen:
            screen = primary_screen.geometry()
        else:
            screen = QRect(0, 0, 1920, 1080)
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def setup_ui(self):
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(75, 27, 27, 0.4), stop:1 rgba(127, 29, 29, 0.4)); 
                border: 1px solid rgba(220, 38, 38, 0.6); 
                border-radius: 10px; 
            }
        """)
        
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)
        
        # Content area only (no title bar)
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("""
            QSplitter {
                background: transparent;
                border: none;
            }
            QSplitter::handle {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(220, 38, 38, 0.6), stop:0.5 rgba(239, 68, 68, 0.6), stop:1 rgba(220, 38, 38, 0.6));
                width: 4px;
                border-radius: 2px;
                margin: 2px 0px;
            }
            QSplitter::handle:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(239, 68, 68, 0.8), stop:0.5 rgba(248, 113, 113, 0.8), stop:1 rgba(239, 68, 68, 0.8));
            }
        """)
        
        left_panel = self.create_control_panel()
        right_panel = self.create_right_panel()
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        content_layout.addWidget(splitter)
        main_layout.addLayout(content_layout)
        self.setCentralWidget(container)
        
        # Set main window background to red theme
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #7f1d1d, stop:1 #991b1b);
                color: #ffffff;
            }
        """)

    def create_control_panel(self):
        panel = QWidget()
        panel.setMaximumWidth(420)
        panel.setMinimumWidth(360)
        panel.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(75, 27, 27, 0.3), stop:1 rgba(127, 29, 29, 0.3)); 
                border: 1px solid rgba(220, 38, 38, 0.5); 
                border-radius: 10px; 
                color: #fff; 
            }
            QLabel { color: #fecaca; }
            QCheckBox { color: #fecaca; }
            QGroupBox { border: none; margin: 0; padding: 0; }
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Title section - single banner box
        title_container = QWidget()
        title_container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(75, 27, 27, 0.6), stop:1 rgba(127, 29, 29, 0.6)); 
                border: 2px solid rgba(220, 38, 38, 0.7); 
                border-radius: 12px; 
                padding: 8px;
            }
        """)
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(16, 12, 16, 12)
        title_layout.setSpacing(4)
        
        title = QLabel("Blur Toolz")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff; font-weight: bold;")
        title_layout.addWidget(title)

        subtitle = QLabel("Developed by @zyex.1z")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: #fca5a5; font-weight: 500;")
        title_layout.addWidget(subtitle)
        
        layout.addWidget(title_container)
        
        # Add spacing after title section
        layout.addSpacing(8)

        # Accounts to generate (label + spin)
        count_label = QLabel("Accounts to generate")
        count_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        layout.addWidget(count_label)
        self.account_count_input = ModernSpinBox()
        self.account_count_input.setRange(1, 100)
        self.account_count_input.setValue(1)
        layout.addWidget(self.account_count_input)
        
        # Add spacing after account count section
        layout.addSpacing(8)

        # Settings
        settings_label = QLabel("Settings")
        settings_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        layout.addWidget(settings_label)

        self.ratelimit_check = QCheckBox("Enable rate limiting")
        self.ratelimit_check.setChecked(True)
        layout.addWidget(self.ratelimit_check)

        # Max wait cap for rate limiting
        cap_label = QLabel("Max rate-limit wait (seconds)")
        cap_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        layout.addWidget(cap_label)
        self.ratelimit_cap_input = ModernSpinBox()
        self.ratelimit_cap_input.setRange(1, 300)
        self.ratelimit_cap_input.setValue(int(self.config.get("ratelimit_max_wait", 20)))
        layout.addWidget(self.ratelimit_cap_input)

        self.notify_check = QCheckBox("Enable desktop notifications")
        self.notify_check.setChecked(True)
        layout.addWidget(self.notify_check)
        
        # Add spacing after settings section
        layout.addSpacing(8)

        # Buttons
        self.start_btn = ModernButton("Start Generation", primary=True)
        self.start_btn.clicked.connect(self.start_generation)
        layout.addWidget(self.start_btn)

        self.stop_btn = ModernButton("Stop Generation")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_generation)
        layout.addWidget(self.stop_btn)

        # Hidden progress placeholders to satisfy existing callbacks
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.progress_label)

        layout.addStretch()
        return panel


    def create_right_panel(self):
        """Create the right panel containing both user info and logs sections"""
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(75, 27, 27, 0.3), stop:1 rgba(127, 29, 29, 0.3)); 
                border: 1px solid rgba(220, 38, 38, 0.5); 
                border-radius: 10px; 
                color: #fff; 
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Create user info section
        user_info_section = self.create_user_info_section()
        layout.addWidget(user_info_section)
        
        # Create logs section
        logs_section = self.create_log_section()
        layout.addWidget(logs_section)
        
        return panel

    def create_user_info_section(self):
        """Create the user interface section"""
        section = QWidget()
        section.setMaximumHeight(180)
        section.setStyleSheet("""
            QWidget { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(75, 27, 27, 0.4), stop:1 rgba(127, 29, 29, 0.4)); 
                border: 2px solid rgba(220, 38, 38, 0.6); 
                border-radius: 12px; 
                color: #fff; 
            }
            QLabel { 
                color: #fecaca; 
                background: transparent;
                border: none;
            }
        """)
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        
        # Header
        header = QLabel("User Interface")
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        header.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #ffffff; font-weight: bold;")
        layout.addWidget(header)
        
        # User info grid
        info_grid = QGridLayout()
        info_grid.setSpacing(8)
        
        # Username row
        username_label = QLabel("Username:")
        username_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        username_label.setStyleSheet("color: #f87171; font-weight: 600;")
        self.main_username_value = QLabel("Not authenticated")
        self.main_username_value.setFont(QFont("Segoe UI", 10))
        self.main_username_value.setStyleSheet("color: #ffffff; background: rgba(55, 65, 81, 0.5); padding: 4px 8px; border-radius: 6px;")
        info_grid.addWidget(username_label, 0, 0)
        info_grid.addWidget(self.main_username_value, 0, 1)
        
        # Expiry row
        expiry_label = QLabel("Expires:")
        expiry_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        expiry_label.setStyleSheet("color: #f87171; font-weight: 600;")
        self.main_expiry_value = QLabel("Unknown")
        self.main_expiry_value.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        self.main_expiry_value.setStyleSheet("color: #ffffff; background: rgba(55, 65, 81, 0.5); padding: 4px 8px; border-radius: 6px; font-family: 'Consolas', 'Monaco', monospace;")
        info_grid.addWidget(expiry_label, 1, 0)
        info_grid.addWidget(self.main_expiry_value, 1, 1)
        
        # Location row
        location_label = QLabel("Location:")
        location_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        location_label.setStyleSheet("color: #f87171; font-weight: 600;")
        self.main_location_value = QLabel(resolve_user_location() or "Unknown")
        self.main_location_value.setFont(QFont("Consolas", 9))
        self.main_location_value.setStyleSheet("color: #ffffff; background: rgba(55, 65, 81, 0.5); padding: 4px 8px; border-radius: 6px; font-family: 'Consolas', 'Monaco', monospace;")
        self.main_location_value.setWordWrap(True)
        info_grid.addWidget(location_label, 2, 0)
        info_grid.addWidget(self.main_location_value, 2, 1)
        
        # Set column stretch
        info_grid.setColumnStretch(0, 0)
        info_grid.setColumnStretch(1, 1)
        
        layout.addLayout(info_grid)
        
        return section

    def create_log_section(self):
        """Create the logs section"""
        section = QWidget()
        section.setStyleSheet("""
            QWidget {
                background: transparent;
                border: none;
                color: #fff; 
            }
            QLabel { color: #fecaca; }
        """)
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Application Logs Section
        logs_header = QLabel("Application Logs")
        logs_header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        logs_header.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        layout.addWidget(logs_header)
        
        # Add spacing after header
        layout.addSpacing(8)

        self.log_widget = LogWidget()
        layout.addWidget(self.log_widget)

        # Simple log controls
        btns = QHBoxLayout()
        btns.setSpacing(8)
        
        clear_btn = ModernButton("Clear")
        clear_btn.setFixedHeight(32)
        clear_btn.setFixedWidth(80)
        clear_btn.clicked.connect(self.clear_logs)
        btns.addWidget(clear_btn)
        
        save_btn = ModernButton("Save")
        save_btn.setFixedHeight(32)
        save_btn.setFixedWidth(80)
        save_btn.clicked.connect(self.save_logs)
        btns.addWidget(save_btn)
        
        btns.addStretch()
        layout.addLayout(btns)

        return section

    def check_authentication(self):
        auth_dialog = AuthDialog(self)
        result = auth_dialog.exec()
        
        if result != QDialog.DialogCode.Accepted or not auth_dialog.authenticated:
            QApplication.quit()
            return False
        
        self.is_authenticated = True
        self.user_data = auth_dialog.user_data
        
        # Force update the UI
        QApplication.processEvents()
        
        self.log_widget.add_log("SUCCESS", "Authentication successful! Welcome to Blur Toolz.")
        
        # Show the main window after successful authentication
        self.show()
        
        # Update user info display
        self.update_main_user_info()
        
        return True
    
    def update_main_user_info(self):
        """Update the main window user information display"""
        if not self.user_data:
            return
        
        try:
            # Update username
            username = self.user_data.get('name', 'Unknown')
            self.main_username_value.setText(username)
            
            # Update expiry
            try:
                expires_at = self.user_data.get('expiresAt')
                if expires_at:
                    if expires_at.tzinfo is None:
                        expires_at = expires_at.replace(tzinfo=timezone.utc)
                    
                    current_time = datetime.now(timezone.utc)
                    time_remaining = expires_at - current_time
                    days_remaining = time_remaining.days
                    
                    # The countdown timer will handle the display, just set initial state
                    if days_remaining > 0:
                        color = "#10b981"  # Always green
                        self.main_expiry_value.setStyleSheet(f"color: {color}; background: rgba(55, 65, 81, 0.5); padding: 4px 8px; border-radius: 6px; font-weight: bold; font-family: 'Consolas', 'Monaco', monospace;")
                    else:
                        color = "#10b981"  # Always green
                        self.main_expiry_value.setStyleSheet(f"color: {color}; background: rgba(55, 65, 81, 0.5); padding: 4px 8px; border-radius: 6px; font-weight: bold; font-family: 'Consolas', 'Monaco', monospace;")
                else:
                    self.main_expiry_value.setText("Never")
                    self.main_expiry_value.setStyleSheet("color: #10b981; background: rgba(55, 65, 81, 0.5); padding: 4px 8px; border-radius: 6px; font-weight: bold; font-family: 'Consolas', 'Monaco', monospace;")
            except:
                self.main_expiry_value.setText("Unknown")
                self.main_expiry_value.setStyleSheet("color: #94a3b8; background: rgba(55, 65, 81, 0.5); padding: 4px 8px; border-radius: 6px; font-weight: bold;")
        
        except Exception as e:
            print(f"Error updating main user info: {e}")

    def update_countdown(self):
        """Update the countdown display every second"""
        if not self.user_data or not hasattr(self, 'main_expiry_value'):
            return
        
        try:
            expires_at = self.user_data.get('expiresAt')
            if expires_at:
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                
                current_time = datetime.now(timezone.utc)
                time_remaining = expires_at - current_time
                
                if time_remaining.total_seconds() > 0:
                    days = time_remaining.days
                    hours, remainder = divmod(time_remaining.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    
                    if days > 0:
                        countdown_text = f"{days}d {hours:02d}h {minutes:02d}m {seconds:02d}s"
                        color = "#10b981"  # Always green
                    else:
                        countdown_text = f"{hours:02d}h {minutes:02d}m {seconds:02d}s"
                        color = "#10b981"  # Always green
                    
                    self.main_expiry_value.setText(countdown_text)
                    self.main_expiry_value.setStyleSheet(f"color: {color}; background: rgba(55, 65, 81, 0.5); padding: 4px 8px; border-radius: 6px; font-weight: bold; font-family: 'Consolas', 'Monaco', monospace;")
                else:
                    self.main_expiry_value.setText("EXPIRED")
                    self.main_expiry_value.setStyleSheet("color: #ef4444; background: rgba(55, 65, 81, 0.5); padding: 4px 8px; border-radius: 6px; font-weight: bold; animation: blink 1s infinite;")
        except Exception as e:
            print(f"Error updating countdown: {e}")

    def start_generation(self):
        if self.generation_thread and self.generation_thread.isRunning():
            return
        
        if not self.is_authenticated:
            QMessageBox.warning(self, "Authentication Required", 
                              "Please restart the application and authenticate properly.")
            return
        
        account_count = self.account_count_input.value()
        
        # Update config based on UI
        self.config["check_ratelimit"] = self.ratelimit_check.isChecked()
        self.config["notify"] = self.notify_check.isChecked()
        if hasattr(self, 'ratelimit_cap_input'):
            try:
                self.config["ratelimit_max_wait"] = int(self.ratelimit_cap_input.value())
            except Exception:
                self.config["ratelimit_max_wait"] = 20
        self.config["save_tokens"] = True
        
        # Save updated config
        self.save_config()
        
        # Update progress bar
        # self.progress_bar.setMaximum(account_count) # Removed progress bar
        # self.progress_bar.setValue(0)
        # self.progress_label.setText(f"Ready: 0 / {account_count} accounts") # Removed progress label
        
        # Create and start generation thread
        self.generation_thread = AccountGeneratorThread(account_count, self.config)
        self.generation_thread.log_signal.connect(self.log_widget.add_log)
        # self.generation_thread.progress_signal.connect(self.update_progress) # Removed progress signal
        self.generation_thread.finished_signal.connect(self.generation_finished)
        
        # Update UI state
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # Start the thread
        self.generation_thread.start()
        
        self.log_widget.add_log("INFO", "Account generation started")

    def stop_generation(self):
        if self.generation_thread and self.generation_thread.isRunning():
            self.generation_thread.stop()
            self.log_widget.add_log("WARNING", "Stopping generation...")

    def generation_finished(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        # self.progress_label.setText("Generation completed successfully!") # Removed progress label
        self.log_widget.add_log("SUCCESS", "Account generation process finished")


    # def update_progress(self, current): # Removed progress update
    #     self.progress_bar.setValue(current)
    #     max_accounts = self.progress_bar.maximum()
    #     self.progress_label.setText(f"Progress: {current} / {max_accounts} accounts completed")

    def clear_logs(self):
        self.log_widget.clear()
        self.log_widget.add_log("INFO", "Logs cleared")

    def save_logs(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Logs", f"discord_creator_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_widget.toPlainText())
                self.log_widget.add_log("SUCCESS", f"Logs saved to: {file_path}")
                QMessageBox.information(self, "Success", f"Logs saved to:\n{file_path}")
            except Exception as e:
                self.log_widget.add_log("ERROR", f"Failed to save logs: {e}")
                QMessageBox.critical(self, "Error", f"Failed to save logs: {e}")

    def apply_modern_theme(self):
        self.setStyleSheet(f"""
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 #0a0f1c, stop:0.5 #1e293b, stop:1 #0a0f1c);
                color: #ffffff;
                border: none;
            }}
            QWidget {{
                background: transparent;
                color: #ffffff;
                border: none;
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid rgba(99, 102, 241, 0.3);
                border-radius: 15px;
                margin-top: 20px;
                padding-top: 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 rgba(71, 85, 105, 0.9), stop:1 rgba(51, 65, 85, 0.9));
                color: #ffffff;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                left: 15px;
                top: -10px;
                padding: 4px 12px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #6366f1, stop:1 #8b5cf6);
                color: white;
                font-weight: bold;
                border-radius: 8px;
            }}
            QLabel {{
                color: #ffffff;
                background: transparent;
                border: none;
                padding: 2px;
            }}
            QFrame {{
                background: transparent;
                border: none;
                color: #ffffff;
            }}
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollArea > QWidget > QWidget {{
                background: transparent;
            }}
        """)

    def closeEvent(self, a0):
        # Stop generation thread if running
        if self.generation_thread and self.generation_thread.isRunning():
            reply = QMessageBox.question(
                self, "Confirm Close",
                "Account generation is still running. Are you sure you want to close?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.generation_thread.stop()
                self.generation_thread.wait(5000)
                if a0:
                    a0.accept()
            else:
                if a0:
                    a0.ignore()
        else:
            # Save configuration before closing
            self.save_config()
            if a0:
                a0.accept()

def main():
    # Required for multiprocessing on Windows
    multiprocessing.freeze_support()
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application properties
    app.setApplicationName("Blur Toolz")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("Blur Toolz")
    
    # Show modern splash screen
    splash = ModernSplashScreen()
    splash.show()
    
    # Center splash screen
    screen = app.primaryScreen()
    if screen:
        geometry = screen.geometry()
        splash.move((geometry.width() - splash.width()) // 2, (geometry.height() - splash.height()) // 2)
    
    app.processEvents()
    
    # Create main window but don't show it yet
    window = MainWindow()
    
    # Handle authentication and show main window after splash
    def handle_authentication():
        splash.close()
        # Trigger authentication - this will show the window if successful
        if not window.check_authentication():
            # Authentication failed, app will quit
            return
    
    QTimer.singleShot(2000, handle_authentication)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
