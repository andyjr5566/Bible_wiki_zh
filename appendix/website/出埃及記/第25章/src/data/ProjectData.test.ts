import { describe, expect, it } from 'vitest';
import { loadProjectData } from './loadProjectData';

describe('project data contracts', () => {
  const data = loadProjectData();
  const assertUnique = (ids: string[]) => expect(new Set(ids).size).toBe(ids.length);
  const assertClaimReferences = (claimIds: Set<string>, ids: string[]) => ids.forEach((id) => { if (!claimIds.has(id)) throw new Error(`Missing claim: ${id}`); });
  it('contains unique ids and valid cross references', () => {
    const locationIds = data.world.locations.map(({ id }) => id);
    const objectIds = data.tabernacle.objects.map(({ id }) => id);
    const characterIds = data.characters.characters.map(({ id }) => id);
    const ritualIds = data.rituals.rituals.map(({ id }) => id);
    const assetIds = data.assets.assets.map(({ id }) => id);
    const locations = new Set(locationIds);
    const objects = new Set(objectIds);
    const characters = new Set(characterIds);
    const rituals = new Set(ritualIds);
    const assets = new Set(assetIds);
    [locationIds, objectIds, characterIds, ritualIds, assetIds].forEach(assertUnique);
    data.tabernacle.objects.forEach((object) => { expect(locations.has(object.locationId)).toBe(true); if (object.assetId) expect(assets.has(object.assetId)).toBe(true); });
    data.rituals.rituals.forEach((ritual) => {
      expect(locations.has(ritual.locationId)).toBe(true);
      ritual.steps.forEach((step) => { expect(locations.has(step.locationId)).toBe(true); step.objectIds.forEach((id) => expect(objects.has(id)).toBe(true)); step.characterIds.forEach((id) => expect(characters.has(id)).toBe(true)); step.nextStepIds.forEach((id) => expect(ritual.steps.some((candidate) => candidate.id === id)).toBe(true)); });
    });
    data.scriptures.passages.forEach((passage) => {
      expect(passage.originalText.length).toBeGreaterThan(0);
      passage.links.objectIds.forEach((id) => expect(objects.has(id)).toBe(true));
      passage.links.ritualIds.forEach((id) => expect(rituals.has(id)).toBe(true));
      passage.links.locationIds.forEach((id) => expect(locations.has(id)).toBe(true));
      passage.links.characterIds.forEach((id) => expect(characters.has(id)).toBe(true));
    });
    const claimIds = new Set(data.evidence.claims.map(({ id }) => id));
    const excerptIds = new Set(data.scriptureExcerpts.excerpts.map(({ id }) => id));
    data.objectDetails.objects.forEach((detail) => {
      expect(objects.has(detail.id)).toBe(true);
      expect(locations.has(detail.locationId)).toBe(true);
      assertClaimReferences(claimIds, detail.claimIds);
      assertClaimReferences(claimIds, detail.dimensions.sourceClaimIds);
    });
    data.tours.tours.forEach((tour) => {
      expect(locations.has(tour.locationId)).toBe(true);
      if (tour.objectId) expect(objects.has(tour.objectId)).toBe(true);
      tour.excerptIds.forEach((id) => expect(excerptIds.has(id)).toBe(true));
    });
    data.assetParts.mappings.forEach((mapping) => {
      expect(assetIds).toContain(mapping.assetId);
      expect(objects).toContain(mapping.objectId);
      mapping.parts.forEach((part) => expect(part.partId).toMatch(/^[a-z0-9][a-z0-9-]*$/));
    });
    expect(data.objectDetails.objects.find(({ id }) => id === 'menorah')?.dimensions.status).toBe('unresolved');
    expect(data.objectDetails.objects.find(({ id }) => id === 'menorah')?.dimensions.heightCubits).toBeNull();
  });
  it('defines all required high-priest garment slots', () => {
    const highPriest = data.characters.characters.find(({ role }) => role === 'HighPriest');
    expect(highPriest?.garments.map(({ slot }) => slot)).toEqual(expect.arrayContaining(['Ephod', 'Breastpiece', 'TurbanMiter', 'Robe', 'Tunic', 'GoldPlate']));
  });
  it('keeps costume states and offering representations traceable', () => {
    const claimIds = new Set(data.evidence.claims.map(({ id }) => id));
    const assetIds = new Set(data.assets.assets.map(({ id }) => id));
    const rituals = new Set(data.rituals.rituals.map(({ id }) => id));
    expect(data.garments.states.map(({ id }) => id)).toEqual(expect.arrayContaining(['daily-priest', 'daily-high-priest', 'atonement-linen', 'post-atonement-garments', 'unspecified']));
    data.garments.states.forEach((state) => {
      state.sourceClaimIds.forEach((id) => expect(claimIds.has(id)).toBe(true));
      state.parts.forEach((part) => part.sourceClaimIds.forEach((id) => expect(claimIds.has(id)).toBe(true)));
    });
    data.offerings.animals.forEach((animal) => {
      animal.sourceClaimIds.forEach((id) => expect(claimIds.has(id)).toBe(true));
      if (animal.assetId) expect(assetIds.has(animal.assetId)).toBe(true);
      if (animal.representation === 'symbol-with-label') expect(animal.assetId).toBeNull();
    });
    data.offerings.branches.forEach((branch) => {
      const animal = data.offerings.animals.find(({ id }) => id === branch.animalId);
      expect(animal?.kind).toBe(branch.branchKind);
      expect(animal?.sourceClaimIds).toContain('C-LV01-BRANCHES');
    });
    expect(data.offerings.branches.find(({ id }) => id === 'burnt-offering-cattle')?.animalId).toBe('offering-bull');
    expect(data.offerings.branches.some(({ animalId }) => animalId === 'offering-cow-candidate')).toBe(false);
    expect(data.offerings.branches.map(({ ritualId }) => ritualId)).toEqual([
      'burnt-offering-service',
      'burnt-offering-sheep-service',
      'burnt-offering-goat-service',
      'burnt-offering-bird-service',
    ]);
    data.offerings.branches.forEach((branch) => expect(rituals.has(branch.ritualId)).toBe(true));
  });

  it('keeps lampstand and shewbread teaching steps source-linked', () => {
    const lampstand = data.rituals.rituals.find(({ id }) => id === 'lampstand-care');
    const shewbread = data.rituals.rituals.find(({ id }) => id === 'shewbread-service');
    expect(lampstand?.steps.map(({ id }) => id)).toEqual(['lamp-oil-present', 'lamp-tend', 'lamp-light']);
    expect(lampstand?.steps[2]?.objectIds).toContain('menorah');
    expect(lampstand?.steps[2]?.displayCue).toContain('七盞燈');
    expect(shewbread?.steps).toHaveLength(4);
    expect(shewbread?.steps[1]?.instruction).toContain('十二個餅');
    expect(shewbread?.steps[2]?.instruction).toContain('安息日');
    expect(shewbread?.steps[3]?.instruction).toContain('亞倫和子孫');
    expect(shewbread?.steps.every(({ actorRole }) => actorRole === 'priest' || actorRole === 'actor-unspecified')).toBe(true);
  });

  it('defines five offering comparisons without merging handling rules', () => {
    const claimIds = new Set(data.evidence.claims.map(({ id }) => id));
    const comparisonIds = data.offerings.comparisons.map(({ id }) => id);
    expect(comparisonIds).toEqual(['burnt-offering', 'grain-offering', 'peace-offering', 'sin-offering', 'guilt-offering']);
    expect(new Set(comparisonIds).size).toBe(5);
    data.offerings.comparisons.forEach((comparison) => {
      comparison.sourceClaimIds.forEach((id) => expect(claimIds.has(id)).toBe(true));
      expect(comparison.scriptureReferences.length).toBeGreaterThan(0);
      expect(comparison.handling.length).toBeGreaterThan(0);
    });
    expect(data.offerings.comparisons.find(({ id }) => id === 'peace-offering')?.handling).toContain('不把全牲都焚燒');
    expect(data.offerings.comparisons.find(({ id }) => id === 'sin-offering')?.handling).toContain('帶血入會幕');
  });
  it('fails closed for duplicate IDs and missing claim references', () => {
    expect(() => assertUnique(['same-id', 'same-id'])).toThrow();
    expect(() => assertClaimReferences(new Set(data.evidence.claims.map(({ id }) => id)), ['C-MISSING'])).toThrow();
  });
});
