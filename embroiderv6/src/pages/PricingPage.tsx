import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { Check } from 'lucide-react';
import { PRICING_PLANS } from '../config';
import { useAuth } from '../hooks/useAuth';

export function PricingPage() {
  const [annual, setAnnual] = useState(false);
  const navigate = useNavigate();
  const { user } = useAuth();

  return (
    <div className="bg-white py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-4xl text-center">
          <h2 className="text-base font-semibold leading-7 text-indigo-600">Pricing</h2>
          <p className="mt-2 text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
            Choose the right plan for&nbsp;you
          </p>
        </div>

        <div className="mt-6 flex justify-center">
          <div className="relative flex rounded-full bg-gray-100 p-1">
            <button
              type="button"
              className={`${
                !annual ? 'bg-white shadow-sm' : 'bg-transparent'
              } relative rounded-full py-1 px-4 text-sm font-semibold text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-600`}
              onClick={() => setAnnual(false)}
            >
              Monthly
            </button>
            <button
              type="button"
              className={`${
                annual ? 'bg-white shadow-sm' : 'bg-transparent'
              } relative rounded-full py-1 px-4 text-sm font-semibold text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-600`}
              onClick={() => setAnnual(true)}
            >
              Annual
            </button>
          </div>
        </div>

        <div className="mx-auto mt-16 grid max-w-lg grid-cols-1 items-center gap-y-6 sm:mt-20 sm:gap-y-0 lg:max-w-4xl lg:grid-cols-2">
          {PRICING_PLANS.map((plan) => (
            <div
              key={plan.id}
              className={`flex flex-col justify-between rounded-3xl bg-white p-8 shadow-xl ring-1 ring-gray-900/10 sm:p-10`}
            >
              <div>
                <h3
                  id={plan.id}
                  className="text-base font-semibold leading-7 text-indigo-600"
                >
                  {plan.name}
                </h3>
                <div className="mt-4 flex items-baseline gap-x-2">
                  <span className="text-5xl font-bold tracking-tight text-gray-900">
                    ${annual ? (plan.price * 10).toFixed(2) : plan.price}
                  </span>
                  <span className="text-base font-semibold leading-7 text-gray-600">
                    /{annual ? 'year' : 'month'}
                  </span>
                </div>
                <ul role="list" className="mt-8 space-y-3 text-sm leading-6 text-gray-600">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex gap-x-3">
                      <Check className="h-6 w-5 flex-none text-indigo-600" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
              <Button
                onClick={() => {
                  if (!user) {
                    navigate('/signup');
                  } else {
                    // TODO: Implement subscription flow
                  }
                }}
                className="mt-8 w-full"
              >
                {user ? 'Subscribe' : 'Get started'}
              </Button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}