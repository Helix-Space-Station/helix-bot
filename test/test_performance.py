import pytest
import time
import sys
import os

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.database_manager import DatabaseManagerSS14

def test_import_performance():
    """Test that imports don't take too long"""
    start_time = time.time()
    
    # Re-import to measure time
    import importlib
    import modules.database_manager
    importlib.reload(modules.database_manager)
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

def test_method_performance():
    """Test performance of database manager methods"""
    db_manager = DatabaseManagerSS14()
    
    # Test add_database performance
    start_time = time.time()
    for i in range(50):
        db_manager.add_database(f'db_{i}', f'database_{i}', 'user', 'pass', 'host', 5432)
    end_time = time.time()
    
    add_time = end_time - start_time
    print(f"Added 50 databases in {add_time:.3f} seconds")
    assert add_time < 0.5, "add_database method too slow"
