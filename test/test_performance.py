import time
import sys
import os
from modules.database_manager import DatabaseManagerSS14

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_import_performance():
    """Test that imports don't take too long"""
    start_time = time.time()
    
    from bot_init import bot, cfg, ss14_db
    from modules.database_manager import DatabaseManagerSS14
    
    end_time = time.time()
    import_time = end_time - start_time
    
    print(f"Import time: {import_time:.3f} seconds")
    assert import_time < 5.0, "Imports took too long"

def test_database_manager_creation():
    """Test performance of database manager creation"""
    start_time = time.time()
    
    test_config = {
        'main': {
            'database': 'test_db',
            'user': 'test_user',
            'password': 'test_pass', 
            'host': 'localhost',
            'port': '5432'
        }
    }
    
    for i in range(100):
        db_manager = DatabaseManagerSS14(test_config)
    
    end_time = time.time()
    creation_time = end_time - start_time
    
    print(f"Created 100 DatabaseManager instances in {creation_time:.3f} seconds")
    assert creation_time < 1.0, "Database manager creation too slow"
