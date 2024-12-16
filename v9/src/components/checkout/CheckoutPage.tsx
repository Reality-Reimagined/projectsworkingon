import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useCheckout } from '../../hooks/useCheckout';
import { Button } from '../ui/Button';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import type { CheckoutItem } from '../../types/checkout';

interface CheckoutPageProps {
  items: CheckoutItem[];
}

export function CheckoutPage({ items }: CheckoutPageProps) {
  const { status, error, createCheckoutSession } = useCheckout();
  const navigate = useNavigate();

  if (status === 'processing') {
    return <LoadingSpinner />;
  }

  const total = items.reduce((sum, item) => sum + item.quantity * item.pricePerUnit, 0);

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Checkout</h1>

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Order Summary</h2>
        
        {items.map((item) => (
          <div key={item.id} className="flex justify-between py-2">
            <span>{item.name} x {item.quantity}</span>
            <span>${(item.pricePerUnit * item.quantity).toFixed(2)}</span>
          </div>
        ))}

        <div className="border-t mt-4 pt-4">
          <div className="flex justify-between font-bold">
            <span>Total</span>
            <span>${total.toFixed(2)}</span>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 text-red-700 p-4 rounded-lg mb-6">
          {error}
        </div>
      )}

      <div className="flex gap-4">
        <Button
          onClick={() => createCheckoutSession(items)}
          disabled={status === 'processing'}
          className="w-full"
        >
          Proceed to Payment
        </Button>
        <Button
          variant="outline"
          onClick={() => navigate(-1)}
          className="w-full"
        >
          Back
        </Button>
      </div>
    </div>
  );
}