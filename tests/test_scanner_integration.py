#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SecureRedLab - Scanner AI Integration Test
===========================================

تست integration Neural Scanner با Offline AI

تاریخ: 2025-12-08
"""

import os
import sys
import unittest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.logging_system import get_logger, LogCategory
from ai.scanner_ai_adapter import get_scanner_ai_engine, AIModelType


class TestScannerAIIntegration(unittest.TestCase):
    """Test Scanner AI Integration"""
    
    @classmethod
    def setUpClass(cls):
        """Setup once before all tests"""
        cls.logger = get_logger(__name__, LogCategory.TEST)
        cls.logger.info("=" * 50)
        cls.logger.info("Starting Scanner AI Integration Tests")
        cls.logger.info("=" * 50)
    
    def test_01_ai_engine_initialization(self):
        """Test 1: AI Engine Initialization"""
        self.logger.info("\n[TEST 1] AI Engine Initialization")
        
        ai_engine = get_scanner_ai_engine()
        
        self.assertIsNotNone(ai_engine)
        self.assertIsNotNone(ai_engine.model_manager)
        
        self.logger.info("✅ AI Engine initialized")
    
    def test_02_model_manager_generation(self):
        """Test 2: Model Manager Generation"""
        self.logger.info("\n[TEST 2] Model Manager Generation")
        
        ai_engine = get_scanner_ai_engine()
        model_manager = ai_engine.model_manager
        
        # Test generation
        prompt = """
        Analyze the following service for vulnerabilities:
        Service: Apache HTTP Server 2.4.41
        Port: 80
        Banner: Apache/2.4.41 (Ubuntu)
        
        Please identify potential vulnerabilities.
        """
        
        result = model_manager.generate(
            prompt=prompt,
            model_type=AIModelType.QWEN_14B,
            validate_output=True
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result['status'], 'success')
        self.assertIn('output', result)
        self.assertGreater(len(result['output']), 0)
        
        # Check validation
        if 'validation' in result:
            self.assertIn('is_valid', result['validation'])
            self.assertIn('confidence_score', result['validation'])
        
        self.logger.info(f"✅ Generation successful: {len(result['output'])} chars")
        self.logger.info(f"   Model: {result.get('model_type', 'unknown')}")
        self.logger.info(f"   Latency: {result.get('latency_ms', 0):.0f}ms")
    
    def test_03_vulnerability_prompt_detection(self):
        """Test 3: Vulnerability Prompt Task Detection"""
        self.logger.info("\n[TEST 3] Vulnerability Prompt Detection")
        
        ai_engine = get_scanner_ai_engine()
        model_manager = ai_engine.model_manager
        
        vuln_prompt = "Analyze this Apache 2.4.41 for CVE vulnerabilities"
        
        task_type = model_manager._detect_task_type(vuln_prompt)
        
        from ai.offline_core import TaskType
        self.assertEqual(task_type, TaskType.VULNERABILITY_ANALYSIS)
        
        self.logger.info(f"✅ Task type detected: {task_type.value}")
    
    def test_04_statistics(self):
        """Test 4: Statistics Collection"""
        self.logger.info("\n[TEST 4] Statistics")
        
        ai_engine = get_scanner_ai_engine()
        
        stats = ai_engine.get_statistics()
        
        self.assertIn('generation_count', stats)
        self.assertIn('llm_stats', stats)
        self.assertIn('vlm_stats', stats)
        
        self.logger.info(f"✅ Stats: {stats['generation_count']} generations")
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup after all tests"""
        cls.logger.info("=" * 50)
        cls.logger.info("Scanner AI Integration Tests Complete")
        cls.logger.info("=" * 50)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestScannerAIIntegration)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print("SCANNER AI INTEGRATION TEST SUMMARY")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
