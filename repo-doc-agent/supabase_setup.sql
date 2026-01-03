-- RepoDocAgent Database Schema for Supabase
-- Run this in Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Repositories table
CREATE TABLE IF NOT EXISTS repositories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    url TEXT NOT NULL,
    name TEXT,
    description TEXT,
    status TEXT NOT NULL CHECK (status IN ('pending', 'cloning', 'analyzing', 'generating_docs', 'completed', 'failed')),
    last_commit_hash TEXT,
    branch TEXT NOT NULL DEFAULT 'main',
    monitoring_enabled BOOLEAN NOT NULL DEFAULT true,
    webhook_id TEXT,
    error_message TEXT,
    last_analyzed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Documentation table
CREATE TABLE IF NOT EXISTS documentation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    repo_id UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    version INTEGER NOT NULL DEFAULT 1,
    commit_hash TEXT NOT NULL,
    content JSONB NOT NULL,
    file_count INTEGER NOT NULL DEFAULT 0,
    lines_of_code INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Monitoring jobs table
CREATE TABLE IF NOT EXISTS monitoring_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    repo_id UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    status TEXT NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    trigger_type TEXT NOT NULL,
    changes_detected JSONB,
    error_message TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_repositories_status ON repositories(status);
CREATE INDEX IF NOT EXISTS idx_repositories_created_at ON repositories(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_documentation_repo_id ON documentation(repo_id);
CREATE INDEX IF NOT EXISTS idx_documentation_created_at ON documentation(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_monitoring_jobs_repo_id ON monitoring_jobs(repo_id);
CREATE INDEX IF NOT EXISTS idx_monitoring_jobs_status ON monitoring_jobs(status);

-- Enable Row Level Security (RLS) - Optional but recommended
ALTER TABLE repositories ENABLE ROW LEVEL SECURITY;
ALTER TABLE documentation ENABLE ROW LEVEL SECURITY;
ALTER TABLE monitoring_jobs ENABLE ROW LEVEL SECURITY;

-- Create policies to allow all operations (adjust based on your auth needs)
CREATE POLICY "Allow all operations on repositories" ON repositories FOR ALL USING (true);
CREATE POLICY "Allow all operations on documentation" ON documentation FOR ALL USING (true);
CREATE POLICY "Allow all operations on monitoring_jobs" ON monitoring_jobs FOR ALL USING (true);
