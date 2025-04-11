v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
L 4 900 -360 900 -110 {}
L 4 1000 -360 1000 -110 {}
L 4 840 -320 1100 -320 {}
L 4 830 -320 840 -320 {}
L 4 800 -320 830 -320 {}
L 4 900 -370 900 -360 {}
L 4 900 -110 900 -100 {}
L 4 1000 -370 1000 -360 {}
L 4 1000 -110 1000 -100 {}
L 4 800 -290 1100 -290 {}
L 4 800 -260 1100 -260 {}
L 4 800 -230 1100 -230 {}
L 4 800 -200 1100 -200 {}
L 4 800 -170 1100 -170 {}
P 4 6 800 -360 800 -100 1100 -100 1100 -370 800 -370 800 -360 {}
T {Corners} 810 -360 0 0 0.4 0.4 {}
T {VGP} 930 -360 0 0 0.4 0.4 {}
T {VGN} 1030 -360 0 0 0.4 0.4 {}
T {tt} 840 -320 0 0 0.4 0.4 {}
T {0.99943} 910 -320 0 0 0.4 0.4 {}
T {0.67224} 1010 -320 0 0 0.4 0.4 {}
T {ss} 840 -290 0 0 0.4 0.4 {}
T {0.93781} 910 -290 0 0 0.4 0.4 {}
T {0.71885} 1010 -290 0 0 0.4 0.4 {}
T {ff} 840 -260 0 0 0.4 0.4 {}
T {1.0612} 910 -260 0 0 0.4 0.4 {}
T {0.62359} 1010 -260 0 0 0.4 0.4 {}
T {fs} 840 -230 0 0 0.4 0.4 {}
T {0.96869} 910 -230 0 0 0.4 0.4 {}
T {0.64786} 1010 -230 0 0 0.4 0.4 {}
T {sf} 840 -200 0 0 0.4 0.4 {}
T {1.0304} 910 -200 0 0 0.4 0.4 {}
T {0.6955} 1010 -200 0 0 0.4 0.4 {}
N 310 -140 340 -140 {lab=GND}
N 340 -140 340 -90 {lab=GND}
N 310 -90 340 -90 {lab=GND}
N 310 -110 310 -90 {lab=GND}
N 200 -140 270 -140 {lab=VGN}
N 200 -200 200 -140 {lab=VGN}
N 200 -200 310 -200 {lab=VGN}
N 310 -200 310 -170 {lab=VGN}
N 310 -270 310 -200 {lab=VGN}
N 310 -90 310 -20 {lab=GND}
N 510 -210 580 -210 {lab=VGP}
N 510 -210 510 -140 {lab=VGP}
N 510 -140 620 -140 {lab=VGP}
N 620 -180 620 -140 {lab=VGP}
N 620 -340 620 -210 {lab=VDD}
N 620 -140 620 -100 {lab=VGP}
N 620 -40 620 -20 {lab=GND}
N 310 -360 310 -330 {lab=VDD}
N 140 -270 140 -250 {lab=GND}
N 140 -360 140 -330 {lab=VDD}
C {sg13g2_pr/sg13_hv_nmos.sym} 290 -140 0 0 {name=M1
l=1u
w=2.3u
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_pmos.sym} 600 -210 0 0 {name=M2
l=0.5u
w=4.5u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {isource.sym} 310 -300 0 0 {name=I0 value=1u}
C {isource.sym} 620 -70 0 0 {name=I1 value=1u}
C {vdd.sym} 310 -360 0 0 {name=l1 lab=VDD}
C {vdd.sym} 620 -340 0 0 {name=l2 lab=VDD}
C {gnd.sym} 310 -20 0 0 {name=l3 lab=GND}
C {gnd.sym} 620 -20 0 0 {name=l4 lab=GND}
C {devices/code_shown.sym} -210 -430 0 0 {name=SAVE_COMMANDS only_toplevel=false
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
C {ngspice_probe.sym} 200 -200 0 0 {name=r1}
C {ngspice_probe.sym} 510 -170 0 0 {name=r2}
C {devices/code_shown.sym} -490 -420 0 0 {name="NGSPICE" only_toplevel=true 
value="
.option wnflag=1
.option savecurrents
.temp 27
.control
save all
write Deadzone_try_1.raw
set appendwrite 
op
write Deadzone_try_1.raw
**dc temp -50 150 1
tran 1m 10m 1m
**ac dec 20 1 1e8
**plot vdb(vout2) vdb(vout1)
.endc
"}
C {devices/launcher.sym} 30 -480 0 0 {name=h1
descr="load op & annotate" 
tclcommand="xschem raw_read $netlist_dir/Deadzone_try_1.raw; set show_hidden_texts 1; xschem annotate_op"}
C {vsource.sym} 140 -300 0 0 {name=V1 value=1.65 savecurrent=false}
C {gnd.sym} 140 -250 0 0 {name=l5 lab=GND}
C {vdd.sym} 140 -360 0 0 {name=l6 lab=VDD}
C {devices/ngspice_get_value.sym} 390 -240 0 0 {name=r3 node=@n.xm1.nsg13_hv_nmos[cgg]
descr="cgg="}
C {devices/ngspice_get_value.sym} 390 -200 0 0 {name=r4 node=v(@n.xm1.nsg13_hv_nmos[vth])
descr="Vt="}
C {devices/ngspice_get_value.sym} 390 -120 0 0 {name=r5 node=@n.xm1.nsg13_hv_nmos[gm]
descr="gm1="}
C {devices/ngspice_get_value.sym} 710 -200 0 0 {name=r6 node=@n.xm2.nsg13_hv_pmos[cgg]
descr="cgg="}
C {devices/ngspice_get_value.sym} 710 -160 0 0 {name=r7 node=v(@n.xm2.nsg13_hv_pmos[vth])
descr="Vt="}
C {devices/ngspice_get_value.sym} 710 -120 0 0 {name=r8 node=@n.xm2.nsg13_hv_pmos[gm]
descr="gm2="}
C {lab_pin.sym} 200 -140 0 0 {name=p1 sig_type=std_logic lab=VGN}
C {lab_pin.sym} 510 -140 0 0 {name=p2 sig_type=std_logic lab=VGP}
C {title.sym} 0 30 0 0 {name=l7 author="Nithin Purushothama"}
C {code_shown.sym} -470 -90 0 0 {
name=TT_MODELS
only_toplevel=true
value="
** IHP models
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
"
spice_ignore=false
      }
