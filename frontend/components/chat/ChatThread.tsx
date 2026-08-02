import React from 'react';
import { CopilotResponse } from '@/lib/api-client';

interface ChatThreadProps {
  messages: Array<{
    sender: 'user' | 'assistant';
    content: string;
    copilotData?: CopilotResponse;
  }>;
}

export const ChatThread: React.FC<ChatThreadProps> = ({ messages }) => {
  return (
    <div className="flex flex-col space-y-4 p-4 overflow-y-auto max-h-[70vh]">
      {messages.map((msg, index) => (
        <div
          key={index}
          className={lex flex-col max-w-2xl \}
        >
          {/* Step Indicator */}
          {msg.copilotData?.active_sop_id && (
            <div className="mb-1 text-xs font-semibold px-2 py-0.5 rounded bg-blue-100 text-blue-800">
              SOP Step {msg.copilotData.active_step_number}: {msg.copilotData.active_step_title}
            </div>
          )}

          {/* Message Bubble */}
          <div
            className={p-4 rounded-lg shadow-sm text-sm \}
          >
            {msg.content}

            {/* Citations section */}
            {msg.copilotData?.citations && msg.copilotData.citations.length > 0 && (
              <div className="mt-3 pt-2 border-t border-gray-200 text-xs text-gray-600">
                <span className="font-semibold block mb-1">Sources & Citations:</span>
                <ul className="list-disc pl-4 space-y-1">
                  {msg.copilotData.citations.map((cite, i) => (
                    <li key={i}>
                      <span className="font-medium">{cite.document_title}</span> (v{cite.version_number}): &quot;{cite.excerpt}&quot;
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Confidence / Escalation Badge */}
          {msg.copilotData && (
            <div className="mt-1 flex items-center space-x-2 text-xs">
              <span
                className={px-2 py-0.5 rounded-full font-medium \}
              >
                Confidence: {(msg.copilotData.confidence_score * 100).toFixed(0)}%
              </span>
              {msg.copilotData.requires_escalation && (
                <span className="bg-red-100 text-red-700 px-2 py-0.5 rounded-full font-semibold">
                  Escalation Triggered
                </span>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
