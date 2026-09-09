import excerptsJson from '../data/scripture-excerpts.json';
import toursJson from '../data/tours.json';
import { scriptureExcerptsSchema } from '../data/schemas/scriptureEvidence';
import { toursSchema } from '../data/schemas/tours';
import { EventChannel, type Unsubscribe } from '../utils/EventChannel';
import type { Vector3Data } from '../types/core';
import type { DimensionUnit } from '../scene/DimensionVisualizer';

export interface CinematicAct {
  id: string;
  actNumber: number;
  totalActs: number;
  title: string;
  subtitle: string;
  scriptureReference: string;
  scriptureText: string;
  hebrewTerm?: string | undefined;
  durationSeconds: number;
  cameraStart: { position: Vector3Data; target: Vector3Data; fov: number };
  cameraEnd: { position: Vector3Data; target: Vector3Data; fov: number };
  dimensionTargetId?: string | undefined;
  peelRoof?: boolean | undefined;
}

export interface CinematicState {
  isPlaying: boolean;
  isPaused: boolean;
  currentActIndex: number;
  currentAct: CinematicAct;
  progressRatio: number;
  playbackSpeed: number;
  showDimensions: boolean;
  dimensionUnit: DimensionUnit;
}

const tourData = toursSchema.parse(toursJson);
const excerptData = scriptureExcerptsSchema.parse(excerptsJson);
const excerptById = new Map(excerptData.excerpts.map((excerpt) => [excerpt.id, excerpt]));

export const CINEMATIC_ACTS: CinematicAct[] = tourData.tours.slice().sort((a, b) => a.order - b.order).map((tour, index, tours) => ({
  id: tour.id,
  actNumber: tour.order,
  totalActs: tours.length,
  title: tour.title,
  subtitle: tour.subtitle,
  scriptureReference: tour.scriptureReference,
  scriptureText: tour.excerptIds.map((id) => excerptById.get(id)?.text ?? '').filter(Boolean).join('\n\n'),
  durationSeconds: tour.durationSeconds,
  cameraStart: tour.cameraStart,
  cameraEnd: tour.cameraEnd,
  dimensionTargetId: tour.dimensionTargetId,
  peelRoof: tour.peelRoof,
}));

export class CinematicTourController {
  readonly #events = new EventChannel<Readonly<CinematicState>>();
  #actIndex = 0;
  #isPlaying = false;
  #isPaused = false;
  #actElapsed = 0;
  #speed = 1;
  #showDimensions = true;
  #dimensionUnit: DimensionUnit = 'cubit';

  constructor(readonly acts = CINEMATIC_ACTS) {}
  get snapshot(): Readonly<CinematicState> {
    const act = this.acts[this.#actIndex] ?? this.acts[0]!;
    return { isPlaying: this.#isPlaying, isPaused: this.#isPaused, currentActIndex: this.#actIndex, currentAct: act, progressRatio: Math.min(1, this.#actElapsed / act.durationSeconds), playbackSpeed: this.#speed, showDimensions: this.#showDimensions, dimensionUnit: this.#dimensionUnit };
  }
  subscribe(listener: (state: Readonly<CinematicState>) => void): Unsubscribe { listener(this.snapshot); return this.#events.subscribe(listener); }
  start(fromIndex = 0): void { this.#actIndex = Math.max(0, Math.min(this.acts.length - 1, fromIndex)); this.#isPlaying = true; this.#isPaused = false; this.#actElapsed = 0; this.#emit(); }
  pause(): void { if (!this.#isPlaying) return; this.#isPaused = true; this.#emit(); }
  resume(): void { if (!this.#isPlaying) { this.start(this.#actIndex); return; } this.#isPaused = false; this.#emit(); }
  togglePlayPause(): void { if (this.#isPaused || !this.#isPlaying) this.resume(); else this.pause(); }
  stop(): void { this.#isPlaying = false; this.#isPaused = false; this.#actElapsed = 0; this.#emit(); }
  next(): void { if (this.#actIndex < this.acts.length - 1) { this.#actIndex += 1; this.#actElapsed = 0; this.#emit(); } else this.stop(); }
  previous(): void { if (this.#actIndex > 0) { this.#actIndex -= 1; this.#actElapsed = 0; this.#emit(); } }
  jumpTo(index: number): void { this.#actIndex = Math.max(0, Math.min(this.acts.length - 1, index)); this.#actElapsed = 0; this.#emit(); }
  setSpeed(speed: number): void { this.#speed = speed; this.#emit(); }
  toggleDimensions(): void { this.#showDimensions = !this.#showDimensions; this.#emit(); }
  setDimensionUnit(unit: DimensionUnit): void { this.#dimensionUnit = unit; this.#emit(); }
  update(deltaSeconds: number): boolean {
    if (!this.#isPlaying || this.#isPaused) return false;
    const act = this.acts[this.#actIndex]; if (!act) return false;
    this.#actElapsed += deltaSeconds * this.#speed; this.#emit();
    if (this.#actElapsed >= act.durationSeconds) { this.next(); return true; }
    return false;
  }
  #emit(): void { this.#events.emit(this.snapshot); }
}
