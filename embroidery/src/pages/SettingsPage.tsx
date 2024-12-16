import React from 'react';
import { useAuth } from '../hooks/useAuth';
import { Button } from '../components/ui/Button';
import { useNavigate } from 'react-router-dom';
import { PRICING_PLANS } from '../config';

export function SettingsPage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const currentPlan = PRICING_PLANS.find(
    plan => plan.id === user?.subscription_tier
  ) || PRICING_PLANS[0];

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Account Settings</h1>

      <div className="space-y-6">
        {/* Profile Section */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h2 className="text-xl font-semibold mb-4">Profile</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Email
              </label>
              <input
                type="email"
                value={user?.email}
                disabled
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm bg-gray-50"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Full Name
              </label>
              <input
                type="text"
                value={user?.full_name || ''}
                onChange={() => {}}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
              />
            </div>
          </div>
        </div>

        {/* Subscription Section */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h2 className="text-xl font-semibold mb-4">Subscription</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">{currentPlan.name} Plan</p>
                <p className="text-sm text-gray-600">
                  {user?.subscription_status === 'active'
                    ? 'Active subscription'
                    : 'No active subscription'}
                </p>
              </div>
              <Button
                variant="outline"
                onClick={() => navigate('/pricing')}
              >
                {user?.subscription_status === 'active'
                  ? 'Change Plan'
                  : 'Upgrade'}
              </Button>
            </div>
          </div>
        </div>

        {/* API Keys Section */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h2 className="text-xl font-semibold mb-4">API Keys</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                API Key
              </label>
              <div className="mt-1 flex rounded-md shadow-sm">
                <input
                  type="text"
                  value="••••••••••••••••"
                  disabled
                  className="flex-1 rounded-l-md border-gray-300 bg-gray-50"
                />
                <Button
                  variant="outline"
                  className="rounded-l-none"
                >
                  Show
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}