import { mapSalienceToColor } from '../SentenceSalienceHeatmap.jsx';

function parseRgb(rgb) {
    const m = rgb.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
    if (!m) return null;
    return [Number(m[1]), Number(m[2]), Number(m[3])];
}

it('maps 0 to the low color for orange scheme', () => {
    const c = mapSalienceToColor(0, 'orange');
    expect(c).toBe('rgb(242, 242, 242)'); // #f2f2f2
});

it('maps 1 to the high color for orange scheme', () => {
    const c = mapSalienceToColor(1, 'orange');
    expect(c).toBe('rgb(255, 123, 0)'); // #ff7b00
});

it('maps mid value approximately to the midpoint for orange', () => {
    const c = mapSalienceToColor(0.5, 'orange');
    const parsed = parseRgb(c);
    // Deterministic rounding expected:
    // r = round(242 + (255-242)*0.5) = round(248.5) = 249
    // g = round(242 + (123-242)*0.5) = round(182.5) = 183
    // b = round(242 + (0-242)*0.5) = round(121) = 121
    expect(parsed).toEqual([249, 183, 121]);
});

it('clamps values below 0 to low color and above 1 to high color', () => {
    expect(mapSalienceToColor(-0.5, 'red')).toBe('rgb(248, 234, 234)'); // red low: #f8eaea
    expect(mapSalienceToColor(2, 'purple')).toBe('rgb(106, 76, 147)'); // purple high: #6a4c93
});

it('falls back to orange scheme when unknown scheme provided', () => {
    const c = mapSalienceToColor(1, 'unknown-scheme');
    expect(c).toBe('rgb(255, 123, 0)'); // same as orange high
});