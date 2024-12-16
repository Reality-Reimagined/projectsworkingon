import React from 'react';
import { HeroSection } from '../components/landing/HeroSection';
import { Features } from '../components/landing/Features';
import { motion } from 'framer-motion';
import { Wand2, Sparkles, Zap, Shield } from 'lucide-react';

export function LandingPage() {
  return (
    <div className="bg-white">
      <HeroSection />
      
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        viewport={{ once: true }}
        className="py-24 sm:py-32"
      >
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl lg:text-center">
            <h2 className="text-base font-semibold leading-7 text-indigo-600">Advanced Technology</h2>
            <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              Everything you need to digitize your designs
            </p>
          </div>
          <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-4xl">
            <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-10 lg:max-w-none lg:grid-cols-2 lg:gap-y-16">
              {features.map((feature, index) => (
                <motion.div
                  key={feature.name}
                  initial={{ opacity: 0, x: index % 2 === 0 ? -20 : 20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.2 }}
                  viewport={{ once: true }}
                  className="relative pl-16"
                >
                  <dt className="text-base font-semibold leading-7 text-gray-900">
                    <div className="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-600">
                      {feature.icon}
                    </div>
                    {feature.name}
                  </dt>
                  <dd className="mt-2 text-base leading-7 text-gray-600">{feature.description}</dd>
                </motion.div>
              ))}
            </dl>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

const features = [
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
];