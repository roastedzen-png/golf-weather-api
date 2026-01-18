-- Add leads table for lead management
-- Run this in Railway PostgreSQL console or via psql

-- Create leads table
CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,

    -- Lead Source
    source VARCHAR(50) NOT NULL, -- 'api_key_request', 'contact_form', 'newsletter'

    -- Contact Information
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    company VARCHAR(255),

    -- API Key Request Specific
    use_case VARCHAR(255),
    description TEXT,
    expected_volume VARCHAR(50),
    api_key_id INTEGER REFERENCES api_keys(id),

    -- Contact Form Specific
    subject VARCHAR(500),
    message TEXT,

    -- Lead Quality
    is_high_value BOOLEAN DEFAULT FALSE,
    priority VARCHAR(20) DEFAULT 'normal', -- 'low', 'normal', 'high', 'urgent'

    -- Status Tracking
    status VARCHAR(50) DEFAULT 'new', -- 'new', 'contacted', 'qualified', 'converted', 'lost'
    assigned_to VARCHAR(255),

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    contacted_at TIMESTAMP,

    -- Notes
    internal_notes TEXT,

    -- Metadata
    ip_address VARCHAR(50),
    user_agent TEXT,
    referrer VARCHAR(500)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS ix_leads_source ON leads(source);
CREATE INDEX IF NOT EXISTS ix_leads_email ON leads(email);
CREATE INDEX IF NOT EXISTS ix_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS ix_leads_is_high_value ON leads(is_high_value);
CREATE INDEX IF NOT EXISTS ix_leads_created_at ON leads(created_at DESC);

-- Composite index for common queries
CREATE INDEX IF NOT EXISTS ix_leads_source_status ON leads(source, status);

-- Add extra columns to api_keys table for lead capture data (if they don't exist)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='api_keys' AND column_name='name') THEN
        ALTER TABLE api_keys ADD COLUMN name VARCHAR(255);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='api_keys' AND column_name='email') THEN
        ALTER TABLE api_keys ADD COLUMN email VARCHAR(255);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='api_keys' AND column_name='company') THEN
        ALTER TABLE api_keys ADD COLUMN company VARCHAR(255);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='api_keys' AND column_name='use_case') THEN
        ALTER TABLE api_keys ADD COLUMN use_case VARCHAR(255);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='api_keys' AND column_name='description') THEN
        ALTER TABLE api_keys ADD COLUMN description TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='api_keys' AND column_name='expected_volume') THEN
        ALTER TABLE api_keys ADD COLUMN expected_volume VARCHAR(50);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='api_keys' AND column_name='status') THEN
        ALTER TABLE api_keys ADD COLUMN status VARCHAR(20) DEFAULT 'active';
    END IF;
END $$;

-- Create email index on api_keys if it doesn't exist
CREATE INDEX IF NOT EXISTS ix_api_keys_email ON api_keys(email);

-- Success message
SELECT 'Leads table and api_keys updates created successfully!' as result;
