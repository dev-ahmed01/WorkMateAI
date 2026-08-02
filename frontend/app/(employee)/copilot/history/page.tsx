'use client';

import React from 'react';
import { useRequireRole } from '@/lib/auth';

export default function CopilotHistoryPage() {
  const { loading } = useRequireRole(['employee', 'admin']);

  if (loading) return <div className="p-8">Loading session history...</div>;

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Copilot Conversation History</h1>
      <div className="space-y-4">
        <div className="p-4 border border-gray-200 rounded-lg hover:shadow-sm cursor-pointer transition">
          <div className="flex justify-between items-center mb-1">
            <span className="font-semibold text-gray-800">Equipment Setup SOP Execution</span>
            <span className="text-xs text-gray-400">2 hours ago</span>
          </div>
          <p className="text-sm text-gray-600">Session ID: sess_9923841 • Status: Completed</p>
        </div>
      </div>
    </div>
  );
}
