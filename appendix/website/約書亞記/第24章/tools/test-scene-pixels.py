"""Negative controls for the screenshot acceptance gate; run from the site root."""
from pathlib import Path

from PIL import Image, ImageDraw
from importlib.util import module_from_spec, spec_from_file_location

spec = spec_from_file_location('pixels', Path(__file__).with_name('check-scene-pixels.py'))
pixels = module_from_spec(spec)
spec.loader.exec_module(pixels)
out = Path('.tmp-shots/shechem-env/pixel-controls')
out.mkdir(parents=True, exist_ok=True)
sample = {'cue':'my-house', 'uiMasks':[{'x0':0,'y0':0,'x1':200,'y1':30}],
          'visual':{'environment':{'from':'morning','to':'morning','amount':0},
                    'figures':[{'id':'person','headX':100,'headY':60,'footX':100,'footY':150,'inFrame':True}]}}


def check(name, image):
    path = out / (name+'.png')
    image.save(path)
    return pixels.measure(path, sample, [200, 180])


black = Image.new('RGB', (200, 180), '#080808')
assert len(check('black', black)['failures']) == 2
bright_ui = black.copy()
ImageDraw.Draw(bright_ui).rectangle((0, 0, 199, 29), fill='white')
assert check('bright-ui-black-scene', bright_ui)['meanL'] < 5
bright = Image.new('RGB', (200, 180), '#d8bb91')
assert check('no-person', bright)['detectedFigures'] == 0
person = bright.copy()
draw = ImageDraw.Draw(person)
draw.ellipse((94, 60, 106, 77), fill='#171315')
draw.rectangle((91, 75, 109, 150), fill='#171315')
assert not check('person', person)['failures']
sample['visual']['figures'][0]['inFrame'] = False
assert check('offscreen', person)['detectedFigures'] == 0
sample['cue'] = 'epilogue-stone'
sample['visual']['environment'] = {'from':'night','to':'night','amount':0}
assert not check('empty-ending', black)['failures']
print('Pixel gate: 6 negative/positive controls PASS')
