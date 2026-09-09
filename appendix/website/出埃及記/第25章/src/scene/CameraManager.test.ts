import { describe, expect, it } from 'vitest';
import { CameraManager } from './CameraManager';
import { loadProjectData } from '../data/loadProjectData';

describe('CameraManager', () => {
  it('uses distinct overview, tour, and learning rigs', () => {
    const camera = new CameraManager(16 / 9);
    const poses = ['overview', 'tour', 'learning'].map((mode) => {
      camera.applyMode(mode as 'overview' | 'tour' | 'learning');
      return camera.pose.position;
    });
    expect(new Set(poses.map((pose) => JSON.stringify(pose))).size).toBe(3);
  });

  it('focuses from a tour-specific angle without changing its mode', () => {
    const camera = new CameraManager(1, undefined, loadProjectData().dimensions.specs);
    camera.applyMode('tour');
    camera.focus({ x: 0, y: 0, z: 9 }, 6);
    expect(camera.pose.mode).toBe('tour');
    expect(camera.pose.fov).toBe(46);
  });

  it('frames an object from its typed dimension spec', () => {
    const camera = new CameraManager(1);
    camera.applyMode('learning');
    camera.focusObject('menorah', { x: -1.2, y: 0, z: -4.35 });
    expect(camera.pose.position.z).toBeGreaterThan(-4.35);
    expect(camera.pose.fov).toBe(43);
  });
});
