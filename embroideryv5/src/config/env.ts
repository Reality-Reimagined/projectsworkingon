import { z } from 'zod';

const envSchema = z.object({
  VITE_SUPABASE_URL: z.string().url(),
  VITE_SUPABASE_ANON_KEY: z.string().min(1),
  VITE_STRIPE_PUBLIC_KEY: z.string().min(1),
  VITE_API_URL: z.string().url(),
});

export const env = envSchema.parse(import.meta.env);