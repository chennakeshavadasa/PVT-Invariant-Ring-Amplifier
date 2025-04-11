v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 370 -210 370 -160 {lab=#net1}
N 500 -160 630 -160 {lab=#net1}
N 630 -210 630 -160 {lab=#net1}
N 560 -240 630 -240 {lab=GND}
N 500 -160 500 -100 {lab=#net1}
N 370 -160 500 -160 {lab=#net1}
N 500 -40 500 -0 {lab=GND}
N 560 -240 560 -0 {lab=GND}
N 370 -240 560 -240 {lab=GND}
N 500 -0 560 -0 {lab=GND}
N 370 -370 370 -270 {lab=#net2}
N 450 -440 590 -440 {lab=#net2}
N 370 -370 450 -370 {lab=#net2}
N 370 -410 370 -370 {lab=#net2}
N 450 -440 450 -370 {lab=#net2}
N 410 -440 450 -440 {lab=#net2}
N 670 -240 760 -240 {lab=#net3}
N 370 -560 370 -440 {lab=VDD}
N 370 -560 630 -560 {lab=VDD}
N 630 -560 630 -440 {lab=VDD}
N 90 -120 90 -80 {lab=GND}
N 90 -220 90 -180 {lab=VDD}
N 220 -160 220 -120 {lab=GND}
N 220 -240 220 -220 {lab=#net4}
N 220 -240 330 -240 {lab=#net4}
N 760 -160 760 -120 {lab=GND}
N 630 -410 630 -270 {lab=vout}
N 760 -240 760 -220 {lab=#net3}
C {sg13g2_pr/sg13_hv_nmos.sym} 350 -240 0 0 {name=M1
l=1u
w=1.75u
ng=1
m=2
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 650 -240 0 1 {name=M2
l=1u
w=1.75u
ng=1
m=2
model=sg13_hv_nmos
spiceprefix=X
}
C {isource.sym} 500 -70 0 0 {name=I0 value=2u}
C {gnd.sym} 500 0 0 0 {name=l1 lab=GND}
C {sg13g2_pr/sg13_hv_pmos.sym} 610 -440 0 0 {name=M3
l=0.75u
w=0.5u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_pmos.sym} 390 -440 0 1 {name=M4
l=0.75u
w=0.5u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {vdd.sym} 500 -560 0 0 {name=l2 lab=VDD}
C {gnd.sym} 90 -80 0 0 {name=l3 lab=GND}
C {vsource.sym} 90 -150 0 0 {name=V1 value=1.65 savecurrent=false}
C {vdd.sym} 90 -220 0 0 {name=l4 lab=VDD}
C {gnd.sym} 220 -120 0 0 {name=l5 lab=GND}
C {vsource.sym} 220 -190 0 0 {name=V2 value="dc 0.93 ac 1" savecurrent=false}
C {gnd.sym} 760 -120 0 0 {name=l6 lab=GND}
C {vsource.sym} 760 -190 0 0 {name=V3 value="dc 0.93 ac 1 180"  savecurrent=false}
C {devices/code_shown.sym} 800 -550 0 0 {name=SAVE_COMMANDS only_toplevel=false
value="
.save @n.xm1.nsg13_hv_nmos[gds]
.save @n.xm1.nsg13_hv_nmos[gm]
.save @n.xm1.nsg13_hv_nmos[gmb]
.save @n.xm1.nsg13_hv_nmos[ids]
.save @n.xm1.nsg13_hv_nmos[l]
.save @n.xm1.nsg13_hv_nmos[vth]
.save @n.xm1.nsg13_hv_nmos[cgg]
.save @n.xm2.nsg13_hv_pmos[cgd]
.save @n.xm2.nsg13_hv_pmos[cgg]
.save @n.xm2.nsg13_hv_pmos[cgs]
.save @n.xm2.nsg13_hv_pmos[gds]
.save @n.xm2.nsg13_hv_pmos[gm]
.save @n.xm2.nsg13_hv_pmos[gmb]
.save @n.xm2.nsg13_hv_pmos[ids]
.save @n.xm2.nsg13_hv_pmos[l]
.save @n.xm2.nsg13_hv_pmos[vth]
"}
C {devices/code_shown.sym} -40 -560 0 0 {name="NGSPICE" only_toplevel=true 
value="
.option wnflag=1
.option savecurrents
.temp 27
.control
save all
write NOTA1.raw
set appendwrite 
op
write NOTA1.raw
**dc temp -50 150 1
tran 1m 10m 1m
ac dec 20 1 1e8
plot vdb(vout)
.endc
"}
C {code_shown.sym} 820 -180 0 0 {
name=TT_MODELS
only_toplevel=true
value="
** IHP models
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
"
spice_ignore=false
      }
C {devices/launcher.sym} 870 -60 0 0 {name=h1
descr="load op & annotate" 
tclcommand="xschem raw_read $netlist_dir/Deadzone_try_1.raw; set show_hidden_texts 1; xschem annotate_op"}
C {devices/ngspice_get_value.sym} 730 -460 0 0 {name=r3 node=@n.xm1.nsg13_hv_nmos[cgg]
descr="cgg="}
C {devices/ngspice_get_value.sym} 730 -420 0 0 {name=r4 node=v(@n.xm1.nsg13_hv_nmos[vth])
descr="Vt="}
C {devices/ngspice_get_value.sym} 730 -370 0 0 {name=r5 node=@n.xm1.nsg13_hv_nmos[gm]
descr="gm1="}
C {ngspice_probe.sym} 370 -320 0 0 {name=r1}
C {ngspice_probe.sym} 500 -160 0 1 {name=r6}
C {lab_pin.sym} 630 -350 0 1 {name=p1 sig_type=std_logic lab=vout}
