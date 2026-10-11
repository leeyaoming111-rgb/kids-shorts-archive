"""Batch Seed-VC singing conversion: load the 44.1k f0-conditioned model once, convert many lines.
usage: python batch.py jobs.json  (list of {src, ref, out_dir, shift})"""
import sys, json, argparse, os, time
import inference as I
jobs = json.load(open(sys.argv[1])); steps = int(sys.argv[2]) if len(sys.argv) > 2 else 15
base = argparse.Namespace(source=None, target=None, output=None, diffusion_steps=steps, length_adjust=1.0, inference_cfg_rate=0.7,
                          f0_condition=True, auto_f0_adjust=False, semi_tone_shift=0, checkpoint=None, config=None, fp16=False)
cache = I.load_models(base); I.load_models = lambda a: cache
for j in jobs:
    t0 = time.time(); os.makedirs(j["out_dir"], exist_ok=True)
    I.main(argparse.Namespace(**{**vars(base), "source": j["src"], "target": j["ref"], "output": j["out_dir"], "semi_tone_shift": j["shift"]}))
    print("DONE", j["src"], round(time.time() - t0), "s", flush=True)
