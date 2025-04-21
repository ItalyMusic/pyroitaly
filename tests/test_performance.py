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
PyroItaly Performance Tests

This script runs performance tests for the PyroItaly library to ensure
the performance improvements are effective.
"""

import asyncio
import os
import sys
import time
import unittest
import statistics
from typing import List, Dict, Any, Optional, Tuple, Callable

# Add parent directory to path to import PyroItaly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyroitaly.logging import log_handler, get_logger
from pyroitaly.utils import json_loads, json_dumps
from pyroitaly.tl_parser import TLParser

# Configure logging for tests
log_handler.configure(level="INFO", log_to_console=True)
logger = get_logger(__name__)


class PerformanceTest:
    """Base class for performance tests"""
    
    def __init__(self, name: str, iterations: int = 1000):
        """Initialize performance test
        
        Args:
            name: Test name
            iterations: Number of iterations to run
        """
        self.name = name
        self.iterations = iterations
        self.results: List[float] = []
    
    def run(self) -> Dict[str, Any]:
        """Run the performance test
        
        Returns:
            Dictionary with test results
        """
        logger.info(f"Running performance test: {self.name} ({self.iterations} iterations)")
        
        # Warm up
        self._run_once()
        
        # Run test
        start_time = time.time()
        
        for _ in range(self.iterations):
            iteration_time = self._run_once()
            self.results.append(iteration_time)
        
        total_time = time.time() - start_time
        
        # Calculate statistics
        avg_time = statistics.mean(self.results)
        median_time = statistics.median(self.results)
        min_time = min(self.results)
        max_time = max(self.results)
        
        if len(self.results) > 1:
            stdev = statistics.stdev(self.results)
        else:
            stdev = 0
        
        # Log results
        logger.info(f"Performance test {self.name} completed:")
        logger.info(f"  Total time: {total_time:.4f}s")
        logger.info(f"  Average time: {avg_time:.6f}s")
        logger.info(f"  Median time: {median_time:.6f}s")
        logger.info(f"  Min time: {min_time:.6f}s")
        logger.info(f"  Max time: {max_time:.6f}s")
        logger.info(f"  Standard deviation: {stdev:.6f}s")
        
        return {
            "name": self.name,
            "iterations": self.iterations,
            "total_time": total_time,
            "avg_time": avg_time,
            "median_time": median_time,
            "min_time": min_time,
            "max_time": max_time,
            "stdev": stdev,
            "results": self.results
        }
    
    def _run_once(self) -> float:
        """Run a single iteration of the test
        
        Returns:
            Time taken for the iteration in seconds
        """
        start_time = time.time()
        self._execute()
        return time.time() - start_time
    
    def _execute(self) -> None:
        """Execute the test logic
        
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _execute method")


class JsonSerializationTest(PerformanceTest):
    """Test JSON serialization performance"""
    
    def __init__(self, iterations: int = 10000):
        """Initialize JSON serialization test
        
        Args:
            iterations: Number of iterations to run
        """
        super().__init__("JSON Serialization", iterations)
        
        # Test data
        self.test_data = {
            "id": 12345,
            "name": "PyroItaly",
            "version": "1.0.0",
            "features": ["fast", "reliable", "easy-to-use"],
            "metadata": {
                "author": "ItalyMusic",
                "license": "LGPL-3.0",
                "repository": "https://github.com/ItalyMusic/pyroitaly",
                "dependencies": ["pyaes", "pysocks", "pymediainfo-pyroitaly"]
            },
            "stats": {
                "stars": 1000,
                "forks": 500,
                "issues": 50,
                "pull_requests": 25
            },
            "nested": {
                "level1": {
                    "level2": {
                        "level3": {
                            "level4": {
                                "level5": "Deep nesting"
                            }
                        }
                    }
                }
            }
        }
    
    def _execute(self) -> None:
        """Execute JSON serialization test"""
        json_str = json_dumps(self.test_data)


class JsonDeserializationTest(PerformanceTest):
    """Test JSON deserialization performance"""
    
    def __init__(self, iterations: int = 10000):
        """Initialize JSON deserialization test
        
        Args:
            iterations: Number of iterations to run
        """
        super().__init__("JSON Deserialization", iterations)
        
        # Test data
        test_data = {
            "id": 12345,
            "name": "PyroItaly",
            "version": "1.0.0",
            "features": ["fast", "reliable", "easy-to-use"],
            "metadata": {
                "author": "ItalyMusic",
                "license": "LGPL-3.0",
                "repository": "https://github.com/ItalyMusic/pyroitaly",
                "dependencies": ["pyaes", "pysocks", "pymediainfo-pyroitaly"]
            },
            "stats": {
                "stars": 1000,
                "forks": 500,
                "issues": 50,
                "pull_requests": 25
            },
            "nested": {
                "level1": {
                    "level2": {
                        "level3": {
                            "level4": {
                                "level5": "Deep nesting"
                            }
                        }
                    }
                }
            }
        }
        
        self.json_str = json_dumps(test_data)
        self.json_bytes = self.json_str.encode('utf-8')
    
    def _execute(self) -> None:
        """Execute JSON deserialization test"""
        # Test with string input
        data1 = json_loads(self.json_str)
        
        # Test with bytes input
        data2 = json_loads(self.json_bytes)


class TLParserTest(PerformanceTest):
    """Test TL parser performance"""
    
    def __init__(self, iterations: int = 10000):
        """Initialize TL parser test
        
        Args:
            iterations: Number of iterations to run
        """
        super().__init__("TL Parser", iterations)
        
        # Initialize parser
        self.parser = TLParser()
        
        # Test data
        self.int_data = (42).to_bytes(4, byteorder='little')
        self.long_data = (1234567890123456789).to_bytes(8, byteorder='little')
        
        import struct
        self.double_data = struct.pack('<d', 3.14159)
        
        self.string_data = "PyroItaly test string with unicode: 🇮🇹"
        self.bytes_data = self.string_data.encode('utf-8')
        
        # Pre-serialize for parsing tests
        self.serialized_bytes = self.parser.serialize_bytes(self.bytes_data)
        self.serialized_string = self.parser.serialize_string(self.string_data)
    
    def _execute(self) -> None:
        """Execute TL parser test"""
        # Test parsing
        int_val = self.parser.parse_int(self.int_data)
        long_val = self.parser.parse_long(self.long_data)
        double_val = self.parser.parse_double(self.double_data)
        
        # Test serialization
        serialized_int = self.parser.serialize_int(int_val)
        serialized_long = self.parser.serialize_long(long_val)
        serialized_double = self.parser.serialize_double(double_val)
        
        # Test parsing serialized data
        bytes_val, _ = self.parser.parse_bytes(self.serialized_bytes)
        string_val, _ = self.parser.parse_string(self.serialized_string)


class AsyncPerformanceTest(PerformanceTest):
    """Base class for asynchronous performance tests"""
    
    async def run_async(self) -> Dict[str, Any]:
        """Run the asynchronous performance test
        
        Returns:
            Dictionary with test results
        """
        logger.info(f"Running async performance test: {self.name} ({self.iterations} iterations)")
        
        # Warm up
        await self._run_once_async()
        
        # Run test
        start_time = time.time()
        
        for _ in range(self.iterations):
            iteration_time = await self._run_once_async()
            self.results.append(iteration_time)
        
        total_time = time.time() - start_time
        
        # Calculate statistics
        avg_time = statistics.mean(self.results)
        median_time = statistics.median(self.results)
        min_time = min(self.results)
        max_time = max(self.results)
        
        if len(self.results) > 1:
            stdev = statistics.stdev(self.results)
        else:
            stdev = 0
        
        # Log results
        logger.info(f"Async performance test {self.name} completed:")
        logger.info(f"  Total time: {total_time:.4f}s")
        logger.info(f"  Average time: {avg_time:.6f}s")
        logger.info(f"  Median time: {median_time:.6f}s")
        logger.info(f"  Min time: {min_time:.6f}s")
        logger.info(f"  Max time: {max_time:.6f}s")
        logger.info(f"  Standard deviation: {stdev:.6f}s")
        
        return {
            "name": self.name,
            "iterations": self.iterations,
            "total_time": total_time,
            "avg_time": avg_time,
            "median_time": median_time,
            "min_time": min_time,
            "max_time": max_time,
            "stdev": stdev,
            "results": self.results
        }
    
    async def _run_once_async(self) -> float:
        """Run a single iteration of the async test
        
        Returns:
            Time taken for the iteration in seconds
        """
        start_time = time.time()
        await self._execute_async()
        return time.time() - start_time
    
    async def _execute_async(self) -> None:
        """Execute the async test logic
        
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _execute_async method")


class AsyncCachedTest(AsyncPerformanceTest):
    """Test async_cached decorator performance"""
    
    def __init__(self, iterations: int = 1000):
        """Initialize async_cached test
        
        Args:
            iterations: Number of iterations to run
        """
        super().__init__("Async Cached", iterations)
        
        # Import async_cached
        from pyroitaly.utils import async_cached
        
        # Define test function
        @async_cached
        async def cached_func(x):
            await asyncio.sleep(0.001)  # Simulate some work
            return x * 2
        
        self.cached_func = cached_func
    
    async def _execute_async(self) -> None:
        """Execute async_cached test"""
        # Call with same argument to test caching
        result = await self.cached_func(42)


class ZeroCopyViewTest(PerformanceTest):
    """Test zero-copy view performance"""
    
    def __init__(self, iterations: int = 10000):
        """Initialize zero-copy view test
        
        Args:
            iterations: Number of iterations to run
        """
        super().__init__("Zero-Copy View", iterations)
        
        # Import zero_copy_view
        from pyroitaly.utils import zero_copy_view
        
        self.zero_copy_view = zero_copy_view
        
        # Test data (1MB)
        self.data = b"x" * (1024 * 1024)
    
    def _execute(self) -> None:
        """Execute zero-copy view test"""
        # Create view
        view = self.zero_copy_view(self.data)
        
        # Access some parts of the view
        for i in range(0, len(view), 1024):
            _ = view[i:i+10]


async def run_async_tests():
    """Run all asynchronous performance tests"""
    logger.info("Running asynchronous performance tests")
    
    # Create and run tests
    tests = [
        AsyncCachedTest()
    ]
    
    results = []
    
    for test in tests:
        result = await test.run_async()
        results.append(result)
    
    return results


def run_tests():
    """Run all performance tests"""
    logger.info("Starting PyroItaly performance tests")
    
    # Create and run tests
    tests = [
        JsonSerializationTest(),
        JsonDeserializationTest(),
        TLParserTest(),
        ZeroCopyViewTest()
    ]
    
    results = []
    
    for test in tests:
        result = test.run()
        results.append(result)
    
    # Run async tests
    async_results = asyncio.run(run_async_tests())
    results.extend(async_results)
    
    # Log summary
    logger.info("Performance tests completed")
    logger.info("Summary:")
    
    for result in results:
        logger.info(f"  {result['name']}: {result['avg_time']:.6f}s avg, {result['median_time']:.6f}s median")
    
    return results


if __name__ == "__main__":
    results = run_tests()
    sys.exit(0)
