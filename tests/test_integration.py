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
PyroItaly Integration Tests

This script runs integration tests for the PyroItaly library to ensure
all features work correctly with the Telegram API.
"""

import asyncio
import os
import sys
import time
import unittest
from typing import List, Dict, Any, Optional

# Add parent directory to path to import PyroItaly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyroitaly import Client
from pyroitaly.logging import log_handler, get_logger
from pyroitaly.errors import PyroItalyError
from pyroitaly.plugins import AutoReconnect, PluginSystem, SessionManager

# Configure logging for tests
log_handler.configure(level="INFO", log_to_console=True)
logger = get_logger(__name__)

# Test configuration
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
PHONE_NUMBER = os.environ.get("PHONE_NUMBER")
SESSION_STRING = os.environ.get("SESSION_STRING")


@unittest.skipIf(not all([API_ID, API_HASH, BOT_TOKEN]), "API credentials not provided")
class BotClientTests(unittest.IsolatedAsyncioTestCase):
    """Test cases for bot client functionality"""
    
    async def asyncSetUp(self):
        """Set up test environment"""
        self.client = Client(
            "test_bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            in_memory=True
        )
        await self.client.start()
        self.me = await self.client.get_me()
        logger.info(f"Bot client started: {self.me.first_name} (@{self.me.username})")
    
    async def asyncTearDown(self):
        """Clean up test environment"""
        await self.client.stop()
        logger.info("Bot client stopped")
    
    async def test_get_me(self):
        """Test getting bot information"""
        self.assertIsNotNone(self.me)
        self.assertTrue(self.me.is_bot)
        self.assertIsNotNone(self.me.username)
    
    async def test_get_chat(self):
        """Test getting chat information"""
        chat = await self.client.get_chat("me")
        self.assertEqual(chat.id, self.me.id)
    
    async def test_send_message(self):
        """Test sending a message"""
        message = await self.client.send_message(
            "me",
            "Test message from PyroItaly integration tests"
        )
        self.assertEqual(message.text, "Test message from PyroItaly integration tests")
        
        # Clean up
        await self.client.delete_messages("me", message.id)


@unittest.skipIf(not all([API_ID, API_HASH]) or (not PHONE_NUMBER and not SESSION_STRING), 
                "User credentials not provided")
class UserClientTests(unittest.IsolatedAsyncioTestCase):
    """Test cases for user client functionality"""
    
    async def asyncSetUp(self):
        """Set up test environment"""
        if SESSION_STRING:
            self.client = Client(
                "test_user",
                api_id=API_ID,
                api_hash=API_HASH,
                session_string=SESSION_STRING,
                in_memory=True
            )
        else:
            self.client = Client(
                "test_user",
                api_id=API_ID,
                api_hash=API_HASH,
                phone_number=PHONE_NUMBER,
                in_memory=True
            )
        
        await self.client.start()
        self.me = await self.client.get_me()
        logger.info(f"User client started: {self.me.first_name} (@{self.me.username or ''})")
    
    async def asyncTearDown(self):
        """Clean up test environment"""
        await self.client.stop()
        logger.info("User client stopped")
    
    async def test_get_me(self):
        """Test getting user information"""
        self.assertIsNotNone(self.me)
        self.assertFalse(self.me.is_bot)
    
    async def test_get_chat(self):
        """Test getting chat information"""
        chat = await self.client.get_chat("me")
        self.assertEqual(chat.id, self.me.id)
    
    async def test_send_message(self):
        """Test sending a message"""
        message = await self.client.send_message(
            "me",
            "Test message from PyroItaly integration tests"
        )
        self.assertEqual(message.text, "Test message from PyroItaly integration tests")
        
        # Clean up
        await self.client.delete_messages("me", message.id)


@unittest.skipIf(not all([API_ID, API_HASH, BOT_TOKEN]), "API credentials not provided")
class PluginSystemTests(unittest.IsolatedAsyncioTestCase):
    """Test cases for plugin system functionality"""
    
    async def asyncSetUp(self):
        """Set up test environment"""
        self.client = Client(
            "test_plugins",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            in_memory=True
        )
        await self.client.start()
        self.plugin_system = PluginSystem(self.client)
        logger.info("Plugin system test client started")
    
    async def asyncTearDown(self):
        """Clean up test environment"""
        await self.client.stop()
        logger.info("Plugin system test client stopped")
    
    async def test_register_plugin(self):
        """Test registering a plugin"""
        plugin = self.plugin_system.register_plugin(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin",
            author="PyroItaly"
        )
        
        self.assertEqual(plugin["name"], "test_plugin")
        self.assertEqual(plugin["version"], "1.0.0")
        self.assertEqual(plugin["description"], "Test plugin")
        self.assertEqual(plugin["author"], "PyroItaly")
        self.assertTrue(plugin["enabled"])
    
    async def test_register_hook(self):
        """Test registering and triggering a hook"""
        hook_triggered = False
        
        async def test_hook():
            nonlocal hook_triggered
            hook_triggered = True
            return "hook_result"
        
        # Register plugin and hook
        self.plugin_system.register_plugin(
            name="hook_test",
            version="1.0.0",
            description="Hook test plugin",
            author="PyroItaly"
        )
        
        self.plugin_system.register_hook("test_hook", test_hook)
        
        # Trigger hook
        results = await self.plugin_system.trigger_hook("test_hook")
        
        self.assertTrue(hook_triggered)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], "hook_result")
    
    async def test_enable_disable_plugin(self):
        """Test enabling and disabling a plugin"""
        plugin = self.plugin_system.register_plugin(
            name="toggle_test",
            version="1.0.0",
            description="Toggle test plugin",
            author="PyroItaly"
        )
        
        # Initially enabled
        self.assertTrue(plugin["enabled"])
        
        # Disable
        result = self.plugin_system.disable_plugin("toggle_test")
        self.assertTrue(result)
        self.assertFalse(self.plugin_system.plugins["toggle_test"]["enabled"])
        
        # Enable
        result = self.plugin_system.enable_plugin("toggle_test")
        self.assertTrue(result)
        self.assertTrue(self.plugin_system.plugins["toggle_test"]["enabled"])


@unittest.skipIf(not all([API_ID, API_HASH, BOT_TOKEN]), "API credentials not provided")
class AutoReconnectTests(unittest.IsolatedAsyncioTestCase):
    """Test cases for auto reconnection functionality"""
    
    async def asyncSetUp(self):
        """Set up test environment"""
        self.client = Client(
            "test_reconnect",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            in_memory=True
        )
        self.auto_reconnect = AutoReconnect(
            self.client,
            max_retries=3,
            retry_delay=1,
            exponential_backoff=True
        )
        await self.client.start()
        await self.auto_reconnect.start()
        logger.info("Auto reconnect test client started")
    
    async def asyncTearDown(self):
        """Clean up test environment"""
        await self.auto_reconnect.stop()
        await self.client.stop()
        logger.info("Auto reconnect test client stopped")
    
    async def test_reconnect_properties(self):
        """Test auto reconnect properties"""
        self.assertEqual(self.auto_reconnect.max_retries, 3)
        self.assertEqual(self.auto_reconnect.retry_delay, 1)
        self.assertTrue(self.auto_reconnect.exponential_backoff)
        self.assertTrue(self.auto_reconnect._is_connected)
        self.assertEqual(self.auto_reconnect._retry_count, 0)


@unittest.skipIf(not all([API_ID, API_HASH, BOT_TOKEN]), "API credentials not provided")
class SessionManagerTests(unittest.IsolatedAsyncioTestCase):
    """Test cases for session management functionality"""
    
    async def asyncSetUp(self):
        """Set up test environment"""
        self.client = Client(
            "test_session",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            in_memory=True
        )
        await self.client.start()
        logger.info("Session manager test client started")
    
    async def asyncTearDown(self):
        """Clean up test environment"""
        await self.client.stop()
        logger.info("Session manager test client stopped")
    
    async def test_export_import_session(self):
        """Test exporting and importing a session"""
        # Export session
        session_str = await SessionManager.export_session(self.client)
        self.assertIsNotNone(session_str)
        self.assertTrue(session_str.startswith("pyroitaly:"))
        
        # Create a new client
        new_client = Client(
            "test_session_import",
            api_id=API_ID,
            api_hash=API_HASH,
            in_memory=True
        )
        
        try:
            # Import session
            result = await SessionManager.import_session(new_client, session_str)
            self.assertTrue(result)
            
            # Test the imported session
            await new_client.start()
            me = await new_client.get_me()
            self.assertIsNotNone(me)
            self.assertEqual(me.id, (await self.client.get_me()).id)
        finally:
            if new_client.is_connected:
                await new_client.stop()
    
    async def test_export_import_with_password(self):
        """Test exporting and importing a session with password"""
        password = "test_password"
        
        # Export session with password
        session_str = await SessionManager.export_session(self.client, password)
        self.assertIsNotNone(session_str)
        self.assertTrue(session_str.startswith("pyroitaly:"))
        
        # Create a new client
        new_client = Client(
            "test_session_import_pwd",
            api_id=API_ID,
            api_hash=API_HASH,
            in_memory=True
        )
        
        try:
            # Import session with password
            result = await SessionManager.import_session(new_client, session_str, password)
            self.assertTrue(result)
            
            # Test the imported session
            await new_client.start()
            me = await new_client.get_me()
            self.assertIsNotNone(me)
            self.assertEqual(me.id, (await self.client.get_me()).id)
        finally:
            if new_client.is_connected:
                await new_client.stop()


def run_tests():
    """Run all integration tests"""
    logger.info("Starting PyroItaly integration tests")
    
    if not all([API_ID, API_HASH]):
        logger.warning("API credentials not provided. Most tests will be skipped.")
        logger.info("Set API_ID and API_HASH environment variables to run all tests.")
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(BotClientTests))
    suite.addTest(unittest.makeSuite(UserClientTests))
    suite.addTest(unittest.makeSuite(PluginSystemTests))
    suite.addTest(unittest.makeSuite(AutoReconnectTests))
    suite.addTest(unittest.makeSuite(SessionManagerTests))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Log results
    logger.info(f"Tests completed: {result.testsRun} run, {len(result.errors)} errors, {len(result.failures)} failures")
    
    return result


if __name__ == "__main__":
    result = run_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
