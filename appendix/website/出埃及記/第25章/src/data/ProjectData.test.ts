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
  });
  it('defines all required high-priest garment slots', () => {
    const highPriest = data.characters.characters.find(({ role }) => role === 'HighPriest');
    expect(highPriest?.garments.map(({ slot }) => slot)).toEqual(expect.arrayContaining(['Ephod', 'Breastpiece', 'TurbanMiter', 'Robe', 'Tunic', 'GoldPlate']));
  });
  it('fails closed for duplicate IDs and missing claim references', () => {
    expect(() => assertUnique(['same-id', 'same-id'])).toThrow();
    expect(() => assertClaimReferences(new Set(data.evidence.claims.map(({ id }) => id)), ['C-MISSING'])).toThrow();
  });
});
