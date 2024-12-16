import React, { useState } from 'react';
import { FileUpload } from '../components/FileUpload';
import { useFileUpload } from '../hooks/useFileUpload';
import { Settings, AlertCircle, Image as ImageIcon } from 'lucide-react';
import { ImageSettings } from '../components/ImageSettings';
import { motion } from 'framer-motion';

export function HomePage() {
  const {
    selectedFile,
    processing,
    messages,
    error,
    downloadUrl,
    handleFileSelect,
    downloadFile
  } = useFileUpload();

  const [settings, setSettings] = useState({
    stitchDensity: 5,
    stitchType: 'normal',
    strokeDepth: 3,
    colorMode: 'color',
    vectorQuality: 3,
    pathSimplification: 2
  });

  const handleFileUpload = (file: File) => {
    handleFileSelect(file, settings);
  };

  return (
    <div className="max-w-6xl mx-auto">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Convert Your Images
        </h1>
        <p className="text-lg text-gray-600">
          Upload an image and customize your embroidery settings
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className="bg-white p-6 rounded-lg shadow-sm border mb-6">
            <div className="flex items-center mb-4">
              <ImageIcon className="h-5 w-5 text-gray-400 mr-2" />
              <h2 className="text-lg font-medium">Image Upload</h2>
            </div>
            <FileUpload
              onFileSelect={handleFileUpload}
              isProcessing={processing}
              onDownload={downloadFile}
              downloadUrl={downloadUrl}
            />
          </div>

          {selectedFile && (
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h3 className="text-lg font-medium mb-4">Preview</h3>
              <div className="aspect-square rounded-lg border-2 border-dashed border-gray-200 flex items-center justify-center">
                <img
                  src={URL.createObjectURL(selectedFile)}
                  alt="Preview"
                  className="max-h-full max-w-full object-contain"
                />
              </div>
            </div>
          )}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="space-y-6"
        >
          <ImageSettings
            settings={settings}
            onChange={setSettings}
          />

          {error && (
            <div className="bg-red-50 p-4 rounded-lg flex items-start">
              <AlertCircle className="h-5 w-5 text-red-400 mt-0.5 mr-2" />
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {messages.length > 0 && (
            <div className="bg-white p-4 rounded-lg shadow-sm border">
              <h3 className="text-sm font-medium text-gray-700 mb-2">Progress</h3>
              <ul className="space-y-2">
                {messages.map((message, index) => (
                  <motion.li
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="text-sm text-gray-600 flex items-center"
                  >
                    <div className="h-1.5 w-1.5 rounded-full bg-indigo-600 mr-2" />
                    {message}
                  </motion.li>
                ))}
              </ul>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}