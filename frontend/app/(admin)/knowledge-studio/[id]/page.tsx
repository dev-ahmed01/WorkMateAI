'use client';

import React from 'react';
import { useRequireRole } from '@/lib/auth';

export default function DocumentDetailsPage({ params }: { params: { id: string } }) {
  const { loading } = useRequireRole(['admin']);

  if (loading) return <div className="p-8">Loading Document...</div>;

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-6">
      <div className="border-b pb-4">
        <h1 className="text-2xl font-bold text-gray-900">Document ID: {params.id}</h1>
        <p className="text-sm text-gray-500">Department Scope: Operations • Status: PUBLISHED</p>
      </div>

      <div className="bg-white p-6 border rounded-lg shadow-sm">
        <h2 className="text-lg font-semibold mb-3">Version History</h2>
        <ul className="space-y-2 text-sm text-gray-700">
          <li className="flex justify-between border-b pb-2">
            <span>v1.2 (Active Published)</span>
            <span className="text-gray-400">Published by Admin • 2026-03-01</span>
          </li>
          <li className="flex justify-between text-gray-400">
            <span>v1.0 (Archived)</span>
            <span>2026-01-15</span>
          </li>
        </ul>
      </div>
    </div>
  );
}
