import { useState } from 'react';
import { useAuth } from './useAuth';

export function useFileUpload() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [processing, setProcessing] = useState(false);
  const [messages, setMessages] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  const handleFileSelect = async (file: File) => {
    setSelectedFile(file);
    setError(null);
    setMessages([]);
    
    if (!user) {
      setError('Please sign in to process files');
      return;
    }

    setProcessing(true);
    // File processing logic here
  };

  return {
    selectedFile,
    processing,
    messages,
    error,
    handleFileSelect,
  };
}