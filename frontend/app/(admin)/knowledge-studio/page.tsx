'use client';

import React from 'react';
import { useRequireRole } from '@/lib/auth';
import Link from 'next/link';

export default function KnowledgeStudioPage() {
  const { loading } = useRequireRole(['admin']);

  if (loading) return <div className="p-8">Loading Knowledge Studio...</div>;

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Knowledge Studio</h1>
        <Link
          href="/knowledge-studio/upload"
          className="bg-blue-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-blue-700"
        >
          Upload New Document
        </Link>
      </div>
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-200 text-xs text-gray-500 font-semibold uppercase">
              <th className="p-4">Title</th>
              <th className="p-4">Department</th>
              <th className="p-4">Status</th>
              <th className="p-4">Version</th>
              <th className="p-4">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 text-sm text-gray-700">
            <tr>
              <td className="p-4 font-medium">Standard Operating Procedure - Valves</td>
              <td className="p-4">Operations</td>
              <td className="p-4">
                <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full font-semibold">
                  PUBLISHED
                </span>
              </td>
              <td className="p-4">v1.2</td>
              <td className="p-4">
                <Link href="/knowledge-studio/doc_101" className="text-blue-600 hover:underline">
                  View / Edit
                </Link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
