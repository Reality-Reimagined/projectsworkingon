import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import { useAuth } from './useAuth';

export function useImageTracking() {
  const { user } = useAuth();
  const [imagesRemaining, setImagesRemaining] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) return;

    const fetchImageCount = async () => {
      try {
        const { data, error } = await supabase
          .from('embroidering')
          .select('images_remaining, images_generated')
          .eq('user_id', user.id)
          .single();

        if (error) throw error;
        setImagesRemaining(data.images_remaining);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch image count');
      } finally {
        setLoading(false);
      }
    };

    fetchImageCount();
  }, [user]);

  return {
    imagesRemaining,
    loading,
    error,
  };
}