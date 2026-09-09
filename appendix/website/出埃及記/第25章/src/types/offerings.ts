import type { ConfidenceLevel, EntityId, ScriptureReference } from './core';

export type OfferingAnimalKind = 'cattle' | 'sheep' | 'goat' | 'bird';
export type OfferingRepresentation = 'model-with-label' | 'symbol-with-label';

export interface OfferingAnimalDefinition {
  id: EntityId;
  label: string;
  kind: OfferingAnimalKind;
  requiredSex: 'male' | 'female' | 'unspecified';
  assetId: EntityId | null;
  representation: OfferingRepresentation;
  confidence: ConfidenceLevel;
  sourceClaimIds: string[];
  scriptureReferences: ScriptureReference[];
  limitations: string[];
}

export interface OfferingBranchDefinition {
  id: EntityId;
  label: string;
  animalId: EntityId;
  ritualId: EntityId;
  branchKind: OfferingAnimalKind;
  actorRole: 'offering-person' | 'priest';
  sourceClaimIds: string[];
  instruction: string;
}

export interface OfferingsData {
  animals: OfferingAnimalDefinition[];
  branches: OfferingBranchDefinition[];
}
