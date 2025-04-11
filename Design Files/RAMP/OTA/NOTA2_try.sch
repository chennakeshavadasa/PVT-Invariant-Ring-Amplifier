v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 510 -240 760 -240 {lab=GND}
N 510 -210 510 -160 {lab=#net1}
N 630 -160 760 -160 {lab=#net1}
N 760 -210 760 -160 {lab=#net1}
N 630 -160 630 -130 {lab=#net1}
N 510 -160 630 -160 {lab=#net1}
N 630 -70 630 -40 {lab=GND}
N 610 -470 720 -470 {lab=#net2}
N 510 -400 510 -270 {lab=#net2}
N 510 -400 610 -400 {lab=#net2}
N 510 -440 510 -400 {lab=#net2}
N 610 -470 610 -400 {lab=#net2}
N 550 -470 610 -470 {lab=#net2}
N 760 -560 760 -470 {lab=VDD}
N 510 -560 760 -560 {lab=VDD}
N 510 -560 510 -470 {lab=VDD}
N 390 -240 470 -240 {lab=#net3}
N 800 -240 880 -240 {lab=#net4}
N 390 -140 390 -110 {lab=GND}
N 390 -240 390 -200 {lab=#net3}
N 880 -140 880 -110 {lab=GND}
N 260 -140 260 -100 {lab=GND}
N 260 -240 260 -200 {lab=VDD}
N 760 -440 760 -270 {lab=vout}
N 880 -240 880 -200 {lab=#net4}
C {sg13g2_pr/sg13_hv_nmos.sym} 490 -240 0 0 {name=M1
l=1.5u
w=3.5u
ng=1
m=2
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 780 -240 0 1 {name=M2
l=1.5u
w=3.5u
ng=1
m=2
model=sg13_hv_nmos
spiceprefix=X
}
C {isource.sym} 630 -100 0 0 {name=I0 value=2u}
C {gnd.sym} 630 -40 0 0 {name=l1 lab=GND}
C {gnd.sym} 630 -240 0 0 {name=l2 lab=GND}
C {sg13g2_pr/sg13_hv_pmos.sym} 740 -470 0 0 {name=M3
l=1u
w=0.5u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_pmos.sym} 530 -470 0 1 {name=M4
l=1u
w=0.5u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {vsource.sym} 390 -170 0 0 {name=V1 value="dc 0.825 ac 1 180" savecurrent=false}
C {gnd.sym} 390 -110 0 0 {name=l3 lab=GND}
C {vsource.sym} 880 -170 0 0 {name=V2 value="dc 0.825 ac 1" savecurrent=false}
C {gnd.sym} 880 -110 0 0 {name=l4 lab=GND}
C {devices/code_shown.sym} 70 -540 0 0 {name="NGSPICE" only_toplevel=true 
value="
.option wnflag=1
.option savecurrents
.temp 27
.control
save all
write NOTA2_try.raw
set appendwrite 
op
write NOTA2_try.raw
**dc temp -50 150 1
tran 1m 10m 1m
ac dec 20 1 1e8
plot vdb(vout)
.endc
"}
C {devices/code_shown.sym} 930 -530 0 0 {name=SAVE_COMMANDS only_toplevel=false
value="
.save @n.xm1.nsg13_hv_nmos[gds]
.save @n.xm1.nsg13_hv_nmos[gm]
.save @n.xm1.nsg13_hv_nmos[gmb]
.save @n.xm1.nsg13_hv_nmos[ids]
.save @n.xm1.nsg13_hv_nmos[l]
.save @n.xm1.nsg13_hv_nmos[vth]
.save @n.xm1.nsg13_hv_nmos[cgg]
.save @n.xm2.nsg13_hv_nmos[cgd]
.save @n.xm2.nsg13_hv_nmos[cgg]
.save @n.xm2.nsg13_hv_nmos[cgs]
.save @n.xm2.nsg13_hv_nmos[gds]
.save @n.xm2.nsg13_hv_nmos[gm]
.save @n.xm2.nsg13_hv_nmos[gmb]
.save @n.xm2.nsg13_hv_nmos[ids]
.save @n.xm2.nsg13_hv_nmos[l]
.save @n.xm2.nsg13_hv_nmos[vth]
"}
C {code_shown.sym} 950 -160 0 0 {
name=TT_MODELS
only_toplevel=true
value="
** IHP models
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
"
spice_ignore=false
      }
C {devices/launcher.sym} 1000 -40 0 0 {name=h1
descr="load op & annotate" 
tclcommand="xschem raw_read $netlist_dir/Deadzone_try_1.raw; set show_hidden_texts 1; xschem annotate_op"}
C {devices/ngspice_get_value.sym} 860 -400 0 0 {name=r3 node=@n.xm1.nsg13_hv_nmos[cgg]
descr="cgg="}
C {devices/ngspice_get_value.sym} 860 -360 0 0 {name=r4 node=v(@n.xm1.nsg13_hv_nmos[vth])
descr="Vt="}
C {devices/ngspice_get_value.sym} 860 -310 0 0 {name=r5 node=@n.xm1.nsg13_hv_nmos[gm]
descr="gm1="}
C {gnd.sym} 260 -100 0 0 {name=l5 lab=GND}
C {vsource.sym} 260 -170 0 0 {name=V3 value=1.65 savecurrent=false}
C {vdd.sym} 260 -240 0 0 {name=l6 lab=VDD}
C {vdd.sym} 640 -560 0 0 {name=l7 lab=VDD}
C {lab_pin.sym} 760 -360 0 1 {name=p1 sig_type=std_logic lab=vout}
C {ngspice_probe.sym} 630 -160 0 0 {name=r1}
C {ngspice_probe.sym} 610 -400 0 0 {name=r2}
