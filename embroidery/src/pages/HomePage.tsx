import React from 'react';
import { FileUpload } from '../components/FileUpload';
import { useFileUpload } from '../hooks/useFileUpload';
import { Settings, AlertCircle } from 'lucide-react';

export function HomePage() {
  const {
    selectedFile,
    processing,
    messages,
    error,
    handleFileSelect
  } = useFileUpload();

  return (
    <div className="max-w-3xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Convert Images to Embroidery Files
        </h1>
        <p className="text-lg text-gray-600">
          Upload your image and we'll convert it into a professional embroidery file format
        </p>
      </div>

      <FileUpload
        onFileSelect={handleFileSelect}
        isProcessing={processing}
      />

      {selectedFile && !processing && (
        <div className="mt-6 bg-white p-4 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Settings className="h-5 w-5 text-gray-400 mr-2" />
              <span className="text-sm font-medium text-gray-700">
                Processing Settings
              </span>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="mt-6 bg-red-50 p-4 rounded-lg flex items-start">
          <AlertCircle className="h-5 w-5 text-red-400 mt-0.5 mr-2" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {messages.length > 0 && (
        <div className="mt-6 bg-white p-4 rounded-lg shadow-sm border">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Progress Updates</h3>
          <ul className="space-y-2">
            {messages.map((message, index) => (
              <li key={index} className="text-sm text-gray-600">
                {message}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}