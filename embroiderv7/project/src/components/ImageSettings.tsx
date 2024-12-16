import React from 'react';
import { Slider } from './ui/Slider';
import { Select } from './ui/Select';
import { Settings } from 'lucide-react';

interface ImageSettingsProps {
  settings: {
    stitchDensity: number;
    stitchType: string;
    strokeDepth: number;
    colorMode: 'monochrome' | 'color';
  };
  onChange: (settings: any) => void;
}

export function ImageSettings({ settings, onChange }: ImageSettingsProps) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <div className="flex items-center mb-4">
        <Settings className="h-5 w-5 text-gray-400 mr-2" />
        <h3 className="text-lg font-medium">Conversion Settings</h3>
      </div>

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Stitch Density
          </label>
          <Slider
            value={settings.stitchDensity}
            onChange={(value) => onChange({ ...settings, stitchDensity: value })}
            min={1}
            max={10}
            step={0.5}
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Sparse</span>
            <span>Dense</span>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Stitch Type
          </label>
          <Select
            value={settings.stitchType}
            onChange={(value) => onChange({ ...settings, stitchType: value })}
            options={[
              { label: 'Normal', value: 'normal' },
              { label: 'Satin', value: 'satin' },
              { label: 'Fill', value: 'fill' },
              { label: 'Running', value: 'running' }
            ]}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Stroke Depth
          </label>
          <Slider
            value={settings.strokeDepth}
            onChange={(value) => onChange({ ...settings, strokeDepth: value })}
            min={1}
            max={5}
            step={0.5}
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Shallow</span>
            <span>Deep</span>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Color Mode
          </label>
          <Select
            value={settings.colorMode}
            onChange={(value) => onChange({ ...settings, colorMode: value })}
            options={[
              { label: 'Monochrome', value: 'monochrome' },
              { label: 'Color', value: 'color' }
            ]}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Vectorization Quality
          </label>
          <Slider
            value={settings.vectorQuality || 2}
            onChange={(value) => onChange({ ...settings, vectorQuality: value })}
            min={1}
            max={5}
            step={0.5}
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Fast</span>
            <span>Detailed</span>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Path Simplification
          </label>
          <Slider
            value={settings.pathSimplification || 2}
            onChange={(value) => onChange({ ...settings, pathSimplification: value })}
            min={1}
            max={5}
            step={0.5}
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Simple</span>
            <span>Complex</span>
          </div>
        </div>
      </div>
    </div>
  );
}