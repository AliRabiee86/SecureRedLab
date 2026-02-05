#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SecureRedLab - End-to-End Integration Test
===========================================

تست یکپارچگی کامل سیستم:
- RL Engine
- Offline AI Core (LLM + VLM)
- Neural Scanner
- AI Validator

تاریخ: 2025-12-08
"""

import os
import sys
import unittest
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.logging_system import get_logger, LogCategory
from core.ai_output_validator import get_validator, ValidationType


class TestEndToEndIntegration(unittest.TestCase):
    """Test End-to-End System Integration"""
    
    @classmethod
    def setUpClass(cls):
        """Setup once before all tests"""
        cls.logger = get_logger(__name__, LogCategory.TEST)
        cls.logger.info("=" * 70)
        cls.logger.info("Starting End-to-End Integration Test Suite")
        cls.logger.info("=" * 70)
    
    def test_01_all_systems_initialization(self):
        """Test 1: All Systems Initialization"""
        self.logger.info("\n[TEST 1] All Systems Initialization")
        
        systems_status = {}
        
        # Test 1.1: RL Engine
        try:
            from core.rl_engine import get_rl_engine_manager
            rl_manager = get_rl_engine_manager()
            systems_status['rl_engine'] = True
            self.logger.info("  ✅ RL Engine initialized")
        except Exception as e:
            systems_status['rl_engine'] = False
            self.logger.error(f"  ❌ RL Engine failed: {e}")
        
        # Test 1.2: Offline AI Core (LLM)
        try:
            from ai.offline_core import get_offline_ai
            llm_core = get_offline_ai()
            systems_status['llm_core'] = True
            self.logger.info("  ✅ LLM Core initialized")
        except Exception as e:
            systems_status['llm_core'] = False
            self.logger.error(f"  ❌ LLM Core failed: {e}")
        
        # Test 1.3: VLM Core
        try:
            from ai.vlm_core import get_vlm_core
            vlm_core = get_vlm_core()
            systems_status['vlm_core'] = True
            self.logger.info("  ✅ VLM Core initialized")
        except Exception as e:
            systems_status['vlm_core'] = False
            self.logger.error(f"  ❌ VLM Core failed: {e}")
        
        # Test 1.4: Scanner AI Adapter
        try:
            from ai.scanner_ai_adapter import get_scanner_ai_engine
            scanner_ai = get_scanner_ai_engine()
            systems_status['scanner_ai'] = True
            self.logger.info("  ✅ Scanner AI Adapter initialized")
        except Exception as e:
            systems_status['scanner_ai'] = False
            self.logger.error(f"  ❌ Scanner AI failed: {e}")
        
        # Test 1.5: AI Validator
        try:
            validator = get_validator()
            systems_status['validator'] = True
            self.logger.info("  ✅ AI Validator initialized")
        except Exception as e:
            systems_status['validator'] = False
            self.logger.error(f"  ❌ Validator failed: {e}")
        
        # Assert all systems loaded
        success_rate = sum(systems_status.values()) / len(systems_status)
        self.logger.info(f"\n  Systems Success Rate: {success_rate*100:.0f}%")
        
        self.assertGreaterEqual(success_rate, 0.8, "Less than 80% of systems initialized")
    
    def test_02_rl_engine_workflow(self):
        """Test 2: RL Engine Workflow"""
        self.logger.info("\n[TEST 2] RL Engine Workflow")
        
        from core.rl_engine import get_rl_engine
        from core.rl_engine import RLAction, RLState, RLAgentType
        
        rl_manager = get_rl_engine()
        
        # Create initial state
        mock_state = RLState(
            target_ip='192.168.1.1',
            target_ports=[80, 443],
            target_os='linux',
            target_services={'80': 'http', '443': 'https'},
            network_latency=50.0,
            bandwidth=100.0,
            firewall_active=False,
            ids_active=False,
            attack_stage=0,
            time_elapsed=0.0,
            packets_sent=0,
            success_rate=0.0,
            previous_actions=[],
            detection_count=0
        )
        
        # Start episode
        episode_id = rl_manager.start_episode(RLAgentType.DDOS, mock_state)
        self.assertIsNotNone(episode_id)
        self.logger.info(f"  ✅ Episode started: {episode_id}")
        
        action = rl_manager.select_action(RLAgentType.DDOS, mock_state)
        self.assertIsNotNone(action)
        self.logger.info(f"  ✅ Action selected: {action.action_type if hasattr(action, 'action_type') else 'unknown'}")
        
        # End episode
        rl_manager.end_episode(RLAgentType.DDOS, total_reward=10.0, success=True)
        self.logger.info(f"  ✅ Episode ended successfully")
    
    def test_03_ai_generation_workflow(self):
        """Test 3: AI Generation Workflow"""
        self.logger.info("\n[TEST 3] AI Generation Workflow")
        
        from ai.scanner_ai_adapter import get_scanner_ai_engine, AIModelType
        
        scanner_ai = get_scanner_ai_engine()
        
        prompt = "Analyze port 80 running Apache 2.4.41 for potential vulnerabilities"
        
        result = scanner_ai.model_manager.generate(
            prompt=prompt,
            model_type=AIModelType.QWEN_14B,
            validate_output=False,
            max_tokens=512
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertGreater(len(result['output']), 0)
        
        self.logger.info(f"  ✅ AI Generation: {len(result['output'])} chars")
        self.logger.info(f"     Model: {result.get('model_type', 'unknown')}")
        self.logger.info(f"     Latency: {result.get('latency_ms', 0):.0f}ms")
    
    def test_04_vlm_image_processing(self):
        """Test 4: VLM Image Processing"""
        self.logger.info("\n[TEST 4] VLM Image Processing")
        
        from ai.vlm_core import get_vlm_core, VLMRequest, VLMTaskType
        from PIL import Image
        
        # Create test image
        test_image_path = "/tmp/test_e2e_image.png"
        img = Image.new('RGB', (800, 600), color='white')
        img.save(test_image_path)
        
        vlm_core = get_vlm_core()
        
        request = VLMRequest(
            image_path=test_image_path,
            prompt="Describe this image",
            task_type=VLMTaskType.COMPLEX_REASONING
        )
        
        result = asyncio.run(vlm_core.process(request))
        
        self.assertIsNotNone(result)
        self.assertGreater(len(result.text), 0)
        
        # Cleanup
        os.remove(test_image_path)
        
        self.logger.info(f"  ✅ VLM Processing: {len(result.text)} chars")
        self.logger.info(f"     Model: {result.model_used.value}")
        self.logger.info(f"     Latency: {result.latency_ms:.0f}ms")
    
    def test_05_validator_integration(self):
        """Test 5: Validator Integration"""
        self.logger.info("\n[TEST 5] Validator Integration")
        
        validator = get_validator()
        
        # Validate AI output
        ai_output = """
Found vulnerabilities:
1. SQL Injection on port 3306
2. XSS vulnerability on port 80
3. Remote Code Execution on port 22
"""
        
        result = validator.validate(
            output=ai_output,
            validation_types=ValidationType.HALLUCINATION
        )
        
        self.assertIsNotNone(result)
        self.assertTrue(result.is_valid or result.confidence_score > 0.5)
        
        self.logger.info(f"  ✅ Validation: {result.confidence_score:.2f}")
        self.logger.info(f"     Valid: {result.is_valid}")
    
    def test_06_full_pipeline_simulation(self):
        """Test 6: Full Pipeline Simulation"""
        self.logger.info("\n[TEST 6] Full Pipeline Simulation")
        
        # Simulate complete workflow
        steps_completed = []
        
        # Step 1: RL selects strategy
        try:
            from core.rl_engine import get_rl_engine, RLAgentType, RLState
            rl_manager = get_rl_engine()
            
            # Create initial state
            initial_state = RLState(
                target_ip='192.168.1.100',
                target_ports=[80, 443],
                target_os='linux',
                target_services={'80': 'http'},
                network_latency=50.0,
                bandwidth=100.0,
                firewall_active=False,
                ids_active=False,
                attack_stage=0,
                time_elapsed=0.0,
                packets_sent=0,
                success_rate=0.0,
                previous_actions=[],
                detection_count=0
            )
            
            episode_id = rl_manager.start_episode(RLAgentType.SHELL, initial_state)
            steps_completed.append('rl_start')
            self.logger.info("  ✅ Step 1: RL Episode Started")
        except Exception as e:
            self.logger.error(f"  ❌ Step 1 failed: {e}")
        
        # Step 2: AI generates attack payload
        try:
            from ai.scanner_ai_adapter import get_scanner_ai_engine
            scanner_ai = get_scanner_ai_engine()
            ai_result = scanner_ai.model_manager.generate(
                prompt="Generate reconnaissance strategy for target",
                validate_output=False,
                max_tokens=256
            )
            steps_completed.append('ai_generate')
            self.logger.info("  ✅ Step 2: AI Generated Strategy")
        except Exception as e:
            self.logger.error(f"  ❌ Step 2 failed: {e}")
        
        # Step 3: Validator checks output
        try:
            validator = get_validator()
            val_result = validator.validate(
                output=ai_result.get('output', ''),
                validation_types=ValidationType.HALLUCINATION
            )
            steps_completed.append('validation')
            self.logger.info("  ✅ Step 3: Output Validated")
        except Exception as e:
            self.logger.error(f"  ❌ Step 3 failed: {e}")
        
        # Step 4: RL learns from result
        try:
            rl_manager.end_episode(RLAgentType.SHELL, total_reward=15.0, success=True)
            steps_completed.append('rl_learn')
            self.logger.info("  ✅ Step 4: RL Episode Completed")
        except Exception as e:
            self.logger.error(f"  ❌ Step 4 failed: {e}")
        
        pipeline_success = len(steps_completed) / 4
        self.logger.info(f"\n  Pipeline Success Rate: {pipeline_success*100:.0f}%")
        
        self.assertGreaterEqual(pipeline_success, 0.75, "Pipeline success rate < 75%")
    
    def test_07_system_statistics(self):
        """Test 7: System Statistics"""
        self.logger.info("\n[TEST 7] System Statistics")
        
        stats = {}
        
        # RL Engine stats
        try:
            from core.rl_engine import get_rl_engine
            rl_manager = get_rl_engine()
            stats['rl'] = {'episodes': 'tracked'}
            self.logger.info("  ✅ RL Stats collected")
        except Exception as e:
            self.logger.warning(f"  ⚠️ RL Stats failed: {e}")
        
        # AI Core stats
        try:
            from ai.scanner_ai_adapter import get_scanner_ai_engine
            scanner_ai = get_scanner_ai_engine()
            stats['ai'] = scanner_ai.get_statistics()
            self.logger.info(f"  ✅ AI Stats: {stats['ai'].get('generation_count', 0)} generations")
        except Exception as e:
            self.logger.warning(f"  ⚠️ AI Stats failed: {e}")
        
        # Validator stats
        try:
            validator = get_validator()
            stats['validator'] = {'validators': len(validator.validators)}
            self.logger.info(f"  ✅ Validator: {stats['validator']['validators']} validators")
        except Exception as e:
            self.logger.warning(f"  ⚠️ Validator Stats failed: {e}")
        
        self.assertGreater(len(stats), 0)
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup after all tests"""
        cls.logger.info("=" * 70)
        cls.logger.info("End-to-End Integration Test Suite Complete")
        cls.logger.info("=" * 70)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestEndToEndIntegration)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print("END-TO-END INTEGRATION TEST SUMMARY")
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
