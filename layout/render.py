"""Render a GDS to PNG with the IHP layer colours.
klayout -b -r layout/render.py -rd gds=<file> -rd png=<out> [-rd box=x0,y0,x1,y1 (um)] [-rd w=2000]"""
import os
import pya
K = os.path.join(os.environ.get("PDK_ROOT", os.path.expanduser("~/.ciel")), "ihp-sg13g2", "libs.tech", "klayout")
w = int(globals().get("w", "2000"))
lv = pya.LayoutView()
lv.set_config("background-color", "#ffffff")
lv.set_config("grid-visible", "false")
lv.set_config("text-visible", "true")
lv.load_layout(gds, 0)
lv.load_layer_props(os.path.join(K, "tech", "sg13g2.lyp"))
lv.max_hier()
if "box" in globals():
    x0, y0, x1, y1 = [float(v) for v in box.split(",")]
    lv.zoom_box(pya.DBox(x0, y0, x1, y1))
else:
    lv.zoom_fit()
bb = lv.box()
h = int(w * bb.height() / bb.width())
lv.save_image(png, w, h)
print("saved", png, w, h)
