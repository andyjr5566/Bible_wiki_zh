import type { AssetProfile } from './assets';
import type { ConfidenceLevel } from './core';
import type { CharacterRole, CharacterVisualPolicy, GarmentState } from './characters';
import type { RitualPlaybackState } from './rituals';

export interface TourStopView { id: string; title: string; locationId: string; objectId: string | null; scriptureReference: string | null; scriptureText: string | null; summary: string; }
export interface TourViewState { playing: boolean; index: number; total: number; current: TourStopView | null; }
export type ScriptureContext = 'design' | 'construction' | 'placement' | 'service' | 'reflection';
export interface ObjectDetailView {
  id: string;
  summary: string;
  dimensions: { status: 'verified' | 'unresolved'; lengthCubits: number | null; widthCubits: number | null; heightCubits: number | null; displayNote: string };
  materials: string[];
  parts: Array<{ id: string; label: string }>;
}
export interface LearningViewState {
  objectId: string | null;
  objectName: string | null;
  confidence: ConfidenceLevel | null;
  locationName: string | null;
  scriptureReferences: Array<{ id: string; summary: string; annotation: string; originalText: string; context: ScriptureContext; sourceUrl: string }>;
  ritualIds: string[];
  characterIds: string[];
  availableObjects: Array<{ id: string; name: string }>;
  detail: ObjectDetailView | null;
}
export interface RitualViewState {
  playback: RitualPlaybackState;
  stepIndex: number;
  stepCount: number;
  branchId: string | null;
  name: string | null;
  stepTitle: string | null;
  instruction: string | null;
  confidence: ConfidenceLevel | null;
  scriptureReferences: string[];
  displayCue: string | null;
  unresolved: string[];
}
export interface MapMarkerView { id: string; label: string; x: number; y: number; kind: 'location' | 'player'; }
export interface CharacterViewState {
  id: string;
  name: string;
  role: CharacterRole;
  roleLabel: string;
  garmentState: GarmentState;
  garmentLabel: string;
  status: 'study' | 'omitted';
  visualPolicy: CharacterVisualPolicy;
  baseAssetId: string | null;
  position: null;
  responsibilities: string[];
  parts: Array<{ id: string; label: string; claimedMaterials: string[]; quantity: string; function: string; unknowns: string[] }>;
  validationNotes: string[];
  disclosure: string;
}
export interface AttributionView { id: string; title: string; author: string; sourceUrl: string; license: string; attribution: string; }

export interface ExperienceState {
  tour: TourViewState;
  learning: LearningViewState;
  ritual: RitualViewState;
  character: CharacterViewState;
  creditsOpen: boolean;
  assetProfile: AssetProfile;
}

export type TourCommand = 'previous' | 'next' | 'close';
export type RitualCommand = 'play-pause' | 'previous' | 'next' | 'replay' | 'close';
