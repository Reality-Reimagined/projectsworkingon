-- Create embroidering table
CREATE TABLE embroidering (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  api_key TEXT UNIQUE,
  images_generated INTEGER DEFAULT 0,
  images_remaining INTEGER,
  last_reset_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  subscription_tier TEXT,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_user_id ON embroidering(user_id);
CREATE INDEX idx_api_key ON embroidering(api_key);

-- Create RLS policies
ALTER TABLE embroidering ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own embroidering data"
  ON embroidering FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can update own embroidering data"
  ON embroidering FOR UPDATE
  USING (auth.uid() = user_id);

-- Create function to handle monthly reset
CREATE OR REPLACE FUNCTION reset_monthly_image_count()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.last_reset_date + INTERVAL '1 month' < CURRENT_TIMESTAMP THEN
    NEW.images_generated := 0;
    NEW.images_remaining := 
      CASE 
        WHEN NEW.subscription_tier = 'monthly' THEN 50
        ELSE NEW.images_remaining
      END;
    NEW.last_reset_date := CURRENT_TIMESTAMP;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for monthly reset
CREATE TRIGGER monthly_reset_trigger
  BEFORE UPDATE ON embroidering
  FOR EACH ROW
  EXECUTE FUNCTION reset_monthly_image_count();