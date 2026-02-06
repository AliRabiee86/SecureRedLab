#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SecureRedLab - RL Engine Test Suite
====================================

این فایل تست‌های جامع برای RL Engine را اجرا می‌کند و عملکرد آن را تأیید می‌نماید.

Tests:
1. Agent Initialization
2. Episode Management (start, store experiences, end)
3. Database Integration (save/load experiences, models)
4. Training & Replay Buffer
5. Model Versioning

Usage:
    python tests/test_rl_engine.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from datetime import datetime

from core.rl_engine import (
    get_rl_engine, 
    RLAgentType, 
    RLState, 
    RLAction,
    RLExperience
)
from core.logging_system import get_logger, LogCategory


logger = get_logger(__name__, LogCategory.TEST)


class TestRLEngine:
    """Test suite for RL Engine"""
    
    def __init__(self):
        self.rl_engine = get_rl_engine()
        self.test_agent = RLAgentType.SHELL
        self.episode_id = None
        self.tests_passed = 0
        self.tests_failed = 0
    
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASSED" if passed else "❌ FAILED"
        
        if passed:
            self.tests_passed += 1
            logger.info(
                f"{status}: {test_name}",
                f"{status}: {test_name}",
                context={'details': details}
            )
        else:
            self.tests_failed += 1
            logger.error(
                f"{status}: {test_name}",
                f"{status}: {test_name}",
                context={'details': details}
            )
    
    def create_mock_state(self, stage: int = 0) -> RLState:
        """Create a mock RLState for testing"""
        return RLState(
            # Target info
            target_ip='192.168.1.100',
            target_ports=[22, 80, 443, 3306],
            target_os='Linux',
            target_services=['ssh', 'http', 'https', 'mysql'],
            
            # Network info
            network_latency=50.0,
            bandwidth=1000.0,
            firewall_active=True,
            ids_active=False,
            
            # Attack info
            attack_stage=stage,
            time_elapsed=30.0 + stage * 10,
            packets_sent=1000 + stage * 500,
            success_rate=0.5 + stage * 0.1,
            
            # Historical
            previous_actions=['recon', 'scan', 'exploit'][:stage],
            detection_count=0
        )
    
    def create_mock_action(self, action_id: int = 0) -> RLAction:
        """Create a mock RLAction for testing"""
        actions = [
            {'type': 'exploit', 'params': {'port': 22, 'payload': 'shell_v1'}},
            {'type': 'escalate', 'params': {'method': 'sudo', 'target': 'root'}},
            {'type': 'persist', 'params': {'method': 'cron', 'interval': 300}},
        ]
        
        action_data = actions[action_id % len(actions)]
        return RLAction(
            action_type=action_data['type'],
            parameters=action_data['params']
        )
    
    def test_1_agent_initialization(self):
        """Test 1: Agent Initialization"""
        test_name = "Agent Initialization"
        
        try:
            # Check if all agents are created
            for agent_type in RLAgentType:
                assert agent_type in self.rl_engine.agents, f"Agent {agent_type} not initialized"
                assert agent_type in self.rl_engine.replay_buffers, f"Buffer for {agent_type} not created"
                assert agent_type in self.rl_engine.reward_functions, f"Reward function for {agent_type} not created"
            
            self.log_test(test_name, True, f"All {len(RLAgentType)} agents initialized")
        
        except AssertionError as e:
            self.log_test(test_name, False, str(e))
    
    def test_2_episode_start(self):
        """Test 2: Start Episode"""
        test_name = "Start Episode"
        
        try:
            state = self.create_mock_state()
            self.episode_id = self.rl_engine.start_episode(
                self.test_agent,
                state,
                context={'test': True}
            )
            
            assert self.episode_id is not None, "Episode ID is None"
            assert self.test_agent in self.rl_engine.current_episodes, "Episode not tracked"
            assert self.rl_engine.current_episodes[self.test_agent] == self.episode_id
            
            self.log_test(test_name, True, f"Episode started: {self.episode_id}")
        
        except Exception as e:
            self.log_test(test_name, False, str(e))
    
    def test_3_action_selection(self):
        """Test 3: Action Selection"""
        test_name = "Action Selection"
        
        try:
            state = self.create_mock_state()
            
            # Test exploration
            action_explore = self.rl_engine.select_action(self.test_agent, state, explore=True)
            assert isinstance(action_explore, int), "Action is not an integer"
            
            # Test exploitation
            action_exploit = self.rl_engine.select_action(self.test_agent, state, explore=False)
            assert isinstance(action_exploit, int), "Action is not an integer"
            
            self.log_test(test_name, True, f"Explore: {action_explore}, Exploit: {action_exploit}")
        
        except Exception as e:
            self.log_test(test_name, False, str(e))
    
    def test_4_store_experiences(self):
        """Test 4: Store Experiences"""
        test_name = "Store Experiences"
        
        try:
            # Simulate 10 steps in an episode
            for step in range(10):
                state = self.create_mock_state(stage=step)
                action = self.create_mock_action(action_id=step)
                next_state = self.create_mock_state(stage=step + 1)
                
                reward = 5.0 + step * 1.0  # Increasing reward
                done = (step == 9)  # Last step
                
                self.rl_engine.store_experience(
                    self.test_agent,
                    state,
                    action,
                    reward,
                    next_state,
                    done,
                    priority=1.0 + step * 0.1
                )
            
            # Check replay buffer
            buffer_size = len(self.rl_engine.replay_buffers[self.test_agent])
            assert buffer_size == 10, f"Expected 10 experiences, got {buffer_size}"
            
            self.log_test(test_name, True, f"Stored 10 experiences, buffer size: {buffer_size}")
        
        except Exception as e:
            self.log_test(test_name, False, str(e))
    
    def test_5_end_episode(self):
        """Test 5: End Episode"""
        test_name = "End Episode"
        
        try:
            metrics = {
                'success_rate': 0.8,
                'average_reward': 9.5,
                'total_damage': 75.0,
                'stealth_score': 0.6
            }
            
            self.rl_engine.end_episode(
                self.test_agent,
                success=True,
                total_reward=95.0,
                metrics=metrics
            )
            
            # Check statistics
            stats = self.rl_engine.get_statistics(self.test_agent)
            assert stats['total_episodes'] > 0, "Episode count not updated"
            assert stats['total_reward'] > 0, "Total reward not updated"
            
            self.log_test(test_name, True, f"Episode ended. Stats: {stats}")
        
        except Exception as e:
            self.log_test(test_name, False, str(e))
    
    def test_6_training(self):
        """Test 6: Agent Training"""
        test_name = "Agent Training"
        
        try:
            # Train with batch size = 5
            self.rl_engine.train_agent(
                self.test_agent,
                batch_size=5,
                epochs=2
            )
            
            # Check that training increased training_steps
            agent = self.rl_engine.agents[self.test_agent]
            assert agent.training_steps > 0, "Training steps not increased"
            
            self.log_test(test_name, True, f"Training completed. Steps: {agent.training_steps}")
        
        except Exception as e:
            self.log_test(test_name, False, str(e))
    
    def test_7_state_serialization(self):
        """Test 7: State Serialization"""
        test_name = "State Serialization (to_dict/from_dict)"
        
        try:
            original_state = self.create_mock_state(stage=5)
            
            # Serialize
            state_dict = original_state.to_dict()
            assert isinstance(state_dict, dict), "to_dict() failed"
            
            # Deserialize
            restored_state = RLState.from_dict(state_dict)
            assert restored_state.target_ip == original_state.target_ip
            assert restored_state.attack_stage == original_state.attack_stage
            
            self.log_test(test_name, True, "State serialization works correctly")
        
        except Exception as e:
            self.log_test(test_name, False, str(e))
    
    def test_8_action_serialization(self):
        """Test 8: Action Serialization"""
        test_name = "Action Serialization (to_dict/from_dict)"
        
        try:
            original_action = self.create_mock_action(action_id=2)
            
            # Serialize
            action_dict = original_action.to_dict()
            assert isinstance(action_dict, dict), "to_dict() failed"
            
            # Deserialize
            restored_action = RLAction.from_dict(action_dict)
            assert restored_action.action_type == original_action.action_type
            assert restored_action.parameters == original_action.parameters
            
            self.log_test(test_name, True, "Action serialization works correctly")
        
        except Exception as e:
            self.log_test(test_name, False, str(e))
    
    def test_9_database_integration(self):
        """Test 9: Database Integration (if DB available)"""
        test_name = "Database Integration"
        
        if not self.rl_engine.db_available:
            self.log_test(test_name, True, "Skipped (DB not available - graceful degradation working)")
            return
        
        try:
            # Test save model
            self.rl_engine.save_model_to_db(self.test_agent)
            
            # Test load model
            self.rl_engine.load_model_from_db(self.test_agent)
            
            self.log_test(test_name, True, "Model save/load to DB successful")
        
        except Exception as e:
            self.log_test(test_name, False, str(e))
    
    def test_10_should_retrain(self):
        """Test 10: Retrain Logic"""
        test_name = "Retrain Logic"
        
        try:
            # Manually set episode count for testing
            self.rl_engine.total_episodes[self.test_agent] = 100
            
            should_retrain = self.rl_engine.should_retrain(self.test_agent)
            assert should_retrain == True, "should_retrain() logic failed"
            
            self.log_test(test_name, True, "Retrain logic correct (100 episodes)")
        
        except Exception as e:
            self.log_test(test_name, False, str(e))
    
    def run_all_tests(self):
        """Run all tests"""
        logger.info(
            "=" * 60,
            "=" * 60
        )
        logger.info(
            "شروع تست‌های RL Engine",
            "Starting RL Engine Test Suite"
        )
        logger.info(
            "=" * 60,
            "=" * 60
        )
        
        # Run tests in order
        self.test_1_agent_initialization()
        self.test_2_episode_start()
        self.test_3_action_selection()
        self.test_4_store_experiences()
        self.test_5_end_episode()
        self.test_6_training()
        self.test_7_state_serialization()
        self.test_8_action_serialization()
        self.test_9_database_integration()
        self.test_10_should_retrain()
        
        # Print summary
        logger.info(
            "=" * 60,
            "=" * 60
        )
        logger.info(
            f"نتیجه کلی: {self.tests_passed} موفق، {self.tests_failed} ناموفق",
            f"Test Summary: {self.tests_passed} passed, {self.tests_failed} failed"
        )
        logger.info(
            "=" * 60,
            "=" * 60
        )
        
        return self.tests_failed == 0


if __name__ == "__main__":
    test_suite = TestRLEngine()
    success = test_suite.run_all_tests()
    
    sys.exit(0 if success else 1)
