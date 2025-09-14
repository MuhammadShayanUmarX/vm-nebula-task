import sqlite3
import os
from typing import Dict, List

class DatabaseManager:
    """Simple database manager for storing chat sessions"""
    
    def __init__(self):
        self.db_path = "sessions.db"
        self.setup_database()
    
    def setup_database(self):
        """Create database and table if they don't exist"""
        # Delete old database if it exists (to fix schema issues)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            print("Old database removed")
        
        # Create new database with correct structure
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create sessions table
        cursor.execute('''
            CREATE TABLE sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                agent_used TEXT NOT NULL,
                model TEXT NOT NULL,
                confidence REAL NOT NULL,
                processing_time REAL NOT NULL,
                token_count INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Database created successfully")
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def save_session(self, session_id: str, query: str, response_data: Dict, agent: str, model: str) -> bool:
        """Save chat session to database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sessions 
                (session_id, query, response, agent_used, model, confidence, processing_time, token_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                query,
                response_data["response"],
                agent,
                model,
                response_data["confidence"],
                response_data["processing_time"],
                response_data["token_count"]
            ))
            
            conn.commit()
            conn.close()
            print(f"Session saved: {session_id}")
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def get_session_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get chat history for a specific session"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM sessions 
                WHERE session_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (session_id, limit))
            
            rows = cursor.fetchall()
            result = [dict(row) for row in rows]
            
            conn.close()
            return result
        except Exception as e:
            print(f"Error getting history: {e}")
            return []
    
    def get_recent_sessions(self, limit: int = 20) -> List[Dict]:
        """Get recent chat sessions"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT DISTINCT session_id, MAX(timestamp) as last_activity, 
                       COUNT(*) as message_count
                FROM sessions 
                GROUP BY session_id 
                ORDER BY last_activity DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            result = [dict(row) for row in rows]
            
            conn.close()
            return result
        except Exception as e:
            print(f"Error getting recent sessions: {e}")
            return []
    
    def get_model_stats(self) -> Dict:
        """Get usage statistics for different models"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT model, 
                       COUNT(*) as usage_count,
                       AVG(processing_time) as avg_processing_time,
                       AVG(confidence) as avg_confidence,
                       SUM(token_count) as total_tokens
                FROM sessions 
                GROUP BY model
            ''')
            
            rows = cursor.fetchall()
            result = {row['model']: dict(row) for row in rows}
            
            conn.close()
            return result
        except Exception as e:
            print(f"Error getting model stats: {e}")
            return {}
    
    def get_agent_stats(self) -> Dict:
        """Get usage statistics for different agents"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT agent_used, 
                       COUNT(*) as usage_count,
                       AVG(processing_time) as avg_processing_time,
                       AVG(confidence) as avg_confidence
                FROM sessions 
                GROUP BY agent_used
            ''')
            
            rows = cursor.fetchall()
            result = {row['agent_used']: dict(row) for row in rows}
            
            conn.close()
            return result
        except Exception as e:
            print(f"Error getting agent stats: {e}")
            return {}
    
    def clear_all_sessions(self):
        """Delete all sessions from database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM sessions')
            conn.commit()
            conn.close()
            
            print("All sessions deleted")
            return True
        except Exception as e:
            print(f"Error clearing sessions: {e}")
            return False
    
    def count_sessions(self) -> int:
        """Count total sessions in database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM sessions')
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
        except Exception as e:
            print(f"Error counting sessions: {e}")
            return 0

# Create database manager instance
db_manager = DatabaseManager()

print(f"Database ready! Sessions will be stored in: {db_manager.db_path}")