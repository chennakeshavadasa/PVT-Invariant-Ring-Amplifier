v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
L 4 390 -550 650 -550 {}
L 4 380 -550 390 -550 {}
L 4 350 -550 380 -550 {}
L 4 450 -600 450 -590 {}
L 4 450 -410 450 -400 {}
L 4 550 -600 550 -590 {}
L 4 550 -410 550 -400 {}
L 4 350 -520 650 -520 {}
L 4 350 -490 650 -490 {}
L 4 350 -460 650 -460 {}
L 4 350 -430 650 -430 {}
L 4 350 -400 650 -400 {}
L 4 450 -590 450 -410 {}
L 4 550 -590 550 -410 {}
P 4 6 450 -600 350 -600 350 -400 650 -400 650 -600 450 -600 {}
T {Corners} 360 -590 0 0 0.4 0.4 {}
T {VGP} 480 -590 0 0 0.4 0.4 {}
T {VGN} 580 -590 0 0 0.4 0.4 {}
T {tt} 390 -550 0 0 0.4 0.4 {}
T {0.99943} 460 -550 0 0 0.4 0.4 {}
T {0.67224} 560 -550 0 0 0.4 0.4 {}
T {ss} 390 -520 0 0 0.4 0.4 {}
T {0.93781} 460 -520 0 0 0.4 0.4 {}
T {0.71885} 560 -520 0 0 0.4 0.4 {}
T {ff} 390 -490 0 0 0.4 0.4 {}
T {1.0612} 460 -490 0 0 0.4 0.4 {}
T {0.62359} 560 -490 0 0 0.4 0.4 {}
T {fs} 390 -460 0 0 0.4 0.4 {}
T {0.96869} 460 -460 0 0 0.4 0.4 {}
T {0.64786} 560 -460 0 0 0.4 0.4 {}
T {sf} 390 -430 0 0 0.4 0.4 {}
T {1.0304} 460 -430 0 0 0.4 0.4 {}
T {0.6955} 560 -430 0 0 0.4 0.4 {}
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
N 530 -210 600 -210 {lab=VGP}
N 530 -210 530 -140 {lab=VGP}
N 530 -140 640 -140 {lab=VGP}
N 640 -180 640 -140 {lab=VGP}
N 640 -340 640 -210 {lab=VDD}
N 640 -140 640 -100 {lab=VGP}
N 640 -40 640 -20 {lab=GND}
N 310 -360 310 -330 {lab=VDD}
N 140 -270 140 -250 {lab=GND}
N 140 -360 140 -330 {lab=VDD}
N 980 -110 980 -30 {lab=GND}
N 980 -380 980 -290 {lab=VDD}
N 980 -200 980 -140 {lab=Vout}
N 830 -290 940 -290 {lab=#net1}
N 840 -110 940 -110 {lab=#net2}
N 980 -200 1180 -200 {lab=Vout}
N 980 -260 980 -200 {lab=Vout}
N 1180 -200 1180 -170 {lab=Vout}
N 1180 -110 1180 -30 {lab=GND}
C {isource.sym} 310 -300 0 0 {name=I0 value=1u}
C {isource.sym} 640 -70 0 0 {name=I1 value=1u}
C {vdd.sym} 310 -360 0 0 {name=l1 lab=VDD}
C {vdd.sym} 640 -340 0 0 {name=l2 lab=VDD}
C {gnd.sym} 310 -20 0 0 {name=l3 lab=GND}
C {gnd.sym} 640 -20 0 0 {name=l4 lab=GND}
C {ngspice_probe.sym} 200 -200 0 0 {name=r1}
C {ngspice_probe.sym} 530 -170 0 0 {name=r2}
C {devices/code_shown.sym} -360 -420 0 0 {name="NGSPICE" only_toplevel=true 
value="
.option wnflag=1
.option savecurrents
.temp 27
.control
save all
write Deadzone_try_ac_1.raw
set appendwrite 
op
write Deadzone_try_ac_1.raw
**dc temp -50 150 1
**tran 1m 10m 1m
ac dec 20 1 1e8
plot vdb(vout)
.endc
"}
C {devices/launcher.sym} 420 -340 0 0 {name=h1
descr="load op & annotate" 
tclcommand="xschem raw_read $netlist_dir/Deadzone_try_ac_1.raw; set show_hidden_texts 1; xschem annotate_op"}
C {vsource.sym} 140 -300 0 0 {name=V1 value=1.65 savecurrent=false}
C {gnd.sym} 140 -250 0 0 {name=l5 lab=GND}
C {vdd.sym} 140 -360 0 0 {name=l6 lab=VDD}
C {lab_pin.sym} 200 -140 0 0 {name=p1 sig_type=std_logic lab=VGN}
C {lab_pin.sym} 530 -140 0 0 {name=p2 sig_type=std_logic lab=VGP}
C {title.sym} 0 30 0 0 {name=l7 author="Nithin Purushothama"}
C {code_shown.sym} -340 -90 0 0 {
name=TT_MODELS
only_toplevel=true
value="
** IHP models
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
"
spice_ignore=false
      }
C {vdd.sym} 980 -380 0 0 {name=l8 lab=VDD}
C {gnd.sym} 980 -30 0 0 {name=l9 lab=GND}
C {vsource.sym} 830 -260 0 0 {name=V2 value="dc 0 ac 1" savecurrent=false}
C {lab_pin.sym} 830 -230 0 0 {name=p3 sig_type=std_logic lab=VGP}
C {vsource.sym} 840 -80 0 0 {name=V3 value="dc 0 ac 1" savecurrent=false}
C {lab_pin.sym} 840 -50 0 0 {name=p4 sig_type=std_logic lab=VGN}
C {capa.sym} 1180 -140 0 0 {name=C1
m=1
value=50p
footprint=1206
device="ceramic capacitor"}
C {gnd.sym} 1180 -30 0 0 {name=l10 lab=GND}
C {lab_pin.sym} 1180 -200 0 1 {name=p5 sig_type=std_logic lab=Vout}
C {/foss/designs/fd_pr/sg13_hv_nmos.sym} 290 -140 0 0 {name=M1
l=1u
w=2.3u
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {/foss/designs/fd_pr/sg13_hv_pmos.sym} 620 -210 0 0 {name=M2
l=0.5u
w=4.5u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {/foss/designs/fd_pr/sg13_hv_pmos.sym} 960 -290 0 0 {name=M4
l=0.5u
w=4.5u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {/foss/designs/fd_pr/sg13_hv_nmos.sym} 960 -110 0 0 {name=M3
l=1u
w=2.3u
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {code.sym} -40 -110 0 0 {name=SAVE_COMMANDS only_toplevel=false
value="
.save @n.xm1.nsg13_hv_nmos[gds]
.save @n.xm1.nsg13_hv_nmos[gm]
.save @n.xm1.nsg13_hv_nmos[gmb]
.save @n.xm1.nsg13_hv_nmos[ids]
.save @n.xm1.nsg13_hv_nmos[l]
.save @n.xm1.nsg13_hv_nmos[vth]
.save @n.xm1.nsg13_hv_nmos[vgs]
.save @n.xm1.nsg13_hv_nmos[vds]
.save @n.xm1.nsg13_hv_nmos[cgg]
.save @n.xm1.nsg13_hv_nmos[vsat]
.save @n.xm2.nsg13_hv_pmos[cgd]
.save @n.xm2.nsg13_hv_pmos[cgg]
.save @n.xm2.nsg13_hv_pmos[cgs]
.save @n.xm2.nsg13_hv_pmos[gds]
.save @n.xm2.nsg13_hv_pmos[gm]
.save @n.xm2.nsg13_hv_pmos[gmb]
.save @n.xm2.nsg13_hv_pmos[ids]
.save @n.xm2.nsg13_hv_pmos[l]
.save @n.xm2.nsg13_hv_pmos[vsat]
.save @n.xm2.nsg13_hv_pmos[vth]
.save @n.xm2.nsg13_hv_pmos[vgs]
.save @n.xm2.nsg13_hv_pmos[vds]
.save @n.xm4.nsg13_hv_pmos[cgd]
.save @n.xm4.nsg13_hv_pmos[vsat]
.save @n.xm4.nsg13_hv_pmos[cgg]
.save @n.xm4.nsg13_hv_pmos[cgs]
.save @n.xm4.nsg13_hv_pmos[gds]
.save @n.xm4.nsg13_hv_pmos[gm]
.save @n.xm4.nsg13_hv_pmos[gmb]
.save @n.xm4.nsg13_hv_pmos[ids]
.save @n.xm4.nsg13_hv_pmos[l]
.save @n.xm4.nsg13_hv_pmos[vth]
.save @n.xm4.nsg13_hv_pmos[vgs]
.save @n.xm4.nsg13_hv_pmos[vds]
.save @n.xm3.nsg13_hv_nmos[gds]
.save @n.xm3.nsg13_hv_nmos[gm]
.save @n.xm3.nsg13_hv_nmos[gmb]
.save @n.xm3.nsg13_hv_nmos[ids]
.save @n.xm3.nsg13_hv_nmos[l]
.save @n.xm3.nsg13_hv_nmos[vth]
.save @n.xm3.nsg13_hv_nmos[vgs]
.save @n.xm3.nsg13_hv_nmos[vds]
.save @n.xm3.nsg13_hv_nmos[cgg]
.save @n.xm3.nsg13_hv_nmos[vsat]
"}
