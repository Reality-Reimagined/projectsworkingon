import { z } from 'zod';

export const CheckoutItemSchema = z.object({
  id: z.string(),
  name: z.string(),
  quantity: z.number().min(1),
  pricePerUnit: z.number().min(0),
});

export type CheckoutItem = z.infer<typeof CheckoutItemSchema>;

export interface CheckoutState {
  items: CheckoutItem[];
  total: number;
  status: 'idle' | 'processing' | 'success' | 'error';
  error?: string;
}