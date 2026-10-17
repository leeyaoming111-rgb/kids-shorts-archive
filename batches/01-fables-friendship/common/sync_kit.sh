#!/bin/sh
# Copy the shared Batch 01 renderer files into every fable's code/ folder (the Mac helper renders from that folder).
cd "$(dirname "$0")/.."
for d in fable-*/code; do
  [ "$d" = "fable-01-tiny-pip-big-help/code" ] && continue   # Fable 1 predates the kit and keeps its own renderer
  cp common/fablekit.py common/render_base.py common/meshes.py common/qa_geom.py "$d/"
done
