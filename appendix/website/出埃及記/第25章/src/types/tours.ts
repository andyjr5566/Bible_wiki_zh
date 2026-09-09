import type { EntityId, Vector3Data } from './core';

export interface CameraPose { position: Vector3Data; target: Vector3Data; fov: number; }

export interface TourDefinition {
  id: string;
  order: number;
  title: string;
  subtitle: string;
  locationId: EntityId;
  objectId: EntityId | null;
  scriptureReference: string;
  excerptIds: string[];
  summary: string;
  durationSeconds: number;
  cameraStart: CameraPose;
  cameraEnd: CameraPose;
  dimensionTargetId?: string;
  peelRoof?: boolean;
}

export interface ToursData { tours: TourDefinition[]; }
