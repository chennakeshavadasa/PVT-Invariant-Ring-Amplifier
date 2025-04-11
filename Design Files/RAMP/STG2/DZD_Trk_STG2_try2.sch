v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 430 -280 430 -230 {lab=#net1}
N 430 -200 430 -100 {lab=GND}
N 330 -200 390 -200 {lab=#net2}
N 330 -280 330 -200 {lab=#net2}
N 330 -370 390 -370 {lab=#net2}
N 430 -510 430 -400 {lab=#net3}
N 430 -370 470 -370 {lab=VDD}
N 470 -540 470 -370 {lab=VDD}
N 430 -600 430 -540 {lab=VDD}
N 430 -540 470 -540 {lab=VDD}
N 270 -280 330 -280 {lab=#net2}
N 330 -370 330 -280 {lab=#net2}
N 270 -220 270 -190 {lab=GND}
N 875 -540 875 -510 {lab=GND}
N 430 -340 430 -280 {lab=#net1}
N 1130 -330 1130 -230 {lab=#net4}
N 1030 -330 1090 -330 {lab=#net5}
N 1030 -410 1030 -330 {lab=#net5}
N 1030 -500 1090 -500 {lab=#net5}
N 970 -410 1030 -410 {lab=#net5}
N 1030 -500 1030 -410 {lab=#net5}
N 970 -350 970 -320 {lab=GND}
N 1130 -410 1130 -360 {lab=#net6}
N 1130 -600 1130 -500 {lab=VDD}
N 1130 -200 1130 -100 {lab=GND}
N 1030 -200 1090 -200 {lab=Y}
N 840 -220 870 -220 {lab=GND}
N 870 -220 870 -170 {lab=GND}
N 840 -170 870 -170 {lab=GND}
N 840 -190 840 -170 {lab=GND}
N 730 -220 800 -220 {lab=#net7}
N 730 -280 730 -220 {lab=#net7}
N 730 -280 840 -280 {lab=#net7}
N 840 -280 840 -250 {lab=#net7}
N 840 -350 840 -280 {lab=#net7}
N 840 -170 840 -100 {lab=GND}
N 840 -440 840 -410 {lab=VDD}
N 550 -400 580 -400 {lab=VDD}
N 730 -400 770 -400 {lab=GND}
N 650 -560 650 -510 {lab=X}
N 300 -540 390 -540 {lab=X}
N 430 -280 620 -280 {lab=#net1}
N 680 -280 730 -280 {lab=#net7}
N 1480 -300 1520 -300 {lab=#net8}
N 1450 -300 1450 -230 {lab=#net8}
N 1450 -230 1560 -230 {lab=#net8}
N 1560 -270 1560 -230 {lab=#net8}
N 1560 -430 1560 -300 {lab=VDD}
N 1560 -230 1560 -190 {lab=#net8}
N 1560 -130 1560 -110 {lab=GND}
N 1230 -380 1260 -380 {lab=GND}
N 1400 -380 1420 -380 {lab=VDD}
N 1350 -490 1350 -460 {lab=#net8}
N 1350 -490 1480 -490 {lab=#net8}
N 1480 -490 1480 -300 {lab=#net8}
N 1450 -300 1480 -300 {lab=#net8}
N 1330 -250 1330 -200 {lab=Y}
N 1200 -490 1310 -490 {lab=#net6}
N 1130 -410 1200 -410 {lab=#net6}
N 1130 -470 1130 -410 {lab=#net6}
N 680 -330 680 -280 {lab=#net7}
N 620 -330 620 -280 {lab=#net1}
N 1310 -490 1310 -460 {lab=#net6}
N 1200 -490 1200 -410 {lab=#net6}
C {sg13g2_pr/sg13_lv_nmos.sym} 410 -200 0 0 {name=MN_STG2_3N1
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 410 -370 0 0 {name=MN_STG2_3P1
l=0.13u
w=0.15u
ng=1
m=3
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 410 -540 0 0 {name=MP_DZ_STG2_3N
l=0.13u
w=0.15u
ng=1
m=5
model=sg13_lv_pmos
spiceprefix=X
}
C {vsource.sym} 270 -250 0 0 {name=V1 value=0.825 savecurrent=false}
C {gnd.sym} 270 -190 0 0 {name=l1 lab=GND}
C {vdd.sym} 430 -600 0 0 {name=l2 lab=VDD}
C {vsource.sym} 875 -570 0 0 {name=V2 value=1.65 savecurrent=false}
C {gnd.sym} 875 -510 0 0 {name=l3 lab=GND}
C {vdd.sym} 875 -600 0 0 {name=l4 lab=VDD}
C {gnd.sym} 430 -100 0 0 {name=l5 lab=GND}
C {sg13g2_pr/sg13_lv_nmos.sym} 1110 -330 0 0 {name=MP_STG2_3P2
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 1110 -500 0 0 {name=MP_STG2_3P1
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {vsource.sym} 970 -380 0 0 {name=V3 value=0.825 savecurrent=false}
C {gnd.sym} 970 -320 0 0 {name=l6 lab=GND}
C {vdd.sym} 1130 -600 0 0 {name=l7 lab=VDD}
C {sg13g2_pr/sg13_lv_nmos.sym} 1110 -200 0 0 {name=MN_DZ_STG2_3P
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {gnd.sym} 1130 -100 0 0 {name=l9 lab=GND}
C {sg13g2_pr/sg13_hv_nmos.sym} 820 -220 0 0 {name=MN_STG2_3N_R
l=1u
w=2.3u
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {isource.sym} 840 -380 0 0 {name=I0 value=1u}
C {vdd.sym} 840 -440 0 0 {name=l8 lab=VDD}
C {gnd.sym} 840 -100 0 0 {name=l10 lab=GND}
C {ngspice_probe.sym} 730 -280 0 0 {name=r1}
C {/foss/designs/RAMP/OTA/POTA.sym} 800 150 3 0 {name=x1}
C {vdd.sym} 550 -400 3 0 {name=l11 lab=VDD}
C {gnd.sym} 770 -400 0 0 {name=l12 lab=GND}
C {lab_pin.sym} 650 -560 1 0 {name=p1 sig_type=std_logic lab=X}
C {lab_pin.sym} 300 -540 0 0 {name=p2 sig_type=std_logic lab=X}
C {ngspice_probe.sym} 430 -280 0 0 {name=r2}
C {sg13g2_pr/sg13_hv_pmos.sym} 1540 -300 0 0 {name=MP_STG2_3P_R
l=0.5u
w=4.5u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {isource.sym} 1560 -160 0 0 {name=I1 value=1u}
C {vdd.sym} 1560 -430 0 0 {name=l13 lab=VDD}
C {gnd.sym} 1560 -110 0 0 {name=l14 lab=GND}
C {ngspice_probe.sym} 1450 -260 0 0 {name=r3}
C {/foss/designs/RAMP/OTA/NOTA.sym} 1330 -660 3 1 {name=x2}
C {vdd.sym} 1420 -380 1 0 {name=l15 lab=VDD}
C {gnd.sym} 1230 -380 0 0 {name=l16 lab=GND}
C {lab_pin.sym} 1330 -210 3 0 {name=p3 sig_type=std_logic lab=Y}
C {lab_pin.sym} 1030 -200 0 0 {name=p4 sig_type=std_logic lab=Y}
C {ngspice_probe.sym} 1130 -410 0 0 {name=r4}
C {title.sym} 160 -30 0 0 {name=l17 author="Nithin Purushothama"}
C {devices/code_shown.sym} 0 -600 0 0 {name="NGSPICE" only_toplevel=true 
value="
.option wnflag=1
.option savecurrents
.temp 27
.control
save all
write DZD_Trk_STG2_try2.raw
set appendwrite 
op
write DZD_Trk_STG2_try2.raw
**dc temp -50 150 1
tran 1m 10m 1m
**ac dec 20 1 1e8
**plot vdb(vout2) vdb(vout1)
.endc
"}
C {code_shown.sym} 20 -160 0 0 {
name=TT_MODELS
only_toplevel=true
value="
** IHP models
.lib cornerMOSlv.lib mos_fs
.lib cornerMOShv.lib mos_fs
"
spice_ignore=false
      }
C {devices/launcher.sym} 540 -130 0 0 {name=h1
descr="load op & annotate" 
tclcommand="xschem raw_read $netlist_dir/Deadzone_try_1.raw; set show_hidden_texts 1; xschem annotate_op"}
