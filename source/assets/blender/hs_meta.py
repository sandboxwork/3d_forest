import json
def C(x0, x1, y0, y1, top, bottom):
    """blender rect (x0..x1, y0..y1) -> three collider (cz = -y)"""
    return {"cx": round((x0 + x1) / 2, 4), "cz": round(-(y0 + y1) / 2, 4), "hx": round((x1 - x0) / 2, 4), "hz": round((y1 - y0) / 2, 4),
            "top": top, "bottom": bottom}
cols = [
    {"cx": 0, "cz": 0, "hx": 4.25, "hz": 3.25, "top": 0.30, "bottom": -1},
    # outer walls (front wall has the door opening between x=-0.5..0.5)
    C(-4.5, -0.5, -3.5, -3.25, 3.2, 0.30), C(0.5, 4.5, -3.5, -3.25, 3.2, 0.30),
    C(-4.5, 4.5, 3.25, 3.5, 3.2, 0.30), C(-4.5, -4.25, -3.25, 3.25, 3.2, 0.30), C(4.25, 4.5, -3.25, 3.25, 3.2, 0.30),
    # partition wall, doorway gap y=-0.875..0.075
    C(1.4, 1.65, -3.25, -0.875, 3.15, 0.30), C(1.4, 1.65, 0.075, 3.25, 3.15, 0.30),
    # foundation plinth ring (top 0.30)
    C(-4.6, 4.6, -3.6, -3.25, 0.30, -0.6), C(-4.6, 4.6, 3.25, 3.6, 0.30, -0.6),
    C(-4.6, -4.25, -3.25, 3.25, 0.30, -0.6), C(4.25, 4.6, -3.25, 3.25, 0.30, -0.6),
    # chimney stack + wide base
    C(-5.05, -4.5, -0.75, 0.75, 7.3, -0.6), C(-5.22, -4.5, -0.93, 0.93, 1.04, -0.6),
    # fireplace: hearth, breast, mantel
    C(-4.25, -3.75, -1.15, 1.15, 0.45, 0.30), C(-4.25, -3.80, -1.1, 1.1, 1.6, 0.45), C(-4.25, -3.90, -0.95, 0.95, 3.15, 1.6), C(-4.25, -3.59, -1.25, 1.25, 1.6, 1.5),
    # porch deck, steps, posts, rails, bench
    C(-2.2, 2.2, -5.8, -3.5, 0.52, 0), C(-0.85, 0.85, -6.1, -5.8, 0.35, 0), C(-0.85, 0.85, -6.4, -6.1, 0.17, 0),
    C(-2.175, -2.025, -5.825, -5.675, 2.43, 0.52), C(2.025, 2.175, -5.825, -5.675, 2.43, 0.52),
    C(-2.175, -2.025, -3.795, -3.645, 2.75, 0.52), C(2.025, 2.175, -3.795, -3.645, 2.75, 0.52),
    C(2.06, 2.14, -5.75, -3.72, 1.51, 0.52), C(-2.14, -2.06, -5.75, -3.72, 1.51, 0.52),
    C(0.98, 2.03, -5.79, -5.71, 1.51, 0.52), C(-2.03, -0.98, -5.79, -5.71, 1.51, 0.52),
    C(0.78, 2.0, -3.93, -3.52, 0.985, 0.52),
    # back: woodpile + shed posts, chopping block; side: garden bed ring
    C(-1.45, 1.45, 3.5, 4.1, 1.65, 0), C(-1.435, -1.325, 4.775, 4.885, 2.02, 0), C(1.325, 1.435, 4.775, 4.885, 2.02, 0),
    C(-2.83, -2.37, 4.47, 4.93, 0.44, 0),
    C(4.75, 6.15, -1.9, 2.5, 0.22, 0),
]
meta = {
    "colliders": cols,
    "doors": [
        {"name": "door_front", "hinge": [-0.497, 1.405, 3.36], "openAngle": 1.75, "interactPos": [0, 4.1],
         "note": "hinge at left edge seen from outside (x=-0.5); leaf extends +x; rotating the part about three Y by +1.75 swings it INWARD (toward -z three). Use -1.75 to swing outward."},
        {"name": "door_bedroom", "hinge": [1.525, 1.30, -0.057], "openAngle": 1.6, "interactPos": [0.95, 0.4],
         "note": "hinge at y=+0.057 (blender), leaf extends toward -y blender; +1.6 about three Y swings it into the bedroom (+x)."},
    ],
    "lights": [],
    "fireEmbers": {"pos": [-4.1, 0.5, 0.0]},
    "floorY": 0.30, "ceilingY": 3.15, "eavesY": 3.2, "ridgeY": 5.4, "chimneyTopY": 7.3,
}
json.dump(meta, open('/shared/river/assets/out/house_shell.meta.json', 'w'), indent=1)
print('meta ok', len(cols))
