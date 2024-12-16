import React from 'react';
import { useImageTracking } from '../../hooks/useImageTracking';
import { AlertTriangle } from 'lucide-react';

export function ImageUsageSection() {
  const { imagesRemaining, loading, error } = useImageTracking();

  const getWarningLevel = (remaining: number, total: number) => {
    const percentage = (remaining / total) * 100;
    if (percentage <= 10) return 'critical';
    if (percentage <= 20) return 'warning';
    return 'normal';
  };

  if (loading) {
    return <div className="animate-pulse h-20 bg-gray-200 rounded" />;
  }

  if (error) {
    return <div className="text-red-600">{error}</div>;
  }

  const warningLevel = imagesRemaining ? getWarningLevel(imagesRemaining, 50) : 'normal';

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <h2 className="text-xl font-semibold mb-4">Image Usage</h2>
      
      <div className="space-y-4">
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">
              Images Remaining
            </span>
            <span className="text-sm text-gray-500">
              {imagesRemaining} / 50 this month
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div
              className={`h-2.5 rounded-full ${
                warningLevel === 'critical' ? 'bg-red-600' :
                warningLevel === 'warning' ? 'bg-yellow-400' :
                'bg-green-600'
              }`}
              style={{ width: `${(imagesRemaining || 0) / 50 * 100}%` }}
            />
          </div>
        </div>

        {warningLevel !== 'normal' && (
          <div className={`flex items-center gap-2 text-sm ${
            warningLevel === 'critical' ? 'text-red-600' : 'text-yellow-600'
          }`}>
            <AlertTriangle className="h-4 w-4" />
            <span>
              {warningLevel === 'critical'
                ? 'You are running very low on images!'
                : 'You are running low on images.'}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}