"""Render a GDS to PNG with the IHP layer colours.
klayout -b -r layout/render.py -rd gds=<file> -rd png=<out> [-rd box=x0,y0,x1,y1 (um)] [-rd w=2000]
        [-rd hide=10/0,30/0,...]"""
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
# optional: hide layers given as "layer/datatype,..." (e.g. upper metals over the devices)
if "hide" in globals():
    hidden = {tuple(int(v) for v in h.split("/")) for h in hide.split(",") if h}
    it = lv.begin_layers()
    while not it.at_end():
        lp = it.current()
        if (lp.source_layer, lp.source_datatype) in hidden:
            lp.visible = False
            lv.set_layer_properties(it, lp)
        it.next()
if "box" in globals():
    x0, y0, x1, y1 = [float(v) for v in box.split(",")]
    target = pya.DBox(x0, y0, x1, y1)
else:
    lv.zoom_fit()
    target = lv.box()
h = int(w * target.height() / target.width())
# exact framing: render the requested box into a w x h image (2x oversampling)
lv.save_image_with_options(png, w, h, 0, 2, 0, target, False)
print("saved", png, w, h)
