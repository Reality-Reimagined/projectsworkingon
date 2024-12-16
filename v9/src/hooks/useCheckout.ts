import { useState } from 'react';
import { loadStripe } from '@stripe/stripe-js';
import { env } from '../config';
import { supabase } from '../lib/supabase';
import type { CheckoutItem } from '../types/checkout';

const stripePromise = loadStripe(env.VITE_STRIPE_PUBLIC_KEY);

export function useCheckout() {
  const [status, setStatus] = useState<'idle' | 'processing' | 'success' | 'error'>('idle');
  const [error, setError] = useState<string | null>(null);

  const createCheckoutSession = async (items: CheckoutItem[]) => {
    try {
      setStatus('processing');
      const stripe = await stripePromise;
      if (!stripe) throw new Error('Stripe failed to initialize');

      const { data: session, error: sessionError } = await supabase
        .from('checkout_sessions')
        .insert({
          items,
          total: items.reduce((sum, item) => sum + item.quantity * item.pricePerUnit, 0),
        })
        .select()
        .single();

      if (sessionError) throw sessionError;

      const result = await stripe.redirectToCheckout({
        sessionId: session.stripe_session_id,
      });

      if (result.error) throw result.error;

      setStatus('success');
    } catch (err) {
      setStatus('error');
      setError(err instanceof Error ? err.message : 'Failed to create checkout session');
    }
  };

  return {
    status,
    error,
    createCheckoutSession,
  };
}