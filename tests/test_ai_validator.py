#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SecureRedLab - AI Validator Test Suite
=======================================

تست جامع AI Output Validator

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
from core.ai_output_validator import (
    get_validator, ValidationType, ConfidenceLevel, ValidationResult
)


class TestAIValidator(unittest.TestCase):
    """Test AI Output Validator"""
    
    @classmethod
    def setUpClass(cls):
        """Setup once before all tests"""
        cls.logger = get_logger(__name__, LogCategory.TEST)
        cls.logger.info("=" * 50)
        cls.logger.info("Starting AI Validator Test Suite")
        cls.logger.info("=" * 50)
    
    def test_01_validator_initialization(self):
        """Test 1: Validator Initialization"""
        self.logger.info("\n[TEST 1] Validator Initialization")
        
        validator = get_validator()
        
        self.assertIsNotNone(validator)
        self.assertGreater(len(validator.validators), 0)
        
        self.logger.info(f"✅ Validator initialized with {len(validator.validators)} validators")
    
    def test_02_file_existence_validation(self):
        """Test 2: File Existence Validation"""
        self.logger.info("\n[TEST 2] File Existence Validation")
        
        validator = get_validator()
        
        # Create a test file
        test_file = "/tmp/test_validator_file.txt"
        with open(test_file, 'w') as f:
            f.write("Test content")
        
        # Test with existing file
        result = validator.validate(
            output=f"The file is located at {test_file}",
            validation_types=ValidationType.FILE_EXISTENCE,
            context={"file_path": test_file}
        )
        
        self.assertTrue(result.is_valid)
        self.assertGreater(result.confidence_score, 0.5)
        
        # Cleanup
        os.remove(test_file)
        
        self.logger.info(f"✅ File validation: {result.confidence_score:.2f}")
    
    def test_03_code_syntax_validation(self):
        """Test 3: Code Syntax Validation"""
        self.logger.info("\n[TEST 3] Code Syntax Validation")
        
        validator = get_validator()
        
        # Valid Python code
        valid_code = """
def hello_world():
    print("Hello, World!")
    return True
"""
        
        result = validator.validate(
            output=valid_code,
            validation_types=ValidationType.CODE_SYNTAX,
            context={"language": "python"}
        )
        
        self.assertTrue(result.is_valid)
        self.assertGreater(result.confidence_score, 0.7)
        
        self.logger.info(f"✅ Code syntax valid: {result.confidence_score:.2f}")
    
    def test_04_command_safety_validation(self):
        """Test 4: Command Safety Validation"""
        self.logger.info("\n[TEST 4] Command Safety Validation")
        
        validator = get_validator()
        
        # Safe command
        safe_result = validator.validate(
            output="ls -la /tmp",
            validation_types=ValidationType.COMMAND_SAFETY
        )
        
        self.assertTrue(safe_result.is_valid)
        
        # Dangerous command
        dangerous_result = validator.validate(
            output="rm -rf /",
            validation_types=ValidationType.COMMAND_SAFETY
        )
        
        self.assertFalse(dangerous_result.is_valid)
        self.assertGreater(len(dangerous_result.errors), 0)
        
        self.logger.info(f"✅ Safe command: {safe_result.is_valid}, Dangerous: {dangerous_result.is_valid}")
    
    def test_05_hallucination_detection(self):
        """Test 5: Hallucination Detection"""
        self.logger.info("\n[TEST 5] Hallucination Detection")
        
        validator = get_validator()
        
        # No hallucination
        clean_result = validator.validate(
            output="The system has 3 open ports: 22, 80, 443",
            validation_types=ValidationType.HALLUCINATION
        )
        
        self.assertTrue(clean_result.is_valid)
        
        # With hallucination indicators
        hallucinated_result = validator.validate(
            output="As an AI, I don't have access to verify this information",
            validation_types=ValidationType.HALLUCINATION
        )
        
        self.assertLess(hallucinated_result.confidence_score, clean_result.confidence_score)
        
        self.logger.info(f"✅ Clean: {clean_result.confidence_score:.2f}, Hallucinated: {hallucinated_result.confidence_score:.2f}")
    
    def test_06_json_format_validation(self):
        """Test 6: JSON Format Validation"""
        self.logger.info("\n[TEST 6] JSON Format Validation")
        
        validator = get_validator()
        
        # Valid JSON
        valid_json = '{"name": "test", "value": 123}'
        result = validator.validate(
            output=valid_json,
            validation_types=ValidationType.JSON_FORMAT
        )
        
        self.assertTrue(result.is_valid)
        
        self.logger.info(f"✅ JSON valid: {result.is_valid}")
    
    def test_07_numeric_range_validation(self):
        """Test 7: Numeric Range Validation"""
        self.logger.info("\n[TEST 7] Numeric Range Validation")
        
        validator = get_validator()
        
        # In range
        result = validator.validate(
            output="Port 8080 is open",
            validation_types=ValidationType.NUMERIC_RANGE,
            context={"min": 1, "max": 65535, "field": "port"}
        )
        
        self.assertTrue(result.is_valid)
        
        self.logger.info(f"✅ Numeric range valid: {result.is_valid}")
    
    def test_08_multiple_validations(self):
        """Test 8: Multiple Validations"""
        self.logger.info("\n[TEST 8] Multiple Validations")
        
        validator = get_validator()
        
        output = """
Found 3 vulnerabilities:
1. SQL Injection on port 3306
2. XSS on port 80
3. RCE on port 22
"""
        
        results = validator.validate_all(
            output=output
        )
        
        self.assertGreater(len(results), 0)
        
        # validate_all returns a list, not a dict
        for result in results:
            self.assertIsInstance(result, ValidationResult)
        
        self.logger.info(f"✅ Multiple validations: {len(results)} results")
    
    def test_09_confidence_levels(self):
        """Test 9: Confidence Levels"""
        self.logger.info("\n[TEST 9] Confidence Levels")
        
        validator = get_validator()
        
        result = validator.validate(
            output="Test output",
            validation_types=ValidationType.HALLUCINATION
        )
        
        self.assertIsInstance(result.confidence_level, ConfidenceLevel)
        self.assertIn(result.confidence_level, list(ConfidenceLevel))
        
        self.logger.info(f"✅ Confidence level: {result.confidence_level.value}")
    
    def test_10_validation_result_serialization(self):
        """Test 10: ValidationResult Serialization"""
        self.logger.info("\n[TEST 10] ValidationResult Serialization")
        
        validator = get_validator()
        
        result = validator.validate(
            output="Test",
            validation_types=ValidationType.HALLUCINATION
        )
        
        result_dict = result.to_dict()
        
        self.assertIsInstance(result_dict, dict)
        self.assertIn('is_valid', result_dict)
        self.assertIn('confidence_score', result_dict)
        self.assertIn('validation_type', result_dict)
        
        self.logger.info(f"✅ Serialization: {list(result_dict.keys())}")
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup after all tests"""
        cls.logger.info("=" * 50)
        cls.logger.info("AI Validator Test Suite Complete")
        cls.logger.info("=" * 50)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestAIValidator)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print("AI VALIDATOR TEST SUMMARY")
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
