import { useState, useEffect } from 'react';
import { useAuth } from './useAuth';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

interface FileUploadSettings {
  stitchDensity: number;
  stitchType: string;
  strokeDepth: number;
  colorMode: string;
  vectorQuality: number;
  pathSimplification: number;
}

export function useFileUpload() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [processing, setProcessing] = useState(false);
  const [messages, setMessages] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [clientId] = useState(uuidv4());
  const { user } = useAuth();

  useEffect(() => {
    const ws = new WebSocket(`${import.meta.env.VITE_API_URL.replace('http', 'ws')}/ws/${clientId}`);

    ws.onopen = () => {
      console.log('WebSocket connection established');
    };

    ws.onmessage = (event) => {
      const message = event.data;
      setMessages((prev) => [...prev, message]);
      
      if (message === 'Digitization complete.') {
        setProcessing(false);
      }
    };

    return () => {
      ws.close();
    };
  }, [clientId]);

  const handleFileSelect = async (file: File, settings: FileUploadSettings) => {
    if (!user) {
      setError('Please sign in to process files');
      return;
    }

    setSelectedFile(file);
    setError(null);
    setMessages([]);
    setProcessing(true);
    setDownloadUrl(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('client_id', clientId);
    formData.append('stitch_density', settings.stitchDensity.toString());
    formData.append('stitch_type', settings.stitchType);
    formData.append('stroke_depth', settings.strokeDepth.toString());
    formData.append('color_mode', settings.colorMode);
    formData.append('vector_quality', settings.vectorQuality.toString());
    formData.append('path_simplification', settings.pathSimplification.toString());

    try {
      const response = await axios.post(`${import.meta.env.VITE_API_URL}/upload/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setDownloadUrl(response.data.download_url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload file');
      setProcessing(false);
    }
  };

  const downloadFile = () => {
    if (downloadUrl) {
      window.location.href = `${import.meta.env.VITE_API_URL}${downloadUrl}`;
    }
  };

  return {
    selectedFile,
    processing,
    messages,
    error,
    downloadUrl,
    handleFileSelect,
    downloadFile,
  };
}