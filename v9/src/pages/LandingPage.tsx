import React from 'react';
import { HeroSection } from '../components/landing/HeroSection';
import { Features } from '../components/landing/Features';
import { Testimonials } from '../components/landing/Testimonials';

export function LandingPage() {
  return (
    <div className="bg-white">
      <HeroSection />
      <Features />
      <Testimonials />
    </div>
  );
}