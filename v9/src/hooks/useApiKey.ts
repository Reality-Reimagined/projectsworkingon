import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import { useAuth } from './useAuth';

export function useApiKey() {
  const { user } = useAuth();
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchApiKey = async () => {
    if (!user) return;
    
    try {
      const { data, error } = await supabase
        .from('embroidering')
        .select('api_key')
        .eq('user_id', user.id)
        .single();

      if (error) throw error;
      setApiKey(data.api_key);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch API key');
    } finally {
      setLoading(false);
    }
  };

  const generateApiKey = async () => {
    if (!user) return;

    try {
      setLoading(true);
      const newApiKey = crypto.randomUUID();
      
      const { error } = await supabase
        .from('embroidering')
        .upsert({
          user_id: user.id,
          api_key: newApiKey,
        });

      if (error) throw error;
      setApiKey(newApiKey);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate API key');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApiKey();
  }, [user]);

  return {
    apiKey,
    loading,
    error,
    generateApiKey,
  };
}