import { AudioManager } from '../audio/AudioManager';
import { CharacterRegistry } from '../characters/CharacterRegistry';
import { CharacterSystem } from '../characters/CharacterSystem';
import { CharacterAppearanceResolver } from '../characters/CharacterAppearanceResolver';
import { runtimeConfig } from '../config/runtime';
import { loadProjectData } from '../data/loadProjectData';
import { RitualPlaybackController } from '../rituals/RitualPlaybackController';
import { RitualRegistry } from '../rituals/RitualRegistry';
import { RitualVisualSystem } from '../rituals/RitualVisualSystem';
import { SceneBootstrap } from '../scene/SceneBootstrap';
import { ObjectRegistry } from '../scene/ObjectRegistry';
import type { AtmosphereMode } from '../types/atmosphere';
import { ScriptureMappingService } from '../scripture/ScriptureMappingService';
import { ScriptureRegistry } from '../scripture/ScriptureRegistry';
import { LearningModeManager } from '../systems/LearningModeManager';
import { TourManager } from '../systems/TourManager';
import { CinematicTourController, type CinematicState } from '../systems/CinematicTourController';
import { AssetManifest } from '../systems/assets/AssetManifest';
import { GLTFAssetLoader } from '../systems/assets/AssetLoader';
import { AssetRuntimeManager } from '../systems/assets/AssetRuntimeManager';
import type { DimensionUnit } from '../scene/DimensionVisualizer';
import type { AppPort, ArchitectureStats } from '../types/app';
import type { AssetProfile, AssetRuntimeState } from '../types/assets';
import type { AttributionView, ExperienceState, RitualCommand, TourCommand } from '../types/experience';
import type { ExperienceMode, UIState } from '../types/ui';
import { UIStateManager } from '../ui/UIStateManager';
import { EventChannel } from '../utils/EventChannel';

export class AppKernel implements AppPort {
  readonly data = loadProjectData();
  readonly uiState = new UIStateManager();
  readonly scene: SceneBootstrap;
  readonly audio = new AudioManager();
  readonly objects = new ObjectRegistry(this.data.tabernacle.objects);
  readonly characters = new CharacterSystem(new CharacterRegistry(this.data.characters.characters));
  readonly characterAppearance = new CharacterAppearanceResolver(this.data.characters.characters, this.data.garments.states, this.data.roleCostumes.roles);
  readonly rituals: RitualPlaybackController;
  readonly scriptures = new ScriptureMappingService(new ScriptureRegistry(this.data.scriptures.passages));
  readonly tour = new TourManager(this.data.tours.tours.slice().sort((a, b) => a.order - b.order).map((tour) => ({
    id: tour.id,
    locationId: tour.locationId,
    objectId: tour.objectId,
    title: tour.title,
    scriptureReference: tour.scriptureReference,
    summary: tour.summary,
  })));
  readonly learning = new LearningModeManager();
  readonly cinematic = new CinematicTourController();
  readonly assets = new AssetManifest(this.data.assets.assets);
  readonly assetLoader: GLTFAssetLoader;
  readonly assetRuntime: AssetRuntimeManager;
  readonly ritualVisuals: RitualVisualSystem;
  readonly stats: ArchitectureStats;
  readonly #experienceEvents = new EventChannel<Readonly<ExperienceState>>();
  #creditsOpen = false;
  #unsubscribe: (() => void) | null = null;
  #assetUnsubscribe: (() => void) | null = null;
  #cinematicUnsubscribe: (() => void) | null = null;

  constructor(canvas: HTMLCanvasElement) {
    this.scene = new SceneBootstrap(canvas, this.data.dimensions.specs);
    this.ritualVisuals = new RitualVisualSystem(this.scene.context.worldRoot);
    this.rituals = new RitualPlaybackController(new RitualRegistry(this.data.rituals.rituals), {
      onStepEnter: (ritual, step) => {
        this.ritualVisuals.play(ritual.id, step);
        this.scene.context.particles.clearNarrativeCues();
        if (step.playbackHook.startsWith('effects.incense') && step.id !== 'incense-boundary') this.scene.context.particles.setCue('incense-smoke');
        if (step.id === 'lamp-light') this.scene.context.particles.setCue('menorah-flames');
        if (step.id === 'atonement-incense') this.scene.context.particles.setCue('incense-smoke');
      },
      onStateChange: (state) => {
        if (state.status === 'paused') { this.ritualVisuals.pause(); this.scene.context.particles.clearNarrativeCues(); }
        if (state.status === 'idle' || state.status === 'complete') { this.ritualVisuals.stop(); this.scene.context.particles.clearNarrativeCues(); }
        const ritual = state.ritualId ? this.rituals?.registry.get(state.ritualId) : undefined;
        const step = ritual?.steps[state.stepIndex];
        this.uiState.selectRitual(state.ritualId, step?.branchId ?? null, step?.id ?? null);
        this.uiState.setPlaybackOwner(state.status === 'idle' || state.status === 'complete' ? 'none' : 'ritual');
        this.publishExperience();
      },
    });
    const forcedFailureAssetId = import.meta.env.DEV ? new URLSearchParams(window.location.search).get('assetFailure') : null;
    this.assetLoader = forcedFailureAssetId ? new GLTFAssetLoader({ forceFailureAssetId: forcedFailureAssetId }) : new GLTFAssetLoader();
    this.assetRuntime = new AssetRuntimeManager(this.assets, this.assetLoader, this.scene.context.assetRoot, runtimeConfig.assetProfile);
    this.stats = {
      objects: this.objects.size,
      characters: this.characters.registry.size,
      rituals: this.rituals.registry.size,
      scriptures: this.scriptures.registry.size,
      locations: this.data.world.locations.length,
      assets: this.assets.size,
    };
    this.#unsubscribe = this.uiState.subscribe((state) => this.applyMode(state.mode));
    this.#assetUnsubscribe = this.assetRuntime.subscribe((state) => this.onAssetState(state));
    this.#cinematicUnsubscribe = this.cinematic.subscribe((state) => this.onCinematicState(state));
    this.scene.setUpdate((deltaSeconds) => this.update(deltaSeconds));

    // Listen to manual orbit dragging to pause cinematic tour cleanly
    this.scene.context.cameraManager.controls?.addEventListener('start', () => {
      if (this.cinematic.snapshot.isPlaying && !this.cinematic.snapshot.isPaused) {
        this.cinematic.pause();
        this.scene.context.cameraManager.stopFlyTo();
      }
    });
  }

  start(): void {
    window.addEventListener('resize', this.#onResize);
    this.scene.start();
    void this.startAssets();
  }

  setAtmosphere(mode: AtmosphereMode): void {
    this.scene.setAtmosphere(mode);
  }

  setQuality(preset: 'high' | 'medium' | 'low'): void {
    this.scene.setQuality(preset);
  }

  getState(): Readonly<UIState> { return this.uiState.snapshot; }
  subscribe(listener: (state: Readonly<UIState>) => void): () => void { return this.uiState.subscribe(listener); }
  transitionTo(mode: ExperienceMode, reason: string): void {
    if (this.cinematic.snapshot.isPlaying) this.stopCinematicTour();
    if (mode === 'tour' && !this.tour.current) return;
    if (mode !== 'ritual' && this.rituals.state.status !== 'idle') this.resetRitualPlayback();
    const isCurrentMode = this.uiState.snapshot.mode === mode;
    this.uiState.transitionTo(mode, reason);
    this.audio.playNav();
    if (mode === 'ritual' && this.rituals.state.status === 'idle') {
      const firstRitual = this.rituals.registry.values().find((ritual) => ritual.type === 'washing' || ritual.type === 'incense');
      if (firstRitual) this.startRitual(firstRitual.id);
      return;
    }
    if (mode === 'tour') { this.tour.reset(); this.focusTourStop(); }
    if (mode === 'learning') this.openLearningObject(this.learning.context.objectId ?? 'burnt-altar');
    if (mode === 'overview' && isCurrentMode) this.scene.context.cameraManager.applyMode('overview');
    this.publishExperience();
  }

  // Cinematic Tour Implementation
  startCinematicTour(fromIndex = 0): void {
    this.resetRitualPlayback();
    void this.audio.enableAudio();
    this.audio.playNav();
    this.assetRuntime.setInteriorReveal(false);
    this.uiState.setPlaybackOwner('cinematic');
    this.cinematic.start(fromIndex);
  }

  stopCinematicTour(): void {
    this.cinematic.stop();
    this.scene.context.dimensions.clear();
    this.scene.context.cameraManager.stopFlyTo();
    this.assetRuntime.setInteriorReveal(this.uiState.snapshot.mode === 'learning');
    if (this.uiState.snapshot.playbackOwner === 'cinematic') this.uiState.setPlaybackOwner('none');
    this.publishExperience();
  }

  toggleCinematicPlayPause(): void {
    this.cinematic.togglePlayPause();
    this.audio.playClick();
  }

  nextCinematicAct(): void {
    this.cinematic.next();
    this.audio.playNav();
  }

  prevCinematicAct(): void {
    this.cinematic.previous();
    this.audio.playNav();
  }

  toggleCinematicDimensions(): void {
    this.cinematic.toggleDimensions();
    this.audio.playClick();
  }

  setCinematicDimensionUnit(unit: DimensionUnit): void {
    this.cinematic.setDimensionUnit(unit);
    this.scene.context.dimensions.setUnit(unit);
    this.audio.playClick();
  }

  setCinematicSpeed(speed: number): void {
    this.cinematic.setSpeed(speed);
    this.audio.playClick();
  }

  subscribeCinematic(listener: (state: Readonly<CinematicState>) => void): () => void {
    return this.cinematic.subscribe(listener);
  }

  getAssetState(): Readonly<AssetRuntimeState> { return this.assetRuntime.snapshot; }
  subscribeAssets(listener: (state: Readonly<AssetRuntimeState>) => void): () => void { return this.assetRuntime.subscribe(listener); }
  setAssetProfile(profile: AssetProfile): void { void this.assetRuntime.selectProfile(profile); }
  loadDetail(assetId: string): void { void this.assetRuntime.loadDetail(assetId); }

  getExperienceState(): Readonly<ExperienceState> {
    const object = this.learning.context.objectId ? this.objects.get(this.learning.context.objectId) : undefined;
    const location = object ? this.requireLocation(object.locationId) : null;
    const passages = object ? this.scriptures.threeDToBible({ kind: 'objectIds', entityId: object.id }) : [];
    const ritualIds = object ? this.rituals.registry.values().filter((ritual) => (ritual.trigger.kind === 'interaction' && ritual.trigger.objectId === object.id) || (ritual.trigger.kind === 'learning-mode' && ritual.trigger.locationId === object.locationId)).map((ritual) => ritual.id) : [];
    const offeringBranches = object?.id === 'burnt-altar'
      ? this.data.offerings.branches.filter(({ id }) => id !== 'burnt-offering-goat').map(({ id, label, ritualId, instruction }) => ({ id, label, ritualId, instruction }))
      : [];
    const offeringComparisons = object?.id === 'burnt-altar' ? this.data.offerings.comparisons : [];
    const characterIds = object ? [...new Set(this.rituals.registry.values().filter((ritual) => ritualIds.includes(ritual.id)).flatMap((ritual) => ritual.steps.flatMap((step) => step.characterIds)))] : [];
    const ritualState = this.rituals.state;
    const ritual = ritualState.ritualId ? this.rituals.registry.get(ritualState.ritualId) : undefined;
    const ritualStep = ritual?.steps[ritualState.stepIndex];
    const characterOmitted = Boolean(ritualStep?.id.startsWith('atonement-') && ritualStep.characterIds.length === 0);
    const defaultCharacterId = object?.id === 'ark' ? 'aaron-high-priest' : 'serving-priest';
    const selectedCharacterId = ritualStep?.characterIds[0] ?? characterIds[0] ?? this.learning.context.characterId ?? defaultCharacterId;
    const selectedCharacter = this.characters.registry.require(selectedCharacterId);
    const characterAppearance = this.characterAppearance.resolve(selectedCharacter.id, ritualStep?.garmentState ?? selectedCharacter.defaultGarmentState);
    const omissionDisclosure = ritualStep?.id === 'atonement-empty-room'
      ? '本步驟依利未記 16:17 顯示會幕裡不可有人；人物模型暫時隱藏。'
      : '本步驟只標示經文指定的路線或處理範圍；來源未提供可核准的人物身份，人物模型暫時隱藏。';
    const currentTour = this.tour.current;
    const currentTourDefinition = currentTour ? this.data.tours.tours.find(({ id }) => id === currentTour.id) : undefined;
    const currentTourExcerptText = currentTourDefinition?.excerptIds.map((id) => this.data.scriptureExcerpts.excerpts.find((excerpt) => excerpt.id === id)?.text).filter((text): text is string => Boolean(text)).join('\n\n') ?? null;
    return {
      tour: {
        playing: this.tour.playing,
        index: this.tour.index,
        total: this.tour.stops.length,
        current: currentTour ? {
          ...currentTour,
          summary: currentTour.summary ?? '',
          scriptureText: currentTourExcerptText,
        } : null,
      },
      learning: {
        objectId: object?.id ?? null,
        objectName: object?.name ?? null,
        confidence: object?.confidence ?? null,
        locationName: location?.name ?? null,
        scriptureReferences: passages.map((passage) => ({
          id: passage.id,
          summary: passage.summary,
          annotation: passage.annotation,
          originalText: passage.originalText,
          context: passage.context,
          sourceUrl: passage.sourceUrl,
        })),
        ritualIds,
        offeringBranches,
        offeringComparisons,
        characterIds,
        availableObjects: this.data.objectDetails.objects.map(({ id, name }) => ({ id, name })),
        detail: object ? (() => {
          const detail = this.data.objectDetails.objects.find((candidate) => candidate.id === object.id);
          return detail ? {
            id: detail.id,
            summary: detail.summary,
            dimensions: detail.dimensions,
            materials: detail.materials,
            parts: detail.parts.map(({ id, label }) => ({ id, label })),
          } : null;
        })() : null,
      },
      ritual: {
        playback: ritualState,
        stepIndex: ritualState.stepIndex,
        stepCount: ritual?.steps.length ?? 0,
        branchId: ritualStep?.branchId ?? null,
        name: ritual?.name ?? null,
        stepTitle: ritualStep?.title ?? null,
        instruction: ritualStep?.instruction ?? null,
        confidence: ritualStep?.confidence ?? null,
        scriptureReferences: ritualStep ? [...ritualStep.scriptureReferences] : [],
        displayCue: ritualStep?.displayCue ?? null,
        unresolved: ritualStep ? [...ritualStep.unresolved] : [],
      },
      character: {
        id: characterAppearance.characterId,
        name: characterAppearance.name,
        role: characterAppearance.role,
        roleLabel: characterAppearance.roleLabel,
        garmentState: characterAppearance.garmentState,
        garmentLabel: characterAppearance.garmentLabel,
        status: characterOmitted ? 'omitted' : 'study',
        visualPolicy: characterAppearance.visualPolicy,
        baseAssetId: characterOmitted ? null : characterAppearance.baseAssetId,
        position: null,
        responsibilities: characterOmitted ? [] : characterAppearance.responsibilities,
        parts: characterOmitted ? [] : characterAppearance.parts.map(({ id, label, claimedMaterials, quantity, function: partFunction, unknowns }) => ({ id, label, claimedMaterials, quantity, function: partFunction, unknowns })),
        validationNotes: characterOmitted ? [] : characterAppearance.validationNotes,
        disclosure: characterOmitted ? omissionDisclosure : characterAppearance.disclosure,
      },
      creditsOpen: this.#creditsOpen,
      assetProfile: this.assetRuntime.snapshot.profile,
    };
  }

  subscribeExperience(listener: (state: Readonly<ExperienceState>) => void): () => void {
    listener(this.getExperienceState());
    return this.#experienceEvents.subscribe(listener);
  }

  commandTour(command: TourCommand): void {
    if (command === 'close') { this.tour.pause(); this.uiState.returnToPrevious('tour-close'); }
    if (command === 'previous') { this.tour.previous(); this.focusTourStop(); }
    if (command === 'next') { this.tour.next(); this.focusTourStop(); }
    this.audio.playClick();
    this.publishExperience();
  }

  selectLearningObject(objectId: string): void {
    if (this.uiState.snapshot.mode !== 'learning') this.uiState.transitionTo('learning', `interaction:${objectId}`);
    this.audio.playInspect();
    this.openLearningObject(objectId);
    this.publishExperience();
  }

  startRitual(ritualId: string): void {
    if (this.cinematic.snapshot.isPlaying) this.stopCinematicTour();
    const ritual = this.rituals.registry.require(ritualId);
    if (!['washing', 'burnt-offering', 'incense', 'lamp-care', 'shewbread', 'atonement-entry'].includes(ritual.type)) return;
    if (this.uiState.snapshot.mode !== 'ritual') this.uiState.transitionTo('ritual', `ritual-start:${ritualId}`);
    this.uiState.selectRitual(ritualId, ritual.steps[0]?.branchId ?? null, ritual.steps[0]?.id ?? null);
    this.uiState.setPlaybackOwner('ritual');
    this.learning.open({ ritualId, locationId: ritual.locationId, characterId: ritual.steps[0]?.characterIds[0] ?? null });
    this.rituals.start(ritualId);
    const ritualLocation = this.requireLocation(ritual.locationId);
    this.scene.context.cameraManager.focus(ritualLocation.position, ritualLocation.position.z < -2 ? 3.4 : 5.8);
    this.audio.playClick();
    this.publishExperience();
  }

  commandRitual(command: RitualCommand): void {
    if (command === 'close') { this.resetRitualPlayback(); this.learning.open({ ritualId: null, characterId: null }); this.uiState.returnToPrevious('ritual-close'); }
    if (command === 'play-pause') {
      if (this.rituals.state.status === 'playing') this.rituals.pause();
      else if (this.rituals.state.status === 'paused') {
        this.rituals.resume();
        const activeRitual = this.rituals.state.ritualId ? this.rituals.registry.get(this.rituals.state.ritualId) : undefined;
        const activeStep = activeRitual?.steps[this.rituals.state.stepIndex];
        if (activeRitual && activeStep) {
          this.ritualVisuals.play(activeRitual.id, activeStep);
          this.scene.context.particles.clearNarrativeCues();
          if (activeStep.playbackHook.startsWith('effects.incense') && activeStep.id !== 'incense-boundary') this.scene.context.particles.setCue('incense-smoke');
          if (activeStep.id === 'atonement-incense') this.scene.context.particles.setCue('incense-smoke');
          if (activeStep.id === 'lamp-light') this.scene.context.particles.setCue('menorah-flames');
        }
      }
    }
    if (command === 'previous') this.rituals.previous();
    if (command === 'next') this.rituals.next();
    if (command === 'replay') this.rituals.replay();
    this.audio.playClick();
    this.publishExperience();
  }

  setCreditsOpen(open: boolean): void { this.#creditsOpen = open; this.publishExperience(); }

  getAttributions(): AttributionView[] {
    return this.assets.values().map((asset) => ({
      id: asset.id,
      title: asset.attribution.split(' by ')[0] ?? asset.id,
      author: asset.author,
      sourceUrl: asset.sourceUrl,
      license: asset.license,
      attribution: asset.attribution,
    }));
  }

  dispose(): void {
    this.#unsubscribe?.();
    this.#assetUnsubscribe?.();
    this.#cinematicUnsubscribe?.();
    this.#experienceEvents.clear();
    this.audio.dispose();
    this.ritualVisuals.dispose();
    this.assetRuntime.dispose();
    this.scene.dispose();
    window.removeEventListener('resize', this.#onResize);
  }

  private async startAssets(): Promise<void> { await this.assetRuntime.selectProfile(runtimeConfig.assetProfile); }

  private applyMode(mode: ExperienceMode): void {
    this.assetRuntime.setProfileVisible(!(mode === 'learning' && this.assetRuntime.snapshot.profile === 'desktop-structural'));
    this.assetRuntime.setInteriorReveal(mode === 'learning' && this.assetRuntime.snapshot.profile !== 'desktop-structural');
    this.scene.context.particles.setLearningDetailFocus(mode === 'learning');
    this.scene.context.cameraManager.applyMode(mode);
    if (mode !== 'tour') this.tour.pause();
    this.publishExperience();
  }

  private update(deltaSeconds: number): void {
    this.ritualVisuals.update(performance.now() / 1000);
    this.cinematic.update(deltaSeconds);

    const cameraPose = this.scene.context.cameraManager.pose;
    this.audio.updatePlayerState(cameraPose.position, false, deltaSeconds);
  }

  #lastHandledActId: string | null = null;
  #detailSelectionGeneration = 0;
  private onCinematicState(state: Readonly<CinematicState>): void {
    if (!state.isPlaying) {
      this.#lastHandledActId = null;
      return;
    }

    const act = state.currentAct;
    if (act.id !== this.#lastHandledActId) {
      this.#lastHandledActId = act.id;

      // Keep tabernacle and curtains fully visible during cinematic walkthrough
      this.assetRuntime.setInteriorReveal(!!act.peelRoof);

      // Start camera smooth flight from act.cameraStart to act.cameraEnd
      this.scene.context.cameraManager.flyAlongPath(
        act.cameraStart,
        act.cameraEnd,
        act.durationSeconds / state.playbackSpeed
      );

      // Trigger 3D Dimensions
      if (state.showDimensions && act.dimensionTargetId) {
        this.scene.context.dimensions.setUnit(state.dimensionUnit);
        this.scene.context.dimensions.showObjectDimensions(act.dimensionTargetId);
      } else {
        this.scene.context.dimensions.clear();
      }
    } else {
      // Dynamic dimension toggle during the same act
      if (state.showDimensions && act.dimensionTargetId) {
        this.scene.context.dimensions.setUnit(state.dimensionUnit);
        this.scene.context.dimensions.showObjectDimensions(act.dimensionTargetId);
      } else if (!state.showDimensions) {
        this.scene.context.dimensions.clear();
      }
    }
  }

  private openLearningObject(objectId: string): void {
    const object = this.objects.require(objectId);
    this.learning.open({ objectId, locationId: object.locationId, scriptureReference: object.scriptureReferences[0] ?? null, ritualId: null, characterId: null });
    this.uiState.selectEntity(objectId, 'object');
    this.scene.context.cameraManager.focusObject(object.id, object.interactionPosition);
    this.assetRuntime.setInteriorReveal(this.uiState.snapshot.mode === 'learning' && this.assetRuntime.snapshot.profile !== 'desktop-structural');
    if (object.assetId) void this.ensureDetailAsset(object.assetId, ++this.#detailSelectionGeneration);
  }

  private async ensureDetailAsset(assetId: string, selectionGeneration: number): Promise<void> {
    if (this.assetRuntime.snapshot.profile !== 'desktop-structural') {
      await this.assetRuntime.selectProfile('desktop-structural');
    }
    if (selectionGeneration !== this.#detailSelectionGeneration) return;
    if (this.getState().mode === 'learning' || this.getState().mode === 'ritual') await this.assetRuntime.loadDetail(assetId);
  }

  private focusTourStop(): void {
    const stop = this.tour.current;
    if (!stop) return;
    if (stop.objectId) {
      const object = this.objects.require(stop.objectId);
      this.scene.context.cameraManager.focusObject(object.id, object.interactionPosition);
      this.publishExperience();
      return;
    }
    this.scene.context.cameraManager.focus(this.requireLocation(stop.locationId).position, 9.5);
    this.publishExperience();
  }

  private requireLocation(locationId: string): (typeof this.data.world.locations)[number] {
    const location = this.data.world.locations.find((candidate) => candidate.id === locationId);
    if (!location) throw new Error(`Missing location: ${locationId}`);
    return location;
  }

  private publishExperience(): void { this.#experienceEvents.emit(this.getExperienceState()); }

  private resetRitualPlayback(): void {
    if (this.rituals.state.status !== 'idle') this.rituals.reset();
    this.ritualVisuals.stop();
    this.scene.context.particles.clearNarrativeCues();
    this.uiState.selectRitual(null);
    if (this.uiState.snapshot.playbackOwner === 'ritual') this.uiState.setPlaybackOwner('none');
  }

  private onAssetState(state: Readonly<AssetRuntimeState>): void {
    this.assetRuntime.setProfileVisible(!(this.getState().mode === 'learning' && state.profile === 'desktop-structural'));
    this.assetRuntime.setInteriorReveal(this.getState().mode === 'learning' && state.profile !== 'desktop-structural');
    if (state.phase === 'ready') {
      const mode = this.getState().mode;
      if (mode === 'overview') {
        const profileAssetId = state.profile === 'desktop-high' ? 'tabernacle-main' : state.profile === 'desktop-structural' ? 'tabernacle-framework' : 'tabernacle-lowpoly';
        const bounds = state.boundsByAssetId[profileAssetId];
        if (bounds) this.scene.context.cameraManager.frameBounds(bounds);
      }
      if (mode === 'learning' && this.learning.context.objectId) {
        const object = this.objects.require(this.learning.context.objectId);
        if (state.profile === 'desktop-structural' && object.assetId && !state.activeAssetIds.includes(object.assetId)) {
          this.loadDetail(object.assetId);
        } else {
          const detailBounds = object.assetId ? state.boundsByAssetId[object.assetId] : undefined;
          if (detailBounds) this.scene.context.cameraManager.frameDetailBounds(detailBounds);
          else this.scene.context.cameraManager.focusObject(object.id, object.interactionPosition);
        }
      }
      if (mode === 'tour') this.focusTourStop();
    }
    this.publishExperience();
  }

  readonly #onResize = (): void => this.scene.resize();
}
