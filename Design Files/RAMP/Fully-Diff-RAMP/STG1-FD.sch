v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
B 4 155 -740 855 -735 {}
B 4 155 -745 855 -740 {}
B 4 855 -745 1025 -735 {}
B 4 135 -145 1025 -135 {}
B 4 135 -745 155 -735 {}
P 4 1 855 -745 {}
T {RING AMPLIFIER FULLY DIFFERENTIAL STAGE-1} 90 -820 0 0 0.75 0.75 {}
N 215 -520 345 -520 {lab=Von_1}
N 475 -650 565 -650 {lab=#net1}
N 345 -740 345 -650 {lab=VDD}
N 345 -740 605 -740 {lab=VDD}
N 605 -740 605 -650 {lab=VDD}
N 345 -620 345 -520 {lab=Von_1}
N 605 -620 605 -520 {lab=Vop_1}
N 585 -520 605 -520 {lab=Vop_1}
N 345 -520 365 -520 {lab=Von_1}
N 475 -520 525 -520 {lab=#net2}
N 605 -520 605 -380 {lab=Vop_1}
N 345 -520 345 -380 {lab=Von_1}
N 345 -320 345 -280 {lab=#net3}
N 475 -280 605 -280 {lab=#net3}
N 605 -320 605 -280 {lab=#net3}
N 475 -280 475 -230 {lab=#net3}
N 345 -280 475 -280 {lab=#net3}
N 475 -170 475 -140 {lab=GND}
N 535 -350 605 -350 {lab=GND}
N 535 -350 535 -140 {lab=GND}
N 345 -350 535 -350 {lab=GND}
N 475 -140 535 -140 {lab=GND}
N 645 -350 715 -350 {lab=Vin}
N 425 -520 475 -520 {lab=#net2}
N 475 -600 970 -600 {lab=#net1}
N 475 -650 475 -600 {lab=#net1}
N 385 -650 475 -650 {lab=#net1}
N 475 -520 475 -430 {lab=#net2}
N 225 -350 305 -350 {lab=Vip}
N 135 -140 475 -140 {lab=GND}
N 605 -520 735 -520 {lab=Vop_1}
N 135 -740 345 -740 {lab=VDD}
N 970 -600 970 -555 {lab=#net1}
N 970 -495 970 -140 {lab=GND}
N 535 -140 970 -140 {lab=GND}
N 930 -505 930 -360 {lab=V1_CM}
N 840 -545 930 -545 {lab=#net2}
N 840 -545 840 -430 {lab=#net2}
N 475 -430 840 -430 {lab=#net2}
N 870 -360 930 -360 {lab=V1_CM}
N 605 -740 970 -740 {lab=VDD}
C {opin.sym} 215 -520 0 1 {name=p6 lab=Von_1}
C {title.sym} 160 -40 0 0 {name=l2 author="Nithin Purushothama"}
C {res.sym} 395 -520 1 0 {name=R1
value=100k
footprint=1206
device=resistor
m=1}
C {res.sym} 555 -520 3 1 {name=R3
value=100k
footprint=1206
device=resistor
m=1}
C {sg13g2_pr/sg13_lv_nmos.sym} 325 -350 0 0 {name=MN_STG1_IP_N1
l=0.5u
w=1.563u
ng=1
m=2
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 625 -350 0 1 {name=MN_STG1_IP_N2
l=0.5u
w=1.563u
ng=1
m=2
model=sg13_lv_nmos
spiceprefix=X
}
C {isource.sym} 475 -200 0 0 {name=I0 value=10u}
C {ngspice_probe.sym} 475 -350 0 0 {name=r2}
C {ngspice_probe.sym} 475 -520 0 0 {name=r4}
C {ngspice_probe.sym} 475 -650 0 0 {name=r5}
C {ngspice_probe.sym} 605 -470 0 0 {name=r8}
C {ngspice_probe.sym} 345 -470 0 1 {name=r9}
C {iopin.sym} 135 -740 0 1 {name=p1 lab=VDD}
C {iopin.sym} 135 -140 0 1 {name=p2 lab=GND}
C {opin.sym} 735 -520 0 0 {name=p3 lab=Vop_1}
C {ipin.sym} 225 -350 0 0 {name=p4 lab=Vip}
C {ipin.sym} 715 -350 0 1 {name=p5 lab=Vin}
C {/foss/designs/fd_pr/sg13_hv_pmos.sym} 365 -650 0 1 {name=MP_STG1_CL_P1
l=1u
w=0.5u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {/foss/designs/fd_pr/sg13_hv_pmos.sym} 585 -650 0 0 {name=MP_STG1_CL_P2
l=1u
w=0.5u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {vcvs.sym} 970 -525 0 0 {name=E1 value=10k}
C {ipin.sym} 870 -360 0 0 {name=p7 lab=V1_CM}
