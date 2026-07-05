import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Check, Zap, Shield, Star } from 'lucide-react';
import { paymentsAPI } from '../lib/api';
import { useAuthStore } from '../store';
import type { Plan, Subscription } from '../types';

declare global {
  interface Window {
    Razorpay: new (opts: Record<string, unknown>) => { open(): void };
  }
}

function loadRazorpayScript(): Promise<boolean> {
  return new Promise((resolve) => {
    if (document.getElementById('razorpay-sdk')) { resolve(true); return; }
    const s = document.createElement('script');
    s.id = 'razorpay-sdk';
    s.src = 'https://checkout.razorpay.com/v1/checkout.js';
    s.onload = () => resolve(true);
    s.onerror = () => resolve(false);
    document.body.appendChild(s);
  });
}

const PLAN_ICONS: Record<string, React.ReactNode> = {
  free:  <Shield className="w-6 h-6" />,
  pro:   <Zap className="w-6 h-6" />,
  firm:  <Star className="w-6 h-6" />,
};

const PLAN_COLORS: Record<string, string> = {
  free:  'border-gray-200',
  pro:   'border-blue-500 ring-2 ring-blue-500',
  firm:  'border-purple-500',
};

const PLAN_BADGE: Record<string, string> = {
  free:  'bg-gray-100 text-gray-600',
  pro:   'bg-blue-600 text-white',
  firm:  'bg-purple-600 text-white',
};

export default function Pricing() {
  const user = useAuthStore((s) => s.user);
  const queryClient = useQueryClient();
  const [upgrading, setUpgrading] = useState<string | null>(null);
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);

  const { data: plansData } = useQuery({
    queryKey: ['plans'],
    queryFn: paymentsAPI.plans,
  });

  const { data: subData } = useQuery<Subscription>({
    queryKey: ['subscription'],
    queryFn: paymentsAPI.subscription,
    enabled: !!user,
  });

  const verifyMutation = useMutation({
    mutationFn: paymentsAPI.verify,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['subscription'] });
      showToast(`Upgraded to ${data.plan.toUpperCase()} plan!`, true);
    },
    onError: () => showToast('Payment verification failed. Contact support.', false),
  });

  const cancelMutation = useMutation({
    mutationFn: paymentsAPI.cancel,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subscription'] });
      showToast('Subscription cancelled. Access continues until period end.', true);
    },
  });

  function showToast(msg: string, ok: boolean) {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 4000);
  }

  async function handleUpgrade(plan: Plan) {
    if (!user) { window.location.href = '/login'; return; }
    setUpgrading(plan.id);
    try {
      const loaded = await loadRazorpayScript();
      if (!loaded) { showToast('Failed to load Razorpay SDK', false); return; }

      const order = await paymentsAPI.createOrder(plan.id);

      const rzp = new window.Razorpay({
        key: order.razorpay_key_id,
        amount: order.amount,
        currency: order.currency,
        name: order.name,
        description: order.description,
        order_id: order.order_id,
        prefill: order.prefill,
        theme: { color: plan.id === 'firm' ? '#7c3aed' : '#2563eb' },
        handler: async (response: {
          razorpay_payment_id: string;
          razorpay_order_id: string;
          razorpay_signature: string;
        }) => {
          await verifyMutation.mutateAsync({
            razorpay_order_id: response.razorpay_order_id,
            razorpay_payment_id: response.razorpay_payment_id,
            razorpay_signature: response.razorpay_signature,
          });
        },
      });
      rzp.open();
    } catch {
      showToast('Failed to initiate payment', false);
    } finally {
      setUpgrading(null);
    }
  }

  const currentPlan = subData?.plan ?? 'free';
  const plans: Plan[] = plansData?.plans ?? [];

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      {/* Toast */}
      {toast && (
        <div className={`fixed top-6 right-6 z-50 px-5 py-3 rounded-lg shadow-lg text-white text-sm font-medium ${toast.ok ? 'bg-green-600' : 'bg-red-600'}`}>
          {toast.msg}
        </div>
      )}

      {/* Header */}
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold text-gray-900">Simple, transparent pricing</h1>
        <p className="mt-2 text-gray-500">Start free. Upgrade when you need more.</p>
        {subData && currentPlan !== 'free' && (
          <div className="mt-3 inline-flex items-center gap-2 bg-blue-50 border border-blue-200 text-blue-700 text-sm px-4 py-1.5 rounded-full">
            <Zap className="w-3.5 h-3.5" />
            Current plan: <strong>{currentPlan.toUpperCase()}</strong>
            {subData.current_period_end && (
              <span className="text-blue-500">
                · renews {new Date(subData.current_period_end).toLocaleDateString('en-IN')}
              </span>
            )}
          </div>
        )}
      </div>

      {/* Plan cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {plans.map((plan) => {
          const isCurrent = plan.id === currentPlan;
          const isDowngrade = ['pro', 'firm'].indexOf(plan.id) < ['pro', 'firm'].indexOf(currentPlan);
          return (
            <div
              key={plan.id}
              className={`relative flex flex-col bg-white rounded-2xl border-2 p-6 shadow-sm ${PLAN_COLORS[plan.id]}`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-600 text-white text-xs font-semibold px-3 py-1 rounded-full">
                  Most Popular
                </div>
              )}

              {/* Icon + name */}
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-4 ${PLAN_BADGE[plan.id]}`}>
                {PLAN_ICONS[plan.id]}
              </div>

              <div className="mb-1">
                <h2 className="text-xl font-bold text-gray-900">{plan.name}</h2>
                <p className="text-sm text-gray-500">{plan.tagline}</p>
              </div>

              <div className="my-4">
                <span className="text-4xl font-extrabold text-gray-900">
                  {plan.price_inr === 0 ? '₹0' : `₹${plan.price_inr.toLocaleString('en-IN')}`}
                </span>
                <span className="text-gray-400 text-sm ml-1">/{plan.billing}</span>
              </div>

              <ul className="space-y-2 mb-6 flex-1">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-start gap-2 text-sm text-gray-700">
                    <Check className="w-4 h-4 text-green-500 mt-0.5 shrink-0" />
                    {f}
                  </li>
                ))}
              </ul>

              {isCurrent ? (
                <div className="w-full text-center py-2 rounded-lg bg-gray-100 text-gray-500 font-medium text-sm">
                  Current plan
                </div>
              ) : plan.price_inr === 0 ? (
                isDowngrade ? (
                  <button
                    onClick={() => cancelMutation.mutate()}
                    disabled={cancelMutation.isPending}
                    className="w-full py-2 rounded-lg border border-gray-300 text-gray-600 text-sm font-medium hover:bg-gray-50 transition"
                  >
                    {cancelMutation.isPending ? 'Cancelling...' : 'Cancel subscription'}
                  </button>
                ) : (
                  <div className="w-full text-center py-2 rounded-lg bg-gray-50 text-gray-400 text-sm">
                    Free forever
                  </div>
                )
              ) : (
                <button
                  onClick={() => handleUpgrade(plan)}
                  disabled={upgrading === plan.id}
                  className={`w-full py-2.5 rounded-lg text-sm font-semibold transition ${
                    plan.id === 'firm'
                      ? 'bg-purple-600 hover:bg-purple-700 text-white'
                      : 'bg-blue-600 hover:bg-blue-700 text-white'
                  } disabled:opacity-60`}
                >
                  {upgrading === plan.id ? 'Loading...' : isCurrent ? 'Current plan' : `Upgrade to ${plan.name}`}
                </button>
              )}
            </div>
          );
        })}
      </div>

      {/* Footer note */}
      <p className="text-center text-xs text-gray-400 mt-8">
        Payments processed securely by Razorpay · GST included · Cancel anytime
      </p>
    </div>
  );
}
