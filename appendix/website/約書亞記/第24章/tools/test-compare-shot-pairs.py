"""Regression checks for real pixel ratios and intentionally steady dialogue."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image

SITE = Path(__file__).resolve().parents[1]
SCRATCH = SITE / '.tmp-shots'
SCRATCH.mkdir(exist_ok=True)


class PixelCheckerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='pair-check-', dir=SCRATCH)
        self.root = Path(self.temp.name).resolve()
        assert self.root.parent == SCRATCH.resolve()
        self.dialogues = []
        for device in ['desktop', 'mobile-landscape']:
            folder = self.root / device
            folder.mkdir()
            for i in range(1, 37):
                cue = f'family-{i}' if i <= 6 else 'motion'
                beat = f'beat-{i:02d}-{cue}'
                a = Image.new('RGB', (100, 100), 'black')
                b = a.copy()
                if i > 6:
                    # Exactly 100 of 10,000 pixels change: one percent.
                    for x in range(100):
                        b.putpixel((x, 0), (255, 255, 255))
                else:
                    self.dialogues.append({'device': device, 'beat': beat, 'visible': True, 'sameText': True, 'dx': 0, 'dy': 0})
                a.save(folder / f'{beat}-a.png')
                b.save(folder / f'{beat}-b.png')
        self.write_dialogues()

    def tearDown(self):
        assert self.root.parent == SCRATCH.resolve()
        self.temp.cleanup()

    def write_dialogues(self):
        (self.root / 'dialogues.json').write_text(json.dumps(self.dialogues), encoding='utf-8')

    def check(self):
        result = subprocess.run([sys.executable, '-I', str(SITE / 'tools/compare-shot-pairs.py'), str(self.root)], capture_output=True)
        return result.returncode, json.loads((self.root / 'pixel-diff.json').read_text(encoding='utf-8'))

    def test_actual_percentage_and_steady_speech_pass(self):
        code, report = self.check()
        self.assertEqual(code, 0)
        self.assertEqual(report['desktop']['minChangedPixels'], .01)
        self.assertEqual(report['desktop']['motionPairs'], 30)
        self.assertEqual(report['desktop']['dialoguePairs'], 6)

    def test_frozen_motion_fails(self):
        Image.new('RGB', (100, 100), 'black').save(self.root / 'desktop/beat-07-motion-b.png')
        code, report = self.check()
        self.assertEqual(code, 1)
        self.assertTrue(any('beat-07-motion' in error for error in report['errors']))

    def test_missing_dialogue_evidence_fails(self):
        self.dialogues.pop(0)
        self.write_dialogues()
        code, report = self.check()
        self.assertEqual(code, 1)
        self.assertTrue(any('speech bubble missing' in error for error in report['errors']))


if __name__ == '__main__':
    unittest.main()
