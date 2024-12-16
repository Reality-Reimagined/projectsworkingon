import { type PricingPlan } from '../types';

export const PRICING_PLANS: readonly PricingPlan[] = [
  {
    id: 'basic',
    name: 'Basic',
    price: 9.99,
    features: [
      'Up to 10 conversions/month',
      'Standard quality',
      'Email support'
    ],
    stripeProductId: 'price_basic123'
  },
  {
    id: 'pro',
    name: 'Professional',
    price: 29.99,
    features: [
      'Unlimited conversions',
      'Premium quality',
      'Priority support',
      'Advanced stitch types'
    ],
    stripeProductId: 'price_pro123'
  }
] as const;