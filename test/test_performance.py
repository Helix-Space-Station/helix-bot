import asyncio
import os
import sys
import time

import pytest

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

def test_dict_operations_performance():
    """Test performance of dictionary operations (simulating database operations)"""
    db_manager = DatabaseManagerSS14()

    # Test dictionary operations performance (similar to what add_database might do)
    start_time = time.time()
    for i in range(1000):
        db_manager.databases[f'db_{i}'] = {
            'database': f'database_{i}',
            'user': 'user',
            'password': 'pass',
            'host': 'host',
            'port': 5432
        }
    end_time = time.time()

    dict_time = end_time - start_time
    print(f"Performed 1000 dictionary operations in {dict_time:.3f} seconds")
    assert dict_time < 0.1, "Dictionary operations too slow"

def test_connection_pool_initialization():
    """Test performance of connection pool initialization"""
    start_time = time.time()

    # Test creating multiple instances with different configs
    for i in range(50):
        config = {
            'main': {
                'database': f'test_db_{i}',
                'user': 'test_user',
                'password': 'test_pass', 
                'host': 'localhost',
                'port': '5432'
            }
        }
        db_manager = DatabaseManagerSS14(config)
        # Simulate some initialization work
        _ = db_manager.databases

    end_time = time.time()
    init_time = end_time - start_time

    print(f"Initialized 50 instances in {init_time:.3f} seconds")
    assert init_time < 2.0, "Connection pool initialization too slow"

@pytest.mark.asyncio
async def test_async_method_performance():
    """Test performance of async methods if they exist"""
    db_manager = DatabaseManagerSS14()

    # If there are async methods, test their performance
    start_time = time.time()

    # Simulate some async work (replace with actual async methods if they exist)
    async def mock_async_operation(i):
        await asyncio.sleep(0.001)  # Simulate async work
        return i

    tasks = [mock_async_operation(i) for i in range(100)]
    results = await asyncio.gather(*tasks)

    end_time = time.time()
    async_time = end_time - start_time

    print(f"Completed 100 async operations in {async_time:.3f} seconds")
    assert async_time < 0.5, "Async operations too slow"
    assert len(results) == 100, "Not all async operations completed"

def test_memory_usage():
    """Test that memory usage doesn't grow excessively"""
    import gc
    import os

    import psutil

    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB

    # Create many instances
    instances = []
    for i in range(100):
        config = {
            'main': {
                'database': f'test_db_{i}',
                'user': 'test_user',
                'password': 'test_pass', 
                'host': 'localhost',
                'port': '5432'
            }
        }
        instances.append(DatabaseManagerSS14(config))

    # Force garbage collection
    gc.collect()

    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory

    print(f"Memory usage: {initial_memory:.2f}MB -> {final_memory:.2f}MB (+{memory_increase:.2f}MB)")
    assert memory_increase < 50.0, f"Memory usage increased too much: {memory_increase:.2f}MB"

def test_config_processing_performance():
    """Test performance of configuration processing"""
    start_time = time.time()

    # Test with complex config
    complex_config = {}
    for i in range(20):
        complex_config[f'server_{i}'] = {
            'database': f'db_{i}',
            'user': f'user_{i}',
            'password': f'pass_{i}',
            'host': f'host_{i}',
            'port': '5432'
        }

    for i in range(10):
        db_manager = DatabaseManagerSS14(complex_config)

    end_time = time.time()
    config_time = end_time - start_time

    print(f"Processed complex config 10 times in {config_time:.3f} seconds")
    assert config_time < 1.0, "Config processing too slow"
