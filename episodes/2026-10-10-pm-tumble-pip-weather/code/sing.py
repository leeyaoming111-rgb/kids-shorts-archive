import numpy as np, soundfile as sf, parselmouth
from parselmouth.praat import call
from scipy import signal
from timeline import TRANSPOSE

def midi_hz(m): return 440.0 * 2 ** ((m + TRANSPOSE - 69) / 12)

def load_trim(path):
    x, sr = sf.read(path)
    env = np.abs(x); idx = np.where(env > 0.02 * env.max())[0]
    return x[max(0, idx[0] - int(0.01 * sr)): min(len(x), idx[-1] + int(0.05 * sr))], sr

def syllable_nuclei(snd, n):
    inten = snd.to_intensity(minimum_pitch=100, time_step=0.005)
    tv = inten.xs(); iv = inten.values[0]
    pitch = snd.to_pitch(0.005, 50, 600)
    voiced = np.array([pitch.get_value_at_time(t) > 0 for t in tv])
    iv_s = np.convolve(iv, np.ones(5) / 5, mode="same")
    peaks = [i for i in range(2, len(iv_s) - 2)
             if voiced[i] and iv_s[i] >= iv_s[i - 1] and iv_s[i] > iv_s[i + 1] and iv_s[i] > iv_s.max() - 25]
    merged = []
    for p in peaks:
        if merged and iv_s[merged[-1]:p + 1].min() > min(iv_s[merged[-1]], iv_s[p]) - 1.5:
            if iv_s[p] > iv_s[merged[-1]]: merged[-1] = p
        else:
            merged.append(p)
    while len(merged) > n:
        merged.remove(min(merged, key=lambda q: iv_s[q]))
    if len(merged) < n:
        vt = tv[voiced]; a, z = vt[0], vt[-1]
        return list(np.linspace(a, z, n + 2)[1:-1]), tv, iv_s
    return [tv[i] for i in merged], tv, iv_s

def sing_phrase(path, onsets, durs, notes, out_sr=44100):
    x, sr = load_trim(path)
    snd = parselmouth.Sound(x, sampling_frequency=sr)
    T = snd.get_total_duration(); n = len(notes)
    nuc, tv, iv = syllable_nuclei(snd, n)
    bnd = [0.0]
    for a, z in zip(nuc, nuc[1:]):
        m = (tv > a) & (tv < z)
        bnd.append(tv[m][np.argmin(iv[m])] if m.any() else (a + z) / 2)
    bnd.append(T)
    lead = nuc[0]
    src_pts = [0.0] + list(nuc) + [T]
    tgt_pts = [0.0] + [lead + (onsets[i] - onsets[0]) for i in range(n)]
    tgt_pts.append(lead + (onsets[-1] - onsets[0]) + max(durs[-1] - 0.06, (T - nuc[-1]) * 0.8))
    manip = call(snd, "To Manipulation", 0.005, 50, 600)
    dt = call(manip, "Extract duration tier"); call(dt, "Remove points between", 0, T)
    pitch = snd.to_pitch(0.005, 50, 600)
    step = 0.005; fr = np.arange(step / 2, T, step)
    voiced = np.array([pitch.get_value_at_time(t) > 0 for t in fr])
    fac = np.ones(len(fr))
    for i in range(len(src_pts) - 1):
        s0, s1 = src_pts[i], src_pts[i + 1]; G = tgt_pts[i + 1] - tgt_pts[i]
        m = (fr >= s0) & (fr < s1)
        if not m.any(): continue
        v = voiced[m].sum() * step; u = (~voiced[m]).sum() * step
        if v > 0.02:
            kv = np.clip((G - u) / v, 0.5, 4.0)
            fac[m] = np.where(voiced[m], kv, 1.0 if G >= u else max(0.6, G / max(u + v, 1e-3)))
        else:
            fac[m] = np.clip(G / max(s1 - s0, 1e-3), 0.6, 1.6)
    for t_, f_ in zip(fr, fac): call(dt, "Add point", t_, float(f_))
    call([dt, manip], "Replace duration tier")
    pt = call(manip, "Extract pitch tier"); call(pt, "Remove points between", 0, T)
    src_to_tgt = lambda s: float(np.interp(s, src_pts, tgt_pts))
    for i in range(n):
        a, z = bnd[i], bnd[i + 1]; f = midi_hz(notes[i])
        prev_f = midi_hz(notes[i - 1]) if i else f * 2 ** (-1 / 12)
        steps = max(6, int((z - a) / 0.01))
        for k in range(steps + 1):
            s = a + (z - a) * k / steps
            tt = src_to_tgt(s) - src_to_tgt(a)
            semis = (1 - min(1.0, tt / 0.045)) * 12 * np.log2(prev_f / f)
            if tt > 0.32:
                semis += 0.22 * np.sin(2 * np.pi * 5.3 * tt) * min(1, (tt - 0.32) / 0.25)
            call(pt, "Add point", min(max(s, 1e-4), T - 1e-4), f * 2 ** (semis / 12))
    call([pt, manip], "Replace pitch tier")
    y = call(manip, "Get resynthesis (overlap-add)").values[0]
    if sr == 24000: y = signal.resample_poly(y, 147, 80)
    fd = int(0.006 * out_sr); y[:fd] *= np.linspace(0, 1, fd); y[-fd * 5:] *= np.linspace(1, 0, fd * 5)
    return y, lead

def hnr(x, sr):
    h = call(parselmouth.Sound(x, sr), "To Harmonicity (cc)", 0.01, 75, 0.1, 1.0).values[0]
    return float(np.mean(h[h > -100]))
