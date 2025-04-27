v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 180 -80 260 -80 {lab=#net1}
N 550 -80 610 -80 {lab=#net2}
N 180 -20 180 0 {lab=GND}
N 180 0 300 0 {lab=GND}
N 300 -80 300 0 {lab=GND}
N 550 -20 550 0 {lab=GND}
N 550 0 650 0 {lab=GND}
N 650 -80 650 0 {lab=GND}
N 420 -30 420 0 {lab=GND}
N 300 0 420 0 {lab=GND}
N 420 -160 420 -90 {lab=#net3}
N 300 -160 420 -160 {lab=#net3}
N 300 -160 300 -110 {lab=#net3}
N 760 -30 760 0 {lab=GND}
N 760 -160 760 -90 {lab=#net4}
N 650 0 760 0 {lab=GND}
N 650 -160 650 -110 {lab=#net4}
N 650 -160 760 -160 {lab=#net4}
N 860 -80 940 -80 {lab=GND}
N 1100 -30 1100 0 {lab=GND}
N 1100 -160 1100 -90 {lab=#net5}
N 980 -160 1100 -160 {lab=#net5}
N 980 -160 980 -80 {lab=#net5}
N 980 90 980 120 {lab=GND}
N 980 -50 980 30 {lab=#net6}
C {sg13g2_pr/sg13_hv_nmos.sym} 280 -80 0 0 {name=M1
l=0.5u
w=0.5u
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 630 -80 0 0 {name=M2
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {vsource.sym} 180 -50 0 0 {name=V2 value=1.65 savecurrent=false}
C {vsource.sym} 550 -50 0 0 {name=V1 value=1.65 savecurrent=false}
C {vsource.sym} 420 -60 0 0 {name=V3 value=50m savecurrent=false}
C {vsource.sym} 760 -60 0 0 {name=V4 value=50m savecurrent=false}
C {gnd.sym} 300 0 0 0 {name=l1 lab=GND}
C {gnd.sym} 650 0 0 0 {name=l2 lab=GND}
C {devices/code_shown.sym} -450 -410 0 0 {name="NGSPICE" only_toplevel=true 
value="
.option wnflag=1
.option savecurrents
.temp 27
.control
save all
write onres_try.raw
set appendwrite 
op
write onres_try.raw
**dc temp -50 150 1
tran 1m 10m 1m
**ac dec 20 1 1e8
**plot vdb(vout2) vdb(vout1)
.endc
"}
C {devices/launcher.sym} 340 -240 0 0 {name=h1
descr="load op & annotate" 
tclcommand="xschem raw_read $netlist_dir/Diff-amp_2.raw; set show_hidden_texts 1; xschem annotate_op"}
C {ngspice_probe.sym} 300 -160 0 0 {name=r1}
C {ngspice_probe.sym} 220 -80 0 0 {name=r2}
C {ngspice_probe.sym} 570 -80 0 0 {name=r3}
C {ngspice_probe.sym} 700 -160 0 0 {name=r4}
C {code_shown.sym} -440 -100 0 0 {
name=TT_MODELS
only_toplevel=true
value="
** IHP models
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
"
spice_ignore=false
      }
C {devices/code_shown.sym} -180 -410 0 0 {name=SAVE_COMMANDS only_toplevel=true 
value="
.save @n.xm1.nsg13_hv_nmos[gm]
.save @n.xm1.nsg13_hv_nmos[gds]
.save @n.xm1.nsg13_hv_nmos[vth]
.save @n.xm1.nsg13_hv_nmos[ids]
.save @n.xm1.nsg13_hv_nmos[vdss]
.save @n.xm1.nsg13_hv_nmos[cgg]
.save @n.xm1.nsg13_hv_nmos[cgsol]
.save @n.xm1.nsg13_hv_nmos[cgdol]
.save @n.xm2.nsg13_lv_nmos[gm]
.save @n.xm2.nsg13_lv_nmos[gds]
.save @n.xm2.nsg13_lv_nmos[ids]
.save @n.xm2.nsg13_lv_nmos[vth]
.save @n.xm2.nsg13_lv_nmos[vdss]
.save @n.xm2.nsg13_lv_nmos[cgg]
.save @n.xm2.nsg13_lv_nmos[cgsol]
.save @n.xm2.nsg13_lv_nmos[cgdol]
.save @n.xm3.nsg13_lv_pmos[gm]
.save @n.xm3.nsg13_lv_pmos[gds]
.save @n.xm3.nsg13_lv_pmos[vth]
.save @n.xm3.nsg13_lv_pmos[ids]
.save @n.xm3.nsg13_lv_pmos[vdss]
.save @n.xm3.nsg13_lv_pmos[cgg]
.save @n.xm3.nsg13_lv_pmos[cgsol]
.save @n.xm3.nsg13_lv_pmos[cgdol]
"}
C {sg13g2_pr/annotate_fet_params.sym} 310 -370 0 0 {name=annot1 ref=M1}
C {sg13g2_pr/annotate_fet_params.sym} 500 -380 0 0 {name=annot2 ref=M2}
C {vsource.sym} 1100 -60 0 0 {name=V6 value=1.65 savecurrent=false}
C {gnd.sym} 860 -80 0 0 {name=l3 lab=GND}
C {ngspice_probe.sym} 980 -160 0 0 {name=r5}
C {ngspice_probe.sym} 900 -80 0 0 {name=r6}
C {sg13g2_pr/sg13_lv_pmos.sym} 960 -80 0 0 {name=M3
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {gnd.sym} 1100 0 0 0 {name=l4 lab=GND}
C {vsource.sym} 980 60 0 0 {name=V7 value=1.6 savecurrent=false}
C {gnd.sym} 980 120 0 0 {name=l5 lab=GND}
C {sg13g2_pr/annotate_fet_params.sym} 640 -390 0 0 {name=annot3 ref=M3}
