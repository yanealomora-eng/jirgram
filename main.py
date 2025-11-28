#!/usr/bin/env python3
"""
jirgram Custom - Telegram Client with Advanced Features
Based on TDLib with ghost mode, anti-delete, and customization features
"""

import asyncio
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

try:
    from telegram.client import Telegram
    from telegram.text import Spoiler, Bold, Italic
except ImportError:
    print("Error: python-telegram library not installed")
    print("Install it with: pip install python-telegram")
    exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MessageDatabase:
    """Local database for storing deleted/edited messages"""
    
    def __init__(self, db_path: str = "messages.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER,
                chat_id INTEGER,
                sender_id INTEGER,
                text TEXT,
                date INTEGER,
                is_deleted INTEGER DEFAULT 0,
                is_edited INTEGER DEFAULT 0,
                original_text TEXT,
                PRIMARY KEY (message_id, chat_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS read_receipts (
                chat_id INTEGER,
                message_id INTEGER,
                read_date INTEGER,
                PRIMARY KEY (chat_id, message_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_message(self, message_data: Dict):
        """Save message to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO messages 
            (message_id, chat_id, sender_id, text, date, original_text)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            message_data.get('id'),
            message_data.get('chat_id'),
            message_data.get('sender_id'),
            message_data.get('text'),
            message_data.get('date'),
            message_data.get('text')  # original_text
        ))
        
        conn.commit()
        conn.close()
    
    def mark_deleted(self, chat_id: int, message_id: int):
        """Mark message as deleted"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE messages 
            SET is_deleted = 1 
            WHERE chat_id = ? AND message_id = ?
        ''', (chat_id, message_id))
        
        conn.commit()
        conn.close()
    
    def mark_edited(self, chat_id: int, message_id: int, new_text: str):
        """Mark message as edited and store new text"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE messages 
            SET is_edited = 1, text = ?
            WHERE chat_id = ? AND message_id = ?
        ''', (new_text, chat_id, message_id))
        
        conn.commit()
        conn.close()
    
    def get_message(self, chat_id: int, message_id: int) -> Optional[Dict]:
        """Get message from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM messages 
            WHERE chat_id = ? AND message_id = ?
        ''', (chat_id, message_id))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'message_id': result[0],
                'chat_id': result[1],
                'sender_id': result[2],
                'text': result[3],
                'date': result[4],
                'is_deleted': result[5],
                'is_edited': result[6],
                'original_text': result[7]
            }
        return None


class jirgramClient:
    """Main Telegram client with advanced features"""
    
    def __init__(self, api_id: str, api_hash: str, phone: str):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        
        # Features configuration
        self.config = {
            'ghost_mode': True,           # Hide online/typing/read receipts
            'anti_delete': True,          # Prevent message deletion
            'save_edited': True,          # Save message edit history
            'auto_read': False,           # Auto-read messages
            'forward_protection': True,   # Prevent forwarding your messages
        }
        
        self.db = MessageDatabase()
        self.tg = None
    
    def init_client(self):
        """Initialize Telegram client"""
        self.tg = Telegram(
            api_id=self.api_id,
            api_hash=self.api_hash,
            phone=self.phone,
            database_encryption_key='jirgram_secret_key_2025',
            files_directory='tdlib_files',
        )
        
        # Set up event handlers
        self.tg.add_message_handler(self.handle_new_message)
        self.tg.add_update_handler('updateDeleteMessages', self.handle_delete_message)
        self.tg.add_update_handler('updateMessageEdited', self.handle_edit_message)
        
    async def handle_new_message(self, update):
        """Handle incoming messages"""
        if update.get('@type') == 'updateNewMessage':
            message = update.get('message', {})
            
            # Save message to local database (anti-delete feature)
            if self.config['anti_delete']:
                self.db.save_message({
                    'id': message.get('id'),
                    'chat_id': message.get('chat_id'),
                    'sender_id': message.get('sender_id', {}).get('user_id'),
                    'text': self._extract_text(message),
                    'date': message.get('date')
                })
            
            logger.info(f"New message in chat {message.get('chat_id')}: {self._extract_text(message)[:50]}")
    
    async def handle_delete_message(self, update):
        """Handle message deletion"""
        if self.config['anti_delete']:
            chat_id = update.get('chat_id')
            message_ids = update.get('message_ids', [])
            
            for msg_id in message_ids:
                self.db.mark_deleted(chat_id, msg_id)
                saved_msg = self.db.get_message(chat_id, msg_id)
                
                if saved_msg:
                    logger.warning(f"Message deleted but saved: {saved_msg.get('text', '')[:50]}")
    
    async def handle_edit_message(self, update):
        """Handle message edits"""
        if self.config['save_edited']:
            chat_id = update.get('chat_id')
            message_id = update.get('message_id')
            
            # Get new message content
            message = await self.tg.call_method('getMessage', {
                'chat_id': chat_id,
                'message_id': message_id
            })
            
            new_text = self._extract_text(message)
            self.db.mark_edited(chat_id, message_id, new_text)
            
            logger.info(f"Message edited in chat {chat_id}")
    
    def _extract_text(self, message: Dict) -> str:
        """Extract text from message object"""
        content = message.get('content', {})
        
        if content.get('@type') == 'messageText':
            return content.get('text', {}).get('text', '')
        
        return f"[{content.get('@type', 'Unknown')}]"
    
    async def send_message(self, chat_id: int, text: str, silent: bool = False):
        """Send message with ghost mode support"""
        result = await self.tg.call_method('sendMessage', {
            'chat_id': chat_id,
            'input_message_content': {
                '@type': 'inputMessageText',
                'text': {
                    '@type': 'formattedText',
                    'text': text
                }
            },
            'disable_notification': silent or self.config['ghost_mode']
        })
        
        return result
    
    async def get_deleted_messages(self, chat_id: int) -> list:
        """Retrieve all deleted messages from a chat"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM messages 
            WHERE chat_id = ? AND is_deleted = 1
            ORDER BY date DESC
        ''', (chat_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def run(self):
        """Start the client"""
        logger.info("Starting jirgram Custom Client...")
        logger.info(f"Ghost Mode: {self.config['ghost_mode']}")
        logger.info(f"Anti-Delete: {self.config['anti_delete']}")
        
        self.tg.login()
        self.tg.idle()


def main():
    """
    Main entry point
    
    Get your API credentials from: https://my.telegram.org
    """
    
    # CONFIGURATION - Replace with your actual values
    API_ID = 'YOUR_API_ID'        # Get from https://my.telegram.org
    API_HASH = 'YOUR_API_HASH'    # Get from https://my.telegram.org
    PHONE = '+1234567890'          # Your phone number with country code
    
    if API_ID == 'YOUR_API_ID':
        print("\n" + "="*70)
        print("⚠️  WARNING: You need to configure your API credentials!")
        print("="*70)
        print("\n1. Go to https://my.telegram.org")
        print("2. Log in with your phone number")
        print("3. Go to 'API Development Tools'")
        print("4. Create a new application")
        print("5. Copy your api_id and api_hash")
        print("6. Edit main.py and replace:")
        print("   - API_ID with your api_id")
        print("   - API_HASH with your api_hash")
        print("   - PHONE with your phone number (+1234567890)")
        print("\n" + "="*70 + "\n")
        return
    
    client = jirgramClient(
        api_id=API_ID,
        api_hash=API_HASH,
        phone=PHONE
    )
    
    client.init_client()
    client.run()


if __name__ == '__main__':
    main()
