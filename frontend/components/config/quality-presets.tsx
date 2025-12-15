"use client";

import { ConversionConfig } from "@/types/api";

export interface QualityPreset {
  id: string;
  name: string;
  description: string;
  config: ConversionConfig;
}

export const QUALITY_PRESETS: QualityPreset[] = [
  {
    id: "low",
    name: "Low Quality",
    description: "128 kbps - Smaller file size",
    config: {
      bitrate: "128k",
      sample_rate: null,
      preserve_metadata: true,
    },
  },
  {
    id: "medium",
    name: "Medium Quality",
    description: "192 kbps - Balanced",
    config: {
      bitrate: "192k",
      sample_rate: null,
      preserve_metadata: true,
    },
  },
  {
    id: "high",
    name: "High Quality",
    description: "256 kbps - Better quality",
    config: {
      bitrate: "256k",
      sample_rate: null,
      preserve_metadata: true,
    },
  },
  {
    id: "custom",
    name: "Custom",
    description: "320 kbps - Best quality",
    config: {
      bitrate: "320k",
      sample_rate: null,
      preserve_metadata: true,
    },
  },
];

export function getPresetById(id: string): QualityPreset | undefined {
  return QUALITY_PRESETS.find((preset) => preset.id === id);
}

export function getPresetByConfig(config: ConversionConfig): QualityPreset | undefined {
  return QUALITY_PRESETS.find(
    (preset) =>
      preset.config.bitrate === config.bitrate &&
      preset.config.sample_rate === config.sample_rate
  );
}
