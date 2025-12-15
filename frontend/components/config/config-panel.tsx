"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { ConversionConfig } from "@/types/api";
import { QUALITY_PRESETS, getPresetById } from "./quality-presets";

interface ConfigPanelProps {
  config: ConversionConfig;
  onChange: (config: ConversionConfig) => void;
  disabled?: boolean;
}

export function ConfigPanel({ config, onChange, disabled = false }: ConfigPanelProps) {
  const [selectedPreset, setSelectedPreset] = useState("custom");

  const handlePresetChange = (presetId: string) => {
    setSelectedPreset(presetId);
    const preset = getPresetById(presetId);
    if (preset) {
      onChange(preset.config);
    }
  };

  const handleBitrateChange = (value: number[]) => {
    const bitrate = `${value[0]}k`;
    onChange({ ...config, bitrate });
    setSelectedPreset("custom");
  };

  const handleSampleRateChange = (value: string) => {
    const sampleRate = value === "auto" ? null : parseInt(value);
    onChange({ ...config, sample_rate: sampleRate });
  };

  const handleMetadataChange = (checked: boolean) => {
    onChange({ ...config, preserve_metadata: checked });
  };

  // Parse current bitrate for slider
  const currentBitrate = parseInt(config.bitrate.replace("k", ""));

  return (
    <Card className="glass-card shadow-lg border-2 transition-all duration-300 hover:shadow-xl">
      <CardHeader className="space-y-0.5 pb-4">
        <CardTitle className="text-xl">Conversion Settings</CardTitle>
        <CardDescription className="text-sm">
          Configure audio quality and metadata options
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Quality Preset */}
        <div className="space-y-2">
          <Label htmlFor="preset">Quality Preset</Label>
          <Select
            value={selectedPreset}
            onValueChange={handlePresetChange}
            disabled={disabled}
          >
            <SelectTrigger id="preset">
              <SelectValue placeholder="Select preset" />
            </SelectTrigger>
            <SelectContent>
              {QUALITY_PRESETS.map((preset) => (
                <SelectItem key={preset.id} value={preset.id}>
                  <div className="flex flex-col">
                    <span className="font-medium">{preset.name}</span>
                    <span className="text-xs text-muted-foreground">
                      {preset.description}
                    </span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Bitrate Slider */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label htmlFor="bitrate">Bitrate</Label>
            <span className="text-sm font-medium">{config.bitrate}</span>
          </div>
          <Slider
            id="bitrate"
            min={128}
            max={320}
            step={32}
            value={[currentBitrate]}
            onValueChange={handleBitrateChange}
            disabled={disabled}
            className="w-full"
          />
          <p className="text-xs text-muted-foreground">
            Higher bitrate = better quality, larger file size
          </p>
        </div>

        {/* Sample Rate */}
        <div className="space-y-2">
          <Label htmlFor="sample-rate">Sample Rate</Label>
          <Select
            value={config.sample_rate?.toString() || "auto"}
            onValueChange={handleSampleRateChange}
            disabled={disabled}
          >
            <SelectTrigger id="sample-rate">
              <SelectValue placeholder="Select sample rate" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="auto">Auto (Original)</SelectItem>
              <SelectItem value="44100">44.1 kHz (CD Quality)</SelectItem>
              <SelectItem value="48000">48 kHz (Professional)</SelectItem>
            </SelectContent>
          </Select>
          <p className="text-xs text-muted-foreground">
            Audio sample rate in Hz
          </p>
        </div>

        {/* Metadata Preservation */}
        <div className="flex items-center justify-between">
          <div className="space-y-0.5">
            <Label htmlFor="metadata">Preserve Metadata</Label>
            <p className="text-xs text-muted-foreground">
              Copy title, artist, album info, and artwork
            </p>
          </div>
          <Switch
            id="metadata"
            checked={config.preserve_metadata}
            onCheckedChange={handleMetadataChange}
            disabled={disabled}
          />
        </div>
      </CardContent>
    </Card>
  );
}
