v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 490 -520 490 -490 {lab=#net1}
N 620 -520 760 -520 {lab=#net1}
N 760 -520 760 -490 {lab=#net1}
N 490 -520 620 -520 {lab=#net1}
N 570 -460 760 -460 {lab=VDD}
N 800 -460 890 -460 {lab=#net2}
N 490 -360 490 -290 {lab=#net3}
N 760 -430 760 -290 {lab=Vout}
N 620 -260 720 -260 {lab=#net3}
N 490 -360 620 -360 {lab=#net3}
N 490 -430 490 -360 {lab=#net3}
N 620 -360 620 -260 {lab=#net3}
N 530 -260 620 -260 {lab=#net3}
N 490 -140 760 -140 {lab=GND}
N 490 -260 490 -140 {lab=GND}
N 760 -260 760 -140 {lab=GND}
N 110 -680 110 -590 {lab=VDD}
N 570 -680 620 -680 {lab=VDD}
N 110 -510 110 -430 {lab=#net4}
N 110 -510 200 -510 {lab=#net4}
N 110 -560 110 -510 {lab=#net4}
N 200 -590 200 -510 {lab=#net4}
N 150 -590 200 -590 {lab=#net4}
N 110 -140 490 -140 {lab=GND}
N 110 -370 110 -140 {lab=GND}
N 0 -300 0 -270 {lab=GND}
N 0 -400 -0 -360 {lab=VDD}
N 340 -400 340 -370 {lab=GND}
N 340 -460 450 -460 {lab=#net5}
N 890 -400 890 -370 {lab=GND}
N 620 -580 620 -520 {lab=#net1}
N 620 -680 620 -640 {lab=VDD}
N 570 -680 570 -460 {lab=VDD}
N 110 -680 570 -680 {lab=VDD}
N 490 -460 570 -460 {lab=VDD}
C {sg13g2_pr/sg13_lv_pmos.sym} 470 -460 0 0 {name=M2
l=0.5u
w=1.2u
ng=1
m=2
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 780 -460 0 1 {name=M3
l=0.5u
w=1.2u
ng=1
m=2
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 740 -260 0 0 {name=M4
l=2u
w=0.5u
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 510 -260 0 1 {name=M5
l=2u
w=0.5u
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_pmos.sym} 130 -590 0 1 {name=M6
l=0.4u
w=0.3u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {isource.sym} 110 -400 0 0 {name=I0 value=1u}
C {gnd.sym} 430 -140 0 0 {name=l1 lab=GND}
C {vsource.sym} 0 -330 0 0 {name=V1 value=1.65 savecurrent=false}
C {gnd.sym} 0 -270 0 0 {name=l2 lab=GND}
C {vdd.sym} 0 -400 0 0 {name=l3 lab=VDD}
C {vdd.sym} 390 -680 0 0 {name=l4 lab=VDD}
C {vsource.sym} 340 -430 0 0 {name=V2 value="dc 0.72 ac 1 180" savecurrent=false}
C {gnd.sym} 340 -370 0 0 {name=l5 lab=GND}
C {vsource.sym} 890 -430 0 0 {name=V3 value="dc 0.72 ac 1 "  savecurrent=false}
C {gnd.sym} 890 -370 0 0 {name=l6 lab=GND}
C {isource.sym} 620 -610 0 0 {name=I1 value=2u}
C {devices/code_shown.sym} 970 -580 0 0 {name="NGSPICE" only_toplevel=true 
value="
.option wnflag=1
.option savecurrents
.temp 27
.control
save all
write POTA1.raw
set appendwrite 
op
write POTA1.raw
**dc temp -50 150 1
**tran 1m 10m 1m
*plot vdb(Vout)
ac dec 20 1 1e8
plot vdb(Vout)
**plot vdb(vout2) vdb(vout1)
.endc
"}
C {code_shown.sym} 970 -250 0 0 {
name=TT_MODELS
only_toplevel=true
value="
** IHP models
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
"
spice_ignore=false
      }
C {devices/code_shown.sym} 1280 -560 0 0 {name=SAVE_COMMANDS only_toplevel=false
value="
.save @n.xm2.nsg13_lv_pmos[gds]
.save @n.xm2.nsg13_lv_pmos[gm]
.save @n.xm2.nsg13_lv_pmos[gmb]
.save @n.xm2.nsg13_lv_pmos[ids]
.save @n.xm2.nsg13_lv_pmos[l]
.save @n.xm2.nsg13_lv_pmos[vth]
.save @n.xm2.nsg13_lv_pmos[cgg]
.save @n.xm3.nsg13_lv_pmos[cgd]
.save @n.xm3.nsg13_lv_pmos[cgg]
.save @n.xm3.nsg13_lv_pmos[cgs]
.save @n.xm3.nsg13_lv_pmos[gds]
.save @n.xm3.nsg13_lv_pmos[gm]
.save @n.xm3.nsg13_lv_pmos[gmb]
.save @n.xm3.nsg13_lv_pmos[ids]
.save @n.xm3.nsg13_lv_pmos[l]
.save @n.xm3.nsg13_lv_pmos[vth]
"}
C {devices/ngspice_get_value.sym} 810 -650 0 0 {name=r3 node=@n.xm2.nsg13_lv_pmos[cgg]
descr="cgg="}
C {devices/ngspice_get_value.sym} 810 -610 0 0 {name=r4 node=v(@n.xm2.nsg13_lv_pmos[vth])
descr="Vt="}
C {devices/ngspice_get_value.sym} 810 -530 0 0 {name=r5 node=@n.xm2.nsg13_lv_pmos[gm]
descr="gm2="}
C {devices/launcher.sym} 940 -130 0 0 {name=h1
descr="load op & annotate" 
tclcommand="xschem raw_read $netlist_dir/Deadzone_try_1.raw; set show_hidden_texts 1; xschem annotate_op"}
C {ngspice_probe.sym} 495 -360 0 0 {name=r1}
C {ngspice_probe.sym} 620 -520 0 0 {name=r2}
C {ngspice_probe.sym} 760 -360 0 0 {name=r6}
C {lab_pin.sym} 760 -340 0 1 {name=p1 sig_type=std_logic lab=Vout}
