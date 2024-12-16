import React from 'react';
import { Wand2, Sparkles, Zap, Shield } from 'lucide-react';

export const features = [
  {
    name: 'Automatic Conversion',
    description: 'Upload any image and our AI will convert it into a professional embroidery file format in seconds.',
    icon: <Wand2 className="h-6 w-6 text-white" />,
  },
  {
    name: 'Smart Optimization',
    description: 'Our algorithms optimize stitch patterns for the best possible output quality and efficiency.',
    icon: <Sparkles className="h-6 w-6 text-white" />,
  },
  {
    name: 'Fast Processing',
    description: 'Get your converted files instantly. Perfect for both single images and bulk processing.',
    icon: <Zap className="h-6 w-6 text-white" />,
  },
  {
    name: 'Multiple Formats',
    description: 'Support for all major embroidery file formats, ensuring compatibility with any machine.',
    icon: <Shield className="h-6 w-6 text-white" />,
  },
] as const;