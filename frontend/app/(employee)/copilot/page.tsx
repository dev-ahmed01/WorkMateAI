'use client';

import React, { useState } from 'react';
import { useRequireRole } from '@/lib/auth';
import { ChatThread } from '@/components/chat/ChatThread';
import { CopilotResponse } from '@/lib/api-client';

export default function CopilotPage() {
  const { user, loading } = useRequireRole(['employee', 'admin']);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<
    Array<{ sender: 'user' | 'assistant'; content: string; copilotData?: CopilotResponse }>
  >([
    {
      sender: 'assistant',
      content: 'Welcome to WorkMate Copilot. Ask a question or request guidance on an operational SOP.',
    },
  ]);

  if (loading) return <div className="p-8">Loading context...</div>;

  const handleSend = () => {
    if (!input.trim()) return;

    // Stub optimistic update
    const userMsg = input;
    setInput('');
    setMessages((prev) => [
      ...prev,
      { sender: 'user', content: userMsg },
      {
        sender: 'assistant',
        content: 'I verified the published SOP. Here is Step 1 to proceed.',
        copilotData: {
          message_id: 'msg_stub_1',
          answer: 'Step 1: Check safety valves.',
          citations: [
            {
              document_id: 'doc_101',
              document_title: 'Equipment Operations SOP',
              version_number: 1,
              chunk_id: 'chk_1',
              excerpt: 'Safety valves must be checked prior to initialization.',
            },
          ],
          confidence_score: 0.94,
          is_grounded: true,
          requires_escalation: false,
          active_sop_id: 'sop_equipment_101',
          active_step_number: 1,
          active_step_title: 'Safety Valve Verification',
        },
      },
    ]);
  };

  return (
    <div className="flex flex-col h-screen bg-white">
      <header className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
        <h1 className="text-xl font-bold text-gray-800">WorkMate Copilot</h1>
        <span className="text-xs bg-gray-100 text-gray-700 px-2.5 py-1 rounded">
          Dept: {user?.department_id}
        </span>
      </header>
      <main className="flex-1 overflow-hidden p-4">
        <ChatThread messages={messages} />
      </main>
      <footer className="p-4 border-t border-gray-200">
        <div className="flex space-x-2">
          <input
            type="text"
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Type your operational question..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          />
          <button
            onClick={handleSend}
            className="bg-blue-600 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition"
          >
            Send
          </button>
        </div>
      </footer>
    </div>
  );
}
