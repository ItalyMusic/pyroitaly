#!/usr/bin/env python3
#  PyroItaly - Telegram MTProto API Client Library for Python
#  Copyright (C) 2025-present ItalyMusic <https://github.com/ItalyMusic>
#
#  This file is part of PyroItaly.
#
#  PyroItaly is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  PyroItaly is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with PyroItaly.  If not, see <http://www.gnu.org/licenses/>.

"""
PyroItaly Test Suite

This script runs comprehensive tests for the PyroItaly library to ensure
all features and improvements work as expected.
"""

import asyncio
import os
import sys
import time
import unittest
from typing import List, Dict, Any, Optional

# Add parent directory to path to import PyroItaly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyroitaly.logging import log_handler, get_logger
from pyroitaly.errors import PyroItalyError, ConnectionError, AuthenticationError
from pyroitaly.utils import json_loads, json_dumps, zero_copy_view, async_cached
from pyroitaly.tl_parser import TLParser
from pyroitaly.connection_pool import ConnectionPool
from pyroitaly.lazy_loader import LazyLoader, LazyObject

# Configure logging for tests
log_handler.configure(level="INFO", log_to_console=True)
logger = get_logger(__name__)


class UtilsTests(unittest.TestCase):
    """Test cases for utility functions"""
    
    def test_json_functions(self):
        """Test JSON serialization and deserialization"""
        data = {"name": "PyroItaly", "version": "1.0.0", "features": ["fast", "reliable"]}
        
        # Test serialization
        json_str = json_dumps(data)
        self.assertIsInstance(json_str, str)
        
        # Test deserialization
        parsed_data = json_loads(json_str)
        self.assertEqual(parsed_data, data)
        
        # Test with bytes input
        json_bytes = json_str.encode('utf-8')
        parsed_from_bytes = json_loads(json_bytes)
        self.assertEqual(parsed_from_bytes, data)
    
    def test_zero_copy_view(self):
        """Test zero-copy view function"""
        data = b"PyroItaly test data"
        
        # Create view
        view = zero_copy_view(data)
        
        # Check type
        self.assertIsInstance(view, memoryview)
        
        # Check content
        self.assertEqual(bytes(view), data)
    
    def test_async_cached(self):
        """Test async caching decorator"""
        call_count = 0
        
        @async_cached
        async def cached_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        async def run_test():
            # First call should execute the function
            result1 = await cached_func(5)
            self.assertEqual(result1, 10)
            self.assertEqual(call_count, 1)
            
            # Second call with same args should use cache
            result2 = await cached_func(5)
            self.assertEqual(result2, 10)
            self.assertEqual(call_count, 1)
            
            # Call with different args should execute again
            result3 = await cached_func(10)
            self.assertEqual(result3, 20)
            self.assertEqual(call_count, 2)
        
        asyncio.run(run_test())


class TLParserTests(unittest.TestCase):
    """Test cases for TL parser"""
    
    def setUp(self):
        """Set up test environment"""
        self.parser = TLParser()
    
    def test_parse_int(self):
        """Test parsing integers"""
        # Test with bytes
        data = (42).to_bytes(4, byteorder='little')
        self.assertEqual(self.parser.parse_int(data), 42)
        
        # Test with memoryview
        view = memoryview(data)
        self.assertEqual(self.parser.parse_int(view), 42)
    
    def test_parse_long(self):
        """Test parsing long integers"""
        # Test with bytes
        data = (1234567890123456789).to_bytes(8, byteorder='little')
        self.assertEqual(self.parser.parse_long(data), 1234567890123456789)
        
        # Test with memoryview
        view = memoryview(data)
        self.assertEqual(self.parser.parse_long(view), 1234567890123456789)
    
    def test_parse_double(self):
        """Test parsing double-precision floats"""
        import struct
        
        # Test with bytes
        value = 3.14159
        data = struct.pack('<d', value)
        self.assertAlmostEqual(self.parser.parse_double(data), value, places=5)
        
        # Test with memoryview
        view = memoryview(data)
        self.assertAlmostEqual(self.parser.parse_double(view), value, places=5)
    
    def test_serialize_deserialize_bytes(self):
        """Test serializing and deserializing bytes"""
        # Test short form (length < 254)
        original = b"PyroItaly test data"
        serialized = self.parser.serialize_bytes(original)
        deserialized, _ = self.parser.parse_bytes(serialized)
        self.assertEqual(deserialized, original)
        
        # Test long form (length >= 254)
        original_long = b"x" * 300
        serialized_long = self.parser.serialize_bytes(original_long)
        deserialized_long, _ = self.parser.parse_bytes(serialized_long)
        self.assertEqual(deserialized_long, original_long)
    
    def test_serialize_deserialize_string(self):
        """Test serializing and deserializing strings"""
        original = "PyroItaly test string with unicode: 🇮🇹"
        serialized = self.parser.serialize_string(original)
        deserialized, _ = self.parser.parse_string(serialized)
        self.assertEqual(deserialized, original)


class LazyLoaderTests(unittest.TestCase):
    """Test cases for lazy loading system"""
    
    def test_lazy_loader(self):
        """Test lazy module loader"""
        loader = LazyLoader()
        
        # Test loading a module
        os_module = loader("os")
        self.assertEqual(os_module, os)
        
        # Test loading an attribute from a module
        path_join = loader("os.path.join")
        self.assertEqual(path_join, os.path.join)
        
        # Test caching
        self.assertIn("os", loader._cached_modules)
        self.assertIn("os.path.join", loader._cached_modules)
    
    def test_lazy_object(self):
        """Test lazy object descriptor"""
        class TestClass:
            lazy_time = LazyObject("time.time")
        
        obj = TestClass()
        
        # Access should load the object
        self.assertEqual(obj.lazy_time, time.time)
        
        # Second access should use cached value
        self.assertEqual(obj.lazy_time, time.time)


class ErrorHandlingTests(unittest.TestCase):
    """Test cases for error handling system"""
    
    def test_error_registry(self):
        """Test error registry and registration"""
        from pyroitaly.errors import ERROR_REGISTRY, register_error
        
        # Check that built-in errors are registered
        self.assertIn("ConnectionError", ERROR_REGISTRY)
        self.assertIn("AuthenticationError", ERROR_REGISTRY)
        
        # Test registering a new error
        @register_error(
            error_class=PyroItalyError,
            code="TEST_001",
            description="Test error",
            resolution="This is just a test"
        )
        class TestError(PyroItalyError):
            pass
        
        # Check registration
        self.assertIn("TestError", ERROR_REGISTRY)
        self.assertEqual(TestError.error_info.code, "TEST_001")
    
    def test_error_formatting(self):
        """Test error message formatting"""
        # Test basic error
        error = ConnectionError("Failed to connect to test server")
        error_str = str(error)
        
        self.assertIn("[CONN_001]", error_str)
        self.assertIn("Failed to connect to test server", error_str)
        
        # Test error with context
        error_with_context = AuthenticationError(
            "Invalid API ID",
            api_id="12345",
            server="test.server"
        )
        error_with_context_str = str(error_with_context)
        
        self.assertIn("[AUTH_001]", error_with_context_str)
        self.assertIn("Invalid API ID", error_with_context_str)
        self.assertIn("api_id: 12345", error_with_context_str)
        self.assertIn("server: test.server", error_with_context_str)


class AsyncTests(unittest.IsolatedAsyncioTestCase):
    """Test cases for asynchronous functionality"""
    
    async def test_connection_pool(self):
        """Test connection pool functionality"""
        # Mock DataCenter class
        class MockDataCenter:
            def __init__(self, ip, port):
                self.ip = ip
                self.port = port
        
        # Mock TCP class
        class MockTCP:
            def __init__(self, ip, port):
                self.ip = ip
                self.port = port
                self.is_connected = False
            
            async def connect(self):
                self.is_connected = True
            
            async def close(self):
                self.is_connected = False
        
        # Create connection pool
        pool = ConnectionPool(max_connections=2)
        await pool.start()
        
        # Patch the connection creation
        original_get_connection = pool.get_connection
        
        async def mock_get_connection(dc, transport_mode="tcp_abridged"):
            if transport_mode == "tcp_abridged":
                conn = MockTCP(dc.ip, dc.port)
                await conn.connect()
                return conn
            return await original_get_connection(dc, transport_mode)
        
        pool.get_connection = mock_get_connection
        
        # Test getting a connection
        dc = MockDataCenter("127.0.0.1", 8888)
        conn1 = await pool.get_connection(dc)
        
        self.assertTrue(conn1.is_connected)
        self.assertEqual(conn1.ip, "127.0.0.1")
        self.assertEqual(conn1.port, 8888)
        
        # Release connection back to pool
        await pool.release_connection(conn1, dc)
        
        # Get another connection (should reuse the first one)
        conn2 = await pool.get_connection(dc)
        self.assertEqual(conn1, conn2)
        
        # Clean up
        await pool.stop()


def run_tests():
    """Run all tests"""
    logger.info("Starting PyroItaly test suite")
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(UtilsTests))
    suite.addTest(unittest.makeSuite(TLParserTests))
    suite.addTest(unittest.makeSuite(LazyLoaderTests))
    suite.addTest(unittest.makeSuite(ErrorHandlingTests))
    suite.addTest(unittest.makeSuite(AsyncTests))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Log results
    logger.info(f"Tests completed: {result.testsRun} run, {len(result.errors)} errors, {len(result.failures)} failures")
    
    return result


if __name__ == "__main__":
    result = run_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
