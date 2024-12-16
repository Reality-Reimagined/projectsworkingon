import React, { useState } from 'react';
import { Copy, RefreshCw } from 'lucide-react';
import { useApiKey } from '../../hooks/useApiKey';
import { Button } from '../ui/Button';

export function ApiKeySection() {
  const { apiKey, loading, error, generateApiKey } = useApiKey();
  const [copied, setCopied] = useState(false);

  const copyApiKey = async () => {
    if (apiKey) {
      await navigator.clipboard.writeText(apiKey);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const sampleCurl = apiKey ? `curl -X POST \\
  -H "Authorization: Bearer ${apiKey}" \\
  -F "file=@image.jpg" \\
  ${window.location.origin}/api/convert` : '';

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <h2 className="text-xl font-semibold mb-4">API Access</h2>
      
      {error ? (
        <div className="text-red-600 mb-4">{error}</div>
      ) : loading ? (
        <div className="animate-pulse h-8 bg-gray-200 rounded mb-4" />
      ) : (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Your API Key
            </label>
            <div className="flex gap-2">
              <code className="flex-1 p-2 bg-gray-50 rounded border font-mono text-sm">
                {apiKey ? '••••••••' + apiKey.slice(-8) : 'No API key generated'}
              </code>
              <Button
                variant="outline"
                onClick={copyApiKey}
                disabled={!apiKey}
              >
                <Copy className={`h-4 w-4 ${copied ? 'text-green-500' : ''}`} />
              </Button>
              <Button
                variant="outline"
                onClick={generateApiKey}
                disabled={loading}
              >
                <RefreshCw className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {apiKey && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sample Usage
              </label>
              <pre className="p-4 bg-gray-900 text-gray-100 rounded-lg overflow-x-auto text-sm">
                {sampleCurl}
              </pre>
            </div>
          )}

          <div className="text-sm text-gray-600">
            <a
              href="/docs/api"
              className="text-indigo-600 hover:text-indigo-500"
            >
              View API Documentation →
            </a>
          </div>
        </div>
      )}
    </div>
  );
}