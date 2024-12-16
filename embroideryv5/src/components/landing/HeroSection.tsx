import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../ui/Button';
import { motion } from 'framer-motion';

export function HeroSection() {
  const navigate = useNavigate();

  return (
    <div className="relative isolate pt-14 pb-8 lg:px-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="mx-auto max-w-2xl text-center"
      >
        <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl mb-8">
          Transform Your Images into Professional Embroidery Files
        </h1>
        
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="relative mx-auto w-full max-w-xl mb-12"
        >
          <div className="absolute -top-4 left-1/2 -translate-x-1/2 w-40 h-40 bg-indigo-100 rounded-full blur-3xl opacity-30"></div>
          <img
            src="/embroidery-preview.jpg"
            alt="Embroidery Preview"
            className="w-full rounded-xl shadow-2xl"
          />
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="mt-6 text-lg leading-8 text-gray-600 mb-8"
        >
          Advanced AI technology that converts your images into high-quality embroidery files, 
          ready for any machine. Perfect for both hobbyists and professionals.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <Button size="lg" onClick={() => navigate('/signup')}>
            Get Started
          </Button>
          <Button variant="outline" size="lg" onClick={() => navigate('/pricing')}>
            View Pricing
          </Button>
        </motion.div>
      </motion.div>
    </div>
  );
}