import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.database_manager import DatabaseManagerSS14
from config import Config

class TestDatabaseManager:
    def test_initialization(self):
        """Test DatabaseManagerSS14 initialization"""
        db_manager = DatabaseManagerSS14()
        assert db_manager.db_params == {}
        
        test_config = {'main': {'database': 'test'}}
        db_manager = DatabaseManagerSS14(test_config)
        assert db_manager.db_params == test_config
    
    def test_add_database(self):
        """Test adding database configuration"""
        db_manager = DatabaseManagerSS14()

        db_config = {
            'database': 'db',
            'user': 'user',
            'password': 'pass',
            'host': 'host',
            'port': 5432
        }
        db_manager.add_database('test', db_config)

        assert 'test' in db_manager.db_params
        assert db_manager.db_params['test']['database'] == 'db'
        assert db_manager.db_params['test']['user'] == 'user'

    def test_missing_database_connection(self):
        """Test error handling for missing database"""
        db_manager = DatabaseManagerSS14()
        
        with pytest.raises(ValueError, match="Unknown database name: main"):
            db_manager._get_connection('main')

    def test_get_connection_with_mock(self):
        """Test get_connection method with mock"""
        import unittest.mock as mock
        
        test_config = {
            'main': {
                'database': 'test_db',
                'user': 'test_user',
                'password': 'test_pass',
                'host': 'localhost',
                'port': '5432'
            }
        }
        db_manager = DatabaseManagerSS14(test_config)

        # Мокаем psycopg2.connect чтобы не пытаться подключаться к реальной БД
        with mock.patch('psycopg2.connect') as mock_connect:
            db_manager._get_connection('main')
            mock_connect.assert_called_once_with(**test_config['main'])

class TestConfig:
    def test_config_attributes(self):
        """Test that Config has required attributes"""
        config = Config()
        
        required_attrs = [
            'DB_DATABASE_SS14_MAIN',
            'DB_USER_SS14_MAIN',
            'DB_PASSWORD_SS14_MAIN', 
            'DB_HOST_SS14_MAIN',
            'DB_PORT_SS14_MAIN',
            'MOSCOW_TIMEZONE'
        ]

        for attr in required_attrs:
            assert hasattr(config, attr), f"Missing attribute: {attr}"
