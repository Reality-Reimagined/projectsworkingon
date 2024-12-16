import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { Wand2, Sparkles, Zap, Shield } from 'lucide-react';

export function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="bg-white">
      {/* Hero Section */}
      <div className="relative isolate px-6 pt-14 lg:px-8">
        <div className="mx-auto max-w-2xl py-32 sm:py-48 lg:py-56">
          <div className="text-center">
            <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
              Transform Your Images into Professional Embroidery Files
            </h1>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              Embroidery AI uses advanced machine learning to convert your images into high-quality embroidery files, ready for any machine.
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <Button size="lg" onClick={() => navigate('/signup')}>
                Get Started
              </Button>
              <Button variant="outline" size="lg" onClick={() => navigate('/pricing')}>
                View Pricing
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl lg:text-center">
            <h2 className="text-base font-semibold leading-7 text-indigo-600">Advanced Technology</h2>
            <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              Everything you need to digitize your designs
            </p>
          </div>
          <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-4xl">
            <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-10 lg:max-w-none lg:grid-cols-2 lg:gap-y-16">
              <div className="relative pl-16">
                <dt className="text-base font-semibold leading-7 text-gray-900">
                  <div className="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-600">
                    <Wand2 className="h-6 w-6 text-white" />
                  </div>
                  Automatic Conversion
                </dt>
                <dd className="mt-2 text-base leading-7 text-gray-600">
                  Upload any image and our AI will convert it into a professional embroidery file format.
                </dd>
              </div>
              <div className="relative pl-16">
                <dt className="text-base font-semibold leading-7 text-gray-900">
                  <div className="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-600">
                    <Sparkles className="h-6 w-6 text-white" />
                  </div>
                  Smart Optimization
                </dt>
                <dd className="mt-2 text-base leading-7 text-gray-600">
                  Our algorithms optimize stitch patterns for the best possible output quality.
                </dd>
              </div>
              <div className="relative pl-16">
                <dt className="text-base font-semibold leading-7 text-gray-900">
                  <div className="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-600">
                    <Zap className="h-6 w-6 text-white" />
                  </div>
                  Fast Processing
                </dt>
                <dd className="mt-2 text-base leading-7 text-gray-600">
                  Get your converted files in seconds, not hours. Perfect for bulk processing.
                </dd>
              </div>
              <div className="relative pl-16">
                <dt className="text-base font-semibold leading-7 text-gray-900">
                  <div className="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-600">
                    <Shield className="h-6 w-6 text-white" />
                  </div>
                  Multiple Formats
                </dt>
                <dd className="mt-2 text-base leading-7 text-gray-600">
                  Support for all major embroidery file formats, compatible with any machine.
                </dd>
              </div>
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
}