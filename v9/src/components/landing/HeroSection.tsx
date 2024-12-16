import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../ui/Button';
import { motion } from 'framer-motion';
import { Wand2, Sparkles } from 'lucide-react';

export function HeroSection() {
  const navigate = useNavigate();

  return (
    <div className="relative isolate overflow-hidden">
      <div className="absolute inset-0 -z-10 bg-gradient-to-b from-indigo-50 via-white to-white" />
      
      <div className="mx-auto max-w-7xl px-6 lg:px-8 pt-10 pb-24 sm:pb-32 lg:pt-40">
        <div className="lg:grid lg:grid-cols-12 lg:gap-x-8 lg:gap-y-20">
          {/* Text Content */}
          <div className="lg:col-span-7">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <div className="inline-flex space-x-6">
                <span className="rounded-full bg-indigo-600/10 px-3 py-1 text-sm font-semibold leading-6 text-indigo-600 ring-1 ring-inset ring-indigo-600/10">
                  Latest updates
                </span>
                <span className="inline-flex items-center space-x-2 text-sm font-medium leading-6 text-gray-600">
                  <span>Just shipped v1.0</span>
                </span>
              </div>

              <motion.h1
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="mt-10 text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl"
              >
                Transform Your Images into Professional Embroidery Files
              </motion.h1>
              
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4 }}
                className="mt-6 text-lg leading-8 text-gray-600"
              >
                Advanced AI technology that converts your images into high-quality embroidery files, 
                ready for any machine. Perfect for both hobbyists and professionals.
              </motion.p>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="mt-10 flex items-center gap-x-6"
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

          {/* Image Section */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 }}
            className="lg:col-span-5"
          >
            <div className="relative">
              {/* Floating elements */}
              <motion.div
                animate={{ 
                  y: [0, -20, 0],
                  rotate: [0, 5, 0]
                }}
                transition={{ 
                  duration: 5,
                  repeat: Infinity,
                  repeatType: "reverse"
                }}
                className="absolute -top-6 -left-6 z-10 bg-white rounded-2xl shadow-xl p-6"
              >
                <Wand2 className="h-8 w-8 text-indigo-600" />
                <p className="mt-2 font-semibold">AI-Powered</p>
              </motion.div>
              
              <motion.div
                animate={{ 
                  y: [0, 20, 0],
                  rotate: [0, -5, 0]
                }}
                transition={{ 
                  duration: 4,
                  repeat: Infinity,
                  repeatType: "reverse",
                  delay: 1
                }}
                className="absolute -bottom-6 -right-6 z-10 bg-white rounded-2xl shadow-xl p-6"
              >
                <Sparkles className="h-8 w-8 text-indigo-600" />
                <p className="mt-2 font-semibold">High Quality</p>
              </motion.div>

              <div className="relative rounded-2xl bg-gray-900/5 p-8">
                <img
                  src="https://images.unsplash.com/photo-1620799140188-3b2a02fd9a77?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80"
                  alt="Embroidery Preview"
                  className="w-full rounded-lg shadow-2xl ring-1 ring-gray-900/10"
                />
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}