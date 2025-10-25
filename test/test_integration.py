import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_bot_initialization():
    """Test that bot initializes correctly with all dependencies"""
    from bot_init import bot, cfg, ss14_db
    
    # Test bot configuration
    assert bot.command_prefix == '$'
    assert bot.help_command is None
    assert bot.intents is not None
    
    # Test config
    assert hasattr(cfg, 'DB_DATABASE_SS14_MAIN')
    assert hasattr(cfg, 'DB_USER_SS14_MAIN')
    
    # Test database manager
    assert ss14_db is not None
    assert hasattr(ss14_db, 'db_params')
    assert 'main' in ss14_db.db_params

def test_module_imports():
    """Test that all modules can be imported"""
    modules_to_test = [
        'bot_init',
        'main', 
        'config',
        'modules.database_manager'
    ]
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✓ Successfully imported {module_name}")
        except ImportError as e:
            pytest.fail(f"Failed to import {module_name}: {e}")
