import React, { useState } from 'react';
import { Upload } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { Button } from './ui/Button';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  isProcessing: boolean;
  onDownload?: () => void;
  downloadUrl?: string | null;
}

export function FileUpload({ onFileSelect, isProcessing, onDownload, downloadUrl }: FileUploadProps) {
  const [dragActive, setDragActive] = useState(false);
  const { user } = useAuth();

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      onFileSelect(e.target.files[0]);
    }
  };

  if (!user) {
    return (
      <div className="text-center">
        <p className="text-gray-600">Please sign in to upload files.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div
        className={`relative border-2 border-dashed rounded-lg p-8 text-center ${
          dragActive ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          className="hidden"
          id="file-upload"
          accept="image/png,image/jpeg"
          onChange={handleChange}
          disabled={isProcessing}
        />
        
        <label
          htmlFor="file-upload"
          className="cursor-pointer flex flex-col items-center justify-center"
        >
          <Upload className="h-12 w-12 text-gray-400" />
          <p className="mt-2 text-sm text-gray-600">
            {isProcessing ? (
              'Processing...'
            ) : (
              <>
                <span className="font-semibold text-indigo-600">Click to upload</span> or drag and drop
              </>
            )}
          </p>
          <p className="mt-1 text-xs text-gray-500">PNG or JPG up to 10MB</p>
        </label>
      </div>

      {downloadUrl && onDownload && (
        <Button
          onClick={onDownload}
          className="w-full"
          variant="outline"
        >
          Download Embroidery File
        </Button>
      )}
    </div>
  );
}