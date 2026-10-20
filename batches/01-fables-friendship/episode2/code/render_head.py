"""Tumble & Pip long-form episode v2: one Story Stump scene per run (16:9).
Built on the Episode 01 stump renderer (sunset-to-night light, storybook with pictures, arm IK) plus:
  - TALK mode: Tumble on the grass, Pip on the stump edge, the book open on the stump; free gestures for both;
  - gestures and looks driven by the script (to the audience, to each other, to the book);
  - a shot planner (timeline.py): wide, two-shot, close-ups, audience shots, book inserts, picture-quiz pages;
  - the dance break (talk positions, Pip hops to Tumble's paw for each chorus) and the recap lullaby on the pages.
python3 render.py --scene <name> [--preview] [out.mp4] | x <secs...> | seg f0 f1 out.mp4 | sheet | qa"""
import os, sys
if "--scene" in sys.argv:
    _i = sys.argv.index("--scene"); os.environ["SCENE"] = sys.argv[_i + 1]; del sys.argv[_i:_i + 2]
os.environ["ASPECT"] = "wide"
from fablekit import *
import fablekit as FK
from functools import lru_cache
from scipy.optimize import minimize
SCENE = T.SCENE
MODE = T.MODE
HERE_ = os.path.dirname(os.path.abspath(__file__))
STILLS = os.path.join(HERE_, "stills")
