-- SecureRedLab - RL Engine Database Schema
-- تاریخ ایجاد: 2025-01-15
-- نسخه: 1.0.0

-- ==============================================================================
-- جدول تجربیات RL (Experience Replay)
-- ==============================================================================

CREATE TABLE IF NOT EXISTS rl_experiences (
    id SERIAL PRIMARY KEY,
    agent_type VARCHAR(50) NOT NULL,
    episode_id UUID NOT NULL,
    step_number INTEGER NOT NULL,
    
    -- S: State (وضعیت فعلی)
    state_json JSONB NOT NULL,
    
    -- A: Action (عمل انجام شده)
    action_json JSONB NOT NULL,
    
    -- R: Reward (پاداش دریافتی)
    reward FLOAT NOT NULL,
    
    -- S': Next State (وضعیت بعدی)
    next_state_json JSONB NOT NULL,
    
    -- Done: آیا episode تمام شد؟
    done BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    timestamp TIMESTAMP DEFAULT NOW(),
    success BOOLEAN,
    target_info JSONB,
    
    -- برای Priority Experience Replay
    priority FLOAT DEFAULT 1.0,
    
    -- Performance indexes
    CONSTRAINT unique_experience UNIQUE(episode_id, step_number)
);

CREATE INDEX IF NOT EXISTS idx_rl_experiences_agent_type ON rl_experiences(agent_type);
CREATE INDEX IF NOT EXISTS idx_rl_experiences_episode ON rl_experiences(episode_id);
CREATE INDEX IF NOT EXISTS idx_rl_experiences_timestamp ON rl_experiences(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_rl_experiences_priority ON rl_experiences(priority DESC);

COMMENT ON TABLE rl_experiences IS 'تجربیات یادگیری تقویتی - RL Experiences for replay buffer';
COMMENT ON COLUMN rl_experiences.agent_type IS 'نوع Agent: ddos, shell, extract, deface, behavior';
COMMENT ON COLUMN rl_experiences.priority IS 'اولویت برای Priority Experience Replay';

-- ==============================================================================
-- جدول نتایج Episode
-- ==============================================================================

CREATE TABLE IF NOT EXISTS rl_episodes (
    id UUID PRIMARY KEY,
    agent_type VARCHAR(50) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    
    total_reward FLOAT,
    steps_count INTEGER,
    success BOOLEAN,
    
    -- Metrics
    success_rate FLOAT,
    average_reward FLOAT,
    total_damage FLOAT,
    stealth_score FLOAT,
    
    -- Model version used
    model_version INTEGER,
    
    -- Metadata
    target_info JSONB,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_rl_episodes_agent_type ON rl_episodes(agent_type);
CREATE INDEX IF NOT EXISTS idx_rl_episodes_agent_success ON rl_episodes(agent_type, success);
CREATE INDEX IF NOT EXISTS idx_rl_episodes_start_time ON rl_episodes(start_time DESC);
CREATE INDEX IF NOT EXISTS idx_rl_episodes_total_reward ON rl_episodes(total_reward DESC);

COMMENT ON TABLE rl_episodes IS 'نتایج Episode های RL - Results of RL episodes';
COMMENT ON COLUMN rl_episodes.total_reward IS 'مجموع پاداش در این episode';
COMMENT ON COLUMN rl_episodes.stealth_score IS 'امتیاز مخفی ماندن (0-1)';

-- ==============================================================================
-- جدول مدل‌های آموزش‌دیده
-- ==============================================================================

CREATE TABLE IF NOT EXISTS rl_models (
    id SERIAL PRIMARY KEY,
    agent_type VARCHAR(50) NOT NULL,
    version INTEGER NOT NULL,
    
    model_weights BYTEA NOT NULL,
    
    -- Training metrics
    training_episodes INTEGER,
    average_reward FLOAT,
    success_rate FLOAT,
    
    -- Metadata
    trained_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT FALSE,
    training_duration_seconds INTEGER,
    notes TEXT,
    
    CONSTRAINT unique_agent_version UNIQUE(agent_type, version)
);

CREATE INDEX IF NOT EXISTS idx_rl_models_agent_type ON rl_models(agent_type);
CREATE INDEX IF NOT EXISTS idx_rl_models_is_active ON rl_models(agent_type, is_active);
CREATE INDEX IF NOT EXISTS idx_rl_models_trained_at ON rl_models(trained_at DESC);

COMMENT ON TABLE rl_models IS 'مدل‌های آموزش‌دیده RL - Trained RL models';
COMMENT ON COLUMN rl_models.model_weights IS 'وزن‌های مدل (serialized pickle)';
COMMENT ON COLUMN rl_models.is_active IS 'آیا این مدل فعال است؟';

-- ==============================================================================
-- جدول آمار Agent
-- ==============================================================================

CREATE TABLE IF NOT EXISTS rl_agent_stats (
    id SERIAL PRIMARY KEY,
    agent_type VARCHAR(50) NOT NULL,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    
    -- Daily statistics
    total_episodes INTEGER DEFAULT 0,
    successful_episodes INTEGER DEFAULT 0,
    failed_episodes INTEGER DEFAULT 0,
    
    total_reward FLOAT DEFAULT 0.0,
    average_reward FLOAT DEFAULT 0.0,
    max_reward FLOAT DEFAULT 0.0,
    min_reward FLOAT DEFAULT 0.0,
    
    -- Performance metrics
    average_success_rate FLOAT DEFAULT 0.0,
    average_stealth_score FLOAT DEFAULT 0.0,
    average_damage FLOAT DEFAULT 0.0,
    
    -- Learning progress
    epsilon FLOAT DEFAULT 1.0,
    training_steps INTEGER DEFAULT 0,
    model_version INTEGER DEFAULT 1,
    
    CONSTRAINT unique_agent_date UNIQUE(agent_type, date)
);

CREATE INDEX IF NOT EXISTS idx_rl_agent_stats_agent_type ON rl_agent_stats(agent_type);
CREATE INDEX IF NOT EXISTS idx_rl_agent_stats_date ON rl_agent_stats(date DESC);

COMMENT ON TABLE rl_agent_stats IS 'آمار روزانه Agent های RL - Daily statistics for RL agents';
COMMENT ON COLUMN rl_agent_stats.epsilon IS 'مقدار فعلی epsilon در استراتژی ε-greedy';

-- ==============================================================================
-- View: آمار کلی RL
-- ==============================================================================

CREATE OR REPLACE VIEW v_rl_overall_stats AS
SELECT 
    agent_type,
    COUNT(*) as total_episodes,
    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_episodes,
    AVG(total_reward) as avg_reward,
    AVG(success_rate) as avg_success_rate,
    AVG(stealth_score) as avg_stealth_score,
    MAX(total_reward) as max_reward,
    MIN(total_reward) as min_reward
FROM rl_episodes
GROUP BY agent_type;

COMMENT ON VIEW v_rl_overall_stats IS 'نمای آمار کلی تمام Agentها - Overall statistics view for all agents';

-- ==============================================================================
-- View: بهترین Episodeها
-- ==============================================================================

CREATE OR REPLACE VIEW v_rl_top_episodes AS
SELECT 
    agent_type,
    id as episode_id,
    total_reward,
    success_rate,
    stealth_score,
    total_damage,
    start_time,
    model_version,
    ROW_NUMBER() OVER (PARTITION BY agent_type ORDER BY total_reward DESC) as rank
FROM rl_episodes
WHERE success = true;

COMMENT ON VIEW v_rl_top_episodes IS 'بهترین Episodeها به ترتیب reward - Top episodes by reward';

-- ==============================================================================
-- Function: به‌روزرسانی آمار روزانه
-- ==============================================================================

CREATE OR REPLACE FUNCTION update_rl_daily_stats()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO rl_agent_stats (
        agent_type, date, total_episodes, successful_episodes, 
        failed_episodes, total_reward, average_reward
    )
    VALUES (
        NEW.agent_type,
        CURRENT_DATE,
        1,
        CASE WHEN NEW.success THEN 1 ELSE 0 END,
        CASE WHEN NOT NEW.success THEN 1 ELSE 0 END,
        NEW.total_reward,
        NEW.average_reward
    )
    ON CONFLICT (agent_type, date) 
    DO UPDATE SET
        total_episodes = rl_agent_stats.total_episodes + 1,
        successful_episodes = rl_agent_stats.successful_episodes + 
            CASE WHEN NEW.success THEN 1 ELSE 0 END,
        failed_episodes = rl_agent_stats.failed_episodes + 
            CASE WHEN NOT NEW.success THEN 1 ELSE 0 END,
        total_reward = rl_agent_stats.total_reward + NEW.total_reward,
        average_reward = (rl_agent_stats.total_reward + NEW.total_reward) / 
            (rl_agent_stats.total_episodes + 1);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger برای به‌روزرسانی خودکار آمار
CREATE TRIGGER trg_update_rl_daily_stats
AFTER INSERT ON rl_episodes
FOR EACH ROW
EXECUTE FUNCTION update_rl_daily_stats();

COMMENT ON FUNCTION update_rl_daily_stats IS 'به‌روزرسانی خودکار آمار روزانه - Auto-update daily statistics';

-- ==============================================================================
-- Sample Queries - کوئری‌های نمونه
-- ==============================================================================

-- کوئری 1: آمار کلی هر Agent
-- SELECT * FROM v_rl_overall_stats;

-- کوئری 2: بهترین 10 Episode
-- SELECT * FROM v_rl_top_episodes WHERE rank <= 10;

-- کوئری 3: پیشرفت یادگیری در طول زمان
-- SELECT agent_type, date, average_success_rate, epsilon
-- FROM rl_agent_stats
-- ORDER BY agent_type, date;

-- کوئری 4: تجربیات با بالاترین priority
-- SELECT * FROM rl_experiences
-- WHERE agent_type = 'ddos'
-- ORDER BY priority DESC
-- LIMIT 100;

-- ==============================================================================
-- Indexes for Performance - ایندکس‌ها برای بهینه‌سازی
-- ==============================================================================

-- GIN index برای جستجوی سریع در JSONB
CREATE INDEX IF NOT EXISTS idx_rl_experiences_state_gin ON rl_experiences USING GIN (state_json);
CREATE INDEX IF NOT EXISTS idx_rl_experiences_action_gin ON rl_experiences USING GIN (action_json);
CREATE INDEX IF NOT EXISTS idx_rl_episodes_target_info_gin ON rl_episodes USING GIN (target_info);

-- Partial index برای Episode های موفق
CREATE INDEX IF NOT EXISTS idx_rl_episodes_successful ON rl_episodes(agent_type, total_reward)
WHERE success = true;

-- ==============================================================================
-- End of Migration
-- ==============================================================================
