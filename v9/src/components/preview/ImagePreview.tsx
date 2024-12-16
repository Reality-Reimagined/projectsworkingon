import React from 'react';
import { PannableSvgPreview } from './PannableSvgPreview';

interface ImagePreviewProps {
  file: File | null;
  previewType: 'original' | 'dst';
  svgContent: string | null;
}

export function ImagePreview({ file, previewType, svgContent }: ImagePreviewProps) {
  if (!file) return null;

  return (
    <div className="aspect-square rounded-lg border-2 border-dashed border-gray-200 flex items-center justify-center overflow-hidden">
      {previewType === 'original' ? (
        <img
          src={URL.createObjectURL(file)}
          alt="Preview"
          className="max-h-full max-w-full object-contain"
        />
      ) : (
        <div className="w-full h-full flex items-center justify-center">
          {svgContent ? (
            <PannableSvgPreview svgContent={svgContent} />
          ) : (
            <div className="text-gray-500">Loading DST preview...</div>
          )}
        </div>
      )}
    </div>
  );
}