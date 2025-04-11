v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 750 -550 840 -550 {lab=#net1}
N 440 -640 440 -550 {lab=VDD}
N 880 -640 880 -550 {lab=VDD}
N 440 -520 440 -420 {lab=#net2}
N 880 -520 880 -420 {lab=Vout}
N 860 -420 880 -420 {lab=Vout}
N 440 -420 460 -420 {lab=#net2}
N 750 -420 800 -420 {lab=#net3}
N 880 -420 880 -280 {lab=Vout}
N 440 -420 440 -280 {lab=#net2}
N 440 -220 440 -180 {lab=#net4}
N 750 -180 880 -180 {lab=#net4}
N 880 -220 880 -180 {lab=#net4}
N 750 -180 750 -130 {lab=#net4}
N 750 -70 750 -40 {lab=GND}
N 810 -250 880 -250 {lab=GND}
N 810 -250 810 -40 {lab=GND}
N 750 -40 810 -40 {lab=GND}
N 920 -250 990 -250 {lab=#net5}
N 330 -250 400 -250 {lab=#net6}
N 750 -500 1220 -500 {lab=#net1}
N 750 -550 750 -500 {lab=#net1}
N 330 -130 330 -100 {lab=GND}
N 330 -250 330 -190 {lab=#net6}
N 990 -250 990 -190 {lab=#net5}
N 990 -130 990 -100 {lab=GND}
N 290 -340 290 -310 {lab=GND}
N 290 -460 290 -400 {lab=VDD}
N 750 -420 750 -330 {lab=#net3}
N 880 -420 920 -420 {lab=Vout}
N 460 -250 460 -40 {lab=GND}
N 440 -250 460 -250 {lab=GND}
N 520 -420 750 -420 {lab=#net3}
N 480 -550 750 -550 {lab=#net1}
N 440 -640 880 -640 {lab=VDD}
N 460 -40 750 -40 {lab=GND}
N 440 -180 750 -180 {lab=#net4}
N 750 -40 750 0 {lab=GND}
N 1220 -500 1220 -450 {lab=#net1}
N 1220 -390 1220 -370 {lab=GND}
N 1080 -440 1080 -330 {lab=#net3}
N 750 -330 1080 -330 {lab=#net3}
N 1080 -440 1180 -440 {lab=#net3}
N 1120 -400 1180 -400 {lab=#net7}
N 1400 -170 1400 -70 {lab=GND}
N 1400 -480 1400 -370 {lab=#net8}
N 1400 -340 1440 -340 {lab=VDD}
N 1440 -510 1440 -340 {lab=VDD}
N 1400 -570 1400 -510 {lab=VDD}
N 1400 -510 1440 -510 {lab=VDD}
N 1400 -250 1400 -200 {lab=#net7}
N 1310 -170 1360 -170 {lab=#net7}
N 1310 -250 1310 -170 {lab=#net7}
N 1310 -340 1360 -340 {lab=#net7}
N 1300 -510 1360 -510 {lab=GND}
N 1310 -250 1400 -250 {lab=#net7}
N 1310 -340 1310 -250 {lab=#net7}
N 1400 -300 1400 -250 {lab=#net7}
N 1650 -300 1650 -200 {lab=#net9}
N 1550 -300 1610 -300 {lab=#net7}
N 1550 -470 1610 -470 {lab=#net7}
N 1550 -380 1550 -300 {lab=#net7}
N 1650 -570 1650 -470 {lab=VDD}
N 1650 -170 1650 -70 {lab=GND}
N 1550 -170 1610 -170 {lab=VDD}
N 1650 -380 1650 -330 {lab=#net7}
N 1550 -380 1650 -380 {lab=#net7}
N 1550 -470 1550 -380 {lab=#net7}
N 1650 -440 1650 -380 {lab=#net7}
N 1400 -300 1550 -300 {lab=#net7}
N 1400 -310 1400 -300 {lab=#net7}
N 1120 -250 1310 -250 {lab=#net7}
N 1120 -400 1120 -250 {lab=#net7}
C {res.sym} 490 -420 1 0 {name=R1
value=100k
footprint=1206
device=resistor
m=1}
C {res.sym} 830 -420 3 1 {name=R3
value=100k
footprint=1206
device=resistor
m=1}
C {isource.sym} 750 -100 0 0 {name=I0 value=10u}
C {gnd.sym} 750 0 0 0 {name=l1 lab=GND}
C {vsource.sym} 990 -160 0 0 {name=V2 value="dc 0.825 ac 1 180" savecurrent=false}
C {vsource.sym} 330 -160 0 0 {name=V3 value="dc 0.825 ac 1" savecurrent=false}
C {gnd.sym} 330 -100 0 0 {name=l3 lab=GND}
C {gnd.sym} 990 -100 0 0 {name=l4 lab=GND}
C {devices/code_shown.sym} 0 -600 0 0 {name="NGSPICE" only_toplevel=true 
value="
.option wnflag=1
.option savecurrents
.temp 27
.control
save all
write STG1-fully-Diff.raw
set appendwrite 
op
write STG1-fully-Diff.raw
**dc temp -50 150 1
**tran 1m 10m 1m
ac dec 20 1 1e15
plot vdb(vout)
.endc
"}
C {code_shown.sym} 20 -160 0 0 {
name=TT_MODELS
only_toplevel=true
value="
** IHP models
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
"
spice_ignore=false
      }
C {title.sym} 190 40 0 0 {name=l17 author="Nithin Purushothama"}
C {devices/launcher.sym} 90 -270 0 0 {name=h1
descr="load op & annotate" 
tclcommand="xschem raw_read $netlist_dir/STG1-fully-Diff.raw; set show_hidden_texts 1; xschem annotate_op"}
C {vsource.sym} 290 -370 0 0 {name=V4 value=1.65 savecurrent=false}
C {gnd.sym} 290 -310 0 0 {name=l5 lab=GND}
C {vdd.sym} 290 -460 0 0 {name=l6 lab=VDD}
C {vdd.sym} 750 -640 0 0 {name=l7 lab=VDD}
C {ngspice_probe.sym} 750 -420 0 0 {name=r4}
C {ngspice_probe.sym} 750 -550 0 0 {name=r5}
C {ngspice_probe.sym} 330 -250 0 0 {name=r6}
C {ngspice_probe.sym} 990 -250 0 0 {name=r7}
C {ngspice_probe.sym} 880 -370 0 0 {name=r8}
C {ngspice_probe.sym} 440 -370 0 1 {name=r9}
C {lab_pin.sym} 920 -420 0 1 {name=p1 sig_type=std_logic lab=Vout}
C {/foss/designs/fd_pr/sg13_lv_nmos.sym} 340 -170 0 0 {name=IP_STG1_MN1
l=0.5u
w=1.563u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {/foss/designs/fd_pr/sg13_lv_nmos.sym} 980 -170 0 1 {name=IP_STG1_MN2
l=0.5u
w=1.563u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {ngspice_probe.sym} 650 -180 0 0 {name=r2}
C {/foss/designs/fd_pr/sg13_hv_pmos.sym} 460 -550 0 1 {name=MP_STG1_CL_P1
l=1u
w=0.5u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {/foss/designs/fd_pr/sg13_hv_pmos.sym} 860 -550 0 0 {name=MP_STG1_CL_P2
l=1u
w=0.5u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {vcvs.sym} 1220 -420 0 0 {name=E1 value=10k}
C {gnd.sym} 1220 -370 0 0 {name=l10 lab=GND}
C {sg13g2_pr/sg13_lv_nmos.sym} 1380 -170 0 0 {name=M1
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 1380 -340 0 0 {name=M2
l=0.13u
w=0.15u
ng=1
m=3
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 1380 -510 0 0 {name=M3
l=0.13u
w=0.15u
ng=1
m=5
model=sg13_lv_pmos
spiceprefix=X
}
C {vdd.sym} 1400 -570 0 0 {name=l2 lab=VDD}
C {gnd.sym} 1400 -70 0 0 {name=l8 lab=GND}
C {ngspice_probe.sym} 1400 -250 0 0 {name=r10}
C {gnd.sym} 1300 -510 0 0 {name=l9 lab=GND}
C {sg13g2_pr/sg13_lv_nmos.sym} 1630 -300 0 0 {name=M4
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 1630 -470 0 0 {name=M5
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {vdd.sym} 1650 -570 0 0 {name=l13 lab=VDD}
C {sg13g2_pr/sg13_lv_nmos.sym} 1630 -170 0 0 {name=M6
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {gnd.sym} 1650 -70 0 0 {name=l14 lab=GND}
C {ngspice_probe.sym} 1650 -380 0 0 {name=r11}
C {vdd.sym} 1550 -170 0 0 {name=l12 lab=VDD}
C {code.sym} 1130 -140 0 0 {name=SAVE_COMMANDS only_toplevel=false
value="
.save @n.xip_stg1_mn1.nsg13_lv_nmos[gds]
.save @n.xip_stg1_mn1.nsg13_lv_nmos[gm]
.save @n.xip_stg1_mn1.nsg13_lv_nmos[gmb]
.save @n.xip_stg1_mn1.nsg13_lv_nmos[ids]
.save @n.xip_stg1_mn1.nsg13_lv_nmos[l]
.save @n.xip_stg1_mn1.nsg13_lv_nmos[vgs]
.save @n.xip_stg1_mn1.nsg13_lv_nmos[vth]
.save @n.xip_stg1_mn1.nsg13_lv_nmos[vds]
.save @n.xip_stg1_mn1.nsg13_lv_nmos[cgg]
.save @n.xip_stg1_mn1.nsg13_lv_nmos[vsat]
.save @n.xip_stg1_mn1.nsg13_lv_nmos[cgd]
.save @n.xip_stg1_mn1.nsg13_lv_nmos[cgs]
.save @n.xip_stg1_mn2.nsg13_lv_nmos[gds]
.save @n.xip_stg1_mn2.nsg13_lv_nmos[gm]
.save @n.xip_stg1_mn2.nsg13_lv_nmos[gmb]
.save @n.xip_stg1_mn2.nsg13_lv_nmos[ids]
.save @n.xip_stg1_mn2.nsg13_lv_nmos[l]
.save @n.xip_stg1_mn2.nsg13_lv_nmos[vth]
.save @n.xip_stg1_mn2.nsg13_lv_nmos[vsat]
.save @n.xip_stg1_mn2.nsg13_lv_nmos[vgs]
.save @n.xip_stg1_mn2.nsg13_lv_nmos[vds]
.save @n.xip_stg1_mn2.nsg13_lv_nmos[cgd]
.save @n.xip_stg1_mn2.nsg13_lv_nmos[cgs]
.save @n.xip_stg1_mn2.nsg13_lv_nmos[cgg]
.save @n.xip_stg1_mn2.nsg13_lv_nmos[gds]

.save @n.xmp_stg1_cl_p1.nsg13_hv_pmos[gds]
.save @n.xmp_stg1_cl_p1.nsg13_hv_pmos[gm]
.save @n.xmp_stg1_cl_p1.nsg13_hv_pmos[gmb]
.save @n.xmp_stg1_cl_p1.nsg13_hv_pmos[ids]
.save @n.xmp_stg1_cl_p1.nsg13_hv_pmos[l]
.save @n.xmp_stg1_cl_p1.nsg13_hv_pmos[vth]
.save @n.xmp_stg1_cl_p1.nsg13_hv_pmos[vsat]
.save @n.xmp_stg1_cl_p1.nsg13_hv_pmos[vgs]
.save @n.xmp_stg1_cl_p1.nsg13_hv_pmos[vds]
.save @n.xmp_stg1_cl_p1.nsg13_hv_pmos[cgd]
.save @n.xmp_stg1_cl_p1.nsg13_hv_pmos[cgs]
.save @n.xmp_stg1_cl_p1.nsg13_hv_pmos[cgg]
.save @n.xmp_stg1_cl_p1.nsg13_hv_pmos[gds]
.save @n.xmp_stg1_cl_p2.nsg13_hv_pmos[gds]
.save @n.xmp_stg1_cl_p2.nsg13_hv_pmos[gm]
.save @n.xmp_stg1_cl_p2.nsg13_hv_pmos[gmb]
.save @n.xmp_stg1_cl_p2.nsg13_hv_pmos[ids]
.save @n.xmp_stg1_cl_p2.nsg13_hv_pmos[l]
.save @n.xmp_stg1_cl_p2.nsg13_hv_pmos[vth]
.save @n.xmp_stg1_cl_p2.nsg13_hv_pmos[vsat]
.save @n.xmp_stg1_cl_p2.nsg13_hv_pmos[vgs]
.save @n.xmp_stg1_cl_p2.nsg13_hv_pmos[vds]
.save @n.xmp_stg1_cl_p2.nsg13_hv_pmos[cgd]
.save @n.xmp_stg1_cl_p2.nsg13_hv_pmos[cgs]
.save @n.xmp_stg1_cl_p2.nsg13_hv_pmos[cgg]
.save @n.xmp_stg1_cl_p2.nsg13_hv_pmos[gds]
"}
