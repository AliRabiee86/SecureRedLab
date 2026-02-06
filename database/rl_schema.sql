-- ============================================================================
-- SecureRedLab - RL Engine Database Schema
-- ============================================================================
-- این schema تمام جداول مورد نیاز موتور یادگیری تقویتی را ایجاد می‌کند
--
-- جداول:
--   1. rl_experiences   - تجربیات Agent (Experience Replay Buffer)
--   2. rl_episodes      - Episode های کامل
--   3. rl_models        - Model های ذخیره شده (versioning)
--   4. rl_agent_stats   - آمار عملکرد Agent ها
--   5. rl_training_logs - Log های بازآموزی
--
-- نسخه: 1.0.0
-- تاریخ: 2025-12-07
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- Table 1: rl_experiences (تجربیات Agent)
-- ============================================================================
CREATE TABLE IF NOT EXISTS rl_experiences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Episode info
    episode_id VARCHAR(255) NOT NULL,
    agent_type VARCHAR(50) NOT NULL,  -- 'ddos', 'shell', 'extract', 'deface', 'behavior'
    step_number INTEGER NOT NULL,
    
    -- Experience tuple: (s, a, r, s', done)
    state JSONB NOT NULL,             -- RLState serialized
    action JSONB NOT NULL,            -- RLAction serialized
    reward REAL NOT NULL,
    next_state JSONB NOT NULL,        -- Next RLState
    done BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Priority Experience Replay
    priority REAL DEFAULT 1.0,
    td_error REAL DEFAULT 0.0,        -- Temporal Difference error
    
    -- Metadata
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_version INTEGER DEFAULT 1,
    
    -- Indexes
    CONSTRAINT unique_experience UNIQUE (episode_id, step_number)
);

CREATE INDEX idx_rl_experiences_agent ON rl_experiences(agent_type);
CREATE INDEX idx_rl_experiences_episode ON rl_experiences(episode_id);
CREATE INDEX idx_rl_experiences_priority ON rl_experiences(priority DESC);
CREATE INDEX idx_rl_experiences_timestamp ON rl_experiences(timestamp DESC);

-- ============================================================================
-- Table 2: rl_episodes (Episode های کامل)
-- ============================================================================
CREATE TABLE IF NOT EXISTS rl_episodes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    episode_id VARCHAR(255) UNIQUE NOT NULL,
    agent_type VARCHAR(50) NOT NULL,
    
    -- Timing
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_seconds REAL,
    
    -- Results
    total_reward REAL NOT NULL DEFAULT 0.0,
    steps_count INTEGER NOT NULL DEFAULT 0,
    success BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Metrics
    success_rate REAL,                -- نرخ موفقیت
    average_reward REAL,              -- میانگین reward
    total_damage REAL,                -- آسیب کل
    stealth_score REAL,               -- امتیاز مخفی ماندن
    detection_count INTEGER DEFAULT 0, -- دفعات شناسایی
    
    -- Model info
    model_version INTEGER DEFAULT 1,
    epsilon REAL,                     -- Exploration rate at episode start
    
    -- Target info
    target_info JSONB,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_rl_episodes_agent ON rl_episodes(agent_type);
CREATE INDEX idx_rl_episodes_success ON rl_episodes(success);
CREATE INDEX idx_rl_episodes_reward ON rl_episodes(total_reward DESC);
CREATE INDEX idx_rl_episodes_start_time ON rl_episodes(start_time DESC);

-- ============================================================================
-- Table 3: rl_models (Model های ذخیره شده)
-- ============================================================================
CREATE TABLE IF NOT EXISTS rl_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_type VARCHAR(50) NOT NULL,
    version INTEGER NOT NULL,
    
    -- Model data (serialized)
    model_data BYTEA NOT NULL,        -- Pickled model (Q-table, Neural Network weights, etc.)
    model_type VARCHAR(50) NOT NULL,   -- 'q_table', 'dqn', 'policy_gradient', etc.
    
    -- Training info
    training_episodes INTEGER NOT NULL,
    training_steps INTEGER NOT NULL,
    training_duration_seconds REAL,
    
    -- Performance metrics
    average_reward REAL,
    success_rate REAL,
    convergence_score REAL,           -- میزان همگرایی
    
    -- Hyperparameters
    hyperparameters JSONB,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,   -- آیا این model فعلی است؟
    notes TEXT,
    
    CONSTRAINT unique_agent_version UNIQUE (agent_type, version)
);

CREATE INDEX idx_rl_models_agent ON rl_models(agent_type);
CREATE INDEX idx_rl_models_active ON rl_models(agent_type, is_active);
CREATE INDEX idx_rl_models_version ON rl_models(agent_type, version DESC);

-- ============================================================================
-- Table 4: rl_agent_stats (آمار عملکرد Agent ها)
-- ============================================================================
CREATE TABLE IF NOT EXISTS rl_agent_stats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_type VARCHAR(50) NOT NULL,
    
    -- Aggregate statistics
    total_episodes INTEGER DEFAULT 0,
    total_steps INTEGER DEFAULT 0,
    total_successes INTEGER DEFAULT 0,
    total_failures INTEGER DEFAULT 0,
    
    -- Performance metrics
    average_reward REAL,
    average_episode_length REAL,
    success_rate REAL,
    average_stealth_score REAL,
    
    -- Learning progress
    current_epsilon REAL,
    current_model_version INTEGER,
    last_training_time TIMESTAMP,
    total_training_time_seconds REAL,
    
    -- Timestamps
    first_episode_time TIMESTAMP,
    last_episode_time TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_agent_stats UNIQUE (agent_type)
);

CREATE INDEX idx_rl_agent_stats_success_rate ON rl_agent_stats(success_rate DESC);
CREATE INDEX idx_rl_agent_stats_updated ON rl_agent_stats(updated_at DESC);

-- ============================================================================
-- Table 5: rl_training_logs (Log های بازآموزی)
-- ============================================================================
CREATE TABLE IF NOT EXISTS rl_training_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_type VARCHAR(50) NOT NULL,
    model_version INTEGER NOT NULL,
    
    -- Training details
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_seconds REAL,
    
    batch_size INTEGER,
    epochs INTEGER,
    learning_rate REAL,
    
    -- Training results
    initial_loss REAL,
    final_loss REAL,
    loss_improvement REAL,
    convergence_reached BOOLEAN DEFAULT FALSE,
    
    -- Performance improvement
    reward_before_training REAL,
    reward_after_training REAL,
    reward_improvement REAL,
    
    -- Metadata
    training_data_size INTEGER,      -- تعداد experiences استفاده شده
    hyperparameters JSONB,
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_rl_training_logs_agent ON rl_training_logs(agent_type);
CREATE INDEX idx_rl_training_logs_version ON rl_training_logs(model_version DESC);
CREATE INDEX idx_rl_training_logs_start_time ON rl_training_logs(start_time DESC);

-- ============================================================================
-- Triggers for updated_at
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_rl_episodes_updated_at BEFORE UPDATE
    ON rl_episodes FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rl_agent_stats_updated_at BEFORE UPDATE
    ON rl_agent_stats FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Initial data: RL Agent Stats (یک رکورد برای هر Agent)
-- ============================================================================
INSERT INTO rl_agent_stats (agent_type, total_episodes, average_reward, success_rate, current_epsilon, current_model_version)
VALUES 
    ('ddos', 0, 0.0, 0.0, 1.0, 1),
    ('shell', 0, 0.0, 0.0, 1.0, 1),
    ('extract', 0, 0.0, 0.0, 1.0, 1),
    ('deface', 0, 0.0, 0.0, 1.0, 1),
    ('behavior', 0, 0.0, 0.0, 1.0, 1)
ON CONFLICT (agent_type) DO NOTHING;

-- ============================================================================
-- Useful Views
-- ============================================================================

-- View 1: Recent Episodes Summary
CREATE OR REPLACE VIEW v_recent_episodes AS
SELECT 
    agent_type,
    episode_id,
    start_time,
    duration_seconds,
    total_reward,
    steps_count,
    success,
    success_rate,
    stealth_score,
    model_version
FROM rl_episodes
ORDER BY start_time DESC
LIMIT 100;

-- View 2: Agent Performance Summary
CREATE OR REPLACE VIEW v_agent_performance AS
SELECT 
    agent_type,
    total_episodes,
    total_successes,
    total_failures,
    success_rate,
    average_reward,
    average_episode_length,
    current_model_version,
    last_training_time
FROM rl_agent_stats
ORDER BY success_rate DESC;

-- View 3: Top Experiences (High Priority)
CREATE OR REPLACE VIEW v_top_experiences AS
SELECT 
    agent_type,
    episode_id,
    step_number,
    reward,
    priority,
    td_error,
    timestamp
FROM rl_experiences
ORDER BY priority DESC, td_error DESC
LIMIT 1000;

-- ============================================================================
-- Indexes for Performance
-- ============================================================================
-- ایندکس‌های اضافی برای کوئری‌های پرکاربرد

CREATE INDEX IF NOT EXISTS idx_rl_experiences_reward ON rl_experiences(reward DESC);
CREATE INDEX IF NOT EXISTS idx_rl_experiences_agent_episode ON rl_experiences(agent_type, episode_id);
CREATE INDEX IF NOT EXISTS idx_rl_episodes_agent_success ON rl_episodes(agent_type, success);

-- ============================================================================
-- Comments for Documentation
-- ============================================================================
COMMENT ON TABLE rl_experiences IS 'تجربیات Agent ها برای Experience Replay Buffer';
COMMENT ON TABLE rl_episodes IS 'Episode های کامل با نتایج و متریک‌ها';
COMMENT ON TABLE rl_models IS 'Model های ذخیره شده با versioning';
COMMENT ON TABLE rl_agent_stats IS 'آمار عملکرد کلی هر Agent';
COMMENT ON TABLE rl_training_logs IS 'Log های بازآموزی Model ها';

-- ============================================================================
-- Success!
-- ============================================================================
-- Schema created successfully
-- Run this with: psql -U secureredlab_user -d secureredlab_production -f rl_schema.sql
