"""
SecureRedLab Database Schema - PostgreSQL
طرح پایگاه داده برای پلتفرم تحقیقاتی شبیه‌سازی تیم قرمز

This schema supports:
- Support-only authentication and approval system
- AI/ML simulation tracking
- Compliance logging with tamper-proof mechanisms
- Persian language support
- Post-quantum encryption ready

تمامی حقوق محفوظ است - پلتفرم تحقیقاتی آکادمیک
"""

# Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "btree_gist";

-- Create database
create database secureredlab with owner postgres encoding 'UTF8';
\c secureredlab;

-- Create schemas for better organization
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS simulations;
CREATE SCHEMA IF NOT EXISTS ai_models;
CREATE SCHEMA IF NOT EXISTS compliance;
CREATE SCHEMA IF NOT EXISTS monitoring;

-- Set timezone to Tehran (Persian locale)
SET timezone = 'Asia/Tehran';

-- Support staff authentication table
CREATE TABLE auth.support_staff (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    support_id VARCHAR(50) UNIQUE NOT NULL,  -- e.g., 'admin_001'
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'senior_support', 'support', 'auditor')),
    department VARCHAR(100),
    institution VARCHAR(100) NOT NULL,
    
    -- Post-quantum encrypted credentials
    encrypted_password_hash TEXT NOT NULL,  -- Argon2id + post-quantum salt
    
    -- Two-factor authentication
    totp_secret_encrypted TEXT,
    backup_codes_encrypted TEXT[],
    
    -- Permissions and scopes
    can_initiate_simulations BOOLEAN DEFAULT FALSE,
    can_adjust_bot_power BOOLEAN DEFAULT FALSE,
    can_access_live_monitoring BOOLEAN DEFAULT FALSE,
    can_export_reports BOOLEAN DEFAULT FALSE,
    can_manage_ai_models BOOLEAN DEFAULT FALSE,
    
    -- Status and validity
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    failed_login_attempts INT DEFAULT 0 CHECK (failed_login_attempts >= 0),
    account_locked_until TIMESTAMP,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES auth.support_staff(id),
    
    -- Compliance and legal
    security_clearance_level VARCHAR(20) CHECK (security_clearance_level IN ('basic', 'intermediate', 'advanced', 'top_secret')),
    legal_authority_scope TEXT,  -- JSON array of legal authorities
    
    -- Indexes for performance
    CONSTRAINT idx_support_staff_active UNIQUE (support_id, is_active) WHERE is_active = true
);

-- Approval authorities table (FBI, IRB, etc.)
CREATE TABLE auth.approval_authorities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    authority_name VARCHAR(100) NOT NULL,  -- e.g., 'FBI', 'University_IRB'
    authority_code VARCHAR(20) UNIQUE NOT NULL,  -- e.g., 'FBI', 'UNIV_IRB'
    contact_person VARCHAR(100),
    contact_email VARCHAR(100),
    contact_phone VARCHAR(20),
    
    -- Approval scope
    can_approve_ddos BOOLEAN DEFAULT FALSE,
    can_approve_penetration BOOLEAN DEFAULT FALSE,
    can_approve_data_extraction BOOLEAN DEFAULT FALSE,
    max_simulation_intensity NUMERIC(3,2) CHECK (max_simulation_intensity BETWEEN 0 AND 1),
    max_simulation_duration INTERVAL,
    
    -- Legal framework
    legal_framework VARCHAR(50),  -- e.g., 'CFAA', 'PCI-DSS'
    jurisdiction VARCHAR(100),
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pre-approval verification requests
CREATE TABLE auth.pre_approvals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id VARCHAR(50) UNIQUE NOT NULL,
    support_staff_id UUID NOT NULL REFERENCES auth.support_staff(id),
    
    -- Target information (simulated only)
    target_description TEXT NOT NULL,
    target_type VARCHAR(50) CHECK (target_type IN ('lab_vm', 'simulated_network', 'test_application', 'docker_container')),
    target_owner VARCHAR(100),  -- e.g., university department
    
    -- Simulation details
    simulation_type VARCHAR(50) NOT NULL CHECK (simulation_type IN (
        'ddos', 'penetration', 'vulnerability_scan', 'deface', 'data_extraction', 'human_behavior'
    )),
    intended_intensity NUMERIC(3,2) CHECK (intended_intensity BETWEEN 0 AND 1),
    estimated_duration INTERVAL,
    bot_count_requested INT CHECK (bot_count_requested BETWEEN 100 AND 1000000),
    
    -- Risk assessment
    risk_level VARCHAR(20) CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    risk_mitigation_plan TEXT,
    
    -- Legal approvals
    fbi_approval_code VARCHAR(50),
    irb_approval_code VARCHAR(50),
    local_police_approval_code VARCHAR(50),
    other_approvals JSONB,  -- Array of {authority: code}
    
    -- Status tracking
    status VARCHAR(30) DEFAULT 'pending' CHECK (status IN (
        'pending', 'under_review', 'approved', 'rejected', 'expired', 'revoked'
    )),
    reviewed_by UUID REFERENCES auth.support_staff(id),
    review_notes TEXT,
    
    -- Time tracking
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP,
    expires_at TIMESTAMP,
    
    -- Tamper-proof hash
    request_hash TEXT GENERATED ALWAYS AS (
        encode(sha256((request_id || support_staff_id::text || requested_at::text)::bytea), 'hex')
    ) STORED,
    
    -- Indexes
    CONSTRAINT idx_pre_approvals_status UNIQUE (status) WHERE status = 'pending',
    CONSTRAINT idx_pre_approvals_active UNIQUE (support_staff_id, status) 
        WHERE status IN ('approved', 'pending')
);

-- Active simulation sessions
CREATE TABLE simulations.active_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(100) UNIQUE NOT NULL,
    pre_approval_id UUID NOT NULL REFERENCES auth.pre_approvals(id),
    support_staff_id UUID NOT NULL REFERENCES auth.support_staff(id),
    
    -- Simulation parameters
    simulation_type VARCHAR(50) NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    current_intensity NUMERIC(3,2) DEFAULT 0.5,
    bot_count INT DEFAULT 1000,
    evasion_rate NUMERIC(3,2) DEFAULT 0.9,
    
    -- AI/ML tracking
    ai_model_used VARCHAR(100),
    ml_optimization_applied BOOLEAN DEFAULT FALSE,
    reinforcement_learning_reward NUMERIC(5,2),
    
    -- Resource limits
    cpu_limit_percent NUMERIC(5,2) DEFAULT 80.00,
    memory_limit_mb INT DEFAULT 8192,
    network_bandwidth_limit_mbps INT DEFAULT 1000,
    
    -- Safety mechanisms
    kill_switch_activated BOOLEAN DEFAULT FALSE,
    anomaly_detected BOOLEAN DEFAULT FALSE,
    safety_violations INT DEFAULT 0 CHECK (safety_violations >= 0),
    
    -- Status
    status VARCHAR(30) DEFAULT 'running' CHECK (status IN (
        'starting', 'running', 'pausing', 'stopped', 'completed', 'failed', 'terminated'
    )),
    
    -- Real-time metrics (updated every 5 seconds)
    current_throughput_gbps NUMERIC(8,2),
    current_requests_per_second INT,
    current_cpu_usage_percent NUMERIC(5,2),
    current_memory_usage_mb INT,
    current_evasion_success_rate NUMERIC(3,2),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI/ML model registry
CREATE TABLE ai_models.model_registry (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(20) NOT NULL,
    model_type VARCHAR(50) CHECK (model_type IN ('tensorflow', 'pytorch', 'huggingface', 'sklearn', 'custom')),
    
    -- Model specifications
    architecture VARCHAR(100),  -- e.g., 'LSTM', 'CNN', 'Transformer'
    parameters_count BIGINT,
    model_size_mb NUMERIC(10,2),
    
    -- Training information
    training_dataset VARCHAR(200),
    training_duration INTERVAL,
    accuracy_percent NUMERIC(5,2),
    loss_value NUMERIC(10,6),
    
    -- Model location
    model_path VARCHAR(500) NOT NULL,
    checksum_sha256 VARCHAR(64) NOT NULL,
    
    -- Usage tracking
    usage_count INT DEFAULT 0,
    last_used TIMESTAMP,
    average_inference_time_ms NUMERIC(8,2),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_production_ready BOOLEAN DEFAULT FALSE,
    
    created_by UUID REFERENCES auth.support_staff(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE (model_name, model_version)
);

-- Compliance audit logs (tamper-proof)
CREATE TABLE compliance.audit_logs (
    id BIGSERIAL PRIMARY KEY,
    event_id UUID DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100) NOT NULL,
    
    -- Actor information
    actor_type VARCHAR(50) CHECK (actor_type IN ('support_staff', 'ai_system', 'automated_process', 'external_system'
    )),
    actor_id VARCHAR(100) NOT NULL,
    actor_name VARCHAR(200),
    
    -- Event details
    event_description TEXT NOT NULL,
    event_data JSONB,
    event_severity VARCHAR(20) CHECK (event_severity IN ('info', 'warning', 'error', 'critical'
    )),
    
    -- Context
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(100),
    
    -- Legal compliance
    legal_framework VARCHAR(50),
    compliance_requirements JSONB,
    
    -- Tamper detection
    previous_hash VARCHAR(64),
    current_hash VARCHAR(64) GENERATED ALWAYS AS (
        encode(sha256((event_id::text || event_type || actor_id || created_at::text)::bytea), 'hex')
    ) STORED,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_audit_logs_event_type (event_type),
    INDEX idx_audit_logs_actor (actor_type, actor_id),
    INDEX idx_audit_logs_created_at (created_at DESC)
);

-- Bot power adjustment logs
CREATE TABLE simulations.bot_power_logs (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    adjustment_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Power adjustment details
    previous_bot_count INT,
    new_bot_count INT,
    previous_intensity NUMERIC(3,2),
    new_intensity NUMERIC(3,2),
    adjustment_reason VARCHAR(200),
    
    -- AI/ML optimization
    ai_model_used VARCHAR(100),
    ml_optimization_type VARCHAR(50),  -- e.g., 'reinforcement_learning', 'genetic_algorithm'
    optimization_score NUMERIC(5,2),
    
    -- Safety checks
    safety_threshold_exceeded BOOLEAN DEFAULT FALSE,
    anomaly_score NUMERIC(3,2),
    
    -- Actor
    adjusted_by VARCHAR(100) NOT NULL,  -- support_staff_id or 'ai_system'
    
    INDEX idx_bot_power_session (session_id, adjustment_timestamp DESC)
);

-- Live monitoring metrics
CREATE TABLE monitoring.real_time_metrics (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    metric_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Performance metrics
    cpu_usage_percent NUMERIC(5,2),
    memory_usage_mb INT,
    network_throughput_gbps NUMERIC(8,2),
    disk_io_rate_mbps NUMERIC(8,2),
    
    -- Attack simulation metrics
    active_bots INT,
    requests_per_second INT,
    evasion_success_rate NUMERIC(3,2),
    detection_rate NUMERIC(3,2),
    
    -- AI/ML metrics
    model_inference_time_ms NUMERIC(8,2),
    learning_accuracy_percent NUMERIC(5,2),
    adaptation_score NUMERIC(5,2),
    
    -- Safety metrics
    safety_violations INT DEFAULT 0,
    kill_switch_triggers INT DEFAULT 0,
    anomaly_alerts INT DEFAULT 0,
    
    INDEX idx_metrics_session_time (session_id, metric_timestamp DESC)
);

-- Persian language support table
CREATE TABLE public.persian_translations (
    id SERIAL PRIMARY KEY,
    translation_key VARCHAR(100) UNIQUE NOT NULL,
    persian_text TEXT NOT NULL,
    context VARCHAR(200),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert common Persian translations
INSERT INTO public.persian_translations (translation_key, persian_text, context) VALUES
('simulation_started', 'شبیه‌سازی با موفقیت آغاز شد', 'Status message'),
('simulation_completed', 'شبیه‌سازی با موفقیت به پایان رسید', 'Status message'),
('bot_power_adjusted', 'قدرت بات توسط هوش مصنوعی تنظیم شد', 'AI optimization'),
('attack_detected', 'حمله شناسایی شد - اقدامات دفاعی فعال شدند', 'Security alert'),
('safety_violation', 'نقض ایمنی شناسایی شد - شبیه‌سازی متوقف شد', 'Safety alert'),
('approval_required', 'تأیید پشتیبانی مورد نیاز است', 'Support requirement'),
('support_only_access', 'دسترسی فقط برای پشتیبانی مجاز است', 'Access control'),
('ml_optimization_active', 'بهینه‌سازی ML فعال است', 'AI status'),
('evasion_rate_high', 'نرخ دور زدن بالا - کیفیت تست عالی', 'Quality metric'),
('simulation_quality', 'کیفیت شبیه‌سازی', 'Quality metric');

-- Create functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for automatic updates
CREATE TRIGGER update_simulations_updated_at 
    BEFORE UPDATE ON simulations.active_sessions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_support_staff_updated_at 
    BEFORE UPDATE ON auth.support_staff 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create indexes for performance optimization
CREATE INDEX idx_sessions_status ON simulations.active_sessions(status);
CREATE INDEX idx_sessions_support_staff ON simulations.active_sessions(support_staff_id);
CREATE INDEX idx_audit_logs_timestamp ON compliance.audit_logs(created_at DESC);
CREATE INDEX idx_bot_power_session_time ON simulations.bot_power_logs(session_id, adjustment_timestamp DESC);
CREATE INDEX idx_metrics_session_timestamp ON monitoring.real_time_metrics(session_id, metric_timestamp DESC);

-- Create views for common queries
CREATE VIEW auth.active_support_staff AS
SELECT * FROM auth.support_staff 
WHERE is_active = true 
AND (account_locked_until IS NULL OR account_locked_until < CURRENT_TIMESTAMP);

CREATE VIEW simulations.running_sessions AS
SELECT * FROM simulations.active_sessions 
WHERE status IN ('starting', 'running', 'pausing');

CREATE VIEW compliance.recent_audit_events AS
SELECT * FROM compliance.audit_logs 
WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
ORDER BY created_at DESC;

-- Grant permissions (to be customized based on deployment)
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA auth TO secureredlab_app;
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA simulations TO secureredlab_app;
-- GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA compliance TO secureredlab_app;
-- GRANT SELECT ON ALL TABLES IN SCHEMA monitoring TO secureredlab_app;
-- GRANT SELECT ON ALL TABLES IN SCHEMA ai_models TO secureredlab_app;

echo "Database schema created successfully!"
echo "طرح پایگاه داده با موفقیت ایجاد شد!"