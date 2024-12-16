import { type PricingPlan } from '../types';

export const PRICING_PLANS: readonly PricingPlan[] = [
  {
    id: 'pay-per-image',
    name: 'Pay Per Image',
    price: 5,
    features: [
      'High-quality conversion',
      'Unlimited edits per image',
      'All file formats supported',
      'Download instantly',
      'Basic support'
    ],
    stripeProductId: 'price_per_image'
  },
  {
    id: 'monthly',
    name: 'Monthly Bundle',
    price: 100,
    features: [
      '50 images per month',
      'Unlimited edits',
      'All file formats supported',
      'Priority support',
      'Bulk processing',
      'API access'
    ],
    stripeProductId: 'price_monthly_bundle'
  }
] as const;