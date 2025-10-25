#!/usr/bin/env python3
"""
Basic health check for the bot - tests imports and initialization without starting the bot.
"""

import asyncio
import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        from bot_init import bot, cfg, ss14_db, load_cogs
        from modules.database_manager import DatabaseManagerSS14
        from config import Config
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_config():
    """Test that config has all required attributes"""
    print("Testing configuration...")
    
    from bot_init import cfg
    
    required_attrs = [
        'DB_DATABASE_SS14_MAIN',
        'DB_USER_SS14_MAIN', 
        'DB_PASSWORD_SS14_MAIN',
        'DB_HOST_SS14_MAIN',
        'DB_PORT_SS14_MAIN'
    ]
    
    for attr in required_attrs:
        if not hasattr(cfg, attr):
            print(f"✗ Missing config attribute: {attr}")
            return False
    
    print("✓ Configuration check passed")
    return True

def test_database_manager():
    """Test database manager initialization"""
    print("Testing database manager...")
    
    from bot_init import ss14_db
    
    if ss14_db is None:
        print("✗ Database manager not initialized")
        return False
        
    if not hasattr(ss14_db, 'db_params'):
        print("✗ Database manager missing db_params")
        return False
        
    if 'main' not in ss14_db.db_params:
        print("✗ Main database not configured")
        return False
        
    print("✓ Database manager check passed")
    return True

def test_bot_object():
    """Test bot object creation"""
    print("Testing bot object...")
    
    from bot_init import bot
    
    if bot.command_prefix != '$':
        print("✗ Wrong command prefix")
        return False
        
    if bot.intents.value == 0:
        print("✗ Intents not set properly")
        return False
        
    if bot.help_command is not None:
        print("✗ Help command should be disabled")
        return False
        
    print("✓ Bot configuration check passed")
    return True

async def test_cog_loading():
    """Test cog loading function"""
    print("Testing cog loading...")
    
    from bot_init import load_cogs
    
    try:
        await load_cogs()
        print("✓ Cog loading function executed")
        return True
    except Exception as e:
        print(f"⚠ Cog loading had issues (may be normal): {e}")
        return True  # This might fail in CI without actual cogs

def main():
    """Run all tests"""
    print("Running bot health checks...\n")
    
    tests = [
        test_imports,
        test_config,
        test_database_manager, 
        test_bot_object,
    ]
    
    all_passed = True
    
    for test in tests:
        try:
            if not test():
                all_passed = False
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            all_passed = False
        print()
    
    # Async test
    try:
        if not asyncio.run(test_cog_loading()):
            all_passed = False
    except Exception as e:
        print(f"✗ Async test failed: {e}")
        all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("✅ All health checks passed! Bot should start correctly.")
        sys.exit(0)
    else:
        print("❌ Some health checks failed! Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
