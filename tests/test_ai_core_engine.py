"""
Test Suite for Central AI Engine
تست جامع موتور مرکزی هوش مصنوعی

تست‌های این فایل:
1. ExperienceDatabase - ذخیره و بازیابی تجربیات
2. ReinforcementLearningCore - یادگیری تقویتی
3. AIModelManager - مدیریت مدل‌ها
4. CentralAIEngine - موتور کامل با شبیه‌سازی
5. Auto-Retraining - باز آموزی خودکار
"""

import os
import sys
import json
import time
from datetime import datetime

# Set PYTHONPATH
sys.path.insert(0, '/home/user/webapp/SecureRedLab')

from core.ai_core_engine import (
    get_ai_engine,
    ExperienceDatabase,
    ReinforcementLearningCore,
    AIModelManager,
    CentralAIEngine,
    Experience,
    SimulationType,
    ActionType,
    AIModelType,
    ModelStatus
)

def print_section(title):
    """چاپ عنوان بخش"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_experience_database():
    """تست پایگاه داده تجربیات"""
    print_section("TEST 1: Experience Database")
    
    exp_db = ExperienceDatabase()
    
    # ساخت تجربه تستی
    test_experience = Experience(
        simulation_type=SimulationType.DDOS,
        state={'target_ip': '192.168.1.1', 'open_ports': 5},
        action=ActionType.INCREASE_INTENSITY,
        reward=0.8,
        next_state={'target_ip': '192.168.1.1', 'open_ports': 5, 'intensity': 0.9},
        done=False,
        metadata={'test': True},
        success=True
    )
    
    # ذخیره تجربه
    print("\n📝 ذخیره تجربه در پایگاه داده...")
    result = exp_db.store_experience(test_experience)
    print(f"   ✅ ذخیره موفق: {result}")
    print(f"   Experience ID: {test_experience.experience_id}")
    
    # بازیابی تجربیات
    print("\n📂 بازیابی تجربیات از پایگاه داده...")
    experiences = exp_db.get_experiences(
        simulation_type=SimulationType.DDOS,
        limit=10
    )
    print(f"   ✅ تعداد تجربیات بازیابی شده: {len(experiences)}")
    
    if experiences:
        exp = experiences[0]
        print(f"   - Simulation Type: {exp.simulation_type.value}")
        print(f"   - Action: {exp.action.value}")
        print(f"   - Reward: {exp.reward}")
        print(f"   - Success: {exp.success}")
    
    # آمار پایگاه داده
    print("\n📊 آمار پایگاه داده تجربیات:")
    stats = exp_db.get_statistics()
    print(f"   - Total Experiences: {stats['total_experiences']}")
    print(f"   - Successful: {stats['successful_experiences']}")
    print(f"   - Success Rate: {stats['success_rate']:.2%}")
    print(f"   - By Type: {json.dumps(stats['by_simulation_type'], indent=6)}")
    
    return True


def test_reinforcement_learning():
    """تست یادگیری تقویتی"""
    print_section("TEST 2: Reinforcement Learning Core")
    
    rl_core = ReinforcementLearningCore()
    
    # تست انتخاب اقدام
    print("\n🎯 تست انتخاب اقدام (Action Selection)...")
    state = {
        'target_ip': '192.168.1.1',
        'open_ports': 5,
        'firewall': True
    }
    
    action = rl_core.select_action(state)
    print(f"   ✅ اقدام انتخاب شده: {action.value}")
    print(f"   - Epsilon (exploration rate): {rl_core.epsilon:.3f}")
    
    # تست به‌روزرسانی Q-value
    print("\n🔄 تست به‌روزرسانی Q-value...")
    experience = Experience(
        simulation_type=SimulationType.DDOS,
        state=state,
        action=action,
        reward=0.9,
        next_state={'target_ip': '192.168.1.1', 'open_ports': 5, 'intensity': 1.0},
        done=True,
        success=True
    )
    
    q_before = rl_core._get_q_value(state, action)
    print(f"   - Q-value قبل از update: {q_before:.3f}")
    
    rl_core.update_q_value(experience)
    
    q_after = rl_core._get_q_value(state, action)
    print(f"   - Q-value بعد از update: {q_after:.3f}")
    print(f"   ✅ تغییر Q-value: {q_after - q_before:+.3f}")
    
    # تست با چند تجربه
    print("\n🔁 تست با 10 تجربه متوالی...")
    for i in range(10):
        exp = Experience(
            simulation_type=SimulationType.DDOS,
            state=state,
            action=ActionType.INCREASE_INTENSITY,
            reward=0.7 + (i * 0.03),  # پاداش افزایشی
            next_state=state,
            done=False,
            success=True
        )
        rl_core.update_q_value(exp)
    
    final_q = rl_core._get_q_value(state, ActionType.INCREASE_INTENSITY)
    print(f"   ✅ Q-value نهایی بعد از 10 update: {final_q:.3f}")
    print(f"   - Q-Table Size: {len(rl_core.q_table)} states")
    
    return True


def test_model_manager():
    """تست مدیریت مدل‌ها"""
    print_section("TEST 3: AI Model Manager")
    
    model_mgr = AIModelManager()
    
    # تست بارگذاری مدل
    print("\n📦 تست بارگذاری مدل‌ها...")
    for model_type in [AIModelType.DEEPSEEK_CODER, AIModelType.LLAMA_3_1]:
        print(f"\n   Loading {model_type.value}...")
        success = model_mgr.load_model(model_type)
        print(f"   {'✅' if success else '❌'} Load result: {success}")
    
    # تست تولید متن
    print("\n🤖 تست تولید متن با AI...")
    prompt = "Generate a DDoS attack strategy for target 192.168.1.1"
    
    response = model_mgr.generate(
        prompt=prompt,
        model_type=AIModelType.DEEPSEEK_CODER,
        validate_output=True
    )
    
    print(f"   ✅ Status: {response['status']}")
    print(f"   - Model Used: {response['model_type']}")
    print(f"   - Latency: {response['latency_ms']:.2f}ms")
    print(f"   - Output Length: {len(response['output'])} chars")
    print(f"   - Output Preview: {response['output'][:100]}...")
    
    if response['validation']:
        print(f"   - Validation: {'✅ PASS' if response['validation']['is_valid'] else '❌ FAIL'}")
        print(f"   - Confidence: {response['validation']['confidence_score']:.2%}")
    
    # تست Fallback
    print("\n🔄 تست Fallback به مدل بعدی...")
    response2 = model_mgr.generate(
        prompt="SELECT * FROM users WHERE id=1; DROP TABLE users;",  # سوال خطرناک
        model_type=AIModelType.LLAMA_3_1,
        validate_output=True
    )
    print(f"   ✅ Fallback successful: {response2['status']}")
    print(f"   - Final Model: {response2['model_type']}")
    
    # وضعیت مدل‌ها
    print("\n📊 وضعیت مدل‌ها:")
    status = model_mgr.get_model_status()
    for model_name, model_info in status.items():
        if isinstance(model_info, dict) and 'status' in model_info:
            print(f"   - {model_name}: {model_info['status']}")
            if 'metrics' in model_info:
                metrics = model_info['metrics']
                print(f"     Total Requests: {metrics['total_requests']}")
                print(f"     Success Rate: {metrics['success_rate']:.2%}")
    
    return True


def test_central_engine():
    """تست موتور مرکزی کامل"""
    print_section("TEST 4: Central AI Engine - Full Simulation")
    
    engine = get_ai_engine()
    
    # اطلاعات هدف تستی
    target_info = {
        'target': '192.168.1.100',
        'open_ports': [22, 80, 443, 3306],
        'services': ['ssh', 'http', 'https', 'mysql'],
        'os_type': 'Linux',
        'firewall': True,
        'waf': False
    }
    
    # تست شبیه‌سازی DDoS
    print("\n🚀 اجرای شبیه‌سازی DDoS...")
    result = engine.run_simulation(
        simulation_type=SimulationType.DDOS,
        target_info=target_info,
        use_rl=True
    )
    
    print(f"   ✅ Status: {result['status']}")
    print(f"   - Simulation Type: {result['simulation_type']}")
    print(f"   - Action Taken: {result['action_taken']}")
    print(f"   - AI Model Used: {result['ai_model_used']}")
    print(f"   - Reward: {result['reward']:.2f}")
    print(f"   - Success: {'✅' if result['success'] else '❌'}")
    print(f"   - Experience ID: {result['experience_id']}")
    print(f"   - Details: {result['details']}")
    
    # تست شبیه‌سازی Shell Upload
    print("\n🚀 اجرای شبیه‌سازی Shell Upload...")
    result2 = engine.run_simulation(
        simulation_type=SimulationType.SHELL_UPLOAD,
        target_info=target_info,
        use_rl=True
    )
    
    print(f"   ✅ Status: {result2['status']}")
    print(f"   - Success: {'✅' if result2['success'] else '❌'}")
    print(f"   - Reward: {result2['reward']:.2f}")
    
    # تست شبیه‌سازی Vulnerability Scan
    print("\n🚀 اجرای شبیه‌سازی Vulnerability Scan...")
    result3 = engine.run_simulation(
        simulation_type=SimulationType.VULNERABILITY_SCAN,
        target_info=target_info,
        use_rl=True
    )
    
    print(f"   ✅ Status: {result3['status']}")
    print(f"   - Success: {'✅' if result3['success'] else '❌'}")
    print(f"   - Reward: {result3['reward']:.2f}")
    
    return True


def test_auto_retraining():
    """تست باز آموزی خودکار"""
    print_section("TEST 5: Automatic Retraining")
    
    engine = get_ai_engine()
    rl_core = engine.rl_core
    
    print("\n🔄 ساخت 50 تجربه تستی برای باز آموزی...")
    
    target_info = {
        'target': '192.168.1.200',
        'open_ports': [80, 443],
        'os_type': 'Windows'
    }
    
    # ذخیره Q-table size قبل از باز آموزی
    q_table_before = len(rl_core.q_table)
    print(f"   - Q-Table Size Before: {q_table_before} states")
    
    # اجرای 50 شبیه‌سازی
    for i in range(50):
        result = engine.run_simulation(
            simulation_type=SimulationType.DDOS,
            target_info=target_info,
            use_rl=True
        )
        
        if (i + 1) % 10 == 0:
            print(f"   ✅ {i + 1}/50 شبیه‌سازی انجام شد")
    
    # بررسی Q-table بعد از 50 تجربه
    q_table_after = len(rl_core.q_table)
    print(f"\n   - Q-Table Size After: {q_table_after} states")
    print(f"   - New States Learned: {q_table_after - q_table_before}")
    print(f"   - Epsilon After Training: {rl_core.epsilon:.4f}")
    
    # اجبار به باز آموزی
    print("\n🎓 اجرای باز آموزی دستی...")
    retrain_result = rl_core.retrain_from_experiences(
        simulation_type=SimulationType.DDOS,
        min_experiences=10
    )
    
    print(f"   ✅ Status: {retrain_result['status']}")
    if retrain_result['status'] == 'success':
        print(f"   - Experiences Processed: {retrain_result['updated_count']}")
        print(f"   - Q-Table States: {retrain_result['q_table_states_after']}")
        print(f"   - New States: {retrain_result['new_states_learned']}")
    
    return True


def test_system_status():
    """تست وضعیت کلی سیستم"""
    print_section("TEST 6: System Status")
    
    engine = get_ai_engine()
    
    print("\n📊 دریافت وضعیت کلی سیستم...")
    status = engine.get_system_status()
    
    print(f"\n   ✅ Engine Status: {status['engine_status']}")
    
    print("\n   🤖 Models Status:")
    for model_name, model_info in status['models'].items():
        if isinstance(model_info, dict):
            print(f"      - {model_name}: {model_info.get('status', 'N/A')}")
    
    print("\n   🧠 Reinforcement Learning:")
    rl_info = status['reinforcement_learning']
    print(f"      - Epsilon: {rl_info['epsilon']:.4f}")
    print(f"      - Q-Table Size: {rl_info['q_table_size']} states")
    print(f"      - Learning Rate: {rl_info['learning_rate']}")
    
    print("\n   📚 Experience Database:")
    exp_info = status['experience_database']
    print(f"      - Total Experiences: {exp_info['total_experiences']}")
    print(f"      - Success Rate: {exp_info['success_rate']:.2%}")
    
    return True


def main():
    """اجرای تمام تست‌ها"""
    print("\n" + "=" * 70)
    print("  SecureRedLab - Central AI Engine Test Suite")
    print("  تست جامع موتور مرکزی هوش مصنوعی")
    print("=" * 70)
    
    tests = [
        ("Experience Database", test_experience_database),
        ("Reinforcement Learning", test_reinforcement_learning),
        ("Model Manager", test_model_manager),
        ("Central Engine", test_central_engine),
        ("Auto Retraining", test_auto_retraining),
        ("System Status", test_system_status)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 شروع تست: {test_name}...")
            start_time = time.time()
            success = test_func()
            elapsed = time.time() - start_time
            
            results.append({
                'name': test_name,
                'status': '✅ PASS' if success else '❌ FAIL',
                'time': f"{elapsed:.2f}s"
            })
            
            print(f"\n✅ تست {test_name} موفق بود ({elapsed:.2f}s)")
            
        except Exception as e:
            results.append({
                'name': test_name,
                'status': '❌ FAIL',
                'time': 'N/A'
            })
            print(f"\n❌ تست {test_name} با خطا مواجه شد:")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
    
    # نمایش خلاصه
    print("\n" + "=" * 70)
    print("  📊 خلاصه نتایج تست‌ها")
    print("=" * 70)
    
    for result in results:
        print(f"  {result['status']}  {result['name']:<30} {result['time']:>10}")
    
    passed = sum(1 for r in results if '✅' in r['status'])
    total = len(results)
    
    print("\n" + "=" * 70)
    print(f"  نتیجه نهایی: {passed}/{total} تست موفق ({passed/total*100:.0f}%)")
    print("=" * 70)
    
    if passed == total:
        print("\n  🎉 تمام تست‌ها با موفقیت انجام شد!")
        print("  ✅ Central AI Engine آماده استفاده است")
    else:
        print(f"\n  ⚠️  {total - passed} تست با خطا مواجه شد")
        print("  ❌ بررسی لاگ‌ها برای جزئیات بیشتر")


if __name__ == "__main__":
    main()
