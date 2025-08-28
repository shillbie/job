import requests
import json
import hashlib
import re
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line
from datetime import datetime
from kivy.app import App
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.utils import platform
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.core.text import LabelBase
from kivy.resources import resource_add_path
import threading
import time
import os
import urllib.request

# Sound and vibration imports
try:
    from kivy.core.audio import SoundLoader
except ImportError:
    SoundLoader = None

try:
    if platform == 'android':
        from jnius import autoclass
        # Android vibration service
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Context = autoclass('android.content.Context')
        Vibrator = autoclass('android.os.Vibrator')
    else:
        PythonActivity = None
        Context = None
        Vibrator = None
except ImportError:
    PythonActivity = None
    Context = None
    Vibrator = None

# Sound and Vibration Manager
class SoundVibrationManager:
    """Manages sound effects and vibration for the app"""
    def __init__(self):
        self.sounds = {}
        self.vibrator = None
        self.init_vibrator()
        self.load_sounds()
    
    def init_vibrator(self):
        """Initialize vibrator for Android"""
        try:
            if platform == 'android' and PythonActivity:
                activity = PythonActivity.mActivity
                self.vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)
        except Exception as e:
            print(f"[VIBRATION] Error initializing vibrator: {e}")
            self.vibrator = None
    
    def load_sounds(self):
        """Load sound effects"""
        try:
            if SoundLoader:
                # Create simple beep sounds programmatically or use system sounds
                # For now, we'll use system notification sounds
                pass
        except Exception as e:
            print(f"[SOUND] Error loading sounds: {e}")
    
    def play_success_sound(self):
        """Play success/connection sound"""
        try:
            if platform == 'android':
                # Use system notification sound for success
                from jnius import autoclass
                RingtoneManager = autoclass('android.media.RingtoneManager')
                Uri = autoclass('android.net.Uri')
                
                notification_uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION)
                ringtone = RingtoneManager.getRingtone(PythonActivity.mActivity, notification_uri)
                if ringtone:
                    ringtone.play()
        except Exception as e:
            print(f"[SOUND] Error playing success sound: {e}")
    
    def play_error_sound(self):
        """Play error sound"""
        try:
            if platform == 'android':
                # Use system alarm sound for errors
                from jnius import autoclass
                RingtoneManager = autoclass('android.media.RingtoneManager')
                
                alarm_uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)
                ringtone = RingtoneManager.getRingtone(PythonActivity.mActivity, alarm_uri)
                if ringtone:
                    ringtone.play()
        except Exception as e:
            print(f"[SOUND] Error playing error sound: {e}")
    
    def vibrate_success(self):
        """Short vibration for success"""
        try:
            if self.vibrator and platform == 'android':
                # Short single vibration (100ms)
                self.vibrator.vibrate(100)
        except Exception as e:
            print(f"[VIBRATION] Error in success vibration: {e}")
    
    def vibrate_error(self):
        """Pattern vibration for errors"""
        try:
            if self.vibrator and platform == 'android':
                # Error pattern: short-pause-short-pause-long (200ms-100ms-200ms-100ms-500ms)
                pattern = [0, 200, 100, 200, 100, 500]
                self.vibrator.vibrate(pattern, -1)  # -1 means don't repeat
        except Exception as e:
            print(f"[VIBRATION] Error in error vibration: {e}")
    
    def success_feedback(self):
        """Combined success feedback (sound + vibration)"""
        self.play_success_sound()
        self.vibrate_success()
    
    def error_feedback(self):
        """Combined error feedback (sound + vibration)"""
        self.play_error_sound()
        self.vibrate_error()

# Global sound/vibration manager instance
sound_manager = SoundVibrationManager()

# Kasir Data Classes
class KasirProduct:
    def __init__(self, id, name, price_per_kg, stock_kg=100):
        self.id = id
        self.name = name
        self.price_per_kg = price_per_kg
        self.stock_kg = stock_kg

class KasirCartItem:
    def __init__(self, product, weight_kg=1):
        self.product = product
        self.weight_kg = weight_kg
    
    def get_total(self):
        return self.product.price_per_kg * self.weight_kg

class KasirExpense:
    def __init__(self, id, name, amount, date_time):
        self.id = id
        self.name = name
        self.amount = amount
        self.date_time = date_time

# Emoji font setup (disabled for development)
def setup_emoji_font():
    """Setup emoji font support for Kivy apps"""
    try:
        print("[EMOJI] Setting up emoji font...")
        
        # Create fonts directory
        fonts_dir = os.path.join(os.path.dirname(__file__), 'fonts')
        if not os.path.exists(fonts_dir):
            os.makedirs(fonts_dir)
            print(f"[EMOJI] Created fonts directory: {fonts_dir}")
        
        # Path for downloaded emoji font
        emoji_font_path = os.path.join(fonts_dir, 'NotoEmoji-Regular.ttf')
        
        # Download emoji font if not exists
        if not os.path.exists(emoji_font_path):
            print("[EMOJI] Downloading Noto Emoji font...")
            try:
                # Use a working Noto Emoji font URL
                font_url = "https://fonts.gstatic.com/s/notoemoji/v47/bMrnmSyK7YY-MEu6aWjPDs-ar6uWaGWuob-r0jwvS-FGJCMY.ttf"
                urllib.request.urlretrieve(font_url, emoji_font_path)
                print(f"[EMOJI] ✅ Font downloaded: {emoji_font_path}")
            except Exception as e:
                print(f"[EMOJI] ❌ Download failed: {e}")
                return False
        
        # Register the emoji font
        if os.path.exists(emoji_font_path):
            try:
                # LabelBase.register(name="EmojiFont", fn_regular=emoji_font_path)
                print(f"[EMOJI] ✅ Registered: NotoEmoji-Regular.ttf")
                return True
            except Exception as e:
                print(f"[EMOJI] ❌ Registration failed: {e}")
                return False
        
        print("[EMOJI] ⚠️ Font file not found after download")
        return False
        
    except Exception as e:
        print(f"[EMOJI] ❌ Setup error: {e}")
        return False

# Initialize emoji font (disabled for development)
EMOJI_FONT_AVAILABLE = False
print(f"[EMOJI] Font disabled for development mode")

# Helper function to create emoji-compatible labels
def create_emoji_label(text, **kwargs):
    """Create a label with emoji font support"""
    # Use default font for development, emoji font only for build
    return Label(text=text, **kwargs)

# Helper function to create emoji-compatible buttons
def create_emoji_button(text, **kwargs):
    """Create a button with emoji font support"""
    # Use default font for development, emoji font only for build
    return Button(text=text, **kwargs)

# Helper function to apply emoji font to existing widgets
def apply_emoji_font(widget):
    """Apply emoji font to existing widget if possible"""
    # DISABLE emoji font application to prevent text boxes
    # Font emoji hanya untuk build, tidak untuk development
    pass

# Set window size for desktop testing
if platform != 'android':
    Window.size = (360, 640)

# Firebase configuration
firebase_config = {
    "apiKey": "AIzaSyDlZeYVX1wjbSVMVl025XKFqhO-CjH7m2c",
    "authDomain": "token-manage-f84df.firebaseapp.com",
    "databaseURL": "https://token-manage-f84df-default-rtdb.asia-southeast1.firebasedatabase.app/",
    "projectId": "token-manage-f84df",
    "storageBucket": "token-manage-f84df.firebasestorage.app",
    "messagingSenderId": "209373957791",
    "appId": "1:209373957791:web:bc3eb1fa76299a94a59caa",
    "measurementId": "G-KPMPPX74ZQ"
}

class SessionManager:
    """Manage login session persistence"""
    def __init__(self):
        try:
            self.session_file = os.path.join(App.get_running_app().user_data_dir, 'user_session.json')
        except:
            self.session_file = 'user_session.json'
    
    def save_session(self, username, user_type):
        """Save login session"""
        try:
            session_data = {
                'username': username,
                'user_type': user_type,
                'login_time': datetime.now().isoformat(),
                'auto_login': True
            }
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f)
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def load_session(self):
        """Load saved session"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r') as f:
                    session_data = json.load(f)
                
                # Check if session is valid (within 7 days)
                login_time = datetime.fromisoformat(session_data['login_time'])
                if (datetime.now() - login_time).days < 7:
                    return session_data
            return None
        except Exception as e:
            print(f"Error loading session: {e}")
            return None
    
    def clear_session(self):
        """Clear saved session"""
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
            return True
        except Exception as e:
            print(f"Error clearing session: {e}")
            return False

class FirebaseManager:
    """Firebase database manager using REST API"""
    def __init__(self):
        try:
            # Firebase config
            self.database_url = firebase_config["databaseURL"]
            self.api_key = firebase_config["apiKey"]
            
            # Default settings
            self.admin_password = self.hash_password('admin2024')
            self.price_per_token = 1500
            
            # Presence management
            self.presence_thread = None
            self.presence_running = False
            self.current_user = None
            
            # Test connection
            self.test_connection()
            
            # Initialize default data if not exists
            self.init_firebase_data()
            
            print("Firebase initialized successfully")
            self.db = True  # Set to True to indicate successful connection
        except Exception as e:
            print(f"Firebase initialization error: {e}")
            self.db = None
    def notify_user_token_banned(self, username, banned_count, lost_value):
        try:
            # Send direct notification via chat
            notification_msg = {
                "user": "Sistem",
                "message": f"PEMBERITAHUAN UNTUK {username.upper()}:\n\n{banned_count} token Anda telah di-ban karena rusak/bermasalah!\n\nPenghasilan dikurangi: Rp {lost_value:,}\n\nSilakan periksa kualitas token sebelum mengirim. Hubungi admin jika ada pertanyaan.",
                "timestamp": datetime.now().isoformat(),
                "type": "system"
            }
            self.push_data("chat_messages", notification_msg)
            
            # Log notification
            self.log_activity("sistem", 'user_notified', f'Notifikasi ban token dikirim ke {username}')
            
        except Exception as e:
            print(f"Error sending ban notification: {e}")

    def test_connection(self):
        """Test Firebase connection"""
        try:
            response = requests.get(f"{self.database_url}/test.json", timeout=10)
            if response.status_code == 200:
                return True
            else:
                raise Exception(f"HTTP {response.status_code}")
        except Exception as e:
            raise Exception(f"Connection failed: {e}")
    
    def get_data(self, path):
        """Get data from Firebase"""
        try:
            url = f"{self.database_url}/{path}.json"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error getting data from {path}: {e}")
            return None
    
    def set_data(self, path, data):
        """Set data to Firebase"""
        try:
            url = f"{self.database_url}/{path}.json"
            response = requests.put(url, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Error setting data to {path}: {e}")
            return False
    
    def push_data(self, path, data):
        """Push data to Firebase (auto-generate key)"""
        try:
            url = f"{self.database_url}/{path}.json"
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                return response.json().get('name')
            return None
        except Exception as e:
            print(f"Error pushing data to {path}: {e}")
            return None
    
    def update_data(self, path, data):
        """Update data in Firebase"""
        try:
            url = f"{self.database_url}/{path}.json"
            response = requests.patch(url, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Error updating data at {path}: {e}")
            return False
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def is_valid_token(self, token):
        if not token or not isinstance(token, str):
            return False
        
        if len(token.strip()) < 50:
            return False
        
        pattern = r'^u[a-f0-9]{32}:[a-zA-Z0-9+/]+={0,2}\.\.[a-zA-Z0-9+/]+=*$'
        
        if not re.match(pattern, token.strip()):
            return False
        
        parts = token.strip().split(':')
        if len(parts) != 2:
            return False
        
        if len(parts[0]) != 33 or not parts[0].startswith('u'):
            return False
        
        if not all(c in '0123456789abcdef' for c in parts[0][1:]):
            return False
        
        if '..' not in parts[1]:
            return False
        
        return True
    
    def init_firebase_data(self):
        """Initialize Firebase with default data"""
        try:
            # Check if settings exist
            settings = self.get_data("settings")
            if not settings:
                default_settings = {
                    "admin_password": self.admin_password,
                    "price_per_token": self.price_per_token,
                    "created": datetime.now().isoformat()
                }
                self.set_data("settings", default_settings)
                print("Default settings created in Firebase")
                
            # Create welcome message in chat if not exists
            chat_messages = self.get_data("chat_messages")
            if not chat_messages:
                welcome_message = {
                    "user": "Sistem",
                    "message": "Selamat datang di Grup Chat Token Manager!",
                    "timestamp": datetime.now().isoformat(),
                    "type": "system"
                }
                self.push_data("chat_messages", welcome_message)
                print("Welcome chat message created")
                
        except Exception as e:
            print(f"Error initializing Firebase data: {e}")
    
    def set_online(self, username):
        """Set user online status"""
        try:
            self.current_user = username
            self.update_data(f"users/{username}", {
                "online": True,
                "last_seen": datetime.now().isoformat()
            })
            
            # Start presence heartbeat
            self.start_presence_heartbeat(username)
            
            # Send online notification to chat
            online_msg = {
                "user": "Sistem",
                "message": f"{username} sedang online!",
                "timestamp": datetime.now().isoformat(),
                "type": "system"
            }
            self.push_data("chat_messages", online_msg)
            
            print(f"User {username} set online")
        except Exception as e:
            print(f"Error setting online status: {e}")
    
    def set_offline(self, username):
        """Set user offline status"""
        try:
            self.presence_running = False
            if self.presence_thread:
                self.presence_thread.join(timeout=1)
            
            self.update_data(f"users/{username}", {
                "online": False,
                "last_seen": datetime.now().isoformat()
            })
            
            # Send offline notification to chat
            offline_msg = {
                "user": "Sistem",
                "message": f"{username} sedang offline!",
                "timestamp": datetime.now().isoformat(),
                "type": "system"
            }
            self.push_data("chat_messages", offline_msg)
            
            print(f"User {username} set offline")
        except Exception as e:
            print(f"Error setting offline status: {e}")
    
    def start_presence_heartbeat(self, username):
        """Start heartbeat to maintain online presence"""
        self.presence_running = True
        
        def heartbeat():
            while self.presence_running:
                try:
                    self.update_data(f"users/{username}", {"last_seen": datetime.now().isoformat()})
                    time.sleep(30)  # Update every 30 seconds
                except:
                    break
        
        self.presence_thread = threading.Thread(target=heartbeat, daemon=True)
        self.presence_thread.start()
    
    def get_online_users(self):
        """Get list of online users"""
        try:
            all_users = self.get_data("users")
            if not all_users:
                return []
            
            online_users = []
            current_time = datetime.now()
            
            for username, user_data in all_users.items():
                if user_data.get("online", False):
                    last_seen = user_data.get("last_seen", "")
                    if last_seen:
                        try:
                            last_seen_time = datetime.fromisoformat(last_seen)
                            # Consider online if last seen within 2 minutes
                            if (current_time - last_seen_time).seconds < 120:
                                online_users.append(username)
                        except:
                            pass
            
            return online_users
        except Exception as e:
            print(f"Error getting online users: {e}")
            return []
    
    def login(self, username, password, user_type):
        try:
            if user_type == 'admin':
                settings = self.get_data("settings")
                if settings and settings.get("admin_password") == self.hash_password(password):
                    self.set_online('admin')
                    self.log_activity('admin', 'login', 'Admin berhasil masuk')
                    return True, "Login admin berhasil"
                else:
                    return False, "Password admin salah"
            else:
                user_data = self.get_data(f"users/{username}")
                if not user_data:
                    return False, "Username belum terdaftar. Hubungi admin untuk mendaftarkan akun Anda."
                
                stored_password = user_data.get("password", "")
                if stored_password and stored_password != self.hash_password(password):
                    return False, "Password salah"
                
                self.update_data(f"users/{username}", {"last_login": datetime.now().isoformat()})
                self.set_online(username)
                self.log_activity(username, 'login', 'User berhasil masuk')
                
                # Check if user info is complete
                wa = user_data.get("wa", "")
                rekening = user_data.get("rekening", "")
                tgl_lahir = user_data.get("tgl_lahir", "")
                tempat_tinggal = user_data.get("tempat_tinggal", "")
                
                if not wa or not rekening or not tgl_lahir or not tempat_tinggal:
                    return True, "Login berhasil - info required"
                
                return True, "Login user berhasil"
        except Exception as e:
            print(f"Login error: {e}")
            return False, f"Error login: {str(e)}"

    def logout(self, username):
        """Logout user"""
        try:
            self.set_offline(username)
        except Exception as e:
            print(f"Logout error: {e}")
    
    def log_activity(self, user, action, details=""):
        """Log user activity"""
        try:
            activity_data = {
                "user": user,
                "action": action,
                "details": details,
                "timestamp": datetime.now().isoformat()
            }
            self.push_data("activity_logs", activity_data)
            print(f"Activity logged: {user} - {action}")
        except Exception as e:
            print(f"Error logging activity: {e}")
    
    def add_user(self, username, added_by, password=""):
        """Add user (admin only)"""
        try:
            # Check if user already exists
            user_data = self.get_data(f"users/{username}")
            if user_data:
                return False, "User sudah ada"
            
            new_user_data = {
                "created": datetime.now().isoformat(),
                "token_count": 0,
                "total_value": 0,
                "last_login": "",
                "online": False,
                "last_seen": "",
                "role": "user",
                "added_by": added_by,
                "password": self.hash_password(password) if password else ""
            }
            
            # Add to Firebase
            if self.set_data(f"users/{username}", new_user_data):
                self.log_activity(added_by, 'user_added', f'Menambahkan user: {username}')
                
                # Send notification to chat
                chat_msg = {
                    "user": "Sistem",
                    "message": f"User baru {username} telah ditambahkan oleh admin!",
                    "timestamp": datetime.now().isoformat(),
                    "type": "system"
                }
                self.push_data("chat_messages", chat_msg)
                
                print(f"User {username} added successfully")
                return True, "User berhasil ditambahkan"
            else:
                return False, "Gagal menambahkan user ke database"
            
        except Exception as e:
            print(f"Error adding user: {e}")
            return False, f"Error menambahkan user: {str(e)}"
    
    def update_user_password(self, username, new_password):
        """Update user password"""
        try:
            user_data = self.get_data(f"users/{username}")
            if not user_data:
                return False, "User tidak ditemukan"
            
            hashed_password = self.hash_password(new_password)
            success = self.update_data(f"users/{username}", {"password": hashed_password})
            
            if success:
                self.log_activity(username, 'password_changed', 'Password berhasil diubah')
                return True, "Password berhasil diubah"
            else:
                return False, "Gagal mengubah password"
                
        except Exception as e:
            print(f"Error updating password: {e}")
            return False, f"Error mengubah password: {str(e)}"
    
    def reset_user_data(self, admin_user):
        """Reset all user earnings and token counts (admin only)"""
        try:
            all_users = self.get_data("users")
            if not all_users:
                return False, "Tidak ada user yang ditemukan"
            
            reset_count = 0
            for username, user_data in all_users.items():
                if user_data.get("role") == "user":
                    # Reset only earnings and token count, keep other data
                    self.update_data(f"users/{username}", {
                        "token_count": 0,
                        "total_value": 0
                    })
                    reset_count += 1
            
            # Log activity
            self.log_activity(admin_user, 'data_reset', f'Reset data {reset_count} user')
            
            # Send notification to chat
            chat_msg = {
                "user": "Sistem",
                "message": f"Admin telah mereset data penghasilan semua user!",
                "timestamp": datetime.now().isoformat(),
                "type": "system"
            }
            self.push_data("chat_messages", chat_msg)
            
            return True, f"Berhasil mereset data {reset_count} user"
            
        except Exception as e:
            print(f"Error resetting user data: {e}")
            return False, f"Error reset data: {str(e)}"
    
    def check_token_owner(self, token_to_check):
        """Check who owns a specific token (admin only)"""
        try:
            all_tokens = self.get_data("tokens")
            if not all_tokens:
                return None, "Tidak ada token yang ditemukan"
            
            for token_id, token_data in all_tokens.items():
                if token_data.get("token") == token_to_check:
                    owner = token_data.get("user", "Unknown")
                    status = token_data.get("status", "unknown")
                    timestamp = token_data.get("timestamp", "")
                    price = token_data.get("price", 0)
                    
                    # Format timestamp
                    try:
                        dt = datetime.fromisoformat(timestamp)
                        formatted_time = dt.strftime('%d/%m/%Y %H:%M')
                    except:
                        formatted_time = "Waktu tidak diketahui"
                    
                    result = {
                        'owner': owner,
                        'status': status,
                        'timestamp': formatted_time,
                        'price': price,
                        'token_id': token_id
                    }
                    
                    return result, "Token ditemukan"
            
            return None, "Token tidak ditemukan dalam database"
            
        except Exception as e:
            print(f"Error checking token owner: {e}")
            return None, f"Error cek token: {str(e)}"
    
    def add_token(self, token, username, added_by):
        """Add token to Firebase (only registered users)"""
        try:
            print(f"Attempting to add token for {username} by {added_by}")
            
            # Check if user is registered
            user_data = self.get_data(f"users/{username}")
            if not user_data:
                return False, "User belum terdaftar. Hubungi admin untuk mendaftarkan akun Anda."
            
            if not self.is_valid_token(token):
                print("Token validation failed")
                return False, "Format token tidak valid"
            
            # Check for duplicates
            all_tokens = self.get_data("tokens")
            if all_tokens:
                for token_id, token_data in all_tokens.items():
                    if token_data.get("token") == token:
                        print("Duplicate token found")
                        return False, "Token sudah ada"
            
            # Get current price
            settings = self.get_data("settings")
            current_price = settings.get("price_per_token", 1500) if settings else 1500
            
            # Add token
            token_data = {
                "token": token,
                "user": username,
                "timestamp": datetime.now().isoformat(),
                "price": int(current_price),
                "status": "available",
                "added_by": added_by
            }
            
            # Push to Firebase
            token_id = self.push_data("tokens", token_data)
            if token_id:
                print(f"Token added to Firebase with ID: {token_id}")
                
                # Update user stats
                current_count = user_data.get("token_count", 0)
                current_value = user_data.get("total_value", 0)
                
                self.update_data(f"users/{username}", {
                    "token_count": current_count + 1,
                    "total_value": current_value + int(current_price)
                })
                print(f"Updated user stats for: {username}")
                
                self.log_activity(added_by, 'token_added', f'Menambahkan token untuk {username}')
                
                # Send notification to chat
                chat_msg = {
                    "user": "Sistem",
                    "message": f"{username} menambahkan token baru! (+Rp {current_price:,})",
                    "timestamp": datetime.now().isoformat(),
                    "type": "system"
                }
                self.push_data("chat_messages", chat_msg)
                
                print(f"Token added successfully for {username}")
                return True, "Token berhasil ditambahkan"
            else:
                return False, "Gagal menambahkan token ke database"
                
        except Exception as e:
            print(f"Error adding token: {e}")
            return False, f"Error menambahkan token: {str(e)}"
    
    def add_bulk_tokens(self, tokens_text, username, added_by):
        """Add multiple tokens"""
        try:
            tokens = [t.strip() for t in tokens_text.split('\n') if t.strip()]
            
            success_count = 0
            duplicate_count = 0
            invalid_count = 0
            
            for token in tokens:
                success, message = self.add_token(token, username, added_by)
                if success:
                    success_count += 1
                else:
                    if "sudah ada" in message:
                        duplicate_count += 1
                    elif "tidak valid" in message:
                        invalid_count += 1
            
            # Send bulk add notification to chat
            if success_count > 0:
                chat_msg = {
                    "user": "Sistem",
                    "message": f"{username} menambahkan {success_count} token sekaligus!",
                    "timestamp": datetime.now().isoformat(),
                    "type": "system"
                }
                self.push_data("chat_messages", chat_msg)
            
            return True, f'Berhasil menambahkan {success_count}/{len(tokens)} token', {
                'success': success_count,
                'duplicates': duplicate_count,
                'invalid': invalid_count,
                'total': len(tokens)
            }
            
        except Exception as e:
            return False, f"Error menambahkan token massal: {str(e)}", {}
    
    def get_available_tokens_count(self):
        """Get count of available tokens"""
        try:
            all_tokens = self.get_data("tokens")
            if not all_tokens:
                return 0
            
            available_count = 0
            for token_data in all_tokens.values():
                if token_data.get("status") == "available":
                    available_count += 1
            
            return available_count
        except Exception as e:
            print(f"Error getting available tokens count: {e}")
            return 0
    
    def take_tokens(self, count, taken_by):
        """Take tokens from available pool"""
        try:
            # Get all available tokens
            all_tokens = self.get_data("tokens")
            if not all_tokens:
                return None
            
            available_tokens = []
            for token_id, token_data in all_tokens.items():
                if token_data.get("status") == "available":
                    available_tokens.append((token_id, token_data))
            
            # Sort by timestamp to get oldest first
            available_tokens.sort(key=lambda x: x[1].get("timestamp", ""))
            
            if len(available_tokens) < count:
                return None
            
            taken_tokens = []
            for i in range(count):
                token_id, token_data = available_tokens[i]
                
                # Mark as taken
                self.update_data(f"tokens/{token_id}", {
                    "status": "taken",
                    "taken_by": taken_by,
                    "taken_timestamp": datetime.now().isoformat()
                })
                
                taken_tokens.append(token_data["token"])
            self.log_activity(taken_by, 'tokens_taken', f'Mengambil {len(taken_tokens)} token')
            
            # Send notification to chat
            chat_msg = {
                "user": "Sistem",
                "message": f"Admin mengambil {len(taken_tokens)} token!",
                "timestamp": datetime.now().isoformat(),
                "type": "system"
            }
            self.push_data("chat_messages", chat_msg)
            
            return {
                'success': True,
                'tokens': taken_tokens,
                'count': len(taken_tokens)
            }
            
        except Exception as e:
            print(f"Error taking tokens: {e}")
            return None
    
    def get_all_stats(self):
        """Get overall statistics"""
        try:
            # Get all tokens
            all_tokens = self.get_data("tokens")
            total_tokens = len(all_tokens) if all_tokens else 0
            
            # Count by status
            available_tokens = 0
            taken_tokens = 0
            total_value = 0
            
            if all_tokens:
                for token_data in all_tokens.values():
                    if token_data.get("status") == "available":
                        available_tokens += 1
                    elif token_data.get("status") == "taken":
                        taken_tokens += 1
                    total_value += token_data.get("price", 0)
            
            # Get user count
            all_users = self.get_data("users")
            total_users = len(all_users) if all_users else 0
            
            # Get online users count
            online_users = len(self.get_online_users())
            
            # Get current price
            settings = self.get_data("settings")
            current_price = settings.get('price_per_token', 1500) if settings else 1500
            
            return {
                'total_tokens': total_tokens,
                'available_tokens': available_tokens,
                'taken_tokens': taken_tokens,
                'total_value': total_value,
                'total_users': total_users,
                'online_users': online_users,
                'price_per_token': current_price
            }
            
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {
                'total_tokens': 0,
                'available_tokens': 0,
                'taken_tokens': 0,
                'total_value': 0,
                'total_users': 0,
                'online_users': 0,
                'price_per_token': 1500
            }
    
    def get_user_stats(self, username):
        """Get specific user stats"""
        try:
            user_data = self.get_data(f"users/{username}")
            if user_data:
                return user_data
            return {}
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return {}
    
    def get_all_users(self):
        try:
            users_data = self.get_data("users")
            if not users_data:
                return []
            
            users = []
            current_time = datetime.now()
            
            for username, user_info in users_data.items():
                # Skip admin dari list user
                if username == 'admin':
                    continue
                
                user_info['username'] = username
                
                last_seen = user_info.get("last_seen", "")
                is_online = False
                if last_seen:
                    try:
                        last_seen_time = datetime.fromisoformat(last_seen)
                        if (current_time - last_seen_time).seconds < 120:
                            is_online = True
                    except:
                        pass
                
                user_info['is_online'] = is_online
                users.append(user_info)
            
            users.sort(key=lambda x: (not x.get('is_online', False), -x.get('token_count', 0)))
            return users
            
        except Exception as e:
            print(f"Error getting users: {e}")
            return []

    def send_chat_message(self, username, message):
        """Send message to group chat"""
        try:
            chat_data = {
                "user": username,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "type": "user"
            }
            result = self.push_data("chat_messages", chat_data)
            if result:
                print(f"Chat message sent by {username}")
                return True
            return False
        except Exception as e:
            print(f"Error sending chat message: {e}")
            return False
    
    def get_chat_messages(self, limit=50):
        """Get chat messages"""
        try:
            all_messages = self.get_data("chat_messages")
            if not all_messages:
                return []
            
            message_list = list(all_messages.values())
            message_list.sort(key=lambda x: x.get('timestamp', ''))
            
            # Return last N messages
            return message_list[-limit:] if len(message_list) > limit else message_list
            
        except Exception as e:
            print(f"Error getting chat messages: {e}")
            return []
    
    def get_activity_logs(self, limit=50):
        """Get activity logs"""
        try:
            all_logs = self.get_data("activity_logs")
            if not all_logs:
                return []
            
            log_list = list(all_logs.values())
            log_list.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return log_list[:limit] if len(log_list) > limit else log_list
            
        except Exception as e:
            print(f"Error getting activity logs: {e}")
            return []
    
    def update_settings(self, settings):
        """Update settings (admin only)"""
        try:
            if 'price_per_token' in settings:
                new_price = int(settings['price_per_token'])
                self.update_data("settings", {"price_per_token": new_price})
                
                # Send notification to chat
                chat_msg = {
                    "user": "Sistem",
                    "message": f"Harga token diubah menjadi Rp {new_price:,} oleh admin! 💲",
                    "timestamp": datetime.now().isoformat(),
                    "type": "system"
                }
                self.push_data("chat_messages", chat_msg)
                
            if 'admin_password' in settings:
                hashed_password = self.hash_password(settings['admin_password'])
                self.update_data("settings", {"admin_password": hashed_password})
            
            return True, "Pengaturan berhasil diperbarui"
        except Exception as e:
            return False, f"Error memperbarui pengaturan: {str(e)}"
    def ban_tokens(self, tokens_text, banned_by):
        try:
            tokens_to_ban = [t.strip() for t in tokens_text.split('\n') if t.strip()]
            
            success_count = 0
            not_found_count = 0
            banned_users = {}  # Track users yang tokennya di-ban
            
            all_tokens = self.get_data("tokens")
            if not all_tokens:
                return False, "Tidak ada token dalam database", {}
            
            for token_to_ban in tokens_to_ban:
                token_found = False
                
                for token_id, token_data in all_tokens.items():
                    if token_data.get("token") == token_to_ban:
                        token_found = True
                        owner = token_data.get("user", "Unknown")
                        token_price = token_data.get("price", 0)
                        
                        # Update token status menjadi banned
                        self.update_data(f"tokens/{token_id}", {
                            "status": "banned",
                            "banned_by": banned_by,
                            "banned_timestamp": datetime.now().isoformat()
                        })
                        
                        # Update user stats - kurangi penghasilan dan token count
                        user_data = self.get_data(f"users/{owner}")
                        if user_data:
                            current_count = user_data.get("token_count", 0)
                            current_value = user_data.get("total_value", 0)
                            current_banned = user_data.get("banned_count", 0)
                            
                            new_count = max(0, current_count - 1)
                            new_value = max(0, current_value - token_price)
                            new_banned = current_banned + 1
                            
                            self.update_data(f"users/{owner}", {
                                "token_count": new_count,
                                "total_value": new_value,
                                "banned_count": new_banned
                            })
                            
                            # Track banned users untuk notifikasi
                            if owner not in banned_users:
                                banned_users[owner] = {'count': 0, 'value': 0}
                            banned_users[owner]['count'] += 1
                            banned_users[owner]['value'] += token_price
                        
                        success_count += 1
                        
                        # Log activity
                        self.log_activity(banned_by, 'token_banned', f'Ban token milik {owner}')
                        break
                
                if not token_found:
                    not_found_count += 1
            
            # Send notifications to chat
            if success_count > 0:
                # General notification
                general_msg = {
                    "user": "Sistem",
                    "message": f"Admin memban {success_count} token rusak! ⚠️",
                    "timestamp": datetime.now().isoformat(),
                    "type": "system"
                }
                self.push_data("chat_messages", general_msg)
                
                # Individual notifications for each affected user
                for username, ban_info in banned_users.items():
                    user_msg = {
                        "user": "Sistem",
                        "message": f"⚠️ {username}: {ban_info['count']} token Anda di-ban karena rusak! Penghasilan dikurangi Rp {ban_info['value']:,}",
                        "timestamp": datetime.now().isoformat(),
                        "type": "system"
                    }
                    self.push_data("chat_messages", user_msg)
            
            return True, f'Proses ban token selesai', {
                'success': success_count,
                'not_found': not_found_count,
                'total': len(tokens_to_ban),
                'affected_users': len(banned_users)
            }
            
        except Exception as e:
            print(f"Error banning tokens: {e}")
            return False, f"Error ban token: {str(e)}", {}

    def delete_data(self, path):
        try:
            url = f"{self.database_url}/{path}.json"
            response = requests.delete(url, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Error deleting data at {path}: {e}")
            return False
    def update_user_info(self, username, wa, rekening, tgl_lahir, tempat_tinggal):
        try:
            user_data = self.get_data(f"users/{username}")
            if not user_data:
                return False, "User tidak ditemukan"
            
            success = self.update_data(f"users/{username}", {
                "wa": wa,
                "rekening": rekening,
                "tgl_lahir": tgl_lahir,
                "tempat_tinggal": tempat_tinggal
            })
            
            if success:
                self.log_activity(username, 'info_updated', 'User memperbarui info pribadi')
                return True, "Info berhasil disimpan"
            else:
                return False, "Gagal menyimpan info"
                
        except Exception as e:
            print(f"Error updating user info: {e}")
            return False, f"Error update info: {str(e)}"

class LoginScreen(Screen):
    """Login screen with session management - Fixed keyboard overlap"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.firebase_manager = None
        self.session_manager = SessionManager()
        self.keyboard_height = 0
        self.selected_user_type = 'user'  # Initialize selected_user_type
        self.build_ui()
    
    def on_input_focus(self, instance, focus):
        # Handle input focus for keyboard visibility
        if focus:
            Clock.schedule_once(lambda dt: self.adjust_for_keyboard(), 0.2)
    
    def on_keyboard(self, window, key, *args):
        # Handle keyboard show/hide for better input visibility
        if hasattr(self, 'message_input') and self.message_input.focus:
            # Adjust scroll when input is focused
            Clock.schedule_once(lambda dt: self.adjust_for_keyboard(), 0.1)
        return False
    
    def adjust_for_keyboard(self):
        # Scroll to bottom when keyboard appears
        if hasattr(self, 'chat_scroll'):
            self.chat_scroll.scroll_y = 0

    def _on_keyboard_height(self, window, height):
        self.keyboard_height = height
        self.adjust_for_keyboard()

    def build_ui(self):
        # Main layout with ScrollView to avoid keyboard overlap
        self.scroll = ScrollView(size_hint=(1, 1))
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None)
        main_layout.bind(minimum_height=main_layout.setter('height'))
        main_layout.height = 640
        main_layout.add_widget(Label(size_hint_y=0.1))
        content_layout = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None)
        content_layout.height = dp(480)
        # Title
        title = Label(
            text='MANAJEMEN TOKEN\nFIREBASE ONLINE',
            font_size='22sp',
            bold=True,
            color=(0.2, 0.6, 1, 1),
            size_hint_y=0.15
        )
        content_layout.add_widget(title)
        
        # Connection status
        self.connection_label = Label(
            text='Menghubungkan ke Firebase...',
            font_size='14sp',
            color=(0.8, 0.8, 0.2, 1),
            size_hint_y=0.08
        )
        content_layout.add_widget(self.connection_label)
        
        # User type selection
        content_layout.add_widget(Label(
            text='Pilih Tipe Login:',
            font_size='16sp',
            bold=True,
            size_hint_y=0.08
        ))
        
        type_layout = BoxLayout(size_hint_y=0.08, spacing=10)
        self.admin_btn = Button(
            text='Admin',
            background_color=(1, 0.6, 0.2, 1)
        )
        self.user_btn = Button(
            text='User',
            background_color=(0.6, 0.6, 0.6, 1)
        )
        
        self.admin_btn.bind(on_press=lambda x: self.select_user_type('admin'))
        self.user_btn.bind(on_press=lambda x: self.select_user_type('user'))
        
        type_layout.add_widget(self.admin_btn)
        type_layout.add_widget(self.user_btn)
        content_layout.add_widget(type_layout)
        
        # Username input
        self.username_input = TextInput(
            hint_text='Masukkan username Anda (harus terdaftar oleh admin)',
            multiline=False,
            font_size='16sp',
            size_hint_y=0.08,
            opacity=0.5
        )
        content_layout.add_widget(self.username_input)
        #self.username_input.bind(focus=self.on_input_focus)
        
        # Password input
        self.password_input = TextInput(
            hint_text='Masukkan password (admin2024 untuk admin)',
            password=True,
            multiline=False,
            font_size='16sp',
            size_hint_y=0.08
        )
        
        #self.password_input.bind(focus=self.on_input_focus)
        content_layout.add_widget(self.password_input)
        
        # Login button
        login_btn = Button(
            text='MASUK',
            font_size='18sp',
            bold=True,
            background_color=(0.2, 0.8, 0.2, 1),
            size_hint_y=0.08
        )
        login_btn.bind(on_press=self.login)
        content_layout.add_widget(login_btn)
        
        # Clear session button
        clear_session_btn = Button(
            text='Hapus Login Tersimpan',
            font_size='14sp',
            background_color=(0.8, 0.8, 0.2, 1),
            size_hint_y=0.06
        )
        clear_session_btn.bind(on_press=self.clear_session)
        content_layout.add_widget(clear_session_btn)
        
        # Status label
        self.status_label = Label(
            text='User harus didaftarkan oleh admin terlebih dahulu',
            font_size='12sp',
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=0.1
        )
        content_layout.add_widget(self.status_label)
        
        main_layout.add_widget(content_layout)
        
        # Bottom spacer
        main_layout.add_widget(Label(size_hint_y=0.1))
        
        self.scroll.add_widget(main_layout)
        self.add_widget(self.scroll)
        # Inisialisasi Firebase sesuai main.txt
        Clock.schedule_once(self.init_firebase, 0.5)

    def on_input_focus(self, instance, value):
        if value:
            Clock.schedule_once(lambda dt: self.adjust_for_keyboard(), 0.1)

    def adjust_for_keyboard(self):
        if self.keyboard_height > 0:
            self.scroll.scroll_y = 1
        else:
            self.scroll.scroll_y = 0
    
    def init_firebase(self, dt):
        """Initialize Firebase connection"""
        try:
            self.firebase_manager = FirebaseManager()
            if self.firebase_manager.db:
                self.status_label.text = 'Firebase terhubung'
                self.status_label.color = (0.2, 0.8, 0.2, 1)
                sound_manager.success_feedback()  # Success feedback for connection
                
                # Check for saved session and auto-login
                Clock.schedule_once(self.check_auto_login, 1)
            else:
                self.connection_label.text = 'Koneksi Firebase gagal. Periksa internet atau konfigurasi.'
                self.connection_label.color = (1, 0.2, 0.2, 1)
                sound_manager.error_feedback()  # Error feedback for connection failure
        except Exception as e:
            self.connection_label.text = f'Error Firebase: {str(e)}'
            self.connection_label.color = (1, 0.2, 0.2, 1)
            sound_manager.error_feedback()  # Error feedback for exception
    
    def check_auto_login(self, dt):
        """Check for saved session and auto-login"""
        saved_session = self.session_manager.load_session()
        if saved_session:
            username = saved_session['username']
            user_type = saved_session['user_type']
            
            self.status_label.text = f'Auto-login sebagai {username}...'
            self.status_label.color = (0.2, 0.6, 1, 1)
            
            # Set online status
            if user_type == 'admin':
                self.firebase_manager.set_online('admin')
            else:
                # Check if user still exists
                user_data = self.firebase_manager.get_data(f"users/{username}")
                if user_data:
                    self.firebase_manager.set_online(username)
                else:
                    # User was deleted, clear session
                    self.session_manager.clear_session()
                    self.status_label.text = 'Akun user dihapus. Silakan login ulang.'
                    self.status_label.color = (1, 0.2, 0.2, 1)
                    return
            
            # Pass to other screens
            app = App.get_running_app()
            app.current_user = username
            app.user_type = user_type
            
            for screen in app.root.screens:
                if hasattr(screen, 'set_firebase'):
                    screen.set_firebase(self.firebase_manager)
                if hasattr(screen, 'set_username'):
                    screen.set_username(username)
            
            # Navigate to appropriate dashboard
            if user_type == 'admin':
                self.manager.current = 'admin_dashboard'
            else:
                self.manager.current = 'user_dashboard'
    
    def select_user_type(self, user_type):
        self.selected_user_type = user_type
        if user_type == 'admin':
            self.admin_btn.background_color = (1, 0.6, 0.2, 1)
            self.user_btn.background_color = (0.6, 0.6, 0.6, 1)
            self.username_input.opacity = 0.5
            self.username_input.hint_text = 'Login admin (username tidak diperlukan)'
            self.password_input.hint_text = 'Masukkan password admin (default: admin2024)'
        else:
            self.admin_btn.background_color = (0.6, 0.6, 0.6, 1)
            self.user_btn.background_color = (0.2, 0.6, 1, 1)
            self.username_input.opacity = 1
            self.username_input.hint_text = 'Masukkan username Anda (harus terdaftar oleh admin)'
            self.password_input.hint_text = 'Masukkan password Anda'
    
    def login(self, instance):
        if not self.firebase_manager or not self.firebase_manager.db:
            self.status_label.text = 'Firebase tidak terhubung'
            self.status_label.color = (1, 0.2, 0.2, 1)
            sound_manager.error_feedback()  # Error feedback for connection issue
            return
        
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        
        if self.selected_user_type == 'user' and not username:
            self.show_popup('Error', 'Silakan masukkan username untuk login user')
            sound_manager.error_feedback()  # Error feedback for validation
            return
        
        if not password:
            self.show_popup('Error', 'Silakan masukkan password')
            sound_manager.error_feedback()  # Error feedback for validation
            return
        
        self.status_label.text = 'Mencoba login...'
        self.status_label.color = (0.2, 0.6, 1, 1)
        
        success, message = self.firebase_manager.login(
            username if self.selected_user_type == 'user' else 'admin',
            password,
            self.selected_user_type
        )
        
        if success:
            current_username = username if self.selected_user_type == 'user' else 'admin'
            
            # Success feedback for login
            sound_manager.success_feedback()
            
            # Check if user info is required
            if message == "Login berhasil - info required":
                self.show_user_info_popup(current_username)
                return
            
            # Normal login flow
            self.session_manager.save_session(current_username, self.selected_user_type)
            
            app = App.get_running_app()
            app.current_user = current_username
            app.user_type = self.selected_user_type
            
            for screen in app.root.screens:
                if hasattr(screen, 'set_firebase'):
                    screen.set_firebase(self.firebase_manager)
                if hasattr(screen, 'set_username'):
                    screen.set_username(app.current_user)
            
            if self.selected_user_type == 'admin':
                self.manager.current = 'admin_dashboard'
            else:
                self.manager.current = 'user_dashboard'
        else:
            self.status_label.text = f'{message}'
            sound_manager.error_feedback()  # Error feedback for failed login
            self.status_label.color = (1, 0.2, 0.2, 1)
    def show_user_info_popup(self, username):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        content.add_widget(Label(
            text='LENGKAPI INFO PRIBADI\nWajib diisi untuk melanjutkan',
            font_size='16sp',
            bold=True,
            size_hint_y=0.2
        ))
        
        wa_input = TextInput(
            hint_text='Nomor WhatsApp (contoh: 081234567890)',
            multiline=False,
            font_size='14sp',
            size_hint_y=0.15
        )
        content.add_widget(wa_input)
        
        rekening_input = TextInput(
            hint_text='Nomor Rekening Bank (contoh: BCA 1234567890)',
            multiline=False,
            font_size='14sp',
            size_hint_y=0.15
        )
        content.add_widget(rekening_input)
        
        tgl_lahir_input = TextInput(
            hint_text='Tanggal Lahir (contoh: 15/08/1990)',
            multiline=False,
            font_size='14sp',
            size_hint_y=0.15
        )
        content.add_widget(tgl_lahir_input)
        
        tempat_tinggal_input = TextInput(
            hint_text='Tempat Tinggal (contoh: Jakarta Selatan)',
            multiline=False,
            font_size='14sp',
            size_hint_y=0.15
        )
        content.add_widget(tempat_tinggal_input)
        
        button_layout = BoxLayout(size_hint_y=0.2, spacing=10)
        
        save_btn = Button(
            text='SIMPAN & LANJUTKAN',
            font_size='14sp',
            bold=True,
            background_color=(0.2, 0.8, 0.2, 1)
        )
        
        button_layout.add_widget(save_btn)
        content.add_widget(button_layout)
        
        popup = Popup(
            title='Info Pribadi Diperlukan',
            content=content,
            size_hint=(0.9, 0.8),
            auto_dismiss=False
        )
        
        def save_info(instance):
            wa = wa_input.text.strip()
            rekening = rekening_input.text.strip()
            tgl_lahir = tgl_lahir_input.text.strip()
            tempat_tinggal = tempat_tinggal_input.text.strip()
            
            if not wa or not rekening or not tgl_lahir or not tempat_tinggal:
                self.show_popup('Error', 'Semua kolom harus diisi!')
                return
            
            def bg_save():
                success, message = self.firebase_manager.update_user_info(username, wa, rekening, tgl_lahir, tempat_tinggal)
                Clock.schedule_once(lambda dt: self.handle_info_save_result(success, message, popup, username), 0)
            
            threading.Thread(target=bg_save, daemon=True).start()
        
        save_btn.bind(on_press=save_info)
        popup.open()
    def handle_info_save_result(self, success, message, popup, username):
        if success:
            popup.dismiss()
            
            # Continue with normal login flow
            self.session_manager.save_session(username, self.selected_user_type)
            
            app = App.get_running_app()
            app.current_user = username
            app.user_type = self.selected_user_type
            
            for screen in app.root.screens:
                if hasattr(screen, 'set_firebase'):
                    screen.set_firebase(self.firebase_manager)
                if hasattr(screen, 'set_username'):
                    screen.set_username(app.current_user)
            
            self.manager.current = 'user_dashboard'
        else:
            self.show_popup('Error', f'Gagal menyimpan info: {message}')

    def clear_session(self, instance):
        """Clear saved session"""
        if self.session_manager.clear_session():
            self.status_label.text = 'Login tersimpan dihapus'
            self.status_label.color = (0.2, 0.8, 0.2, 1)
        else:
            self.status_label.text = 'Gagal menghapus sesi'
            self.status_label.color = (1, 0.2, 0.2, 1)
        
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', 'User harus didaftarkan oleh admin terlebih dahulu'), 3)
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'color', (0.5, 0.5, 0.5, 1)), 3)
    
    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.8, 0.3)
        )
        popup.open()

class AdminDashboardScreen(Screen):
    """Admin dashboard - Indonesian language"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.firebase_manager = None
        self.username = None
        self.build_ui()
    
    def set_firebase(self, firebase_manager):
        self.firebase_manager = firebase_manager
    
    def set_username(self, username):
        self.username = username
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = BoxLayout(size_hint_y=0.1)
        header.add_widget(Label(
            text='DASHBOARD ADMIN',
            font_size='20sp',
            bold=True
        ))
        
        logout_btn = Button(
            text='Keluar',
            size_hint_x=0.3,
            background_color=(1, 0.3, 0.3, 1)
        )
        logout_btn.bind(on_press=self.logout)
        header.add_widget(logout_btn)
        
        layout.add_widget(header)
        
        # Online users notification
        self.online_label = Label(
            text='Memuat pengguna online...',
            size_hint_y=0.08,
            font_size='12sp',
            color=(0.2, 0.8, 0.2, 1)
        )
        layout.add_widget(self.online_label)
        
        # Stats panel
        self.stats_layout = GridLayout(
            cols=2,
            size_hint_y=0.25,
            padding=10,
            spacing=5
        )
        layout.add_widget(self.stats_layout)
        
        # Menu buttons (admin functions only)
        menu_layout = GridLayout(
            cols=2,
            size_hint_y=0.4,
            padding=10,
            spacing=10
        )
        
        buttons = [
            ('Tambah User', self.go_to_add_user, (0.2, 0.8, 0.2, 1)),
            ('Ambil Token', self.go_to_take_tokens, (1, 0.6, 0.2, 1)),
            ('Ban Token', self.go_to_ban_token, (1, 0.2, 0.2, 1)),
            ('Cek Token', self.go_to_check_token, (0.8, 0.2, 0.2, 1)),
            ('Lihat User', self.go_to_users, (0.2, 0.6, 1, 1)),
            ('Grup Chat', self.go_to_chat, (0.8, 0.2, 0.8, 1)),
            ('Pengaturan', self.go_to_settings, (0.6, 0.6, 0.6, 1)),
            ('Log Aktivitas', self.go_to_activity, (0.6, 0.2, 0.8, 1))
        ]

        
        for text, callback, color in buttons:
            btn = Button(
                text=text,
                font_size='14sp',
                bold=True,
                background_color=color
            )
            btn.bind(on_press=callback)
            menu_layout.add_widget(btn)
        
        layout.add_widget(menu_layout)
        
        # Status info
        self.status_label = Label(
            text='Admin: Kelola pengguna, ambil token, monitor sistem',
            size_hint_y=0.17,
            font_size='12sp',
            color=(0.5, 0.5, 0.5, 1)
        )
        layout.add_widget(self.status_label)
        
        self.add_widget(layout)

    def go_to_ban_token(self, instance):
        self.manager.current = 'ban_token'


    def update_stats(self):
        if not self.firebase_manager:
            return
        
        def update_in_background():
            stats = self.firebase_manager.get_all_stats()
            online_users = self.firebase_manager.get_online_users()
            Clock.schedule_once(lambda dt: self._update_stats_ui(stats, online_users), 0)
        
        threading.Thread(target=update_in_background, daemon=True).start()
    
    def _update_stats_ui(self, stats, online_users):
        self.stats_layout.clear_widgets()
        
        # Update online users notification
        if online_users:
            online_text = f"Online: {', '.join(online_users)}"
        else:
            online_text = "Tidak ada pengguna online"
        self.online_label.text = online_text
        # self.online_label.font_name = 'EmojiFont'
        
        stats_items = [
            ('Total Token:', f"{stats.get('total_tokens', 0):,}"),
            ('Tersedia:', f"{stats.get('available_tokens', 0):,}"),
            ('Diambil:', f"{stats.get('taken_tokens', 0):,}"),
            ('Total User:', f"{stats.get('total_users', 0)}"),
            ('User Online:', f"{stats.get('online_users', 0)}"),
            ('Harga/Token:', f"Rp {stats.get('price_per_token', 1500):,}")
        ]
        
        for label, value in stats_items:
            self.stats_layout.add_widget(Label(
                text=label,
                font_size='11sp',
                bold=True
            ))
            self.stats_layout.add_widget(Label(
                text=value,
                font_size='11sp',
                color=(0.2, 0.6, 1, 1)
            ))
    
    def on_enter(self):
        Clock.schedule_once(lambda dt: self.update_stats(), 0.1)
        # Auto-refresh stats every 15 seconds
        Clock.schedule_interval(lambda dt: self.update_stats(), 15)
    
    def on_leave(self):
        Clock.unschedule(self.update_stats)
    
    def logout(self, instance):
        if self.firebase_manager and self.username:
            self.firebase_manager.logout(self.username)
        
        # Clear session
        SessionManager().clear_session()
        
        self.manager.current = 'login'
    
    def go_to_add_user(self, instance):
        self.manager.current = 'add_user'
    
    def go_to_take_tokens(self, instance):
        self.manager.current = 'take_tokens'
    
    def go_to_users(self, instance):
        self.manager.current = 'users'
    
    def go_to_chat(self, instance):
        self.manager.current = 'chat'
    
    def go_to_settings(self, instance):
        self.manager.current = 'settings'
    
    def go_to_activity(self, instance):
        self.manager.current = 'activity'
    
    def go_to_check_token(self, instance):
        self.manager.current = 'check_token'

class UserDashboardScreen(Screen):
    """User dashboard with Indonesian language"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.firebase_manager = None
        self.username = None
        self.build_ui()
    
    def set_firebase(self, firebase_manager):
        self.firebase_manager = firebase_manager
    
    def set_username(self, username):
        self.username = username
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = BoxLayout(size_hint_y=0.1)
        self.title_label = Label(
            text='DASHBOARD USER',
            font_size='20sp',
            bold=True
        )
        header.add_widget(self.title_label)
        
        logout_btn = Button(
            text='Keluar',
            size_hint_x=0.3,
            background_color=(1, 0.3, 0.3, 1)
        )
        logout_btn.bind(on_press=self.logout)
        header.add_widget(logout_btn)
        
        layout.add_widget(header)
        
        # Online users notification
        self.online_label = Label(
            text='Memuat pengguna online...',
            size_hint_y=0.08,
            font_size='12sp',
            color=(0.2, 0.8, 0.2, 1)
        )
        layout.add_widget(self.online_label)
        
        # Stats panel
        self.stats_layout = GridLayout(
            cols=2,
            size_hint_y=0.25,
            padding=10,
            spacing=5
        )
        self.update_stats()
        layout.add_widget(self.stats_layout)
        
        # Menu buttons (user functions only)
        menu_layout = GridLayout(
            cols=2,
            size_hint_y=0.4,
            padding=10,
            spacing=10
        )
        
        buttons = [
            ('Tambah Token', self.go_to_add_token, (0.2, 0.8, 0.2, 1)),
            ('Penghasilan Saya', self.show_earnings, (0.2, 0.8, 0.8, 1)),
            ('Info Pribadi', self.go_to_user_info, (0.8, 0.6, 0.2, 1)),
            ('Lihat User', self.go_to_users, (0.2, 0.6, 1, 1)),
            ('Grup Chat', self.go_to_chat, (0.8, 0.2, 0.8, 1)),
            ('Pengaturan', self.go_to_user_settings, (0.6, 0.6, 0.6, 1))
        ]

        for text, callback, color in buttons:
            btn = Button(
                text=text,
                font_size='14sp',
                bold=True,
                background_color=color
            )
            btn.bind(on_press=callback)
            menu_layout.add_widget(btn)
        
        layout.add_widget(menu_layout)
        
        # Status info
        self.status_label = Label(
            text='User: Tambahkan token untuk mendapatkan uang, chat dengan tim',
            size_hint_y=0.17,
            font_size='12sp',
            color=(0.5, 0.5, 0.5, 1)
        )
        layout.add_widget(self.status_label)
        
        self.add_widget(layout)
    
    def update_stats(self):
        if not self.firebase_manager or not self.username:
            return
        
        def update_in_background():
            user_stats = self.firebase_manager.get_user_stats(self.username)
            all_stats = self.firebase_manager.get_all_stats()
            online_users = self.firebase_manager.get_online_users()
            Clock.schedule_once(lambda dt: self._update_stats_ui(user_stats, all_stats, online_users), 0)
        
        threading.Thread(target=update_in_background, daemon=True).start()
    
    def _update_stats_ui(self, user_stats, all_stats, online_users):
        self.stats_layout.clear_widgets()
        
        if self.username:
            self.title_label.text = f'Selamat datang, {self.username.upper()}'
        
        # Update online users notification
        online_users_filtered = [u for u in online_users if u != self.username]
        if online_users_filtered:
            online_text = f"Online: {', '.join(online_users_filtered)}"
        else:
            online_text = "Tidak ada pengguna lain yang online"
        self.online_label.text = online_text
        # self.online_label.font_name = 'EmojiFont'
        
        # Show user-specific stats with bancet info
        banned_count = user_stats.get('banned_count', 0)
        stats_items = [
            ('Token Anda:', f"{user_stats.get('token_count', 0):,}"),
            ('Token Bancet:', f"Bancet: {banned_count:,}"),
            ('Penghasilan Anda:', f"Rp {user_stats.get('total_value', 0):,}"),
            ('Total Token Sistem:', f"{all_stats.get('total_tokens', 0):,}"),
            ('Tersedia Sistem:', f"{all_stats.get('available_tokens', 0):,}"),
            ('Harga Token:', f"Rp {all_stats.get('price_per_token', 1500):,}")
        ]
        
        for label, value in stats_items:
            label_widget = Label(
                text=label,
                font_size='11sp',
                bold=True
            )
            
            # Highlight bancet count if > 0
            if 'Bancet' in label and banned_count > 0:
                value_widget = Label(
                    text=value,
                    font_size='11sp',
                    color=(1, 0.2, 0.2, 1)  # Red color for bancet
                )
            else:
                value_widget = Label(
                    text=value,
                    font_size='11sp',
                    color=(0.2, 0.6, 1, 1)
                )
            
            self.stats_layout.add_widget(label_widget)
            self.stats_layout.add_widget(value_widget)

    def show_earnings(self, instance):
        if not self.firebase_manager or not self.username:
            return
        
        def get_earnings_in_background():
            user_stats = self.firebase_manager.get_user_stats(self.username)
            banned_count = user_stats.get('banned_count', 0)
            earnings_text = f"Total Token: {user_stats.get('token_count', 0):,}\n"
            earnings_text += f"Token Bancet: {banned_count:,}\n"
            earnings_text += f"Total Nilai: Rp {user_stats.get('total_value', 0):,}\n"
            
            if user_stats.get('token_count', 0) > 0:
                avg_per_token = user_stats.get('total_value', 0) // max(user_stats.get('token_count', 1), 1)
                earnings_text += f"Rata-rata per Token: Rp {avg_per_token:,}\n"
            
            earnings_text += f"Akun Dibuat: {user_stats.get('created', 'Tidak diketahui')[:10]}\n"
            earnings_text += f"Login Terakhir: {user_stats.get('last_login', 'Belum pernah')[:10]}\n\n"
            
            if banned_count > 0:
                earnings_text += f"Catatan: {banned_count} token Anda pernah di-ban karena rusak/bermasalah"
            
            Clock.schedule_once(lambda dt: self.show_earnings_popup(earnings_text), 0)
        
        threading.Thread(target=get_earnings_in_background, daemon=True).start()

    def show_earnings_popup(self, earnings_text):
        # Create scrollable content for earnings
        scroll = ScrollView()
        content_label = Label(
            text=earnings_text,
            text_size=(None, None),
            halign='left',
            valign='top',
            size_hint_y=None
        )
        content_label.bind(texture_size=content_label.setter('size'))
        
        def update_text_size(instance, *args):
            if instance.parent and instance.parent.width > 40:
                instance.text_size = (instance.parent.width - 40, None)
        
        content_label.bind(parent=update_text_size)
        scroll.bind(size=lambda *args: update_text_size(content_label))
        scroll.add_widget(content_label)
        
        popup = Popup(
            title='Ringkasan Penghasilan Anda',
            content=scroll,
            size_hint=(0.9, 0.7)
        )
        popup.open()
    
    def show_help(self, instance):
        help_text = """Cara menggunakan Token Manager:

1. Tambah Token: Kirim token yang valid untuk mendapatkan uang
2. Penghasilan Saya: Lihat total penghasilan Anda
3. Lihat User: Lihat semua pengguna dan statistik mereka
4. Grup Chat: Chat dengan pengguna lain
5. Pengaturan: Ubah password Anda

Format Token:
- Harus dimulai dengan 'u' diikuti 32 karakter hex
- Kemudian ':' dan data base64 encoded
- Harus mengandung separator '..'
- Minimal 50 karakter total

Hubungi admin jika butuh bantuan!"""
        
        popup = Popup(
            title='Bantuan & Instruksi',
            content=Label(text=help_text),
            size_hint=(0.9, 0.8)
        )
        popup.open()
    
    def on_enter(self):
        Clock.schedule_once(lambda dt: self.update_stats(), 0.1)
        # Auto-refresh stats every 15 seconds
        Clock.schedule_interval(lambda dt: self.update_stats(), 15)
    
    def on_leave(self):
        Clock.unschedule(self.update_stats)
    
    def logout(self, instance):
        if self.firebase_manager and self.username:
            self.firebase_manager.logout(self.username)
        
        # Clear session
        SessionManager().clear_session()
        
        self.manager.current = 'login'
    
    def go_to_add_token(self, instance):
        self.manager.current = 'add_token'
    
    def go_to_users(self, instance):
        self.manager.current = 'users'
    
    def go_to_chat(self, instance):
        self.manager.current = 'chat'
    
    def go_to_user_settings(self, instance):
        self.manager.current = 'user_settings'
    
    def go_to_user_info(self, instance):
        self.manager.current = 'user_info'

class AddUserScreen(Screen):
    """Screen for adding new users (admin only) - Indonesian"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.firebase_manager = None
        self.build_ui()
    
    def set_firebase(self, firebase_manager):
        self.firebase_manager = firebase_manager
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Header
        header = BoxLayout(size_hint_y=0.15)
        back_btn = Button(
            text='Kembali',
            size_hint_x=0.3,
            background_color=(0.6, 0.6, 0.6, 1)
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'admin_dashboard'))
        header.add_widget(back_btn)
        
        header.add_widget(Label(
            text='TAMBAH USER BARU',
            font_size='20sp',
            bold=True
        ))
        
        layout.add_widget(header)
        
        # Instructions
        instructions = Label(
            text='Masukkan username untuk user baru.\nUser akan dapat login dan menambahkan token.',
            font_size='14sp',
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=0.15
        )
        layout.add_widget(instructions)
        
        # Username input
        self.username_input = TextInput(
            hint_text='Masukkan username baru (huruf, angka, underscore saja)',
            multiline=False,
            font_size='16sp',
            size_hint_y=0.1
        )
        layout.add_widget(self.username_input)
        
        # Password input
        self.password_input = TextInput(
            hint_text='Masukkan password untuk user (opsional)',
            password=True,
            multiline=False,
            font_size='16sp',
            size_hint_y=0.1
        )
        layout.add_widget(self.password_input)
        
        # Add user button
        add_btn = Button(
            text='TAMBAH USER',
            font_size='18sp',
            bold=True,
            background_color=(0.2, 0.8, 0.2, 1),
            size_hint_y=0.12
        )
        add_btn.bind(on_press=self.add_user)
        layout.add_widget(add_btn)
        
        # Status label
        self.status_label = Label(
            text='',
            font_size='14sp',
            size_hint_y=0.2
        )
        layout.add_widget(self.status_label)
        
        # Recent users list
        recent_label = Label(
            text='User yang Baru Ditambahkan:',
            font_size='16sp',
            bold=True,
            size_hint_y=0.08
        )
        layout.add_widget(recent_label)
        
        self.recent_users_scroll = ScrollView(size_hint_y=0.2)
        self.recent_users_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.recent_users_layout.bind(minimum_height=self.recent_users_layout.setter('height'))
        self.recent_users_scroll.add_widget(self.recent_users_layout)
        layout.add_widget(self.recent_users_scroll)
        
        self.add_widget(layout)
    
    def on_enter(self):
        self.load_recent_users()
    
    def load_recent_users(self):
        if not self.firebase_manager:
            return
        
        def load_in_background():
            users = self.firebase_manager.get_all_users()
            # Sort by creation date, newest first
            users.sort(key=lambda x: x.get('created', ''), reverse=True)
            recent_users = users[:5]  # Show last 5 users
            Clock.schedule_once(lambda dt: self.update_recent_users_ui(recent_users), 0)
        
        threading.Thread(target=load_in_background, daemon=True).start()
    
    def update_recent_users_ui(self, users):
        self.recent_users_layout.clear_widgets()
        
        if users:
            for user in users:
                user_info = f"{user['username']} - {user.get('token_count', 0)} token - {user.get('created', '')[:10]}"
                user_label = Label(
                    text=user_info,
                    size_hint_y=None,
                    height=30,
                    font_size='12sp'
                )
                self.recent_users_layout.add_widget(user_label)
        else:
            self.recent_users_layout.add_widget(Label(
                text='Tidak ada user ditemukan',
                size_hint_y=None,
                height=30
            ))
    
    def add_user(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        
        if not username:
            self.status_label.text = 'Silakan masukkan username'
            self.status_label.color = (1, 0.2, 0.2, 1)
            return
        
        # Validate username
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            self.status_label.text = 'Username hanya boleh berisi huruf, angka, dan underscore'
            self.status_label.color = (1, 0.2, 0.2, 1)
            return
        
        if len(username) < 3:
            self.status_label.text = 'Username minimal 3 karakter'
            self.status_label.color = (1, 0.2, 0.2, 1)
            return
        
        if not password:
            self.status_label.text = 'Silakan masukkan password untuk user'
            self.status_label.color = (1, 0.2, 0.2, 1)
            return
        
        if len(password) < 6:
            self.status_label.text = '✗ Password minimal 6 karakter'
            self.status_label.color = (1, 0.2, 0.2, 1)
            return
        
        self.status_label.text = 'Menambahkan user...'
        self.status_label.color = (0.2, 0.6, 1, 1)
        
        def add_user_in_background():
            success, message = self.firebase_manager.add_user(username, App.get_running_app().current_user, password)
            Clock.schedule_once(lambda dt: self.handle_add_result(success, message), 0)
        
        threading.Thread(target=add_user_in_background, daemon=True).start()
    
    def handle_add_result(self, success, message):
        self.status_label.text = f'{"✓" if success else "✗"} {message}'
        self.status_label.color = (0.2, 0.8, 0.2, 1) if success else (1, 0.2, 0.2, 1)
        
        if success:
            self.username_input.text = ''
            self.password_input.text = ''
            self.load_recent_users()

class AddTokenScreen(Screen):
    """Screen for adding tokens (users only) - Indonesian"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.firebase_manager = None
        self.username = None
        self.build_ui()
    
    def set_firebase(self, firebase_manager):
        self.firebase_manager = firebase_manager
    
    def set_username(self, username):
        self.username = username
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Header
        header = BoxLayout(size_hint_y=0.12)
        back_btn = Button(
            text='Kembali',
            size_hint_x=0.3,
            background_color=(0.6, 0.6, 0.6, 1)
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'user_dashboard'))
        header.add_widget(back_btn)
        
        header.add_widget(Label(
            text='TAMBAH TOKEN',
            font_size='20sp',
            bold=True
        ))
        
        layout.add_widget(header)
        
        # Current price info
        self.price_label = Label(
            text='Memuat harga saat ini...',
            font_size='14sp',
            color=(0.2, 0.8, 0.2, 1),
            size_hint_y=0.08
        )
        layout.add_widget(self.price_label)
        
        # Token input modes
        mode_layout = BoxLayout(size_hint_y=0.1, spacing=10)
        self.single_btn = Button(
            text='Token Tunggal',
            background_color=(0.2, 0.8, 0.2, 1)
        )
        self.bulk_btn = Button(
            text='Token Massal',
            background_color=(0.6, 0.6, 0.6, 1)
        )
        
        self.single_btn.bind(on_press=lambda x: self.select_mode('single'))
        self.bulk_btn.bind(on_press=lambda x: self.select_mode('bulk'))
        
        mode_layout.add_widget(self.single_btn)
        mode_layout.add_widget(self.bulk_btn)
        layout.add_widget(mode_layout)
        
        # Token input
        self.token_input = TextInput(
            hint_text='Tempel token Anda di sini (harus dimulai dengan u dan format valid)',
            multiline=False,
            font_size='14sp',
            size_hint_y=0.12
        )
        layout.add_widget(self.token_input)
        
        # Add token button
        add_btn = Button(
            text='TAMBAH TOKEN',
            font_size='18sp',
            bold=True,
            background_color=(0.2, 0.8, 0.2, 1),
            size_hint_y=0.12
        )
        add_btn.bind(on_press=self.add_token)
        layout.add_widget(add_btn)
        
        # Status label
        self.status_label = Label(
            text='',
            font_size='14sp',
            size_hint_y=0.15
        )
        layout.add_widget(self.status_label)
        
        # Token format help
        help_text = """Persyaratan Format Token:
• Harus dimulai dengan 'u' + 32 karakter hex
• Diikuti ':' dan data base64

• Harus mengandung separator '..'
• Minimal 50 karakter total
• Contoh: u1234567890abcdef...:data..more"""
        
        help_label = Label(
            text=help_text,
            font_size='11sp',
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=0.31
        )
        layout.add_widget(help_label)
        
        self.current_mode = 'single'
        
        self.add_widget(layout)
    
    def on_enter(self):
        self.load_current_price()
    
    def load_current_price(self):
        if not self.firebase_manager:
            return
        
        def load_in_background():
            settings = self.firebase_manager.get_data("settings")
            price = settings.get('price_per_token', 1500) if settings else 1500
            Clock.schedule_once(lambda dt: self.update_price_ui(price), 0)
        
        threading.Thread(target=load_in_background, daemon=True).start()
    
    def update_price_ui(self, price):
        self.price_label.text = f'Harga Saat Ini: Rp {price:,} per token'
        apply_emoji_font(self.price_label)
    
    def select_mode(self, mode):
        self.current_mode = mode
        if mode == 'single':
            self.single_btn.background_color = (0.2, 0.8, 0.2, 1)
            self.bulk_btn.background_color = (0.6, 0.6, 0.6, 1)
            self.token_input.multiline = False
            self.token_input.hint_text = 'Tempel token Anda di sini (harus dimulai dengan u dan format valid)'
        else:
            self.single_btn.background_color = (0.6, 0.6, 0.6, 1)
            self.bulk_btn.background_color = (0.2, 0.8, 0.2, 1)
            self.token_input.multiline = True
            self.token_input.hint_text = 'Tempel beberapa token di sini (satu per baris)'
    
    def add_token(self, instance):
        token_text = self.token_input.text.strip()
        
        if not token_text:
            self.status_label.text = 'Silakan masukkan token'
            self.status_label.color = (1, 0.2, 0.2, 1)
            return
        
        self.status_label.text = 'Menambahkan token...'
        self.status_label.color = (0.2, 0.6, 1, 1)
        
        def add_token_in_background():
            if self.current_mode == 'single':
                success, message = self.firebase_manager.add_token(token_text, self.username, self.username)
                Clock.schedule_once(lambda dt: self.handle_add_result(success, message, None), 0)
            else:
                success, message, details = self.firebase_manager.add_bulk_tokens(token_text, self.username, self.username)
                Clock.schedule_once(lambda dt: self.handle_add_result(success, message, details), 0)
        
        threading.Thread(target=add_token_in_background, daemon=True).start()
    
    def handle_add_result(self, success, message, details):
        if details:  # Bulk mode
            result_text = f"{message}\n"
            result_text += f"Berhasil: {details.get('success', 0)}\n"
            result_text += f"Duplikat: {details.get('duplicates', 0)}\n"
            result_text += f"Tidak Valid: {details.get('invalid', 0)}"
            self.status_label.text = result_text
        else:  # Single mode
            self.status_label.text = f'{"✓" if success else "✗"} {message}'
        
        self.status_label.color = (0.2, 0.8, 0.2, 1) if success else (1, 0.2, 0.2, 1)
        
        if success:
            self.token_input.text = ''

class TakeTokensScreen(Screen):
    """Screen for taking tokens (admin only) - Indonesian with bulk copy"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.firebase_manager = None
        self.taken_tokens_list = []
        self.build_ui()
    
    def set_firebase(self, firebase_manager):
        self.firebase_manager = firebase_manager
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Header
        header = BoxLayout(size_hint_y=0.12)
        back_btn = Button(
            text='Kembali',
            size_hint_x=0.3,
            background_color=(0.6, 0.6, 0.6, 1)
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'admin_dashboard'))
        header.add_widget(back_btn)
        
        header.add_widget(Label(
            text='AMBIL TOKEN',
            font_size='20sp',
            bold=True
        ))
        
        layout.add_widget(header)
        
        # Available tokens info
        self.available_label = Label(
            text='Memuat token yang tersedia...',
            font_size='14sp',
            color=(0.2, 0.8, 0.2, 1),
            size_hint_y=0.1
        )
        layout.add_widget(self.available_label)
        
        # Count input
        self.count_input = TextInput(
            hint_text='Masukkan jumlah token yang akan diambil',
            multiline=False,
            font_size='16sp',
            size_hint_y=0.1,
            input_filter='int'
        )
        layout.add_widget(self.count_input)
        
        # Take tokens button
        take_btn = Button(
            text='AMBIL TOKEN',
            font_size='18sp',
            bold=True,
            background_color=(1, 0.6, 0.2, 1),
            size_hint_y=0.12
        )
        take_btn.bind(on_press=self.take_tokens)
        layout.add_widget(take_btn)
        
        # Status label
        self.status_label = Label(
            text='',
            font_size='14sp',
            size_hint_y=0.15
        )
        layout.add_widget(self.status_label)
        
        # Copy all tokens button
        self.copy_all_btn = Button(
            text='📋 SALIN SEMUA TOKEN',
            font_size='16sp',
            bold=True,
            background_color=(0.2, 0.8, 0.2, 1),
            size_hint_y=0.1,
            opacity=0
        )
        self.copy_all_btn.bind(on_press=self.copy_all_tokens)
        layout.add_widget(self.copy_all_btn)
        
        # Taken tokens display
        taken_label = Label(
            text='Token yang Diambil:',
            font_size='16sp',
            bold=True,
            size_hint_y=0.08
        )
        layout.add_widget(taken_label)
        
        self.taken_tokens_scroll = ScrollView(size_hint_y=0.23)
        self.taken_tokens_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.taken_tokens_layout.bind(minimum_height=self.taken_tokens_layout.setter('height'))
        self.taken_tokens_scroll.add_widget(self.taken_tokens_layout)
        layout.add_widget(self.taken_tokens_scroll)
        
        self.add_widget(layout)
    
    def on_enter(self):
        self.load_available_count()
    
    def load_available_count(self):
        if not self.firebase_manager:
            return
        
        def load_in_background():
            count = self.firebase_manager.get_available_tokens_count()
            Clock.schedule_once(lambda dt: self.update_available_ui(count), 0)
        
        threading.Thread(target=load_in_background, daemon=True).start()
    
    def update_available_ui(self, count):
        self.available_label.text = f'Token Tersedia: {count:,}'
        apply_emoji_font(self.available_label)
    
    def take_tokens(self, instance):
        count_text = self.count_input.text.strip()
        
        if not count_text or not count_text.isdigit():
            self.status_label.text = 'Silakan masukkan angka yang valid'
            self.status_label.color = (1, 0.2, 0.2, 1)
            return
        
        count = int(count_text)
        if count <= 0:
            self.status_label.text = 'Harga harus lebih besar dari 0'
            self.status_label.color = (1, 0.2, 0.2, 1)
            return
        
        self.status_label.text = f'Mengambil {count} token...'
        self.status_label.color = (0.2, 0.6, 1, 1)
        
        def take_tokens_in_background():
            result = self.firebase_manager.take_tokens(count, App.get_running_app().current_user)
            Clock.schedule_once(lambda dt: self.handle_take_result(result), 0)
        
        threading.Thread(target=take_tokens_in_background, daemon=True).start()
    
    def handle_take_result(self, result):
        if result and result.get('success'):
            tokens = result.get('tokens', [])
            count = result.get('count', 0)
            
            # Store tokens for bulk copy
            self.taken_tokens_list = tokens
            
            self.status_label.text = f'✅Berhasil mengambil {count} token!'
            self.status_label.color = (0.2, 0.8, 0.2, 1)
            
            # Show copy all button
            self.copy_all_btn.opacity = 1
            
            # Display taken tokens (preview only)
            self.taken_tokens_layout.clear_widgets()
            for i, token in enumerate(tokens, 1):
                token_preview = Label(
                    text=f'{i}. {token[:15]}...{token[-10:]}',
                    size_hint_y=None,
                    height=30,
                    font_size='12sp',
                    color=(0.8, 0.8, 0.8, 1)
                )
                self.taken_tokens_layout.add_widget(token_preview)
            
            # Clear input and refresh available count
            self.count_input.text = ''
            self.load_available_count()
        else:
            self.status_label.text = '✗ Gagal mengambil token (tidak cukup tersedia?)'
            self.status_label.color = (1, 0.2, 0.2, 1)
    
    def copy_all_tokens(self, instance):
        """Copy all taken tokens to clipboard at once"""
        if not self.taken_tokens_list:
            self.status_label.text = '✗ Tidak ada token untuk disalin'
            self.status_label.color = (1, 0.2, 0.2, 1)
            return
        
        try:
            # Join all tokens with newline
            all_tokens_text = '\n'.join(self.taken_tokens_list)
            Clipboard.copy(all_tokens_text)
            
            self.status_label.text = f'✅{len(self.taken_tokens_list)} token berhasil disalin ke clipboard!'
            self.status_label.color = (0.2, 0.8, 0.2, 1)
            
            # Hide copy button after successful copy
            self.copy_all_btn.opacity = 0
            
        except Exception as e:
            self.status_label.text = '✗ Gagal menyalin token'
            self.status_label.color = (1, 0.2, 0.2, 1)

class CheckTokenScreen(Screen):
    """Screen for checking token ownership (admin only)"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.firebase_manager = None
        self.build_ui()
    
    def set_firebase(self, firebase_manager):
        self.firebase_manager = firebase_manager
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Header
        header = BoxLayout(size_hint_y=0.12)
        back_btn = Button(
            text='Kembali',
            size_hint_x=0.3,
            background_color=(0.6, 0.6, 0.6, 1)
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'admin_dashboard'))
        header.add_widget(back_btn)
        
        header.add_widget(Label(
            text='CEK PEMILIK TOKEN',
            font_size='20sp',
            bold=True
        ))
        
        layout.add_widget(header)
        
        # Instructions
        instructions = Label(
            text='Masukkan token untuk mengetahui siapa pemiliknya dan status token tersebut.',
            font_size='14sp',
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=0.1
        )
        layout.add_widget(instructions)
        
        # Token input
        self.token_input = TextInput(
            hint_text='Tempel token yang ingin dicek di sini',
            multiline=False,
            font_size='14sp',
            size_hint_y=0.12
        )
        layout.add_widget(self.token_input)
        
        # Check button
        check_btn = Button(
            text='CEK TOKEN',
            font_size='18sp',
            bold=True,
            background_color=(0.2, 0.6, 1, 1),
            size_hint_y=0.1
        )
        check_btn.bind(on_press=self.check_token)
        layout.add_widget(check_btn)
        
        # Result display
        self.result_scroll = ScrollView(size_hint_y=0.46)
        self.result_layout = BoxLayout(orientation='vertical', size_hint_y=None, padding=10, spacing=10)
        self.result_layout.bind(minimum_height=self.result_layout.setter('height'))
        self.result_scroll.add_widget(self.result_layout)
        layout.add_widget(self.result_scroll)
        
        self.add_widget(layout)
    
    def check_token(self, instance):
        token_to_check = self.token_input.text.strip()
        
        if not token_to_check:
            self.show_result('✗ Silakan masukkan token', (1, 0.2, 0.2, 1))
            return
        
        self.show_result('Mencari token...', (0.2, 0.6, 1, 1))
        
        def check_in_background():
            result, message = self.firebase_manager.check_token_owner(token_to_check)
            Clock.schedule_once(lambda dt: self.handle_check_result(result, message), 0)
        
        threading.Thread(target=check_in_background, daemon=True).start()
    
    def handle_check_result(self, result, message):
        self.result_layout.clear_widgets()
        
        if result:
            # Token found - show detailed info
            info_text = f"""TOKEN DITEMUKAN

Pemilik: {result['owner']}
Status: {result['status']}
Ditambahkan: {result['timestamp']}
Harga: Rp {result['price']:,}
ID Token: {result['token_id']}"""
            
            self.result_layout.add_widget(Label(
                text=info_text,
                font_size='14sp',
                color=(0.2, 0.8, 0.2, 1),
                size_hint_y=None,
                height=200,
                halign='left'
            ))
            
            # Add action buttons if needed
            if result['status'] == 'available':
                action_btn = Button(
                    text='Tandai sebagai Bermasalah',
                    font_size='14sp',
                    background_color=(1, 0.6, 0.2, 1),
                    size_hint_y=None,
                    height=40
                )
                # You can add functionality here
                self.result_layout.add_widget(action_btn)
                
        else:
            # Token not found
            self.result_layout.add_widget(Label(
                text=f'✗ {message}',
                font_size='14sp',
                color=(1, 0.2, 0.2, 1),
                size_hint_y=None,
                height=50
            ))
    
    def show_result(self, text, color):
        self.result_layout.clear_widgets()
        self.result_layout.add_widget(Label(
            text=text,
            font_size='14sp',
            color=color,
            size_hint_y=None,
            height=50
        ))

class UsersScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.firebase_manager = None
        self.build_ui()
    
    def set_firebase(self, firebase_manager):
        self.firebase_manager = firebase_manager
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        header = BoxLayout(size_hint_y=0.12)
        back_btn = Button(
            text='Kembali', 
            size_hint_x=0.3, 
            background_color=(0.6, 0.6, 0.6, 1)
        )
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        
        header.add_widget(Label(
            text='SEMUA PENGGUNA', 
            font_size='20sp', 
            bold=True
        ))
        
        layout.add_widget(header)
        
        self.stats_label = Label(
            text='Memuat pengguna...', 
            font_size='14sp', 
            color=(0.2, 0.8, 0.2, 1), 
            size_hint_y=0.08
        )
        layout.add_widget(self.stats_label)
        
        refresh_btn = Button(
            text='Refresh', 
            font_size='16sp', 
            background_color=(0.2, 0.6, 1, 1), 
            size_hint_y=0.1,
            # font_name='EmojiFont'
        )
        refresh_btn.bind(on_press=lambda x: self.load_users())
        layout.add_widget(refresh_btn)
        
        self.users_scroll = ScrollView(size_hint_y=0.6)
        self.users_layout = BoxLayout(
            orientation='vertical', 
            size_hint_y=None, 
            spacing=15, 
            padding=10
        )
        self.users_layout.bind(minimum_height=self.users_layout.setter('height'))
        self.users_scroll.add_widget(self.users_layout)
        layout.add_widget(self.users_scroll)
        
        self.add_widget(layout)
    
    def on_enter(self):
        self.load_users()
    
    def go_back(self, instance):
        app = App.get_running_app()
        if hasattr(app, 'user_type') and app.user_type == 'admin':
            self.manager.current = 'admin_dashboard'
        else:
            self.manager.current = 'user_dashboard'
    
    def load_users(self):
        if not self.firebase_manager:
            return
        
        def load_in_background():
            users = self.firebase_manager.get_all_users()
            Clock.schedule_once(lambda dt: self.update_users_ui(users), 0)
        
        threading.Thread(target=load_in_background, daemon=True).start()
    
    def update_users_ui(self, users):
        self.users_layout.clear_widgets()
        
        if users:
            total_users = len(users)
            online_users = len([u for u in users if u.get('is_online', False)])
            total_tokens = sum(u.get('token_count', 0) for u in users)
            
            self.stats_label.text = f'{total_users} pengguna | {online_users} online | {total_tokens:,} total token'
            apply_emoji_font(self.stats_label)
            
            for user in users:
                user_card = self.create_user_card(user)
                self.users_layout.add_widget(user_card)
        else:
            self.stats_label.text = 'Tidak ada pengguna ditemukan'
            self.users_layout.add_widget(Label(
                text='Tidak ada pengguna ditemukan', 
                size_hint_y=None, 
                height=50
            ))
    
    def create_user_card(self, user):
        card_container = BoxLayout(
            orientation='vertical', 
            size_hint_y=None, 
            height=120, 
            padding=15, 
            spacing=8
        )
        
        header = BoxLayout(size_hint_y=0.3, spacing=10)
        
        status_color = (0.2, 0.8, 0.2, 1) if user.get('is_online', False) else (0.6, 0.6, 0.6, 1)
        status_text = 'ONLINE' if user.get('is_online', False) else 'OFFLINE'
        
        username_label = Label(
            text=f"{user['username']} ({status_text})", 
            font_size='16sp', 
            bold=True, 
            color=status_color, 
            halign='left', 
            size_hint_x=0.7
        )
        username_label.bind(size=username_label.setter('text_size'))
        header.add_widget(username_label)
        
        tokens_label = Label(
            text=f"🪙 {user.get('token_count', 0):,}", 
            font_size='14sp', 
            color=(0.2, 0.6, 1, 1), 
            size_hint_x=0.3, 
            halign='right'
        )
        tokens_label.bind(size=tokens_label.setter('text_size'))
        header.add_widget(tokens_label)
        
        card_container.add_widget(header)
        
        details = BoxLayout(size_hint_y=0.4, spacing=10, orientation='horizontal')
        earnings_text = f"Rp {user.get('total_value', 0):,}"
        banned_text = f"Bancet: {user.get('banned_count', 0)}"
        created_text = f"Bergabung: {user.get('created', '')[:10]}"
        
        details_label = Label(
            text=f"{earnings_text} | {banned_text} | {created_text}", 
            font_size='12sp', 
            color=(0.7, 0.7, 0.7, 1), 
            halign='left'
        )
        details_label.bind(size=details_label.setter('text_size'))
        details.add_widget(details_label)
        
        info_btn = Button(
            text='Lihat Info', 
            font_size='12sp', 
            bold=True, 
            background_color=(0.2, 0.6, 1, 1), 
            size_hint_x=0.3
        )
        info_btn.bind(on_press=lambda instance: self.show_user_info(user))
        details.add_widget(info_btn)
        
        app = App.get_running_app()
        if app.user_type == 'admin':
            delete_btn = Button(
                text='Hapus', 
                font_size='12sp', 
                bold=True, 
                background_color=(1, 0.2, 0.2, 1), 
                size_hint_x=0.3
            )
            delete_btn.bind(on_press=lambda instance: self.confirm_delete_user(user['username']))
            details.add_widget(delete_btn)
        
        card_container.add_widget(details)
        
        separator = BoxLayout(size_hint_y=None, height=2)
        separator.add_widget(Label(text='', size_hint_y=None, height=1))
        final_container = BoxLayout(orientation='vertical', size_hint_y=None, height=130, spacing=5)
        final_container.add_widget(card_container)
        final_container.add_widget(separator)
        
        return final_container
    
    def show_user_info(self, user):
        info_text = (
            f"Info {user['username']}:\n\n"
            f"Nomor WA: {user.get('wa', 'Belum diisi')}\n"
            f"Nomor Rekening: {user.get('rekening', 'Belum diisi')}\n"
            f"Tanggal Lahir: {user.get('tgl_lahir', 'Belum diisi')}\n"
            f"Tempat Tinggal: {user.get('tempat_tinggal', 'Belum diisi')}\n\n"
            f"Token Bancet: {user.get('banned_count', 0):,}\n"
            f"Total Token: {user.get('token_count', 0):,}\n"
            f"Total Penghasilan: Rp {user.get('total_value', 0):,}"
        )
        Popup(
            title=f'Info {user["username"]}', 
            content=Label(text=info_text), 
            size_hint=(0.8, 0.6)
        ).open()
    
    def confirm_delete_user(self, username):
        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(Label(
            text=f'Yakin hapus {username}?\nIni tidak dapat dibatalkan!'
        ))
        button_layout = BoxLayout(spacing=10, size_hint_y=0.3)
        confirm_btn = Button(text='YA, HAPUS', background_color=(1, 0.2, 0.2, 1))
        cancel_btn = Button(text='BATAL', background_color=(0.6, 0.6, 0.6, 1))
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(confirm_btn)
        content.add_widget(button_layout)
        
        popup = Popup(
            title='Konfirmasi Hapus User', 
            content=content, 
            size_hint=(0.8, 0.6)
        )
        
        def confirm(instance):
            popup.dismiss()
            self.delete_user(username)
        
        def cancel(instance):
            popup.dismiss()
        
        confirm_btn.bind(on_press=confirm)
        cancel_btn.bind(on_press=cancel)
        popup.open()
    
    def delete_user(self, username):
        if not self.firebase_manager:
            return
        
        def bg():
            success, message = self.firebase_manager.delete_user(username, App.get_running_app().current_user)
            Clock.schedule_once(lambda dt: self.handle_delete_result(success, message), 0)
        
        threading.Thread(target=bg, daemon=True).start()
    
    def handle_delete_result(self, success, message):
        if success:
            self.load_users()
        Popup(
            title='Hasil Hapus', 
            content=Label(text=message), 
            size_hint=(0.8, 0.3)
        ).open()


class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.firebase_manager = None
        self.username = None
        self.build_ui()
    
    def set_firebase(self, firebase_manager):
        self.firebase_manager = firebase_manager
    
    def set_username(self, username):
        self.username = username
    
    def build_ui(self):
        # Main layout - use normal BoxLayout without ScrollView wrapper
        from kivy.core.window import Window
        
        # Main container layout
        layout = BoxLayout(orientation='vertical', padding=10, spacing=5)
        
        # Bind keyboard events for mobile keyboard handling
        from kivy.utils import platform
        if platform == 'android':
            Window.bind(on_keyboard=self.on_keyboard)
            Window.softinput_mode = 'below_target'
        
        # Header - fixed at top
        header = BoxLayout(size_hint_y=None, height=60, spacing=10)
        back_btn = Button(text='Kembali', size_hint_x=0.3, background_color=(0.6,0.6,0.6,1))
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        header.add_widget(Label(text='GRUP CHAT', font_size='18sp', bold=True))
        layout.add_widget(header)
        
        # Online users label
        self.online_users_label = Label(text='Memuat pengguna online...', font_size='12sp', color=(0.2,0.8,0.2,1), size_hint_y=None, height=30)
        layout.add_widget(self.online_users_label)
        
        # Chat area - takes remaining space
        self.chat_scroll = ScrollView()
        self.chat_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=8, padding=[10, 10, 10, 10])
        self.chat_layout.bind(minimum_height=self.chat_layout.setter('height'))
        self.chat_scroll.add_widget(self.chat_layout)
        layout.add_widget(self.chat_scroll)
        
        # Input layout - larger and fixed at bottom
        self.input_container = BoxLayout(size_hint_y=None, height=120, spacing=10, padding=[10, 10, 10, 10])
        input_layout = self.input_container
        self.message_input = TextInput(
            hint_text='Ketik pesan Anda di sini... (Enter untuk baris baru)', 
            multiline=True, 
            font_size='16sp',
            size_hint_y=1
        )
        # Bind focus events for keyboard handling
        self.message_input.bind(focus=self.on_input_focus)
        input_layout.add_widget(self.message_input)
        send_btn = Button(
            text='Kirim', 
            font_size='16sp', 
            bold=True, 
            background_color=(0.2,0.8,0.2,1), 
            size_hint_x=0.25
        )
        send_btn.bind(on_press=self.send_message)
        input_layout.add_widget(send_btn)
        layout.add_widget(input_layout)
        
        # Add main layout directly to screen
        self.add_widget(layout)
    
    def on_input_focus(self, instance, focus):
        # Handle input focus for keyboard visibility
        if focus:
            Clock.schedule_once(lambda dt: self.adjust_for_keyboard(), 0.2)
    
    def on_keyboard(self, window, key, *args):
        # Handle keyboard show/hide for better input visibility
        if hasattr(self, 'message_input') and self.message_input.focus:
            # Adjust scroll when input is focused
            Clock.schedule_once(lambda dt: self.adjust_for_keyboard(), 0.1)
        return False
    
    def adjust_for_keyboard(self):
        # Scroll to bottom when keyboard appears
        if hasattr(self, 'chat_scroll'):
            self.chat_scroll.scroll_y = 0

    def on_enter(self):
        self.load_messages()
        self.load_online_users()
        Clock.schedule_interval(self.auto_refresh, 10)
    
    def on_leave(self):
        Clock.unschedule(self.auto_refresh)
    
    def auto_refresh(self, dt):
        self.load_messages()
        self.load_online_users()
    
    def go_back(self, instance):
        app = App.get_running_app()
        if hasattr(app, 'user_type') and app.user_type == 'admin':
            self.manager.current = 'admin_dashboard'
        else:
            self.manager.current = 'user_dashboard'
    
    def load_online_users(self):
        if not self.firebase_manager:
            return
        def bg():
            online_users = self.firebase_manager.get_online_users()
            Clock.schedule_once(lambda dt: self.update_online_users_ui(online_users), 0)
        threading.Thread(target=bg, daemon=True).start()
    
    def update_online_users_ui(self, online_users):
        if online_users:
            self.online_users_label.text = f"Online: {', '.join(online_users)}"
            apply_emoji_font(self.online_users_label)
        else:
            self.online_users_label.text = "Tidak ada pengguna online"
            apply_emoji_font(self.online_users_label)
    
    def load_messages(self):
        if not self.firebase_manager:
            return
        def bg():
            messages = self.firebase_manager.get_chat_messages(50)
            Clock.schedule_once(lambda dt: self.update_messages_ui(messages), 0)
        threading.Thread(target=bg, daemon=True).start()
    
    def update_messages_ui(self, messages):
        self.chat_layout.clear_widgets()
        if messages:
            for message in messages:
                message_widget = self.create_message_widget(message)
                self.chat_layout.add_widget(message_widget)
            Clock.schedule_once(lambda dt: setattr(self.chat_scroll, 'scroll_y', 0), 0.2)
        else:
            placeholder = Label(text='Belum ada pesan. Jadilah yang pertama menyapa!', size_hint_y=None, height=60, color=(0.6,0.6,0.6,1), font_size='14sp')
            self.chat_layout.add_widget(placeholder)
    
    def create_message_widget(self, message):
        user = message.get('user', 'Unknown')
        timestamp = message.get('timestamp', '')
        msg_type = message.get('type', 'user')
        content = message.get('message', '')
        
        try:
            dt = datetime.fromisoformat(timestamp)
            time_str = dt.strftime('%H:%M')
        except:
            time_str = ''
        
        # More conservative text calculation for mobile compatibility
        content_lines = len(content) // 25 + content.count('\n') + 1
        dynamic_height = max(90, 60 + (content_lines * 18))
        
        main_container = BoxLayout(
            orientation='horizontal', 
            size_hint_y=None, 
            height=dynamic_height + 20, 
            spacing=5, 
            padding=[5, 5, 5, 5]
        )
        
        bubble_container = BoxLayout(
            orientation='vertical', 
            size_hint_y=None, 
            height=dynamic_height, 
            size_hint_x=0.75,  # Reduced from 0.8 for better mobile fit
            spacing=3, 
            padding=[12, 8, 12, 8]  # Reduced padding for mobile
        )
        
        if msg_type == 'system':
            bubble_color = (0.9, 0.7, 0.2, 0.9)
            text_color = (0.2, 0.2, 0.2, 1)
            alignment = 'center'
            user_display = f"Sistem {user}"
            bubble_container.size_hint_x = 0.8
        elif user == self.username:
            bubble_color = (0.2, 0.8, 0.3, 0.9)
            text_color = (1, 1, 1, 1)
            alignment = 'right'
            user_display = "Anda"
        else:
            bubble_color = (0.2, 0.6, 1, 0.9)
            text_color = (1, 1, 1, 1)
            alignment = 'left'
            user_display = user
        
        with bubble_container.canvas.before:
            Color(*bubble_color)
            bubble_rect = RoundedRectangle(
                size=bubble_container.size, 
                pos=bubble_container.pos, 
                radius=[15, 15, 15, 15]
            )
        
        def update_bubble_rect(instance, value):
            bubble_rect.size = instance.size
            bubble_rect.pos = instance.pos
        
        bubble_container.bind(size=update_bubble_rect, pos=update_bubble_rect)
        
        header_text = f"{user_display} • {time_str}"
        header_label = Label(
            text=header_text, 
            font_size='9sp',  # Smaller for mobile
            color=text_color, 
            bold=True, 
            size_hint_y=None, 
            height=18, 
            halign='left', 
            valign='middle',
            text_size=(None, None)
        )
        
        def set_header_text_size(instance, *args):
            if instance.parent and instance.parent.width > 20:
                instance.text_size = (instance.parent.width - 20, None)
        
        header_label.bind(parent=set_header_text_size)
        bubble_container.bind(size=lambda *args: set_header_text_size(header_label))
        bubble_container.add_widget(header_label)
        
        content_label = Label(
            text=content, 
            font_size='11sp',  # Slightly smaller for mobile
            color=text_color, 
            size_hint_y=None, 
            height=dynamic_height - 35, 
            halign='left', 
            valign='top', 
            markup=True,
            text_size=(None, None)
        )
        
        def set_content_text_size(instance, *args):
            if instance.parent and instance.parent.width > 24:
                # More conservative width calculation for mobile
                parent_width = instance.parent.width
                # Account for padding and ensure proper wrapping on mobile
                available_width = max(150, parent_width - 24)  # Reduced from 30 to 24
                instance.text_size = (available_width, None)
                
                # Force texture update and recalculate height
                Clock.schedule_once(lambda dt: self._update_label_height(instance), 0.1)
        
        def _update_label_height(instance):
            instance.texture_update()
            if instance.texture_size[1] > 0:
                new_height = max(35, instance.texture_size[1] + 15)
                instance.height = new_height
                # Update parent container height as well
                if instance.parent:
                    instance.parent.height = new_height + 40
        
        # Bind the function to the class for mobile compatibility
        self._update_label_height = _update_label_height
        
        content_label.bind(parent=set_content_text_size)
        bubble_container.bind(size=lambda *args: set_content_text_size(content_label))
        bubble_container.add_widget(content_label)
        
        if alignment == 'right':
            main_container.add_widget(Label(size_hint_x=0.25))  # Increased spacing for mobile
            main_container.add_widget(bubble_container)
        elif alignment == 'left':
            main_container.add_widget(bubble_container)
            main_container.add_widget(Label(size_hint_x=0.25))  # Increased spacing for mobile
        else:
            main_container.add_widget(Label(size_hint_x=0.125))
            main_container.add_widget(bubble_container)
            main_container.add_widget(Label(size_hint_x=0.125))
        
        return main_container

    def send_message(self, instance):
        message = self.message_input.text.strip()
        if not message or not self.username:
            return
        def bg():
            success = self.firebase_manager.send_chat_message(self.username, message)
            if success:
                Clock.schedule_once(lambda dt: self.message_sent_success(), 0)
        threading.Thread(target=bg, daemon=True).start()
    
    def message_sent_success(self):
        self.message_input.text = ''
        Clock.schedule_once(lambda dt: self.load_messages(), 0.5)

class UserSettingsScreen(Screen):
    """Screen for user settings - change password"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.firebase_manager = None
        self.username = None
        self.build_ui()
    
    def set_firebase(self, firebase_manager):
        self.firebase_manager = firebase_manager
    
    def set_username(self, username):
        self.username = username
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Header
        header = BoxLayout(size_hint_y=0.12)
        back_btn = Button(
            text='Kembali',
            size_hint_x=0.3,
            background_color=(0.6, 0.6, 0.6, 1)
        )
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        
        header.add_widget(Label(
            text='PENGATURAN AKUN',
            font_size='20sp',
            bold=True
        ))
        
        layout.add_widget(header)
        
        # Current password input
        self.current_password_input = TextInput(
            hint_text='Masukkan password saat ini',
            password=True,
            multiline=False,
            font_size='16sp',
            size_hint_y=0.1
        )
        layout.add_widget(self.current_password_input)
        
        # New password input
        self.new_password_input = TextInput(
            hint_text='Masukkan password baru',
            password=True,
            multiline=False,
            font_size='16sp',
            size_hint_y=0.1
        )
        layout.add_widget(self.new_password_input)
        
        # Confirm new password input
        self.confirm_password_input = TextInput(
            hint_text='Konfirmasi password baru',
            password=True,
            multiline=False,
            font_size='16sp',
            size_hint_y=0.1
        )
        layout.add_widget(self.confirm_password_input)
        
        # Update password button
        update_btn = Button(
            text='PERBARUI PASSWORD',
            font_size='18sp',
            bold=True,
            background_color=(0.2, 0.8, 0.2, 1),
            size_hint_y=0.12
        )
        update_btn.bind(on_press=self.update_password)
        layout.add_widget(update_btn)
        
        # Status label
        self.status_label = Label(
            text='',
            font_size='14sp',
            size_hint_y=0.35
        )
        layout.add_widget(self.status_label)
        
        self.add_widget(layout)
    
    def go_back(self, instance):
        app = App.get_running_app()
        if hasattr(app, 'user_type') and app.user_type == 'admin':
            self.manager.current = 'admin_dashboard'
        else:
            self.manager.current = 'user_dashboard'
    
    def update_password(self, instance):
        current_password = self.current_password_input.text.strip()
        new_password = self.new_password_input.text.strip()
        confirm_password = self.confirm_password_input.text.strip()
        
        if not current_password or not new_password or not confirm_password:
            self.status_label.text = '✗ Semua kolom harus diisi'
            self.status_label.color = (1, 0.2, 0.2, 1)
            return
        
        if new_password != confirm_password:
            self.status_label.text = '✗ Password baru tidak cocok'
            self.status_label.color = (1, 0.2, 0.2, 1)
            return
        
        self.status_label.text = 'Memperbarui password...'
        self.status_label.color = (0.2, 0.6, 1, 1)
        
        def update_in_background():
            success, message = self.firebase_manager.update_user_password(self.username, new_password)
            Clock.schedule_once(lambda dt: self.handle_update_result(success, message), 0)
        
        threading.Thread(target=update_in_background, daemon=True).start()
    
    def handle_update_result(self, success, message):
        self.status_label.text = f'{"✓" if success else "✗"} {message}'
        self.status_label.color = (0.2, 0.8, 0.2, 1) if success else (1, 0.2, 0.2, 1)
        
        if success:
            self.current_password_input.text = ''
            self.new_password_input.text = ''
            self.confirm_password_input.text = ''

class UserInfoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.firebase_manager = None
        self.username = None
        self.build_ui()
    
    def set_firebase(self, firebase_manager):
        self.firebase_manager = firebase_manager
    
    def set_username(self, username):
        self.username = username
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        header = BoxLayout(size_hint_y=0.12)
        back_btn = Button(
            text='Kembali',
            size_hint_x=0.3,
            background_color=(0.6, 0.6, 0.6, 1)
        )
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        
        header.add_widget(Label(
            text='INFO PRIBADI',
            font_size='20sp',
            bold=True
        ))
        
        layout.add_widget(header)
        
        self.wa_input = TextInput(
            hint_text='Nomor WhatsApp (contoh: 081234567890)',
            multiline=False,
            font_size='16sp',
            size_hint_y=0.1
        )
        layout.add_widget(self.wa_input)
        
        self.rekening_input = TextInput(
            hint_text='Nomor Rekening Bank (contoh: BCA 1234567890)',
            multiline=False,
            font_size='16sp',
            size_hint_y=0.1
        )
        layout.add_widget(self.rekening_input)
        
        self.tgl_lahir_input = TextInput(
            hint_text='Tanggal Lahir (contoh: 15/08/1990)',
            multiline=False,
            font_size='16sp',
            size_hint_y=0.1
        )
        layout.add_widget(self.tgl_lahir_input)
        
        self.tempat_tinggal_input = TextInput(
            hint_text='Tempat Tinggal (contoh: Jakarta Selatan)',
            multiline=False,
            font_size='16sp',
            size_hint_y=0.1
        )
        layout.add_widget(self.tempat_tinggal_input)
        
        update_btn = Button(
            text='PERBARUI INFO',
            font_size='18sp',
            bold=True,
            background_color=(0.2, 0.8, 0.2, 1),
            size_hint_y=0.12
        )
        update_btn.bind(on_press=self.update_info)
        layout.add_widget(update_btn)
        
        self.status_label = Label(
            text='',
            font_size='14sp',
            size_hint_y=0.35
        )
        layout.add_widget(self.status_label)
        
        self.add_widget(layout)
    
    def on_enter(self):
        self.load_current_info()
    
    def load_current_info(self):
        if not self.firebase_manager or not self.username:
            return
        
        def bg():
            user_data = self.firebase_manager.get_data(f"users/{self.username}")
            Clock.schedule_once(lambda dt: self.update_info_ui(user_data), 0)
        
        threading.Thread(target=bg, daemon=True).start()
    
    def update_info_ui(self, user_data):
        if user_data:
            self.wa_input.text = user_data.get('wa', '')
            self.rekening_input.text = user_data.get('rekening', '')
            self.tgl_lahir_input.text = user_data.get('tgl_lahir', '')
            self.tempat_tinggal_input.text = user_data.get('tempat_tinggal', '')
    
    def go_back(self, instance):
        app = App.get_running_app()
        if hasattr(app, 'user_type') and app.user_type == 'admin':
            self.manager.current = 'admin_dashboard'
        else:
            self.manager.current = 'user_dashboard'
    
    def update_info(self, instance):
        wa = self.wa_input.text.strip()
        rekening = self.rekening_input.text.strip()
        tgl_lahir = self.tgl_lahir_input.text.strip()
        tempat_tinggal = self.tempat_tinggal_input.text.strip()
        
        if not wa or not rekening or not tgl_lahir or not tempat_tinggal:
            self.status_label.text = '✗ Semua kolom harus diisi'
            self.status_label.color = (1, 0.2, 0.2, 1)
            return
        
        self.status_label.text = 'Memperbarui info...'
        self.status_label.color = (0.2, 0.6, 1, 1)
        
        def bg():
            success, message = self.firebase_manager.update_user_info(self.username, wa, rekening, tgl_lahir, tempat_tinggal)
            Clock.schedule_once(lambda dt: self.handle_update_result(success, message), 0)
        
        threading.Thread(target=bg, daemon=True).start()
    
    def handle_update_result(self, success, message):
        self.status_label.text = f'{"✓" if success else "✗"} {message}'
        self.status_label.color = (0.2, 0.8, 0.2, 1) if success else (1, 0.2, 0.2, 1)

class ActivityLogScreen(Screen):
    """Screen for viewing activity logs - Indonesian"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.firebase_manager = None
        self.build_ui()
    
    def set_firebase(self, firebase_manager):
        self.firebase_manager = firebase_manager
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Header
        header = BoxLayout(size_hint_y=0.12)
        back_btn = Button(
            text='Kembali ',
            size_hint_x=0.3,
            background_color=(0.6, 0.6, 0.6, 1)
        )
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        
        header.add_widget(Label(
            text='LOG AKTIVITAS',
            font_size='20sp',
            bold=True
        ))
        
        layout.add_widget(header)
        
        # Activity logs display
        self.logs_scroll = ScrollView(size_hint_y=0.8)
        self.logs_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.logs_layout.bind(minimum_height=self.logs_layout.setter('height'))
        self.logs_scroll.add_widget(self.logs_layout)
        layout.add_widget(self.logs_scroll)
        
        # Load logs button
        load_btn = Button(
            text='Muat Log',
            font_size='16sp',
            background_color=(0.2, 0.6, 1, 1),
            size_hint_y=0.1,
            # font_name='EmojiFont'
        )
        load_btn.bind(on_press=self.load_logs)
        layout.add_widget(load_btn)
        
        self.add_widget(layout)
    
    def go_back(self, instance):
        app = App.get_running_app()
        if hasattr(app, 'user_type') and app.user_type == 'admin':
            self.manager.current = 'admin_dashboard'
        else:
            self.manager.current = 'user_dashboard'
    
    def load_logs(self, instance):
        if not self.firebase_manager:
            return
        
        def load_in_background():
            logs = self.firebase_manager.get_activity_logs(50)
            Clock.schedule_once(lambda dt: self.update_logs_ui(logs), 0)
        
        threading.Thread(target=load_in_background, daemon=True).start()
    
    def update_logs_ui(self, logs):
        self.logs_layout.clear_widgets()
        
        if logs:
            for log in logs:
                log_widget = self.create_log_widget(log)
                self.logs_layout.add_widget(log_widget)
        else:
            self.logs_layout.add_widget(Label(
                text='Tidak ada log aktivitas ditemukan.',
                size_hint_y=None,
                height=50
            ))
    
    def create_log_widget(self, log):
        # Log container
        log_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=60,
            padding=10,
            spacing=5
        )
        
        # Log details
        user_label = Label(
            text=f"{log['user']} - {log['action']}",
            font_size='14sp',
            bold=True,
            color=(0.2, 0.6, 1, 1)
        )
        
        timestamp = log.get('timestamp', '')
        log_time = datetime.fromisoformat(timestamp).strftime('%d/%m/%Y %H:%M') if timestamp else 'Waktu tidak diketahui'
        
        time_label = Label(
            text=f"Waktu: {log_time}",
            font_size='12sp',
            color=(0.6, 0.6, 0.6, 1)
        )
        
        log_container.add_widget(user_label)
        log_container.add_widget(time_label)
        
        return log_container

class SettingsScreen(Screen):
    """Screen for admin settings - Indonesian with reset data feature"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.firebase_manager = None
        self.build_ui()
    
    def set_firebase(self, firebase_manager):
        self.firebase_manager = firebase_manager
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Header
        header = BoxLayout(size_hint_y=0.12)
        back_btn = Button(
            text='Kembali',
            size_hint_x=0.3,
            background_color=(0.6, 0.6, 0.6, 1)
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'admin_dashboard'))
        header.add_widget(back_btn)
        
        header.add_widget(Label(
            text='PENGATURAN ADMIN',
            font_size='20sp',
            bold=True
        ))
        
        layout.add_widget(header)
        
        # Current settings display
        self.current_settings_label = Label(
            text='Memuat pengaturan saat ini...',
            font_size='14sp',
            color=(0.2, 0.8, 0.2, 1),
            size_hint_y=0.1
        )
        layout.add_widget(self.current_settings_label)
        
        # Price per token setting
        price_layout = BoxLayout(size_hint_y=0.12, spacing=10)
        price_layout.add_widget(Label(
            text='Harga Token (Rp):',
            font_size='16sp',
            size_hint_x=0.4
        ))
        
        self.price_input = TextInput(
            hint_text='Masukkan harga baru per token',
            multiline=False,
            font_size='16sp',
            input_filter='int'
        )
        price_layout.add_widget(self.price_input)
        
        layout.add_widget(price_layout)
        
        # Admin password setting
        password_layout = BoxLayout(size_hint_y=0.12, spacing=10)
        password_layout.add_widget(Label(
            text='Password Admin:',
            font_size='16sp',
            size_hint_x=0.4
        ))
        
        self.password_input = TextInput(
            hint_text='Masukkan password admin baru',
            multiline=False,
            password=True,
            font_size='16sp'
        )
        password_layout.add_widget(self.password_input)
        
        layout.add_widget(password_layout)
        
        # Update buttons
        button_layout = BoxLayout(size_hint_y=0.12, spacing=10)
        
        update_price_btn = Button(
            text='Perbarui Harga',
            font_size='16sp',
            bold=True,
            background_color=(0.2, 0.8, 0.2, 1)
        )
        update_price_btn.bind(on_press=self.update_price)
        button_layout.add_widget(update_price_btn)
        
        update_password_btn = Button(
            text='Perbarui Password',
            font_size='16sp',
            bold=True,
            background_color=(1, 0.6, 0.2, 1)
        )
        update_password_btn.bind(on_press=self.update_password)
        button_layout.add_widget(update_password_btn)
        
        layout.add_widget(button_layout)
        
        # Reset data button
        reset_btn = Button(
            text='RESET DATA PENGHASILAN USER',
            font_size='16sp',
            bold=True,
            background_color=(1, 0.2, 0.2, 1),
            # font_name='EmojiFont',
            size_hint_y=0.12
        )
        reset_btn.bind(on_press=self.reset_user_data)
        layout.add_widget(reset_btn)
        
        # Status label
        self.status_label = Label(
            text='',
            font_size='14sp',
            size_hint_y=0.15
        )
        layout.add_widget(self.status_label)
        
        # Warning text
        warning_text = """⚠️ PERINGATAN:
• Mengubah harga token hanya berlaku untuk token baru
• Mengubah password admin memerlukan restart
• Reset data akan menghapus penghasilan semua user!
• Pastikan ingat password baru!"""
        
        warning_label = Label(
            text=warning_text,
            font_size='12sp',
            color=(1, 0.6, 0.2, 1),
            size_hint_y=0.27
        )
        layout.add_widget(warning_label)
        
        self.add_widget(layout)
    
    def on_enter(self):
        self.load_current_settings()
    
    def load_current_settings(self):
        if not self.firebase_manager:
            return
        
        def load_in_background():
            settings = self.firebase_manager.get_data("settings")
            Clock.schedule_once(lambda dt: self.update_current_settings_ui(settings), 0)
        
        threading.Thread(target=load_in_background, daemon=True).start()
    
    def update_current_settings_ui(self, settings):
        if settings:
            price = settings.get('price_per_token', 1500)
            self.current_settings_label.text = f'Harga Token Saat Ini: Rp {price:,}'
            apply_emoji_font(self.current_settings_label)
            self.price_input.hint_text = f'Saat ini: Rp {price:,}'
        else:
            self.current_settings_label.text = 'Tidak dapat memuat pengaturan saat ini'
    
    def update_price(self, instance):
        new_price = self.price_input.text.strip()
        
        if not new_price or not new_price.isdigit():
            self.status_label.text = 'Silakan masukkan harga yang valid'
            self.status_label.color = (1, 0.2, 0.2, 1)
            return
        
        price = int(new_price)
        if price < 100:
            self.status_label.text = 'Harga minimal Rp 100'
            self.status_label.color = (1, 0.2, 0.2, 1)
            return
        
        self.status_label.text = 'Memperbarui harga...'
        self.status_label.color = (0.2, 0.6, 1, 1)
        
        def update_in_background():
            success, message = self.firebase_manager.update_settings({'price_per_token': price})
            Clock.schedule_once(lambda dt: self.handle_update_result(success, message), 0)
        
        threading.Thread(target=update_in_background, daemon=True).start()
    
    def update_password(self, instance):
        new_password = self.password_input.text.strip()
        
        if not new_password:
            self.status_label.text = '✗ Silakan masukkan password baru'
            self.status_label.color = (1, 0.2, 0.2, 1)
            return
        
        if len(new_password) < 6:
            self.status_label.text = '✗ Password minimal 6 karakter'
            self.status_label.color = (1, 0.2, 0.2, 1)
            return
        
        self.status_label.text = 'Memperbarui password...'
        self.status_label.color = (0.2, 0.6, 1, 1)
        
        def update_in_background():
            success, message = self.firebase_manager.update_settings({'admin_password': new_password})
            Clock.schedule_once(lambda dt: self.handle_update_result(success, message), 0)
        
        threading.Thread(target=update_in_background, daemon=True).start()
    
    def reset_user_data(self, instance):
        """Reset all user earnings and token counts"""
        # Show confirmation popup
        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(Label(
            text='PERINGATAN!\n\nIni akan menghapus semua penghasilan dan jumlah token user.\nToken yang tersimpan di database tidak akan dihapus.\n\nApakah Anda yakin?',
            font_size='14sp'
        ))
        
        button_layout = BoxLayout(spacing=10, size_hint_y=0.3)
        
        confirm_btn = Button(
            text='YA, RESET',
            background_color=(1, 0.2, 0.2, 1)
        )
        cancel_btn = Button(
            text='BATAL',
            background_color=(0.6, 0.6, 0.6, 1)
        )
        
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(confirm_btn)
        content.add_widget(button_layout)
        
        popup = Popup(
            title='Konfirmasi Reset Data',
            content=content,
            size_hint=(0.8, 0.6)
        )
        
        def confirm_reset(instance):
            popup.dismiss()
            self.perform_reset()
        
        def cancel_reset(instance):
            popup.dismiss()
        
        confirm_btn.bind(on_press=confirm_reset)
        cancel_btn.bind(on_press=cancel_reset)
        
        popup.open()
    
    def perform_reset(self):
        """Actually perform the reset"""
        self.status_label.text = 'Mereset data user...'
        self.status_label.color = (0.2, 0.6, 1, 1)
        
        def reset_in_background():
            success, message = self.firebase_manager.reset_user_data(App.get_running_app().current_user)
            Clock.schedule_once(lambda dt: self.handle_update_result(success, message), 0)
        
        threading.Thread(target=reset_in_background, daemon=True).start()
    
    def handle_update_result(self, success, message):
        self.status_label.text = f'{"✓" if success else "✗"} {message}'
        self.status_label.color = (0.2, 0.8, 0.2, 1) if success else (1, 0.2, 0.2, 1)
        
        if success:
            self.price_input.text = ''
            self.password_input.text = ''
            self.load_current_settings()

class BanTokenScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.firebase_manager = None
        self.build_ui()
    
    def set_firebase(self, firebase_manager):
        self.firebase_manager = firebase_manager
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        header = BoxLayout(size_hint_y=0.12)
        back_btn = Button(
            text='Kembali', 
            size_hint_x=0.3, 
            background_color=(0.6, 0.6, 0.6, 1)
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'admin_dashboard'))
        header.add_widget(back_btn)
        
        header.add_widget(Label(
            text='BAN TOKEN RUSAK', 
            font_size='20sp', 
            bold=True
        ))
        
        layout.add_widget(header)
        
        instructions = Label(
            text='Masukkan token rusak untuk dihapus (satu per baris).\nPenghasilan pemilik akan dikurangi otomatis.\nToken bancet akan ditambahkan ke statistik user.',
            font_size='14sp',
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=0.15
        )
        layout.add_widget(instructions)
        
        self.tokens_input = TextInput(
            hint_text='Tempel token rusak di sini (satu per baris)',
            multiline=True,
            font_size='14sp',
            size_hint_y=0.3
        )
        layout.add_widget(self.tokens_input)
        
        ban_btn = Button(
            text='BAN TOKEN',
            font_size='18sp',
            bold=True,
            background_color=(1, 0.2, 0.2, 1),
            size_hint_y=0.12
        )
        ban_btn.bind(on_press=self.ban_tokens)
        layout.add_widget(ban_btn)
        
        self.status_label = Label(
            text='',
            font_size='14sp',
            size_hint_y=0.31
        )
        layout.add_widget(self.status_label)
        
        self.add_widget(layout)
    
    def ban_tokens(self, instance):
        tokens_text = self.tokens_input.text.strip()
        
        if not tokens_text:
            self.status_label.text = '✗ Silakan masukkan token yang akan diban'
            self.status_label.color = (1, 0.2, 0.2, 1)
            return
        
        self.status_label.text = 'Memban token...'
        self.status_label.color = (0.2, 0.6, 1, 1)
        
        def bg():
            success, message, details = self.firebase_manager.ban_tokens(tokens_text, App.get_running_app().current_user)
            Clock.schedule_once(lambda dt: self.handle_ban_result(success, message, details), 0)
        
        threading.Thread(target=bg, daemon=True).start()
    
    def handle_ban_result(self, success, message, details):
        if details:
            result_text = (
                f"{message}\n\n"
                f"Berhasil diban: {details.get('success', 0)}\n"
                f"Tidak ditemukan: {details.get('not_found', 0)}\n"
                f"User terdampak: {details.get('affected_users', 0)}\n"
                f"Total kerugian: Rp {details.get('total_loss', 0):,}\n\n"
                f"Notifikasi telah dikirim ke chat untuk memberitahu user yang terdampak"
            )
            self.status_label.text = result_text
        else:
            self.status_label.text = f'{"✓" if success else "✗"} {message}'
        
        self.status_label.color = (0.2, 0.8, 0.2, 1) if success else (1, 0.2, 0.2, 1)
        
        if success:
            self.tokens_input.text = ''


# Category Selection Screen
class CategorySelectionScreen(Screen):
    """Screen to select between Online Token Manager or Offline Kasir"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        # Main layout with proper background
        main_layout = BoxLayout(orientation='vertical')
        
        # Set background color
        from kivy.graphics import Color, Rectangle
        with main_layout.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Light gray background
            self.bg_rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
            main_layout.bind(size=self._update_bg, pos=self._update_bg)
        
        # Content layout with responsive padding
        layout = BoxLayout(orientation='vertical', padding=[10, 20, 10, 20], spacing=20)
        
        # App Title with responsive sizing
        title = Label(
            text='KATEGORI',
            font_size='24sp',
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height='60dp',
            text_size=(None, None),
            halign='center',
            valign='middle'
        )
        layout.add_widget(title)
        
        # Simple buttons container with responsive spacing
        buttons_container = BoxLayout(orientation='vertical', spacing='15dp')
        
        # Token Manager Button with responsive sizing
        token_btn = Button(
            text='🪙  TOKEN MANAGER\nManajemen token online',
            font_size='14sp',
            bold=True,
            background_color=(0.2, 0.6, 0.8, 1),
            size_hint_y=None,
            height='70dp',
            halign='center',
            valign='middle'
        )
        token_btn.bind(texture_size=token_btn.setter('text_size'))
        token_btn.bind(on_press=self.go_to_online_mode)
        buttons_container.add_widget(token_btn)
        
        # Kasir Button with responsive sizing
        kasir_btn = Button(
            text='🏪  KASIR\nSistem kasir offline',
            font_size='14sp',
            bold=True,
            background_color=(0.8, 0.4, 0.2, 1),
            size_hint_y=None,
            height='70dp',
            halign='center',
            valign='middle'
        )
        kasir_btn.bind(texture_size=kasir_btn.setter('text_size'))
        kasir_btn.bind(on_press=self.go_to_offline_mode)
        buttons_container.add_widget(kasir_btn)
        
        layout.add_widget(buttons_container)
        
        # Footer with responsive sizing
        footer = Label(
            text='Pilih sesuai kebutuhan bisnis Anda',
            font_size='10sp',
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=None,
            height='30dp',
            text_size=(None, None),
            halign='center'
        )
        layout.add_widget(footer)
        
        main_layout.add_widget(layout)
        self.add_widget(main_layout)
    
    
    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos
    
    def go_to_online_mode(self, instance):
        app = App.get_running_app()
        app.app_mode = 'online'
        sound_manager.success_feedback()
        self.manager.current = 'login'
    
    def go_to_offline_mode(self, instance):
        app = App.get_running_app()
        app.app_mode = 'offline'
        sound_manager.success_feedback()
        self.manager.current = 'kasir_main'

class MyApp(App):
    def build(self):
        self.current_user = None
        self.user_type = None
        self.app_mode = None  # 'online' or 'offline'
        
        # Kasir variables (for offline mode)
        self.username = "Admin"
        self.shop_name = "Toko Ayam Potong"
        self.products = []
        self.cart = []
        self.daily_expenses = []
        self.transaction_counter = 1
        self.last_payment = 0
        self.last_change = 0
        
        # Bind hardware back button for Android
        from kivy.core.window import Window
        Window.bind(on_keyboard=self.on_keyboard)
        
        sm = ScreenManager()
        self.screen_manager = sm  # Store reference for back button handling
        
        # Add category selection as first screen
        sm.add_widget(CategorySelectionScreen(name='category'))
        
        # Add existing online screens
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(AdminDashboardScreen(name='admin_dashboard'))
        sm.add_widget(UserDashboardScreen(name='user_dashboard'))
        sm.add_widget(AddUserScreen(name='add_user'))
        sm.add_widget(AddTokenScreen(name='add_token'))
        sm.add_widget(TakeTokensScreen(name='take_tokens'))
        sm.add_widget(CheckTokenScreen(name='check_token'))
        sm.add_widget(BanTokenScreen(name='ban_token'))
        sm.add_widget(UsersScreen(name='users'))
        sm.add_widget(ChatScreen(name='chat'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(UserSettingsScreen(name='user_settings'))
        sm.add_widget(UserInfoScreen(name='user_info'))
        sm.add_widget(ActivityLogScreen(name='activity'))
        
        # Add kasir screens (offline mode)
        sm.add_widget(KasirMainScreen(name='kasir_main'))
        sm.add_widget(KasirExpensesScreen(name='kasir_expenses'))
        sm.add_widget(KasirReportsScreen(name='kasir_reports'))
        sm.add_widget(KasirReceiptScreen(name='kasir_receipt'))
        
        # Initialize kasir data
        self.init_kasir_data()
        
        # Set initial screen to category selection
        sm.current = 'category'
        
        return sm
    
    def init_kasir_data(self):
        """Initialize kasir data and load from files"""
        try:
            # Initialize kasir variables
            self.cart = []
            self.daily_sales = 0
            self.expenses = []
            self.username = 'Admin'
            self.shop_name = 'Toko Ayam Potong'
            
            # Load user config
            if os.path.exists('user_config.json'):
                with open('user_config.json', 'r', encoding='utf-8') as f:
                    user_data = json.load(f)
                    self.username = user_data.get('username', 'Admin')
                    self.shop_name = user_data.get('shop_name', 'Toko Ayam Potong')
            
            # Load products
            self.load_kasir_products()
            
            # Load transaction counter
            self.transaction_counter = self.load_transaction_counter()
            
            # Load daily expenses
            self.load_kasir_expenses()
            
            # Load daily sales
            self.load_daily_sales()
            
        except Exception as e:
            print(f"Error initializing kasir data: {e}")
    
    def load_kasir_products(self):
        """Load products from JSON file or create defaults"""
        try:
            if os.path.exists('products.json'):
                with open('products.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.products = []
                    for item in data:
                        product = KasirProduct(
                            item['id'], 
                            item['name'], 
                            item['price_per_kg'], 
                            item['stock_kg']
                        )
                        self.products.append(product)
            else:
                # Create default products
                self.products = [
                    KasirProduct(1, "Ayam Utuh", 35000, 15.0),
                    KasirProduct(2, "Dada Ayam", 45000, 10.0),
                    KasirProduct(3, "Sayap Ayam", 30000, 8.0),
                    KasirProduct(4, "Ceker Ayam", 25000, 12.0),
                    KasirProduct(5, "Paha Ayam", 40000, 20.0),
                    KasirProduct(6, "Leher Ayam", 20000, 5.0),
                ]
                self.save_kasir_products()
        except Exception as e:
            print(f"Error loading products: {e}")
            self.products = []
    
    def save_kasir_products(self):
        """Save products to JSON file"""
        try:
            products_data = []
            for product in self.products:
                # Handle both dictionary and object products
                if hasattr(product, 'id'):
                    # Product is an object
                    products_data.append({
                        'id': product.id,
                        'name': product.name,
                        'price_per_kg': product.price_per_kg,
                        'stock_kg': product.stock_kg
                    })
                elif isinstance(product, dict):
                    # Product is already a dictionary
                    products_data.append({
                        'id': product.get('id', len(products_data) + 1),
                        'name': product.get('name', 'Produk Baru'),
                        'price_per_kg': product.get('price_per_kg', 0),
                        'stock_kg': product.get('stock_kg', 0)
                    })
            
            with open('products.json', 'w', encoding='utf-8') as f:
                json.dump(products_data, f, indent=4, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving products: {e}")
            show_error_popup(f'Gagal menyimpan produk: {str(e)}')
            # Re-raise the exception after showing error
            raise
    
    def load_transaction_counter(self):
        """Load transaction counter"""
        try:
            if os.path.exists('counter.json'):
                with open('counter.json', 'r') as f:
                    data = json.load(f)
                    return data.get('counter', 1)
        except:
            pass
        return 1
    
    def save_transaction_counter(self):
        """Save transaction counter"""
        try:
            with open('counter.json', 'w') as f:
                json.dump({'counter': self.transaction_counter}, f)
        except Exception as e:
            print(f"Error saving counter: {e}")
    
    def load_kasir_expenses(self):
        """Load kasir expenses"""
        try:
            if os.path.exists('kasir_expenses.json'):
                with open('kasir_expenses.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.expenses = []
                    for item in data:
                        expense = KasirExpense(
                            item['id'],
                            item['name'],
                            item['amount'],
                            item['date_time']
                        )
                        self.expenses.append(expense)
            else:
                self.expenses = []
        except Exception as e:
            print(f"Error loading expenses: {e}")
            self.expenses = []
    
    def save_kasir_expenses(self):
        """Save kasir expenses"""
        try:
            data = []
            for expense in self.expenses:
                data.append({
                    'id': expense.id,
                    'name': expense.name,
                    'amount': expense.amount,
                    'date_time': expense.date_time
                })
            with open('kasir_expenses.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving expenses: {e}")
    
    def load_daily_sales(self):
        """Load daily sales total"""
        try:
            if os.path.exists('daily_sales.json'):
                with open('daily_sales.json', 'r') as f:
                    data = json.load(f)
                    self.daily_sales = data.get('daily_sales', 0)
            else:
                self.daily_sales = 0
        except Exception as e:
            print(f"Error loading daily sales: {e}")
            self.daily_sales = 0
    
    def save_daily_sales(self):
        """Save daily sales total"""
        try:
            with open('daily_sales.json', 'w') as f:
                json.dump({'daily_sales': self.daily_sales}, f)
        except Exception as e:
            print(f"Error saving daily sales: {e}")
    
    def save_kasir_counter(self):
        """Save kasir transaction counter"""
        try:
            with open('kasir_counter.json', 'w') as f:
                json.dump({'counter': self.transaction_counter}, f)
        except Exception as e:
            print(f"Error saving kasir counter: {e}")
    
    def get_cart_total(self):
        """Calculate total cart amount"""
        return sum(item.get_total() for item in self.cart)
    
    def format_currency(self, amount):
        """Format currency for display"""
        try:
            return f"Rp {amount:,.0f}".replace(',', '.')
        except:
            return "Rp 0"
    
    def show_popup(self, title, message):
        """Show simple popup message"""
        popup = Popup(
            title=title,
            content=Label(text=message, text_size=(None, None), halign='center'),
            size_hint=(0.8, 0.4),
            auto_dismiss=True
        )
        popup.open()
    
    def on_keyboard(self, window, key, *args):
        """Handle hardware back button on Android"""
        if key == 27:  # Back button key code
            return self.handle_back_button()
        return False
    
    def handle_back_button(self):
        """Handle back button navigation logic"""
        current_screen = self.screen_manager.current
        
        # Define navigation hierarchy
        navigation_map = {
            'add_user': 'admin_dashboard',
            'add_token': 'admin_dashboard', 
            'ban_token': 'admin_dashboard',
            'users': 'admin_dashboard',
            'settings': 'admin_dashboard',
            'activity': 'admin_dashboard',
            'take_tokens': 'user_dashboard',
            'check_token': 'user_dashboard',
            'chat': 'user_dashboard' if self.user_type == 'user' else 'admin_dashboard',
            'user_settings': 'user_dashboard',
            'user_info': 'user_dashboard',
            'admin_dashboard': 'login',
            'user_dashboard': 'login',
            'kasir_main': 'category',
            'kasir_expenses': 'kasir_main',
            'kasir_reports': 'kasir_main',
            'kasir_receipt': 'kasir_main',
            'login': 'category'
        }
        
        # Navigate back based on current screen
        if current_screen in navigation_map:
            self.screen_manager.current = navigation_map[current_screen]
            return True
        elif current_screen == 'login':
            # Exit app if on login screen
            self.stop()
            return True
        
        return False

    def on_stop(self):
        """Called when app is closing"""
        try:
            # Logout current user if logged in
            if hasattr(self, 'current_user') and self.current_user:
                # Try to get firebase manager from login screen
                login_screen = None
                for screen in self.root.screens:
                    if screen.name == 'login':
                        login_screen = screen
                        break
                
                if login_screen and hasattr(login_screen, 'firebase_manager') and login_screen.firebase_manager:
                    login_screen.firebase_manager.logout(self.current_user)
                    print(f"Logged out {self.current_user} on app close")
        except Exception as e:
            print(f"Error during app close: {e}")

    def configure_fonts(self):
        """Konfigurasi font untuk mendukung emoji"""
        try:
            # Tambahkan path untuk font lokal
            if hasattr(sys, '_MEIPASS'):
                # Jika di-build dengan PyInstaller
                resource_add_path(os.path.join(sys._MEIPASS, 'fonts'))
            else:
                # Mode development
                resource_add_path('fonts')
            
            # Daftarkan font fallback untuk emoji
            # LabelBase.register(
            #     name='EmojiFont',
            #     fn_regular='NotoColorEmoji.ttf',
            #     fn_bold='NotoColorEmoji.ttf'
            # )
            
            # Set default font dengan emoji support
            from kivy.core.text import LabelBase
            LabelBase.register(
                name='Default',
                fn_regular='Roboto-Regular.ttf',
                fn_bold='Roboto-Bold.ttf'
            )
            
        except Exception as e:
            print(f"Warning: Font configuration failed: {e}")
            # Fallback ke font sistem
            pass
    
 
    def on_stop(self):
        """Called when app stops"""
        try:
            # Cleanup
            pass
        except Exception as e:
            print(f"Error during app close: {e}")
            return False

# Kasir Main Screen
class KasirMainScreen(Screen):
    """Main kasir screen with product management and cart"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = None
        self.build_ui()
    
    def on_enter(self):
        if not self.app_ref:
            self.app_ref = App.get_running_app()
            self.update_products_display()
    
    def update_cart_display(self):
        """Update cart display"""
        if not self.app_ref:
            return
        
        self.cart_layout.clear_widgets()
        
        if hasattr(self.app_ref, 'cart') and self.app_ref.cart:
            for cart_item in self.app_ref.cart:
                cart_widget = self.create_cart_widget(cart_item)
                self.cart_layout.add_widget(cart_widget)
        
        # Update total
        total = self.app_ref.get_cart_total() if hasattr(self.app_ref, 'get_cart_total') else 0
        self.total_label.text = f'Total: {self.app_ref.format_currency(total) if hasattr(self.app_ref, "format_currency") else f"Rp {total:,.0f}"}'
        self.checkout_btn.disabled = not (hasattr(self.app_ref, 'cart') and self.app_ref.cart)
    
    def update_products_display(self):
        """Update products display"""
        if not self.app_ref or not hasattr(self.app_ref, 'products'):
            return
        
        self.products_layout.clear_widgets()
        for product in self.app_ref.products:
            product_widget = self.create_product_widget(product)
            self.products_layout.add_widget(product_widget)
            
    def show_weight_input(self, product):
        """Show popup to input product weight"""
        if not self.app_ref:
            return
            
        # Create popup content
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        # Title
        title_label = Label(
            text=f'Masukkan Berat {product.name}',
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=40
        )
        
        # Weight input
        weight_layout = BoxLayout(size_hint_y=None, height=60, spacing=10)
        weight_label = Label(text='Berat (kg):', size_hint_x=0.4)
        self.weight_input = TextInput(
            text='1',
            input_filter='float',
            multiline=False,
            size_hint_x=0.6,
            font_size='16sp'
        )
        weight_layout.add_widget(weight_label)
        weight_layout.add_widget(self.weight_input)
        
        # Price display
        price_layout = BoxLayout(size_hint_y=None, height=40)
        price_label = Label(text='Harga:', size_hint_x=0.4)
        self.price_display = Label(
            text='Rp 0',
            size_hint_x=0.6,
            font_size='16sp',
            halign='right',
            color=(0.2, 0.6, 0.2, 1)
        )
        price_layout.add_widget(price_label)
        price_layout.add_widget(self.price_display)
        
        # Buttons
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        cancel_btn = Button(text='BATAL')
        add_btn = Button(
            text='TAMBAH',
            background_color=(0.2, 0.8, 0.2, 1),
            disabled=True
        )
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(add_btn)
        
        # Add all widgets to content
        content.add_widget(title_label)
        content.add_widget(weight_layout)
        content.add_widget(price_layout)
        content.add_widget(btn_layout)
        
        # Create and open popup
        popup = Popup(
            title='Input Berat Produk',
            content=content,
            size_hint=(0.9, 0.5)
        )
        
        def update_price(instance, value):
            try:
                weight = float(self.weight_input.text) if self.weight_input.text else 0
                if weight > 0:
                    total = weight * product.price_per_kg
                    self.price_display.text = self.app_ref.format_currency(total)
                    add_btn.disabled = False
                else:
                    self.price_display.text = 'Rp 0'
                    add_btn.disabled = True
            except ValueError:
                self.price_display.text = 'Rp 0'
                add_btn.disabled = True
        
        # Initialize price display
        update_price(None, '1')
        
        # Bind events
        self.weight_input.bind(text=update_price)
        cancel_btn.bind(on_press=popup.dismiss)
        add_btn.bind(
            on_press=lambda x: self.add_to_cart_with_weight(product, self.weight_input.text, popup)
        )
        
        popup.open()
        
    def add_to_cart_with_weight(self, product, weight_text, popup=None):
        """Add product to cart with specified weight"""
        if not self.app_ref:
            return
            
        try:
            # Validate weight input
            if not weight_text or not weight_text.strip():
                show_error_popup('Masukkan berat produk', title='Input Tidak Valid')
                sound_manager.error_feedback()
                return
                
            weight = float(weight_text)
            if weight <= 0:
                show_error_popup('Berat harus lebih dari 0', title='Input Tidak Valid')
                sound_manager.error_feedback()
                return
                
            # Add to cart
            cart_item = KasirCartItem(product, weight)
            self.app_ref.cart.append(cart_item)
            self.update_cart_display()
            sound_manager.success_feedback()
            
        except ValueError:
            show_error_popup('Masukkan berat yang valid (contoh: 0.5, 1, 1.5)', title='Input Tidak Valid')
            sound_manager.error_feedback()
            return
            
        if popup:
            popup.dismiss()
    
    def show_payment(self, instance):
        """Show payment popup"""
        if not self.app_ref or not self.app_ref.cart:
            return
            
        total = sum(item.get_total() for item in self.app_ref.cart)
        
        # Create popup content
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        # Total amount
        total_layout = BoxLayout(size_hint_y=None, height=40)
        total_label = Label(
            text='Total Pembayaran:',
            size_hint_x=0.6,
            font_size='16sp',
            bold=True
        )
        total_amount = Label(
            text=self.app_ref.format_currency(total),
            size_hint_x=0.4,
            font_size='18sp',
            bold=True,
            color=(0.2, 0.6, 0.2, 1),
            halign='right'
        )
        total_layout.add_widget(total_label)
        total_layout.add_widget(total_amount)
        
        # Payment input
        payment_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        payment_label = Label(text='Jumlah Bayar:', size_hint_x=0.4)
        payment_input = TextInput(
            input_filter='float',
            multiline=False,
            size_hint_x=0.6,
            font_size='16sp',
            text=str(int(total))
        )
        payment_layout.add_widget(payment_label)
        payment_layout.add_widget(payment_input)
        
        # Change display
        change_layout = BoxLayout(size_hint_y=None, height=40, opacity=0)
        change_label = Label(
            text='Kembalian:',
            size_hint_x=0.4,
            font_size='16sp',
            bold=True
        )
        change_amount = Label(
            text='Rp 0',
            size_hint_x=0.6,
            font_size='16sp',
            bold=True,
            color=(0.2, 0.2, 0.8, 1),
            halign='right'
        )
        change_layout.add_widget(change_label)
        change_layout.add_widget(change_amount)
        
        # Buttons
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        cancel_btn = Button(text='BATAL')
        process_btn = Button(
            text='PROSES',
            background_color=(0.2, 0.8, 0.2, 1),
            font_size='14sp',
            disabled=True
        )
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(process_btn)
        
        # Quick payment buttons
        quick_payment_layout = BoxLayout(size_hint_y=None, height=40, spacing=5)
        
        def set_payment_amount(amount):
            payment_input.text = str(amount)
            update_change(None, None)
        
        # Tombol pembayaran cepat
        pas_btn = Button(text='PAS', font_size='12sp', size_hint_x=0.25)
        pas_btn.bind(on_press=lambda x: set_payment_amount(int(total)))
        
        btn_50k = Button(text='50K', font_size='12sp', size_hint_x=0.25)
        btn_50k.bind(on_press=lambda x: set_payment_amount(50000))
        
        btn_100k = Button(text='100K', font_size='12sp', size_hint_x=0.25)
        btn_100k.bind(on_press=lambda x: set_payment_amount(100000))
        
        btn_200k = Button(text='200K', font_size='12sp', size_hint_x=0.25)
        btn_200k.bind(on_press=lambda x: set_payment_amount(200000))
        
        quick_payment_layout.add_widget(pas_btn)
        quick_payment_layout.add_widget(btn_50k)
        quick_payment_layout.add_widget(btn_100k)
        quick_payment_layout.add_widget(btn_200k)
        
        # Add all widgets to content
        content.add_widget(total_layout)
        content.add_widget(payment_layout)
        content.add_widget(quick_payment_layout)
        content.add_widget(change_layout)
        content.add_widget(btn_layout)
        
        # Create and open popup
        popup = Popup(
            title='Pembayaran',
            content=content,
            size_hint=(0.9, 0.7)
        )
        
        def update_change(instance, value):
            try:
                payment = float(payment_input.text) if payment_input.text else 0
                change = payment - total
                
                if payment >= total:
                    change_layout.opacity = 1
                    change_amount.text = self.app_ref.format_currency(change)
                    process_btn.disabled = False
                    process_btn.background_color = (0.2, 0.8, 0.2, 1)  # Green
                else:
                    change_layout.opacity = 0.5
                    change_amount.text = self.app_ref.format_currency(0)
                    process_btn.disabled = True
                    process_btn.background_color = (0.8, 0.2, 0.2, 1)  # Red
                    
            except ValueError:
                change_layout.opacity = 0.5
                process_btn.disabled = True
        
        def process_payment(instance):
            try:
                payment = float(payment_input.text) if payment_input.text else 0
                change = payment - total
                
                if payment < total or payment <= 0:
                    raise ValueError('Jumlah pembayaran tidak valid')
                
                # Process the payment
                self.process_payment(payment, change)
                sound_manager.success_feedback()
                popup.dismiss()
                
            except ValueError as e:
                show_error_popup(str(e), 'Pembayaran Gagal')
                sound_manager.error_feedback()
        
        payment_input.bind(text=update_change)
        process_btn.bind(on_release=process_payment)
        cancel_btn.bind(on_release=popup.dismiss)
        
        popup.open()
    
    def show_add_product(self, instance):
        """Show popup to add new product"""
        from kivy.app import App
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.textinput import TextInput
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        # Product name input
        name_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        name_label = Label(text='Nama Produk:', size_hint_x=0.4)
        name_input = TextInput(multiline=False, size_hint_x=0.6)
        name_layout.add_widget(name_label)
        name_layout.add_widget(name_input)
        
        # Price input
        price_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        price_label = Label(text='Harga per kg:', size_hint_x=0.4)
        price_input = TextInput(input_filter='float', multiline=False, size_hint_x=0.6)
        price_layout.add_widget(price_label)
        price_layout.add_widget(price_input)
        
        # Stock input
        stock_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        stock_label = Label(text='Stok (kg):', size_hint_x=0.4)
        stock_input = TextInput(input_filter='float', multiline=False, size_hint_x=0.6)
        stock_layout.add_widget(stock_label)
        stock_layout.add_widget(stock_input)
        
        # Buttons
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        cancel_btn = Button(text='BATAL')
        save_btn = Button(text='SIMPAN', background_color=(0.2, 0.8, 0.2, 1))
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(save_btn)
        
        # Add all widgets to content
        content.add_widget(name_layout)
        content.add_widget(price_layout)
        content.add_widget(stock_layout)
        content.add_widget(btn_layout)
        
        # Create and open popup
        popup = Popup(
            title='Tambah Produk Baru',
            content=content,
            size_hint=(0.9, 0.6)
        )
        
        def save_product(instance):
            try:
                name = name_input.text.strip()
                price = float(price_input.text) if price_input.text else 0
                stock = float(stock_input.text) if stock_input.text else 0
                
                if not name:
                    raise ValueError('Nama produk tidak boleh kosong')
                if price <= 0:
                    raise ValueError('Harga harus lebih dari 0')
                if stock < 0:
                    raise ValueError('Stok tidak boleh negatif')
                
                # Add new product
                new_product = {
                    'id': str(int(time.time())),
                    'name': name,
                    'price_per_kg': price,
                    'stock_kg': stock
                }
                
                self.app_ref.products.append(new_product)
                self.app_ref.save_kasir_products()
                self.update_products_display()
                
                sound_manager.success_feedback()
                popup.dismiss()
                
            except ValueError as e:
                show_error_popup(str(e), 'Kesalahan Input')
                sound_manager.error_feedback()
        
        save_btn.bind(on_release=save_product)
        cancel_btn.bind(on_release=popup.dismiss)
        
        popup.open()
        self.update_header()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=['5dp', '10dp', '5dp', '10dp'], spacing='8dp')
        
        # Header with responsive sizing
        header = BoxLayout(size_hint_y=None, height='50dp')
        back_btn = Button(
            text='Kembali',
            size_hint_x=0.25,
            background_color=(0.6, 0.6, 0.6, 1),
            font_size='12sp'
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'category'))
        header.add_widget(back_btn)
        
        self.title_label = Label(
            text='KASIR AYAM POTONG',
            font_size='18sp',
            bold=True,
            text_size=(None, None),
            halign='center',
            valign='middle',
            size_hint_y=None,
            height='50dp'
        )
        header.add_widget(self.title_label)
        layout.add_widget(header)
        
        # Navigation buttons with responsive sizing
        nav_layout = BoxLayout(size_hint_y=None, height='50dp', spacing='5dp')
        
        expenses_btn = Button(
            text='PENGELUARAN',
            background_color=(0.8, 0.4, 0.2, 1),
            font_size='14sp',
            bold=True,
            size_hint_y=None,
            height='45dp'
        )
        expenses_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'kasir_expenses'))
        
        reports_btn = Button(
            text='LAPORAN',
            background_color=(0.2, 0.6, 0.8, 1),
            font_size='14sp',
            bold=True,
            size_hint_y=None,
            height='45dp'
        )
        reports_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'kasir_reports'))
        
        nav_layout.add_widget(expenses_btn)
        nav_layout.add_widget(reports_btn)
        layout.add_widget(nav_layout)
        
        # Content area with responsive layout
        content = BoxLayout(orientation='horizontal', spacing='8dp')
        
        # Products section
        products_section = BoxLayout(orientation='vertical', size_hint_x=0.6, spacing='3dp')
        
        # Add product button with responsive sizing
        add_product_btn = Button(
            text='+ TAMBAH PRODUK',
            size_hint_y=None,
            height='50dp',
            background_color=(0.2, 0.8, 0.2, 1),
            font_size='14sp',
            bold=True
        )
        add_product_btn.bind(on_press=self.show_add_product)
        products_section.add_widget(add_product_btn)
        
        # Products scroll
        self.products_scroll = ScrollView()
        self.products_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing='3dp')
        self.products_layout.bind(minimum_height=self.products_layout.setter('height'))
        self.products_scroll.add_widget(self.products_layout)
        products_section.add_widget(self.products_scroll)
        
        # Cart section
        cart_section = BoxLayout(orientation='vertical', size_hint_x=0.4, spacing='3dp')
        
        cart_header = Label(
            text='KERANJANG',
            size_hint_y=None,
            height='35dp',
            font_size='16sp',
            bold=True,
            color=(0.2, 0.6, 0.8, 1),
            text_size=(None, None),
            halign='center',
            valign='middle'
        )
        cart_section.add_widget(cart_header)
        
        # Cart scroll
        self.cart_scroll = ScrollView()
        self.cart_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=3)
        self.cart_layout.bind(minimum_height=self.cart_layout.setter('height'))
        self.cart_scroll.add_widget(self.cart_layout)
        cart_section.add_widget(self.cart_scroll)
        
        # Cart total with responsive sizing
        self.total_label = Label(
            text='Total: Rp 0',
            size_hint_y=None,
            height='30dp',
            font_size='14sp',
            bold=True,
            color=(0.1, 0.6, 0.1, 1),
            text_size=(None, None),
            halign='center',
            valign='middle'
        )
        cart_section.add_widget(self.total_label)
        
        # Checkout button with responsive sizing
        self.checkout_btn = Button(
            text='BAYAR',
            size_hint_y=None,
            height='40dp',
            background_color=(0.1, 0.7, 0.3, 1),
            font_size='14sp',
            bold=True,
            disabled=True
        )
        self.checkout_btn.bind(on_press=self.show_payment)
        cart_section.add_widget(self.checkout_btn)
        
        content.add_widget(products_section)
        content.add_widget(cart_section)
        layout.add_widget(content)
        
        self.add_widget(layout)
        
        self.products_layout.clear_widgets()
        if self.app_ref and hasattr(self.app_ref, 'products'):
            for product in self.app_ref.products:
                product_widget = self.create_product_widget(product)
                self.products_layout.add_widget(product_widget)
    
    def create_product_widget(self, product):
        widget = BoxLayout(orientation='vertical', size_hint_y=None, height=120, spacing=3, padding=5)
        
        # Handle both dictionary and object access
        is_dict = isinstance(product, dict)
        product_name = product.get('name') if is_dict else product.name
        product_price = product.get('price_per_kg') if is_dict else product.price_per_kg
        product_stock = product.get('stock_kg') if is_dict else product.stock_kg
        product_id = product.get('id') if is_dict else product.id
        
        # Create a proper product object if we have a dictionary
        if is_dict:
            product_obj = KasirProduct(
                product_id,
                product_name,
                product_price,
                product_stock
            )
        else:
            product_obj = product
        
        # Product name
        name_label = Label(
            text=product_name,
            size_hint_y=None,
            height=25,
            font_size='12sp',
            bold=True,
            color=(0.1, 0.1, 0.1, 1)
        )
        widget.add_widget(name_label)
        
        # Price
        price_label = Label(
            text=f'{self.app_ref.format_currency(product_price)}/kg',
            size_hint_y=None,
            height=20,
            font_size='10sp',
            color=(0.1, 0.6, 0.1, 1)
        )
        widget.add_widget(price_label)
        
        # Stock
        stock_color = (0.1, 0.7, 0.1, 1) if product_stock > 5 else (0.9, 0.6, 0.1, 1) if product_stock > 0 else (0.9, 0.1, 0.1, 1)
        stock_label = Label(
            text=f'Stok: {product_stock} kg',
            size_hint_y=None,
            height=20,
            font_size='10sp',
            color=stock_color
        )
        widget.add_widget(stock_label)
        
        # Buttons layout
        buttons_layout = BoxLayout(size_hint_y=None, height=40, spacing=5)
        
        # Add to cart button
        add_btn = Button(
            text='Tambah',
            size_hint_x=0.7,
            background_color=(0.2, 0.6, 0.9, 1),
            font_size='10sp',
            disabled=product_stock <= 0
        )
        add_btn.bind(on_press=lambda x: self.show_weight_input(product_obj))
        
        # Delete button
        delete_btn = Button(
            text='X',
            background_color=(0.9, 0.2, 0.2, 1),
            font_size='10sp',
            size_hint_x=0.3
        )
        delete_btn.bind(on_press=lambda x: self.show_delete_product_confirmation(product_obj))
        
        buttons_layout.add_widget(add_btn)
        buttons_layout.add_widget(delete_btn)
        widget.add_widget(buttons_layout)
        
        return widget
    
    def refresh_cart(self):
        if not self.app_ref:
            return
            
        self.cart_layout.clear_widgets()
        
        if not self.app_ref.cart:
            self.total_label.text = 'Total: Rp 0'
            self.checkout_btn.disabled = True
            return
            
        total = 0
        for cart_item in self.app_ref.cart:
            cart_widget = self.create_cart_widget(cart_item)
            self.cart_layout.add_widget(cart_widget)
            total += cart_item.get_total()
            
        self.total_label.text = f'Total: {self.app_ref.format_currency(total)}'
        self.checkout_btn.disabled = len(self.app_ref.cart) == 0
    
    def show_payment(self, instance):
        """Show payment popup"""
        if not self.app_ref or not self.app_ref.cart:
            return
            
        total = sum(item.get_total() for item in self.app_ref.cart)
        
        # Create popup content
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        # Total amount
        total_layout = BoxLayout(size_hint_y=None, height=40)
        total_label = Label(
            text='Total Pembayaran:',
            size_hint_x=0.6,
            font_size='16sp',
            bold=True
        )
        total_amount = Label(
            text=self.app_ref.format_currency(total),
            size_hint_x=0.4,
            font_size='18sp',
            bold=True,
            color=(0.2, 0.6, 0.2, 1),
            halign='right'
        )
        total_layout.add_widget(total_label)
        total_layout.add_widget(total_amount)
        
        # Payment input
        payment_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        payment_label = Label(text='Jumlah Bayar:', size_hint_x=0.4)
        payment_input = TextInput(
            input_filter='float',
            multiline=False,
            size_hint_x=0.6,
            font_size='16sp',
            text=str(int(total))
        )
        payment_layout.add_widget(payment_label)
        payment_layout.add_widget(payment_input)
        
        # Change display
        change_layout = BoxLayout(size_hint_y=None, height=40, opacity=0)
        change_label = Label(
            text='Kembalian:',
            size_hint_x=0.4,
            font_size='16sp',
            bold=True
        )
        change_amount = Label(
            text='Rp 0',
            size_hint_x=0.6,
            font_size='16sp',
            bold=True,
            color=(0.2, 0.2, 0.8, 1),
            halign='right'
        )
        change_layout.add_widget(change_label)
        change_layout.add_widget(change_amount)
        
        # Buttons
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        cancel_btn = Button(text='BATAL')
        process_btn = Button(
            text='PROSES',
            background_color=(0.2, 0.8, 0.2, 1),
            font_size='14sp',
            disabled=True
        )
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(process_btn)
        
        # Quick payment buttons
        quick_payment_layout = BoxLayout(size_hint_y=None, height=40, spacing=5)
        
        def set_payment_amount(amount):
            payment_input.text = str(amount)
            update_change(None, None)
        
        # Tombol pembayaran cepat
        pas_btn = Button(text='PAS', font_size='12sp', size_hint_x=0.25)
        pas_btn.bind(on_press=lambda x: set_payment_amount(int(total)))
        
        btn_50k = Button(text='50K', font_size='12sp', size_hint_x=0.25)
        btn_50k.bind(on_press=lambda x: set_payment_amount(50000))
        
        btn_100k = Button(text='100K', font_size='12sp', size_hint_x=0.25)
        btn_100k.bind(on_press=lambda x: set_payment_amount(100000))
        
        btn_200k = Button(text='200K', font_size='12sp', size_hint_x=0.25)
        btn_200k.bind(on_press=lambda x: set_payment_amount(200000))
        
        quick_payment_layout.add_widget(pas_btn)
        quick_payment_layout.add_widget(btn_50k)
        quick_payment_layout.add_widget(btn_100k)
        quick_payment_layout.add_widget(btn_200k)
        
        # Add all widgets to content
        content.add_widget(total_layout)
        content.add_widget(payment_layout)
        content.add_widget(quick_payment_layout)
        content.add_widget(change_layout)
        content.add_widget(btn_layout)
        
        # Create and open popup
        popup = Popup(
            title='Pembayaran',
            content=content,
            size_hint=(0.9, 0.7)
        )
        
        def update_change(instance, value):
            try:
                payment = float(payment_input.text) if payment_input.text else 0
                change = payment - total
                
                if payment >= total:
                    change_layout.opacity = 1
                    change_amount.text = self.app_ref.format_currency(change)
                    process_btn.disabled = False
                    process_btn.background_color = (0.2, 0.8, 0.2, 1)  # Green
                else:
                    change_layout.opacity = 0.5
                    change_amount.text = self.app_ref.format_currency(0)
                    process_btn.disabled = True
                    process_btn.background_color = (0.8, 0.2, 0.2, 1)  # Red
                    
            except ValueError:
                change_layout.opacity = 0.5
                process_btn.disabled = True
        
        def process_payment(instance):
            try:
                payment = float(payment_input.text) if payment_input.text else 0
                change = payment - total
                
                if payment < total or payment <= 0:
                    raise ValueError('Jumlah pembayaran tidak valid')
                
                # Process the payment
                self.process_payment(payment, change)
                sound_manager.success_feedback()
                popup.dismiss()
                
            except ValueError as e:
                show_error_popup(str(e), 'Pembayaran Gagal')
                sound_manager.error_feedback()
        
        payment_input.bind(text=update_change)
        process_btn.bind(on_release=process_payment)
        cancel_btn.bind(on_release=popup.dismiss)
        
        popup.open()
        
        self.cart_layout.clear_widgets()
        for cart_item in self.app_ref.cart:
            cart_widget = self.create_cart_widget(cart_item)
            self.cart_layout.add_widget(cart_widget)
        
        # Update total
        total = self.app_ref.get_cart_total()
        self.total_label.text = f'Total: {self.app_ref.format_currency(total)}'
        self.checkout_btn.disabled = len(self.app_ref.cart) == 0
    
    def refresh_cart(self):
        """Legacy method - redirects to update_cart_display"""
        self.update_cart_display()
    
    def create_cart_widget(self, cart_item):
        widget = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='70dp',
            spacing='15dp',
            padding=('15dp', '8dp', '15dp', '8dp')
        )
        
        # Product info layout - lebih terstruktur
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.65, spacing='2dp')
        
        # Nama produk
        name_label = Label(
            text=cart_item.product.name,
            font_size='12sp',
            bold=True,
            size_hint_y=None,
            height='20dp',
            text_size=(dp(180), None),
            halign='left',
            valign='middle',
            color=(0.1, 0.1, 0.1, 1),
            shorten=True,
            shorten_from='right'
        )
        
        # Detail berat dan harga per kg
        detail_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='20dp', spacing='10dp')
        
        weight_label = Label(
            text=f"{cart_item.weight_kg} kg",
            font_size='11sp',
            size_hint_x=None,
            width='60dp',
            color=(0.3, 0.3, 0.3, 1),
            halign='left'
        )
        
        price_per_kg_label = Label(
            text=f"@ {self.app_ref.format_currency(cart_item.product.price_per_kg)}/kg",
            font_size='11sp',
            color=(0.5, 0.5, 0.5, 1),
            halign='left'
        )
        
        detail_layout.add_widget(weight_label)
        detail_layout.add_widget(price_per_kg_label)
        
        info_layout.add_widget(name_label)
        info_layout.add_widget(detail_layout)
        
        # Total price - lebih prominent
        total_label = Label(
            text=self.app_ref.format_currency(cart_item.get_total()),
            font_size='13sp',
            bold=True,
            size_hint_x=0.35,
            text_size=(dp(90), None),
            halign='right',
            valign='middle',
            color=(0.1, 0.6, 0.1, 1),
            shorten=True
        )
        
        widget.add_widget(info_layout)
        widget.add_widget(total_label)
        
        return widget
        
    def show_delete_product_confirmation(self, product):
        """Show confirmation popup before deleting product"""
        popup = ConfirmationPopup(
            "Hapus Produk",
            f"Yakin ingin menghapus produk {product.name}?",
            confirm_callback=lambda: self.confirm_delete_product(product)
        )
        popup.open()
    
    def confirm_delete_product(self, product):
        """Delete product from inventory"""
        self.app_ref.products.remove(product)
        self.app_ref.save_kasir_products()
        self.refresh_products()
        self.app_ref.show_popup('Berhasil', f'Produk "{product.name}" berhasil dihapus!')
    
    def process_payment(self, payment_amount, change_amount):
        """Process payment and generate receipt"""
        from datetime import datetime
        
        # Create receipt data
        receipt_data = {
            'transaction_id': self.app_ref.transaction_counter,
            'date_time': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'items': [],
            'total': self.app_ref.get_cart_total(),
            'payment': payment_amount,
            'change': change_amount
        }
            
        # Add cart items to receipt
        for cart_item in self.app_ref.cart:
            receipt_data['items'].append({
                'name': cart_item.product.name,
                'weight': cart_item.weight_kg,
                'price_per_kg': cart_item.product.price_per_kg,
                'total': cart_item.get_total()
            })
        
        # Update sales and counter
        self.app_ref.daily_sales += receipt_data['total']
        self.app_ref.transaction_counter += 1
        
        # Clear cart
        self.app_ref.cart.clear()
        
        # Save data
        self.app_ref.save_kasir_products()
        self.app_ref.save_kasir_expenses()
        self.app_ref.save_kasir_counter()
        
        # Show receipt
        receipt_screen = self.manager.get_screen('kasir_receipt')
        receipt_screen.set_receipt_data(receipt_data)
        self.manager.current = 'kasir_receipt'
        
        # Refresh displays
        self.update_cart_display()
        self.update_products_display()

# Kasir Expenses Screen
class KasirExpensesScreen(Screen):
    """Screen for managing expenses"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = None
        self.build_ui()
    
    def on_enter(self):
        self.app_ref = App.get_running_app()
        self.refresh_expenses()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=['5dp', '10dp', '5dp', '10dp'], spacing='8dp')
        
        # Header with responsive sizing
        header = BoxLayout(size_hint_y=None, height='50dp')
        back_btn = Button(
            text='Kembali',
            size_hint_x=0.25,
            background_color=(0.6, 0.6, 0.6, 1),
            font_size='12sp'
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'kasir_main'))
        header.add_widget(back_btn)
        
        title_label = Label(
            text='PENGELUARAN',
            font_size='18sp',
            bold=True,
            text_size=(None, None),
            halign='center',
            valign='middle',
            size_hint_y=None,
            height='50dp'
        )
        header.add_widget(title_label)
        layout.add_widget(header)
        
        # Add expense button
        add_expense_btn = Button(
            text='+ TAMBAH PENGELUARAN',
            size_hint_y=None,
            height='50dp',
            background_color=(0.2, 0.8, 0.2, 1),
            font_size='14sp',
            bold=True,
            padding=('10dp', '5dp')
        )
        add_expense_btn.bind(on_press=self.show_add_expense)
        layout.add_widget(add_expense_btn)
        
        # Expenses list
        self.expenses_scroll = ScrollView(bar_width='6dp', bar_color=(0.5, 0.5, 0.5, 0.5))
        self.expenses_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing='8dp', padding='5dp')
        self.expenses_layout.bind(minimum_height=self.expenses_layout.setter('height'))
        self.expenses_scroll.add_widget(self.expenses_layout)
        layout.add_widget(self.expenses_scroll)
        
        # Total expenses with better styling
        total_container = BoxLayout(size_hint_y=None, height='60dp', padding=('10dp', '5dp'))
        
        # Create canvas for background
        with total_container.canvas.before:
            self.rect_color = Color(0.9, 0.9, 0.9, 1)
            self.rect = Rectangle(pos=total_container.pos, size=total_container.size)
        
        # Bind update method
        def update_rect(instance, value):
            self.rect.pos = instance.pos
            self.rect.size = instance.size
            
        total_container.bind(pos=update_rect, size=update_rect)
        
        total_text = Label(
            text='Total Pengeluaran:',
            size_hint_x=0.6,
            font_size='16sp',
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            text_size=(None, None),
            halign='left',
            valign='middle'
        )
        
        self.total_label = Label(
            text='Rp 0',
            size_hint_x=0.4,
            font_size='18sp',
            bold=True,
            color=(0.8, 0.2, 0.2, 1),
            text_size=(None, None),
            halign='right',
            valign='middle'
        )
        
        total_container.add_widget(total_text)
        total_container.add_widget(self.total_label)
        
        layout.add_widget(total_container)
        
        self.add_widget(layout)
    
    def refresh_expenses(self):
        if not self.app_ref:
            return
        
        self.expenses_layout.clear_widgets()
        total = 0
        
        for expense in self.app_ref.expenses:
            expense_widget = self.create_expense_widget(expense)
            self.expenses_layout.add_widget(expense_widget)
            total += expense['amount']
        
        self.total_label.text = f'Total Pengeluaran: {self.app_ref.format_currency(total)}'
    
    def create_expense_widget(self, expense):
        # Create main widget with card-like appearance
        widget = BoxLayout(
            orientation='horizontal', 
            size_hint_y=None, 
            height='90dp',  # Increased height for better touch
            spacing='15dp', 
            padding=('20dp', '15dp', '20dp', '15dp')  # More padding for better spacing
        )
        
        # Add card background
        with widget.canvas.before:
            # Background color
            widget.bg_color = Color(1, 1, 1, 1)  # White background
            widget.rect = RoundedRectangle(
                pos=widget.pos,
                size=widget.size,
                radius=[10, 10, 10, 10]
            )
            # Border color
            widget.border_color = Color(0.9, 0.9, 0.9, 1)
            widget.border = Line(
                rounded_rectangle=(
                    widget.x, 
                    widget.y, 
                    widget.width, 
                    widget.height, 
                    10
                ),
                width=1.5
            )
        
        # Update function for position/size changes
        def update_expense_rect(instance, value):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size
            instance.border.rounded_rectangle = (
                instance.x, instance.y, instance.width, instance.height, 10
            )
        
        # Bind the update function
        widget.bind(pos=update_expense_rect, size=update_expense_rect)
        
        # Expense info with better layout
        info_layout = BoxLayout(
            orientation='vertical', 
            size_hint_x=0.6,  # More space for text
            spacing='4dp'  # Slightly more spacing between lines
        )
        
        name_label = Label(
            text=expense['name'],
            font_size='16sp',  # Larger font for better readability
            bold=True,
            size_hint_y=None,
            height='32dp',  # More height for the name
            text_size=(Window.width * 0.4, None),  # Limit width to prevent overflow
            halign='left',
            valign='middle',
            color=(0.2, 0.2, 0.2, 1),  # Darker text for better contrast
            shorten=True,
            shorten_from='right'
        )
        
        date_label = Label(
            text=expense.get('date', 'No date'),
            font_size='12sp',
            size_hint_y=None,
            height='25dp',
            color=(0.5, 0.5, 0.5, 1),
            text_size=(None, None),
            halign='left',
            valign='top'
        )
        
        info_layout.add_widget(name_label)
        info_layout.add_widget(date_label)
        
        # Amount with better styling
        amount_label = Label(
            text=self.app_ref.format_currency(expense['amount']),
            font_size='16sp',
            bold=True,
            size_hint_x=0.3,
            color=(0.8, 0.2, 0.2, 1),  # More vibrant red for better visibility
            text_size=(Window.width * 0.25, None),  # Set width to 25% of window width
            halign='right',
            valign='middle',
            size_hint_y=None,
            height='60dp'
        )
        
        # Delete button with better styling
        delete_btn = Button(
            text='HAPUS',
            size_hint_x=0.2,
            size_hint_y=None,
            height='40dp',
            background_color=(0.9, 0.2, 0.2, 1),
            background_normal='',
            background_down='atlas://data/images/defaulttheme/button_pressed',
            font_size='12sp',
            bold=True,
            color=(1, 1, 1, 1),  # White text
            padding=('5dp', '2dp'),
            pos_hint={'center_y': 0.5}
        )
        delete_btn.bind(on_press=lambda x, exp=expense: self.delete_expense(exp))
        
        # Add all widgets to the main layout
        widget.add_widget(info_layout)
        widget.add_widget(amount_label)
        widget.add_widget(delete_btn)
        
        # Add shadow effect
        with widget.canvas.after:
            widget.shadow_color = Color(0, 0, 0, 0.1)
            widget.shadow = RoundedRectangle(
                pos=(widget.x + 2, widget.y - 2),
                size=widget.size,
                radius=[10, 10, 10, 10]
            )
        
        # Update function for shadow
        def update_shadow(instance, value):
            if hasattr(instance, 'shadow'):
                instance.shadow.pos = (instance.x + 2, instance.y - 2)
                instance.shadow.size = instance.size
        
        # Bind shadow update
        widget.bind(pos=update_shadow, size=update_shadow)
        
        return widget
        
    def show_add_expense(self, instance):
        popup = AddExpensePopup(callback=self.add_new_expense)
        popup.open()
    
    def show_weight_input(self, product):
        """Tampilkan popup untuk memasukkan berat produk - menggunakan pola yang sama dengan kasir.py"""
        if not product:
            show_error_popup('Produk tidak valid')
            return
            
        try:
            # Dapatkan detail produk dengan aman
            if hasattr(product, 'get') and callable(getattr(product, 'get')):
                product_name = product.get('name', 'Produk')
                price_per_kg = float(product.get('price_per_kg', 0))
            else:
                product_name = getattr(product, 'name', 'Produk')
                price_per_kg = float(getattr(product, 'price_per_kg', 0))
            
            # Create popup dengan pola yang sama persis dengan kasir.py WeightInputPopup
            popup = Popup(
                title=f'Input Berat - {product_name}',
                size_hint=(0.9, 0.7),
                auto_dismiss=False
            )
            
            layout = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
            
            # Product info
            info_label = Label(
                text=f'{product_name}\nHarga: {self.app_ref.format_currency(price_per_kg)}/kg',
                size_hint_y=None,
                height=dp(70),
                font_size=dp(14),
                bold=True,
                halign='center',
                color=(0.2, 0.6, 0.2, 1)
            )
            layout.add_widget(info_label)
            
            # Weight input dengan keypad numerik virtual
            weight_label = Label(
                text='Masukkan Berat:',
                size_hint_y=None,
                height=dp(30),
                font_size=dp(14),
                bold=True,
                color=(0.2, 0.2, 0.2, 1),
                halign='center'
            )
            layout.add_widget(weight_label)
            
            # Display untuk menampilkan angka yang diinput
            weight_display_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
            
            weight_display = Label(
                text='1',
                font_size=dp(20),
                size_hint_x=0.8,
                bold=True,
                color=(0.1, 0.1, 0.1, 1),
                halign='center'
            )
            
            # Add background to display
            with weight_display.canvas.before:
                from kivy.graphics import Color, RoundedRectangle
                Color(0.95, 0.95, 0.95, 1)
                weight_display.bg = RoundedRectangle(size=weight_display.size, pos=weight_display.pos, radius=[5])
            weight_display.bind(size=lambda instance, value: setattr(instance.bg, 'size', value))
            weight_display.bind(pos=lambda instance, value: setattr(instance.bg, 'pos', value))
            
            kg_label = Label(
                text='KG',
                size_hint_x=0.2,
                font_size=dp(14),
                bold=True,
                color=(0.4, 0.4, 0.4, 1)
            )
            
            weight_display_layout.add_widget(weight_display)
            weight_display_layout.add_widget(kg_label)
            layout.add_widget(weight_display_layout)
            
            # Keypad numerik
            keypad_layout = GridLayout(cols=3, spacing=dp(5), size_hint_y=None, height=dp(180))
            
            current_value = ['1']
            
            def update_display():
                value_str = ''.join(current_value)
                weight_display.text = value_str
                try:
                    weight = float(value_str) if value_str else 0
                    total = price_per_kg * weight
                    total_label.text = f'Total: {self.app_ref.format_currency(total)}'
                except:
                    total_label.text = 'Total: Rp 0'
            
            def add_digit(digit):
                if digit == '.' and '.' in current_value:
                    return
                if len(''.join(current_value)) < 6:  # Limit input length
                    current_value.append(digit)
                    update_display()
            
            def clear_input():
                current_value.clear()
                current_value.extend(['0'])
                update_display()
            
            def backspace():
                if len(current_value) > 1:
                    current_value.pop()
                else:
                    current_value[0] = '0'
                update_display()
            
            # Tombol angka 1-9
            for i in range(1, 10):
                btn = Button(
                    text=str(i),
                    font_size=dp(18),
                    bold=True,
                    background_color=(0.9, 0.9, 0.9, 1),
                    color=(0, 0, 0, 1)
                )
                btn.bind(on_press=lambda x, digit=str(i): add_digit(digit))
                keypad_layout.add_widget(btn)
            
            # Tombol titik desimal
            dot_btn = Button(
                text='.',
                font_size=dp(18),
                bold=True,
                background_color=(0.9, 0.9, 0.9, 1),
                color=(0, 0, 0, 1)
            )
            dot_btn.bind(on_press=lambda x: add_digit('.'))
            keypad_layout.add_widget(dot_btn)
            
            # Tombol 0
            zero_btn = Button(
                text='0',
                font_size=dp(18),
                bold=True,
                background_color=(0.9, 0.9, 0.9, 1),
                color=(0, 0, 0, 1)
            )
            zero_btn.bind(on_press=lambda x: add_digit('0'))
            keypad_layout.add_widget(zero_btn)
            
            # Tombol backspace
            back_btn = Button(
                text='←',
                font_size=dp(18),
                bold=True,
                background_color=(0.8, 0.6, 0.6, 1),
                color=(1, 1, 1, 1)
            )
            back_btn.bind(on_press=lambda x: backspace())
            keypad_layout.add_widget(back_btn)
            
            layout.add_widget(keypad_layout)
            
            # Quick preset buttons
            preset_layout = BoxLayout(spacing=dp(5), size_hint_y=None, height=dp(40))
            presets = ['0.5', '1.0', '2.0', '5.0']
            
            for preset in presets:
                btn = Button(
                    text=f'{preset} kg',
                    font_size=dp(12),
                    background_color=(0.7, 0.8, 0.9, 1),
                    color=(0, 0, 0, 1)
                )
                def set_preset(preset_val):
                    current_value.clear()
                    current_value.extend(list(preset_val))
                    update_display()
                btn.bind(on_press=lambda x, p=preset: set_preset(p))
                preset_layout.add_widget(btn)
            
            layout.add_widget(preset_layout)
            
            # Total preview
            total_label = Label(
                text='Total: Rp 0',
                size_hint_y=None,
                height=dp(40),
                font_size=dp(16),
                bold=True,
                color=(0.1, 0.6, 0.1, 1),
                halign='center'
            )
            layout.add_widget(total_label)
            
            # Initialize display
            update_display()
            
            # Action buttons - sama dengan kasir.py
            buttons_layout = BoxLayout(spacing=dp(15), size_hint_y=None, height=dp(50))
            
            add_btn = Button(
                text='TAMBAH KE KERANJANG',
                background_color=(0.1, 0.7, 0.3, 1),
                font_size=dp(13),
                bold=True
            )
            
            cancel_btn = Button(
                text='BATAL',
                background_color=(0.9, 0.2, 0.2, 1),
                font_size=dp(13),
                bold=True,
                size_hint_x=0.4
            )
            
            # Bind button actions
            add_btn.bind(on_press=lambda x: self.add_to_cart_with_weight(product, weight_display.text, popup))
            cancel_btn.bind(on_press=lambda x: popup.dismiss())
            
            buttons_layout.add_widget(add_btn)
            buttons_layout.add_widget(cancel_btn)
            layout.add_widget(buttons_layout)
            
            popup.content = layout
            popup.open()
            
        except Exception as e:
            show_error_popup(f'Terjadi kesalahan: {str(e)}')
            print(f'Error in show_weight_input: {str(e)}')
    
    def update_weight_display_bg(self, instance):
        """Update background for weight display"""
        try:
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(0.9, 0.9, 0.9, 1)
                Rectangle(pos=instance.pos, size=instance.size)
        except:
            pass
        
    def add_to_cart_with_weight(self, product, weight_text, popup):
        """Tambah produk ke keranjang dengan berat yang ditentukan"""
        try:
            # Validasi input berat
            weight = float(weight_text)
            if weight <= 0:
                raise ValueError('Berat harus lebih dari 0')
            
            # Dapatkan detail produk (mendukung dict dan objek)
            if hasattr(product, 'get') and callable(getattr(product, 'get')):
                # Jika product adalah dictionary
                product_id = product.get('id')
                product_name = product.get('name', 'Produk')
                price_per_kg = float(product.get('price_per_kg', 0))
                stock_kg = float(product.get('stock_kg', 0))
            else:
                # Jika product adalah objek KasirProduct
                product_id = getattr(product, 'id', 0)
                product_name = getattr(product, 'name', 'Produk')
                price_per_kg = float(getattr(product, 'price_per_kg', 0))
                stock_kg = float(getattr(product, 'stock_kg', 0))
            
            # Hitung total harga
            total_price = price_per_kg * weight
            
            # Buat cart item
            cart_item = {
                'id': product_id,
                'name': product_name,
                'price_per_kg': price_per_kg,
                'weight': weight,
                'total_price': total_price,
                'stock_kg': stock_kg
            }
            
            # Inisialisasi keranjang jika belum ada
            if not hasattr(self, 'app_ref') or not hasattr(self.app_ref, 'cart'):
                if hasattr(self, 'app_ref'):
                    self.app_ref.cart = []
                else:
                    show_error_popup('Terjadi kesalahan: Aplikasi tidak terinisialisasi dengan benar')
                    return
            
            # Tambahkan ke keranjang
            self.app_ref.cart.append(cart_item)
            
            # Perbarui tampilan keranjang
            if hasattr(self, 'update_cart_display'):
                self.update_cart_display()
            
            # Beri umpan balik sukses
            if hasattr(sound_manager, 'success_feedback'):
                sound_manager.success_feedback()
            
            # Tampilkan notifikasi sukses
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: show_popup(
                'Berhasil', 
                f'{product_name} ({weight} kg) berhasil ditambahkan ke keranjang',
                auto_dismiss=True
            ), 0.1)
            
        except ValueError as e:
            # Tampilkan pesan error yang lebih spesifik
            error_msg = str(e) if str(e) else 'Masukkan berat yang valid (contoh: 0.5, 1, 1.5)'
            show_error_popup(error_msg, title='Input Tidak Valid')
            if hasattr(sound_manager, 'error_feedback'):
                sound_manager.error_feedback()
        except Exception as e:
            # Tangani error tak terduga
            show_error_popup(f'Terjadi kesalahan: {str(e)}', title='Error')
            if hasattr(sound_manager, 'error_feedback'):
                sound_manager.error_feedback()
        finally:
            # Selalu tutup popup jika ada
            if popup and hasattr(popup, 'dismiss'):
                popup.dismiss()
    
    def delete_expense(self, expense):
        popup = ConfirmationPopup(
            "Hapus Pengeluaran",
            f"Yakin ingin menghapus pengeluaran {expense['name']}?",
            confirm_callback=lambda: self.confirm_delete_expense(expense)
        )
        popup.open()

    def add_new_expense(self, name, amount, note=''):
        if not self.app_ref:
            return

        # Convert to string first to handle both string and numeric inputs
        name = str(name) if name is not None else ""
        amount = str(amount) if amount is not None else ""
        note = str(note) if note is not None else ""
        
        # Handle case where instance is passed as the first argument (from button press)
        if hasattr(name, 'text'):  # If name is actually the instance
            instance = name
            name = amount  # Shift parameters
            amount = note
            note = ''

        # Validasi input
        if not name.strip():
            show_error_popup('Nama pengeluaran tidak boleh kosong', title='Kesalahan Input')
            sound_manager.error_feedback()
            return
            
        if not amount.strip():
            show_error_popup('Jumlah pengeluaran tidak boleh kosong', title='Kesalahan Input')
            sound_manager.error_feedback()
            return

        try:
            # Hapus karakter non-digit kecuali koma dan titik
            clean_amount = str(amount).strip()
            # Ganti koma dengan titik untuk format desimal
            clean_amount = clean_amount.replace(',', '.')
            
            # Validasi format angka
            if not re.match(r'^\d+(\.\d+)?$', clean_amount):
                raise ValueError('Format jumlah tidak valid. Gunakan angka (contoh: 10000 atau 10000.50)')
                
            # Convert amount to float
            amount_float = float(clean_amount)
            
            if amount_float <= 0:
                raise ValueError('Jumlah harus lebih dari 0')

            # Add to app's expenses list
            expense = {
                'id': str(int(time.time())),
                'name': name.strip(),
                'amount': amount_float,
                'note': note.strip(),
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            self.app_ref.expenses.append(expense)

            # Save to database
            self.app_ref.save_kasir_expenses()

            # Refresh the display
            self.refresh_expenses()

            # Play success sound
            sound_manager.success_feedback()

        except ValueError as e:
            # Show error popup if amount is invalid
            error_msg = str(e) if str(e) else 'Terjadi kesalahan saat memproses input'
            show_error_popup(error_msg, title='Kesalahan Input')
            sound_manager.error_feedback()

    def confirm_delete_expense(self, expense):
        """Delete expense"""
        self.app_ref.expenses.remove(expense)
        self.app_ref.save_kasir_expenses()
        self.refresh_expenses()

# Kasir Reports Screen
class KasirReportsScreen(Screen):
    """Screen for viewing sales reports"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = None
        self.build_ui()
    
    def on_enter(self):
        self.app_ref = App.get_running_app()
        self.refresh_reports()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=['5dp', '10dp', '5dp', '10dp'], spacing='8dp')
        
        # Header with responsive sizing
        header = BoxLayout(size_hint_y=None, height='50dp')
        back_btn = Button(
            text='Kembali',
            size_hint_x=0.25,
            background_color=(0.6, 0.6, 0.6, 1),
            font_size='12sp'
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'kasir_main'))
        header.add_widget(back_btn)
        
        title_label = Label(
            text='LAPORAN PENJUALAN',
            font_size='18sp',
            bold=True,
            text_size=(None, None),
            halign='center',
            valign='middle'
        )
        header.add_widget(title_label)
        layout.add_widget(header)
        
        # Summary cards with responsive sizing
        summary_scroll = ScrollView()
        summary_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing='5dp')
        summary_layout.bind(minimum_height=summary_layout.setter('height'))
        
        # Sales card with responsive sizing
        sales_card = BoxLayout(orientation='horizontal', size_hint_y=None, height='80dp', padding=['15dp', '10dp', '15dp', '10dp'], spacing='12dp')
        sales_info = BoxLayout(orientation='vertical', size_hint_x=0.7)
        sales_title = Label(
            text='PENJUALAN HARI INI',
            font_size='12sp',
            bold=True,
            size_hint_y=None,
            height='30dp',
            color=(0.1, 0.6, 0.1, 1),
            text_size=(None, None),
            halign='left',
            valign='middle'
        )
        sales_subtitle = Label(
            text='Total penjualan hari ini',
            font_size='9sp',
            size_hint_y=None,
            height='25dp',
            color=(0.5, 0.5, 0.5, 1),
            text_size=(None, None),
            halign='left',
            valign='middle'
        )
        sales_info.add_widget(sales_title)
        sales_info.add_widget(sales_subtitle)
        
        self.sales_amount = Label(
            text='Rp 0',
            font_size='14sp',
            bold=True,
            size_hint_x=0.3,
            color=(0.1, 0.6, 0.1, 1),
            text_size=(None, None),
            halign='right',
            valign='middle'
        )
        sales_card.add_widget(sales_info)
        sales_card.add_widget(self.sales_amount)
        
        # Expenses card
        expenses_card = BoxLayout(orientation='horizontal', size_hint_y=None, height=80, padding=15, spacing=12)
        expenses_info = BoxLayout(orientation='vertical', size_hint_x=0.7)
        expenses_title = Label(
            text='PENGELUARAN HARI INI',
            font_size='14sp',
            bold=True,
            size_hint_y=None,
            height=25,
            color=(0.8, 0.4, 0.2, 1),
            text_size=(None, None),
            halign='left'
        )
        expenses_subtitle = Label(
            text='Total pengeluaran hari ini',
            font_size='10sp',
            size_hint_y=None,
            height=20,
            color=(0.5, 0.5, 0.5, 1),
            text_size=(None, None),
            halign='left'
        )
        expenses_info.add_widget(expenses_title)
        expenses_info.add_widget(expenses_subtitle)
        
        self.expenses_amount = Label(
            text='Rp 0',
            font_size='18sp',
            bold=True,
            size_hint_x=0.3,
            color=(0.8, 0.4, 0.2, 1),
            text_size=(None, None),
            halign='right'
        )
        expenses_card.add_widget(expenses_info)
        expenses_card.add_widget(self.expenses_amount)
        
        # Profit card
        profit_card = BoxLayout(orientation='horizontal', size_hint_y=None, height=80, padding=15, spacing=12)
        profit_info = BoxLayout(orientation='vertical', size_hint_x=0.7)
        profit_title = Label(
            text='KEUNTUNGAN HARI INI',
            font_size='14sp',
            bold=True,
            size_hint_y=None,
            height=25,
            color=(0.2, 0.6, 0.8, 1),
            text_size=(None, None),
            halign='left'
        )
        profit_subtitle = Label(
            text='Penjualan - Pengeluaran',
            font_size='10sp',
            size_hint_y=None,
            height=20,
            color=(0.5, 0.5, 0.5, 1),
            text_size=(None, None),
            halign='left'
        )
        profit_info.add_widget(profit_title)
        profit_info.add_widget(profit_subtitle)
        
        self.profit_amount = Label(
            text='Rp 0',
            font_size='18sp',
            bold=True,
            size_hint_x=0.3,
            color=(0.2, 0.6, 0.8, 1),
            text_size=(None, None),
            halign='right'
        )
        profit_card.add_widget(profit_info)
        profit_card.add_widget(self.profit_amount)
        
        summary_layout.add_widget(sales_card)
        summary_layout.add_widget(expenses_card)
        summary_layout.add_widget(profit_card)
        
        # Transaction counter with better spacing
        counter_container = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, padding=15)
        counter_label_text = Label(
            text='Nomor Transaksi Selanjutnya:',
            font_size='12sp',
            size_hint_x=0.7,
            text_size=(None, None),
            halign='left',
            color=(0.4, 0.4, 0.4, 1)
        )
        self.counter_label = Label(
            text='#1',
            font_size='16sp',
            bold=True,
            size_hint_x=0.3,
            color=(0.2, 0.6, 0.8, 1),
            text_size=(None, None),
            halign='right'
        )
        counter_container.add_widget(counter_label_text)
        counter_container.add_widget(self.counter_label)
        summary_layout.add_widget(counter_container)
        
        # Reset button with better spacing
        reset_container = BoxLayout(size_hint_y=None, height=80, padding=15)
        reset_btn = Button(
            text='RESET LAPORAN HARIAN',
            background_color=(0.9, 0.2, 0.2, 1),
            font_size='14sp',
            bold=True
        )
        reset_btn.bind(on_press=self.show_reset_confirmation)
        reset_container.add_widget(reset_btn)
        summary_layout.add_widget(reset_container)
        
        # Add to scroll and main layout
        summary_scroll.add_widget(summary_layout)
        layout.add_widget(summary_scroll)
        
        self.add_widget(layout)
    
    def refresh_reports(self):
        if not self.app_ref:
            return
        
        # Calculate today's totals (simplified - in real app would filter by date)
        total_sales = self.app_ref.daily_sales
        total_expenses = sum(expense['amount'] if isinstance(expense, dict) else expense.amount for expense in self.app_ref.expenses)
        profit = total_sales - total_expenses
        
        self.sales_amount.text = self.app_ref.format_currency(total_sales)
        self.expenses_amount.text = self.app_ref.format_currency(total_expenses)
        self.profit_amount.text = self.app_ref.format_currency(profit)
        self.counter_label.text = f'#{self.app_ref.transaction_counter}'
    
    def show_reset_confirmation(self, instance):
        popup = ConfirmationPopup(
            "Reset Laporan",
            "Yakin ingin mereset semua data laporan harian?\nData penjualan dan pengeluaran akan dihapus.",
            confirm_callback=self.reset_daily_reports
        )
        popup.open()
    
    def reset_daily_reports(self):
        """Reset daily sales and expenses"""
        self.app_ref.daily_sales = 0
        self.app_ref.expenses.clear()
        self.app_ref.transaction_counter = 1
        
        # Save data
        self.app_ref.save_kasir_expenses()
        self.app_ref.save_kasir_counter()
        
        # Refresh display
        self.refresh_reports()

# Kasir Receipt Screen
class KasirReceiptScreen(Screen):
    """Screen for displaying receipt"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = None
        self.receipt_data = None
        self.build_ui()
    
    def on_enter(self):
        self.app_ref = App.get_running_app()
        if self.receipt_data:
            self.display_receipt()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=['5dp', '10dp', '5dp', '10dp'], spacing='8dp')
        
        # Header with responsive sizing
        header = BoxLayout(size_hint_y=None, height='50dp')
        back_btn = Button(
            text='Kembali',
            size_hint_x=0.25,
            background_color=(0.6, 0.6, 0.6, 1),
            font_size='12sp'
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'kasir_main'))
        header.add_widget(back_btn)
        
        title_label = Label(
            text='STRUK PEMBAYARAN',
            font_size='16sp',
            bold=True,
            text_size=(None, None),
            halign='center',
            valign='middle'
        )
        header.add_widget(title_label)
        layout.add_widget(header)
        
        # Receipt content with responsive sizing
        self.receipt_scroll = ScrollView()
        self.receipt_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing='3dp', padding=['8dp', '5dp', '8dp', '5dp'])
        self.receipt_layout.bind(minimum_height=self.receipt_layout.setter('height'))
        self.receipt_scroll.add_widget(self.receipt_layout)
        layout.add_widget(self.receipt_scroll)
        
        # Print button with responsive sizing
        print_btn = Button(
            text='CETAK STRUK',
            size_hint_y=None,
            height='40dp',
            background_color=(0.2, 0.6, 0.8, 1),
            font_size='12sp',
            bold=True
        )
        print_btn.bind(on_press=self.print_receipt)
        layout.add_widget(print_btn)
        
        self.add_widget(layout)
    
    def set_receipt_data(self, receipt_data):
        """Set receipt data to display"""
        self.receipt_data = receipt_data
        if self.app_ref:
            self.display_receipt()
    
    def display_receipt(self):
        if not self.receipt_data:
            return
        
        self.receipt_layout.clear_widgets()
        
        # Shop header
        shop_label = Label(
            text=self.app_ref.shop_name,
            font_size='16sp',
            bold=True,
            size_hint_y=None,
            height=30
        )
        self.receipt_layout.add_widget(shop_label)
        
        # Transaction info
        trans_info = Label(
            text=f"Transaksi #{self.receipt_data['transaction_id']}\n{self.receipt_data['date_time']}",
            font_size='12sp',
            size_hint_y=None,
            height=40,
            color=(0.4, 0.4, 0.4, 1)
        )
        self.receipt_layout.add_widget(trans_info)
        
        # Separator
        separator1 = Label(
            text='-' * 40,
            font_size='10sp',
            size_hint_y=None,
            height=20
        )
        self.receipt_layout.add_widget(separator1)
        
        # Items
        for item in self.receipt_data['items']:
            item_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
            
            item_info = Label(
                text=f"{item['name']}\n{item['weight']} kg × {self.app_ref.format_currency(item['price_per_kg'])}/kg",
                font_size='10sp',
                size_hint_x=0.7,
                text_size=(None, None),
                halign='left'
            )
            
            item_total = Label(
                text=self.app_ref.format_currency(item['total']),
                font_size='10sp',
                size_hint_x=0.3,
                text_size=(None, None),
                halign='right'
            )
            
            item_layout.add_widget(item_info)
            item_layout.add_widget(item_total)
            self.receipt_layout.add_widget(item_layout)
        
        # Separator
        separator2 = Label(
            text='-' * 40,
            font_size='10sp',
            size_hint_y=None,
            height=20
        )
        self.receipt_layout.add_widget(separator2)
        
        # Total
        total_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        total_label = Label(
            text='TOTAL:',
            font_size='14sp',
            bold=True,
            size_hint_x=0.7
        )
        total_amount = Label(
            text=self.app_ref.format_currency(self.receipt_data['total']),
            font_size='14sp',
            bold=True,
            size_hint_x=0.3,
            color=(0.1, 0.6, 0.1, 1)
        )
        total_layout.add_widget(total_label)
        total_layout.add_widget(total_amount)
        self.receipt_layout.add_widget(total_layout)
        
        # Payment info
        payment_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        payment_label = Label(
            text='Bayar:',
            font_size='12sp',
            size_hint_x=0.7
        )
        payment_amount = Label(
            text=self.app_ref.format_currency(self.receipt_data['payment']),
            font_size='12sp',
            size_hint_x=0.3
        )
        payment_layout.add_widget(payment_label)
        payment_layout.add_widget(payment_amount)
        self.receipt_layout.add_widget(payment_layout)
        
        # Change
        change_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        change_label = Label(
            text='Kembalian:',
            font_size='12sp',
            size_hint_x=0.7
        )
        change_amount = Label(
            text=self.app_ref.format_currency(self.receipt_data['change']),
            font_size='12sp',
            size_hint_x=0.3,
            color=(0.2, 0.6, 0.8, 1)
        )
        change_layout.add_widget(change_label)
        change_layout.add_widget(change_amount)
        self.receipt_layout.add_widget(change_layout)
        
        # Thank you message
        thanks_label = Label(
            text='\nTerima kasih atas kunjungan Anda!',
            font_size='12sp',
            size_hint_y=None,
            height=40,
            italic=True
        )
        self.receipt_layout.add_widget(thanks_label)
    
    def print_receipt(self, instance):
        # Placeholder for print functionality
        self.app_ref.show_popup("Info", "Fitur cetak struk akan segera ditambahkan")

# Kasir Popup Classes
class AddProductPopup(Popup):
    """Popup for adding new products"""
    def __init__(self, callback=None, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.title = 'Tambah Produk Baru'
        self.size_hint = (0.9, 0.7)
        self.build_content()
    
    def build_content(self):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Product name
        name_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        name_layout.add_widget(Label(text='Nama Produk:', size_hint_x=0.3, font_size='12sp'))
        self.name_input = TextInput(
            multiline=False,
            size_hint_x=0.7,
            font_size='12sp'
        )
        name_layout.add_widget(self.name_input)
        layout.add_widget(name_layout)
        
        # Price per kg
        price_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        price_layout.add_widget(Label(text='Harga/kg:', size_hint_x=0.3, font_size='12sp'))
        self.price_input = TextInput(
            multiline=False,
            size_hint_x=0.7,
            input_filter='int',
            font_size='12sp'
        )
        price_layout.add_widget(self.price_input)
        layout.add_widget(price_layout)
        
        # Stock
        stock_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        stock_layout.add_widget(Label(text='Stok (kg):', size_hint_x=0.3, font_size='12sp'))
        self.stock_input = TextInput(
            multiline=False,
            size_hint_x=0.7,
            input_filter='float',
            text='100',
            font_size='12sp'
        )
        stock_layout.add_widget(self.stock_input)
        layout.add_widget(stock_layout)
        
        # Buttons
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        cancel_btn = Button(
            text='Batal',
            background_color=(0.6, 0.6, 0.6, 1),
            font_size='12sp'
        )
        cancel_btn.bind(on_press=self.dismiss)
        
        save_btn = Button(
            text='Simpan',
            background_color=(0.2, 0.8, 0.2, 1),
            font_size='12sp'
        )
        save_btn.bind(on_press=self.save_product)
        
        buttons_layout.add_widget(cancel_btn)
        buttons_layout.add_widget(save_btn)
        layout.add_widget(buttons_layout)
        
        self.content = layout
    
    def save_product(self, instance):
        name = self.name_input.text.strip()
        price_text = self.price_input.text.strip()
        stock_text = self.stock_input.text.strip()
        
        if not name:
            sound_manager.error_feedback()
            return
        
        try:
            price = int(price_text)
            stock = float(stock_text)
            
            if price <= 0 or stock < 0:
                sound_manager.error_feedback()
                return
            
            if self.callback:
                self.callback(name, price, stock)
            
            sound_manager.success_feedback()
            self.dismiss()
            
        except ValueError:
            sound_manager.error_feedback()

class WeightInputPopup(Popup):
    """Popup for inputting product weight"""
    def __init__(self, product, callback=None, **kwargs):
        super().__init__(**kwargs)
        self.product = product
        self.callback = callback
        self.title = f'Input Berat - {product.name}'
        self.size_hint = (0.8, 0.5)
        self.build_content()
    
    def build_content(self):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Product info
        info_label = Label(
            text=f'{self.product.name}\n{App.get_running_app().format_currency(self.product.price_per_kg)}/kg\nStok: {self.product.stock_kg} kg',
            font_size='12sp',
            size_hint_y=None,
            height=60,
            color=(0.4, 0.4, 0.4, 1)
        )
        layout.add_widget(info_label)
        
        # Weight input
        weight_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        weight_layout.add_widget(Label(text='Berat (kg):', size_hint_x=0.4, font_size='12sp'))
        self.weight_input = TextInput(
            multiline=False,
            size_hint_x=0.6,
            input_filter='float',
            text='1',
            font_size='12sp'
        )
        weight_layout.add_widget(self.weight_input)
        layout.add_widget(weight_layout)
        
        # Total preview
        self.total_label = Label(
            text='Total: Rp 0',
            font_size='14sp',
            bold=True,
            size_hint_y=None,
            height=30,
            color=(0.1, 0.6, 0.1, 1)
        )
        layout.add_widget(self.total_label)
        
        # Update total when weight changes
        self.weight_input.bind(text=self.update_total)
        self.update_total()
        
        # Buttons
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        cancel_btn = Button(
            text='Batal',
            background_color=(0.6, 0.6, 0.6, 1),
            font_size='12sp'
        )
        cancel_btn.bind(on_press=self.dismiss)
        
        add_btn = Button(
            text='Tambah ke Keranjang',
            background_color=(0.1, 0.7, 0.3, 1),
            font_size='12sp'
        )
        add_btn.bind(on_press=self.add_to_cart)
        
        buttons_layout.add_widget(cancel_btn)
        buttons_layout.add_widget(add_btn)
        layout.add_widget(buttons_layout)
        
        self.content = layout
    
    def update_total(self, instance=None, text=None):
        try:
            weight = float(self.weight_input.text or '0')
            total = weight * self.product.price_per_kg
            self.total_label.text = f'Total: {App.get_running_app().format_currency(total)}'
        except ValueError:
            self.total_label.text = 'Total: Rp 0'
    
    def add_to_cart(self, instance):
        try:
            weight = float(self.weight_input.text or '0')
            
            if weight <= 0:
                sound_manager.error_feedback()
                return
            
            if weight > self.product.stock_kg:
                sound_manager.error_feedback()
                return
            
            if self.callback:
                self.callback(self.product, weight)
            
            sound_manager.success_feedback()
            self.dismiss()
            
        except ValueError:
            sound_manager.error_feedback()

class PaymentPopup(Popup):
    """Popup for payment processing"""
    def __init__(self, total_amount, cart_items, callback=None, **kwargs):
        super().__init__(**kwargs)
        self.total_amount = total_amount
        self.cart_items = cart_items
        self.callback = callback
        self.title = 'Pembayaran'
        self.size_hint = (0.9, 0.8)
        self.build_content()
    
    def build_content(self):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Order summary
        summary_label = Label(
            text='RINGKASAN PESANAN',
            font_size='14sp',
            bold=True,
            size_hint_y=None,
            height=30,
            color=(0.2, 0.6, 0.8, 1)
        )
        layout.add_widget(summary_label)
        
        # Items list
        items_scroll = ScrollView(size_hint_y=0.4)
        items_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=3)
        items_layout.bind(minimum_height=items_layout.setter('height'))
        
        for item in self.cart_items:
            item_widget = BoxLayout(orientation='horizontal', size_hint_y=None, height=25)
            
            item_info = Label(
                text=f'{item.product.name} - {item.weight_kg} kg',
                font_size='10sp',
                size_hint_x=0.7,
                text_size=(None, None),
                halign='left'
            )
            
            item_total = Label(
                text=App.get_running_app().format_currency(item.get_total()),
                font_size='10sp',
                size_hint_x=0.3,
                text_size=(None, None),
                halign='right'
            )
            
            item_widget.add_widget(item_info)
            item_widget.add_widget(item_total)
            items_layout.add_widget(item_widget)
        
        items_scroll.add_widget(items_layout)
        layout.add_widget(items_scroll)
        
        # Total
        total_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        total_layout.add_widget(Label(text='TOTAL:', font_size='16sp', bold=True, size_hint_x=0.7))
        total_layout.add_widget(Label(
            text=App.get_running_app().format_currency(self.total_amount),
            font_size='16sp',
            bold=True,
            size_hint_x=0.3,
            color=(0.1, 0.6, 0.1, 1)
        ))
        layout.add_widget(total_layout)
        
        # Payment input
        payment_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        payment_layout.add_widget(Label(text='Bayar:', size_hint_x=0.3, font_size='12sp'))
        self.payment_input = TextInput(
            multiline=False,
            size_hint_x=0.7,
            input_filter='int',
            font_size='12sp'
        )
        payment_layout.add_widget(self.payment_input)
        layout.add_widget(payment_layout)
        
        # Change preview
        self.change_label = Label(
            text='Kembalian: Rp 0',
            font_size='14sp',
            bold=True,
            size_hint_y=None,
            height=30,
            color=(0.2, 0.6, 0.8, 1)
        )
        layout.add_widget(self.change_label)
        
        # Update change when payment changes
        self.payment_input.bind(text=self.update_change)
        
        # Quick payment buttons
        quick_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        
        amounts = [50000, 100000, 200000]
        for amount in amounts:
            btn = Button(
                text=f'{amount//1000}k',
                background_color=(0.2, 0.6, 0.8, 1),
                font_size='10sp'
            )
            btn.bind(on_press=lambda x, amt=amount: setattr(self.payment_input, 'text', str(amt)))
            quick_layout.add_widget(btn)
        
        exact_btn = Button(
            text='Pas',
            background_color=(0.8, 0.6, 0.2, 1),
            font_size='10sp'
        )
        exact_btn.bind(on_press=lambda x: setattr(self.payment_input, 'text', str(int(self.total_amount))))
        quick_layout.add_widget(exact_btn)
        
        layout.add_widget(quick_layout)
        
        # Buttons
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        cancel_btn = Button(
            text='Batal',
            background_color=(0.6, 0.6, 0.6, 1),
            font_size='12sp'
        )
        cancel_btn.bind(on_press=self.dismiss)
        
        process_btn = Button(
            text='Proses Pembayaran',
            background_color=(0.1, 0.7, 0.3, 1),
            font_size='12sp'
        )
        process_btn.bind(on_press=self.process_payment)
        
        buttons_layout.add_widget(cancel_btn)
        buttons_layout.add_widget(process_btn)
        layout.add_widget(buttons_layout)
        
        self.content = layout
    
    def update_change(self, instance=None, text=None):
        try:
            payment = int(self.payment_input.text or '0')
            change = payment - self.total_amount
            
            if change >= 0:
                self.change_label.text = f'Kembalian: {App.get_running_app().format_currency(change)}'
                self.change_label.color = (0.2, 0.6, 0.8, 1)
            else:
                self.change_label.text = f'Kurang: {App.get_running_app().format_currency(abs(change))}'
                self.change_label.color = (0.9, 0.2, 0.2, 1)
        except ValueError:
            self.change_label.text = 'Kembalian: Rp 0'
            self.change_label.color = (0.2, 0.6, 0.8, 1)
    
    def process_payment(self, instance):
        try:
            payment = int(self.payment_input.text or '0')
            
            if payment < self.total_amount:
                sound_manager.error_feedback()
                return
            
            change = payment - self.total_amount
            
            if self.callback:
                self.callback(payment, change)
            
            sound_manager.success_feedback()
            self.dismiss()
            
        except ValueError:
            sound_manager.error_feedback()

class AddExpensePopup(Popup):
    """Popup for adding expenses"""
    def __init__(self, callback, **kwargs):
        super(AddExpensePopup, self).__init__(**kwargs)
        self.title = 'TAMBAH PENGELUARAN BARU'
        self.title_size = '16sp'
        self.title_color = (0.2, 0.6, 0.8, 1)
        self.title_align = 'center'
        self.size_hint = (0.9, 0.7)
        self.background = 'atlas://data/images/defaulttheme/button_pressed'
        self.separator_color = (0.8, 0.8, 0.8, 1)
        self.callback = callback
        
        # Main layout with better spacing
        layout = BoxLayout(orientation='vertical', padding='15dp', spacing='15dp')
        
        # Scroll view for the form
        scroll = ScrollView(bar_width='6dp', bar_color=(0.5, 0.5, 0.5, 0.5))
        form_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing='12dp')
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        # Nama Pengeluaran with better styling
        name_layout = BoxLayout(orientation='vertical', size_hint_y=None, height='90dp')
        name_label = Label(
            text='NAMA PENGELUARAN:', 
            size_hint_y=None, 
            height='30dp', 
            font_size='14sp',
            bold=True,
            color=(0.3, 0.3, 0.3, 1)
        )
        self.name_input = TextInput(
            multiline=False, 
            size_hint_y=None, 
            height='50dp', 
            font_size='16sp',
            padding='10dp',
            background_normal='atlas://data/images/defaulttheme/textinput',
            background_active='atlas://data/images/defaulttheme/textinput_active',
            foreground_color=(0.1, 0.1, 0.1, 1),
            cursor_color=(0.2, 0.6, 0.8, 1),
            cursor_width='2sp'
        )
        name_layout.add_widget(name_label)
        name_layout.add_widget(self.name_input)
        
        # Jumlah with better styling
        amount_layout = BoxLayout(orientation='vertical', size_hint_y=None, height='90dp')
        amount_label = Label(
            text='JUMLAH (Rp):', 
            size_hint_y=None, 
            height='30dp', 
            font_size='14sp',
            bold=True,
            color=(0.3, 0.3, 0.3, 1)
        )
        self.amount_input = TextInput(
            multiline=False, 
            size_hint_y=None, 
            height='50dp', 
            font_size='16sp',
            input_type='number', 
            input_filter='float',
            padding='10dp',
            background_normal='atlas://data/images/defaulttheme/textinput',
            background_active='atlas://data/images/defaulttheme/textinput_active',
            foreground_color=(0.1, 0.1, 0.1, 1),
            cursor_color=(0.2, 0.6, 0.8, 1),
            cursor_width='2sp',
            halign='right'
        )
        amount_layout.add_widget(amount_label)
        amount_layout.add_widget(self.amount_input)
        
        # Keterangan with better styling
        note_layout = BoxLayout(orientation='vertical', size_hint_y=None, height='140dp')
        note_label = Label(
            text='KETERANGAN (OPSIONAL):', 
            size_hint_y=None, 
            height='30dp', 
            font_size='14sp',
            bold=True,
            color=(0.3, 0.3, 0.3, 1)
        )
        self.note_input = TextInput(
            multiline=True, 
            size_hint_y=None, 
            height='100dp', 
            font_size='14sp',
            padding='10dp',
            background_normal='atlas://data/images/defaulttheme/textinput',
            background_active='atlas://data/images/defaulttheme/textinput_active',
            foreground_color=(0.1, 0.1, 0.1, 1),
            cursor_color=(0.2, 0.6, 0.8, 1),
            cursor_width='2sp'
        )
        note_layout.add_widget(note_label)
        note_layout.add_widget(self.note_input)
        
        # Add all input fields to form
        form_layout.add_widget(name_layout)
        form_layout.add_widget(amount_layout)
        form_layout.add_widget(note_layout)
        
        # Add form to scroll view
        scroll.add_widget(form_layout)
        layout.add_widget(scroll)
        
        # Tombol with better styling
        btn_layout = BoxLayout(size_hint_y=None, height='60dp', spacing='10dp', padding=('10dp', 0, '10dp', 0))
        
        cancel_btn = Button(
            text='BATAL', 
            background_color=(0.8, 0.2, 0.2, 1),
            background_normal='',
            color=(1, 1, 1, 1),
            font_size='14sp',
            bold=True,
            size_hint_x=0.4
        )
        
        submit_btn = Button(
            text='SIMPAN', 
            background_color=(0.2, 0.8, 0.2, 1),
            background_normal='',
            color=(1, 1, 1, 1),
            font_size='14sp',
            bold=True,
            size_hint_x=0.6
        )
        
        cancel_btn.bind(on_press=self.dismiss)
        submit_btn.bind(on_press=self.submit)
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(submit_btn)
        
        layout.add_widget(btn_layout)
        self.content = layout
        
        # Set focus to name input when popup opens
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        
    def _keyboard_closed(self):
        if hasattr(self, '_keyboard'):
            self._keyboard.unbind(on_key_down=self._on_keyboard_down)
            self._keyboard = None
    
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        # Handle Enter key to move between fields or submit
        if keycode[1] == 'enter' or keycode[1] == 'numpadenter':
            if self.name_input.focus:
                self.amount_input.focus = True
            elif self.amount_input.focus:
                self.note_input.focus = True
            elif self.note_input.focus:
                self.submit(None)
            return True
        return False
        
    def submit(self, instance):
        name = self.name_input.text.strip()
        amount = self.amount_input.text.strip()
        note = self.note_input.text.strip()
        
        if not name or not amount:
            show_error_popup('Nama dan jumlah harus diisi', title='Kesalahan Input')
            return
            
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError('Jumlah harus lebih dari 0')
                
            self.callback(name, amount, note)
            sound_manager.success_feedback()
            self.dismiss()
            
        except ValueError:
            show_error_popup('Jumlah harus berupa angka yang valid', title='Format Tidak Valid')

class ConfirmationPopup(Popup):
    """Generic confirmation popup with improved styling"""
    def __init__(self, title_text, message, confirm_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.confirm_callback = confirm_callback
        self.title = title_text.upper()
        self.title_size = '16sp'
        self.title_color = (0.2, 0.6, 0.8, 1)
        self.title_align = 'center'
        self.size_hint = (0.85, 0.5)
        self.background = 'atlas://data/images/defaulttheme/button_pressed'
        self.separator_color = (0.8, 0.8, 0.8, 1)
        self.auto_dismiss = False
        self.build_content(message)
    
    def build_content(self, message):
        # Main layout
        layout = BoxLayout(orientation='vertical', padding='20dp', spacing='20dp')
        
        # Message with better styling
        message_label = Label(
            text=message,
            text_size=(None, None),
            halign='center',
            valign='middle',
            size_hint_y=0.7,
            font_size='15sp',
            color=(0.2, 0.2, 0.2, 1),
            padding=('10dp', '10dp')
        )
        
        # Buttons with better styling
        btn_layout = BoxLayout(
            size_hint_y=0.3, 
            spacing='15dp',
            padding=('10dp', 0, '10dp', 0)
        )
        
        cancel_btn = Button(
            text='BATAL',
            background_color=(0.8, 0.2, 0.2, 1),
            background_normal='',
            color=(1, 1, 1, 1),
            font_size='14sp',
            bold=True,
            size_hint_x=0.4
        )
        
        confirm_btn = Button(
            text='YA',
            background_color=(0.2, 0.8, 0.2, 1),
            background_normal='',
            color=(1, 1, 1, 1),
            font_size='14sp',
            bold=True,
            size_hint_x=0.6
        )
        
        # Bind buttons
        cancel_btn.bind(on_press=self.dismiss)
        confirm_btn.bind(on_release=self.confirm)
        
        # Add buttons to layout
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(confirm_btn)
        
        # Add all widgets to main layout
        layout.add_widget(message_label)
        layout.add_widget(btn_layout)
        
        self.content = layout
        
        # Set focus to confirm button by default
        confirm_btn.focus = True
    
    def confirm(self, instance):
        sound_manager.success_feedback()
        if self.confirm_callback:
            self.confirm_callback()
        self.dismiss()

if __name__ == '__main__':
    MyApp().run()
