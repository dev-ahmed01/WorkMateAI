import React, { useState } from 'react';
import { apiClient } from '@/lib/api-client';

export const UploadDropzone: React.FC = () => {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState<string | null>(null);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setProgress(30);
    setMessage('Uploading file to Snowflake stage...');

    try {
      const formData = new FormData();
      formData.append('file', file);

      setProgress(60);
      await apiClient('/knowledge/upload', {
        method: 'POST',
        body: formData,
      });

      setProgress(100);
      setMessage('Successfully uploaded and queued for processing!');
    } catch (err: any) {
      setMessage(Upload failed: \);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center bg-gray-50 hover:bg-gray-100 transition">
      <input
        type="file"
        id="file-upload"
        className="hidden"
        onChange={handleFileUpload}
        disabled={uploading}
      />
      <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center">
        <svg
          className="w-12 h-12 text-gray-400 mb-3"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          />
        </svg>
        <span className="text-sm font-medium text-gray-700">
          Click to upload or drag & drop document
        </span>
        <span className="text-xs text-gray-500 mt-1">PDF, DOCX, Markdown or TXT</span>
      </label>

      {uploading && (
        <div className="mt-4 w-full bg-gray-200 rounded-full h-2.5">
          <div
            className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
            style={{ width: \% }}
          />
        </div>
      )}

      {message && <p className="mt-3 text-xs text-gray-600 font-medium">{message}</p>}
    </div>
  );
};
