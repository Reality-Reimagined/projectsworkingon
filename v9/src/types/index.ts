export interface User {
  id: string;
  email: string;
  full_name?: string;
  avatar_url?: string;
  subscription_status?: 'active' | 'inactive' | 'trial';
}

export interface PricingPlan {
  id: string;
  name: string;
  price: number;
  features: string[];
  stripeProductId: string;
}

export interface ConversionJob {
  id: string;
  userId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  inputFile: string;
  outputFile?: string;
  createdAt: string;
  settings: {
    stitchDensity: number;
    stitchType: string;
  };
}