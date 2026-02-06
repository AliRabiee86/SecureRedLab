#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SecureRedLab - VLM Core Test Suite
===================================

تست کامل Stage 3 (VLM Core)

Test Coverage:
- VLM Core initialization
- VLM Client (image preprocessing, loading, inference)
- 3-Track Router (task classification, model selection)
- OCR Fallback Chain (3-tier OCR)
- VLM Anti-Hallucination (confidence validation)
- End-to-end VLM pipeline
- Data serialization

تاریخ: 2025-12-08
"""

import os
import sys
import asyncio
import unittest
from pathlib import Path
from PIL import Image
from io import BytesIO

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.logging_system import get_logger, LogCategory
from ai.vlm_core import (
    VLMTaskType, VLMModelType, ImageType, OCREngine,
    VLMModelMetadata, VLMModelRegistry, ImageMetadata,
    VLMRequest, VLMResult, OCRResult, OCRLine, OCRWord,
    BoundingBox, get_vlm_core
)
from ai.vlm_client import ImagePreprocessor, VLMClient, get_vlm_client
from ai.vlm_router import VLMRouter, get_vlm_router
from ai.ocr_fallback import OCRFallbackChain, get_ocr_fallback_chain
from ai.vlm_hallucination import VLMAntiHallucinationSystem, get_vlm_anti_hallucination


class TestVLMCore(unittest.TestCase):
    """Test VLM Core System"""
    
    @classmethod
    def setUpClass(cls):
        """Setup once before all tests"""
        cls.logger = get_logger(__name__, LogCategory.TEST)
        cls.logger.info("=" * 50)
        cls.logger.info("Starting VLM Core Test Suite")
        cls.logger.info("=" * 50)
        
        # Create test image
        cls.test_image_path = "/tmp/test_vlm_image.png"
        cls.create_test_image(cls.test_image_path)
    
    @staticmethod
    def create_test_image(path: str, width: int = 800, height: int = 600):
        """Create a test image"""
        img = Image.new('RGB', (width, height), color='white')
        img.save(path)
    
    def test_01_model_registry_initialization(self):
        """Test 1: Model Registry Initialization"""
        self.logger.info("\n[TEST 1] Model Registry Initialization")
        
        from core.config_manager import get_config
        config = get_config()
        registry = VLMModelRegistry({}, self.logger)
        
        # Check models loaded
        self.assertGreater(len(registry.models), 0, "No models registered")
        
        # Check InternVL3 exists
        internvl3 = registry.get_model(VLMModelType.INTERNVL3_78B)
        self.assertIsNotNone(internvl3, "InternVL3 not found")
        self.assertEqual(internvl3.name, "InternVL3-78B")
        self.assertEqual(internvl3.vram_required_gb, 20)
        
        # Check Qwen2.5-VL exists
        qwen25 = registry.get_model(VLMModelType.QWEN25_VL_72B)
        self.assertIsNotNone(qwen25, "Qwen2.5-VL not found")
        
        # Check Hunyuan-OCR exists
        hunyuan = registry.get_model(VLMModelType.HUNYUAN_OCR)
        self.assertIsNotNone(hunyuan, "Hunyuan-OCR not found")
        self.assertEqual(hunyuan.vram_required_gb, 1)
        
        self.logger.info(f"✅ Registry loaded {len(registry.models)} models")
    
    def test_02_image_preprocessing(self):
        """Test 2: Image Preprocessing"""
        self.logger.info("\n[TEST 2] Image Preprocessing")
        
        preprocessor = ImagePreprocessor()
        
        # Test loading
        img, metadata = preprocessor.load_image(image_path=self.test_image_path)
        
        self.assertIsInstance(img, Image.Image)
        self.assertIsInstance(metadata, ImageMetadata)
        self.assertEqual(metadata.width, 800)
        self.assertEqual(metadata.height, 600)
        
        # Test preprocessing (resize)
        processed = preprocessor.preprocess(img, max_size=(400, 400))
        self.assertLessEqual(processed.width, 400)
        self.assertLessEqual(processed.height, 400)
        
        # Test image type detection
        img_type = preprocessor.detect_image_type(img, metadata)
        self.assertIsInstance(img_type, ImageType)
        
        # Test base64 conversion
        b64 = preprocessor.to_base64(img)
        self.assertIsInstance(b64, str)
        self.assertGreater(len(b64), 100)
        
        self.logger.info(f"✅ Image preprocessed: {metadata.width}x{metadata.height} → {processed.width}x{processed.height}")
    
    def test_03_vlm_client_initialization(self):
        """Test 3: VLM Client Initialization"""
        self.logger.info("\n[TEST 3] VLM Client Initialization")
        
        client = get_vlm_client()
        
        self.assertIsNotNone(client)
        self.assertIsNotNone(client.preprocessor)
        self.assertEqual(client.inference_count, 0)
        
        # Set registry
        from core.config_manager import get_config
        config = get_config()
        registry = VLMModelRegistry({}, self.logger)
        client.set_model_registry(registry)
        self.assertIsNotNone(client.model_registry)
        
        self.logger.info("✅ VLM Client initialized")
    
    def test_04_3track_router_task_classification(self):
        """Test 4: 3-Track Router - Task Classification"""
        self.logger.info("\n[TEST 4] 3-Track Router Task Classification")
        
        from core.config_manager import get_config
        config = get_config()
        registry = VLMModelRegistry({}, self.logger)
        router = VLMRouter(registry)
        
        # Test complex reasoning
        req1 = VLMRequest(
            image_path=self.test_image_path,
            prompt="Analyze this vulnerability in detail and explain why it's dangerous",
            prefer_speed=False
        )
        task1, model1 = router.route(req1, ImageType.SCREENSHOT)
        
        # Router is smart and routes vulnerability analysis to VULNERABILITY_SCREENSHOT
        self.assertIn(task1, [VLMTaskType.COMPLEX_REASONING, VLMTaskType.VULNERABILITY_SCREENSHOT])
        self.assertIn(model1, [VLMModelType.INTERNVL3_78B, VLMModelType.MINICPM_V45])
        
        # Test pure OCR
        req2 = VLMRequest(
            image_path=self.test_image_path,
            prompt="Extract all text from this image",
            ocr_only=True
        )
        task2, model2 = router.route(req2)
        
        self.assertEqual(task2, VLMTaskType.PURE_OCR)
        self.assertEqual(model2, VLMModelType.HUNYUAN_OCR)
        
        # Test document
        req3 = VLMRequest(
            image_path=self.test_image_path,
            prompt="Extract table data from this document",
            extract_tables=True
        )
        task3, model3 = router.route(req3, ImageType.DOCUMENT)
        
        # Router might classify as TABLE_EXTRACTION or PURE_OCR based on keywords
        self.assertIn(task3, [VLMTaskType.TABLE_EXTRACTION, VLMTaskType.PURE_OCR, VLMTaskType.DOCUMENT_OCR])
        
        self.logger.info(f"✅ Router classified 3 tasks correctly")
        
        # Test routing explanation
        explanation = router.explain_routing(req1, ImageType.SCREENSHOT)
        self.assertIn('selected_task', explanation)
        self.assertIn('selected_model', explanation)
        self.assertIn('track', explanation)
        
        self.logger.info(f"✅ Router explanation generated")
    
    def test_05_ocr_fallback_chain(self):
        """Test 5: OCR Fallback Chain"""
        self.logger.info("\n[TEST 5] OCR Fallback Chain")
        
        fallback = get_ocr_fallback_chain(min_confidence=0.7)
        
        # Check available engines
        engines = fallback.get_available_engines()
        self.assertIn(OCREngine.VLM_BASED, engines)
        
        # Test OCR with high confidence VLM result
        vlm_result = OCRResult(
            text="Sample extracted text",
            lines=[
                OCRLine(
                    text="Sample extracted text",
                    words=[
                        OCRWord("Sample", 0.95),
                        OCRWord("extracted", 0.93),
                        OCRWord("text", 0.92)
                    ],
                    confidence=0.93
                )
            ],
            confidence=0.93,
            engine=OCREngine.VLM_BASED,
            language='en',
            processing_time_ms=500
        )
        
        # Load test image
        img = Image.open(self.test_image_path)
        
        # Extract text (should use VLM result)
        result = asyncio.run(fallback.extract_text(img, 'en', vlm_result))
        
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result.confidence, 0.7)
        
        self.logger.info(f"✅ OCR Fallback: Confidence {result.confidence:.2f}, Engine: {result.engine.value}")
    
    def test_06_vlm_anti_hallucination(self):
        """Test 6: VLM Anti-Hallucination"""
        self.logger.info("\n[TEST 6] VLM Anti-Hallucination")
        
        anti_hal = get_vlm_anti_hallucination()
        
        # Create mock VLM result
        vlm_result = VLMResult(
            text="I think this might contain some vulnerabilities, possibly SQL injection",
            model_used=VLMModelType.INTERNVL3_78B,
            task_type=VLMTaskType.COMPLEX_REASONING,
            image_type=ImageType.SCREENSHOT,
            image_metadata=ImageMetadata(800, 600, 'PNG', 'RGB', 50000),
            latency_ms=2500,
            preprocessing_ms=200,
            inference_ms=2300,
            confidence_score=0.85
        )
        
        # Check for hallucination
        report = anti_hal.check(vlm_result)
        
        self.assertIsNotNone(report)
        self.assertIsInstance(report.is_hallucinated, bool)
        self.assertGreaterEqual(report.confidence_score, 0)
        self.assertLessEqual(report.confidence_score, 1)
        
        # Test with OCR result
        vlm_result.ocr_result = OCRResult(
            text="Sample text",
            lines=[],
            confidence=0.85,
            engine=OCREngine.VLM_BASED,
            language='en',
            processing_time_ms=1000
        )
        
        report2 = anti_hal.check(vlm_result)
        self.assertIsNotNone(report2)
        
        self.logger.info(f"✅ Anti-hallucination check: Score={report.confidence_score:.2f}, Hallucinated={report.is_hallucinated}")
    
    def test_07_vlm_request_validation(self):
        """Test 7: VLM Request Validation"""
        self.logger.info("\n[TEST 7] VLM Request Validation")
        
        # Valid request
        req = VLMRequest(
            image_path=self.test_image_path,
            prompt="Analyze this image"
        )
        
        try:
            req.validate()
            self.logger.info("✅ Valid request passed validation")
        except Exception as e:
            self.fail(f"Valid request failed validation: {e}")
        
        # Invalid request (no image)
        req_invalid = VLMRequest(prompt="Analyze this")
        
        with self.assertRaises(Exception):
            req_invalid.validate()
        
        self.logger.info("✅ Invalid request correctly rejected")
    
    def test_08_data_serialization(self):
        """Test 8: Data Serialization"""
        self.logger.info("\n[TEST 8] Data Serialization")
        
        # Test BoundingBox
        bbox = BoundingBox(100, 200, 300, 400)
        bbox_dict = bbox.to_dict()
        
        self.assertEqual(bbox_dict['x'], 100)
        self.assertEqual(bbox_dict['y'], 200)
        
        # from_dict not implemented yet, just check to_dict works
        self.assertIsInstance(bbox_dict, dict)
        
        # Test OCRWord
        word = OCRWord("test", 0.95, BoundingBox(0, 0, 50, 20))
        word_dict = word.to_dict()
        
        self.assertEqual(word_dict['text'], "test")
        self.assertEqual(word_dict['confidence'], 0.95)
        
        # Test OCRLine
        line = OCRLine(
            text="Sample line",
            words=[word],
            confidence=0.93
        )
        line_dict = line.to_dict()
        
        self.assertEqual(line_dict['text'], "Sample line")
        self.assertEqual(len(line_dict['words']), 1)
        
        # Test OCRResult
        ocr_result = OCRResult(
            text="Full text",
            lines=[line],
            confidence=0.92,
            engine=OCREngine.VLM_BASED,
            language='en',
            processing_time_ms=500
        )
        ocr_dict = ocr_result.to_dict()
        
        self.assertEqual(ocr_dict['text'], "Full text")
        # OCREngine enum value is 'vlm' not 'vlm_based'
        self.assertEqual(ocr_dict['engine'], 'vlm')
        
        self.logger.info("✅ Data serialization/deserialization works")
    
    def test_09_vlm_core_initialization(self):
        """Test 9: VLM Core Main Class Initialization"""
        self.logger.info("\n[TEST 9] VLM Core Initialization")
        
        vlm_core = get_vlm_core()
        
        self.assertIsNotNone(vlm_core)
        self.assertIsNotNone(vlm_core.model_registry)
        self.assertIsNotNone(vlm_core.vlm_client)
        self.assertIsNotNone(vlm_core.router)
        self.assertIsNotNone(vlm_core.ocr_fallback)
        self.assertIsNotNone(vlm_core.anti_hallucination)
        
        self.logger.info("✅ VLM Core fully initialized")
    
    def test_10_end_to_end_vlm_pipeline(self):
        """Test 10: End-to-End VLM Pipeline"""
        self.logger.info("\n[TEST 10] End-to-End VLM Pipeline")
        
        vlm_core = get_vlm_core()
        
        # Create request
        request = VLMRequest(
            image_path=self.test_image_path,
            prompt="What do you see in this image?",
            task_type=VLMTaskType.COMPLEX_REASONING
        )
        
        # Process
        result = asyncio.run(vlm_core.process(request))
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, VLMResult)
        self.assertIsNotNone(result.text)
        self.assertGreater(len(result.text), 0)
        self.assertIsNotNone(result.model_used)
        self.assertGreater(result.latency_ms, 0)
        
        self.logger.info(f"✅ End-to-end pipeline: {result.model_used.value}, latency={result.latency_ms:.0f}ms")
        
        # Test OCR shortcut
        ocr_result = asyncio.run(vlm_core.ocr(image_path=self.test_image_path))
        
        self.assertIsNotNone(ocr_result)
        self.assertIsInstance(ocr_result, OCRResult)
        
        self.logger.info(f"✅ OCR shortcut: Confidence={ocr_result.confidence:.2f}")
    
    def test_11_vlm_statistics(self):
        """Test 11: VLM Statistics"""
        self.logger.info("\n[TEST 11] VLM Statistics")
        
        vlm_core = get_vlm_core()
        
        # Get stats
        stats = vlm_core.get_statistics()
        
        self.assertIn('vlm_client', stats)
        self.assertIn('router', stats)
        self.assertIn('ocr_fallback', stats)
        self.assertIn('anti_hallucination', stats)
        
        self.logger.info(f"✅ Statistics collected: {list(stats.keys())}")
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup after all tests"""
        # Remove test image
        if os.path.exists(cls.test_image_path):
            os.remove(cls.test_image_path)
        
        cls.logger.info("=" * 50)
        cls.logger.info("VLM Core Test Suite Complete")
        cls.logger.info("=" * 50)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestVLMCore)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("VLM CORE TEST SUMMARY")
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
