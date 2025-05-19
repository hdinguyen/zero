import os
from typing import Any, Dict, List, Optional, Tuple, Union, cast

from requests import post
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

from conf import config
from memory.conversation import Conversation

Base = declarative_base()

class Database:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        supabase = config['supabase']

        # Fetch variables
        USER = supabase['user']
        PASSWORD = supabase['password']
        HOST = supabase['host']
        PORT = supabase['port']
        DBNAME = supabase['dbname']

        self.DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"
        
        self.engine = create_engine(self.DATABASE_URL)
        self.session = sessionmaker(bind=self.engine)()
        try:
            with self.engine.connect() as connection:
                print("Connection successful!")
        except Exception as e:
            print(f"Failed to connect: {e}")
            
        self._initialized = True
    
    def get_connection(self) -> Connection:
        """Get a connection from the engine."""
        return self.engine.connect()
    
    def query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a query and return the results."""
        try:
            with self.get_connection() as conn:
                result = conn.execute(text(sql), params or {})
                return [dict(row) for row in result]
        except SQLAlchemyError as e:
            print(f"Query error: {e}")
            return []
        
    def retrieve_similar_conversations(self, embedding: list[float], top_n=5):
        # Use SQL function to cast array to vector
        vector_embedding = func.vector(embedding)
        
        # Query with proper vector casting
        top_n_results = self.session.query(Conversation).order_by(
            Conversation.embedding.op('<->')(vector_embedding)
        ).limit(top_n).all()

        # Convert result to list of dictionaries
        conversations = [
            {
                "id": row.id,
                "created_at": row.created_at,
                "question": row.question,
                "answer": row.answer,
                "summary": row.summary,
                "title": row.title,

            }
            for row in top_n_results
        ]

        return conversations
        
    def add_row(self, row: Any) -> Optional[int]:
        """Insert a new record and return its ID."""
        if not row:
            return None

        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return cast(int, row.id)
    
    def add(self, table: str, data: Dict[str, Any]) -> Optional[int]:
        """Insert a new record and return its ID."""
        if not data:
            return None
            
        columns = ', '.join(data.keys())
        placeholders = ', '.join(f":{k}" for k in data.keys())
        
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING id"
        
        try:
            with self.get_connection() as conn:
                result = conn.execute(text(sql), data)
                conn.commit()
                row = result.fetchone()
                return row[0] if row else None
        except SQLAlchemyError as e:
            print(f"Add error: {e}")
            return None
    
    def update(self, table: str, id_value: int, data: Dict[str, Any]) -> bool:
        """Update a record by ID."""
        if not data:
            return False
            
        set_clause = ', '.join(f"{k} = :{k}" for k in data.keys())
        sql = f"UPDATE {table} SET {set_clause} WHERE id = :id"
        
        params = {**data, 'id': id_value}
        
        try:
            with self.get_connection() as conn:
                result = conn.execute(text(sql), params)
                conn.commit()
                return result.rowcount > 0
        except SQLAlchemyError as e:
            print(f"Update error: {e}")
            return False
    
    def close(self):
        self.engine.dispose()

# Create a singleton instance
db = Database()

def embed_text(text: str) -> list[float]:
    response = post(
        config["embeddings"]["url"],
        headers={"x-api-key": config['embeddings']['api_key']},
        json={"text": text}
    )
    return response.json()["embedding"]