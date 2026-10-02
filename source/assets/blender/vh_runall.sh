#!/bin/bash
# usage: vh_runall.sh "names" ; env VH_RENDER / VH_VIEWS pass through
cd /shared/river/assets/blender
for n in $1; do
  ~/.cache/motion-video-deps/blender/bin/blender -b --python vh_$n.py -- > /tmp/vh_$n.log 2>&1 &
done
wait
grep -hE "BUILD|Error|Trace|line [0-9]+, in" $(for n in $1; do echo /tmp/vh_$n.log; done)
