'use client';

import React from 'react';
import { useRequireRole } from '@/lib/auth';
import { MetricCard } from '@/components/dashboard/MetricCard';

export default function IntelligenceHubPage() {
  const { loading } = useRequireRole(['manager', 'admin']);

  if (loading) return <div className="p-8">Loading Intelligence Hub...</div>;

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Manager Intelligence Hub</h1>
        <p className="text-sm text-gray-500">Read-only operational analytics and SOP metrics.</p>
      </div>

      {/* Overview Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <MetricCard title="Total SOP Executions" value="1,420" change="+12%" trend="up" />
        <MetricCard title="Avg. Response Confidence" value="92.4%" change="+1.2%" trend="up" />
        <MetricCard title="Confusing Procedures Flagged" value="3" change="-2" trend="down" />
        <MetricCard title="Department Adoption Rate" value="88%" change="+5%" trend="up" />
      </div>

      {/* Analytics Dashboard Panels */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-6 bg-white border border-gray-200 rounded-xl shadow-sm">
          <h2 className="text-lg font-bold text-gray-800 mb-4">Most Confusing Procedures</h2>
          <ul className="space-y-3 text-sm">
            <li className="flex justify-between items-center border-b pb-2">
              <span className="font-medium text-gray-700">Valve Maintenance Procedure v2</span>
              <span className="text-red-600 font-semibold">18% Escalation Rate</span>
            </li>
          </ul>
        </div>
        <div className="p-6 bg-white border border-gray-200 rounded-xl shadow-sm">
          <h2 className="text-lg font-bold text-gray-800 mb-4">Confidence Score Trends</h2>
          <div className="h-40 flex items-center justify-center border-2 border-dashed border-gray-200 text-gray-400 rounded-lg">
            [ Time-Series Chart Component Stub ]
          </div>
        </div>
      </div>
    </div>
  );
}
