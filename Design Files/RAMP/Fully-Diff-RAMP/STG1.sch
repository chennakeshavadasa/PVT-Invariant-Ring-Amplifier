v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
B 4 155 -730 855 -725 {}
B 4 155 -735 855 -730 {}
B 4 855 -735 1025 -725 {}
B 4 135 -135 1025 -125 {}
B 4 135 -735 155 -725 {}
P 4 1 855 -735 {}
T {RING AMPLIFIER STAGE-1} 550 -820 0 0 0.75 0.75 {}
N 475 -640 565 -640 {lab=#net1}
N 345 -730 345 -640 {lab=VDD}
N 345 -730 605 -730 {lab=VDD}
N 605 -730 605 -640 {lab=VDD}
N 345 -610 345 -510 {lab=#net2}
N 605 -610 605 -510 {lab=Vo1}
N 585 -510 605 -510 {lab=Vo1}
N 345 -510 365 -510 {lab=#net2}
N 475 -510 525 -510 {lab=#net3}
N 605 -510 605 -370 {lab=Vo1}
N 345 -510 345 -370 {lab=#net2}
N 345 -310 345 -270 {lab=#net4}
N 475 -270 605 -270 {lab=#net4}
N 605 -310 605 -270 {lab=#net4}
N 475 -270 475 -220 {lab=#net4}
N 345 -270 475 -270 {lab=#net4}
N 475 -160 475 -130 {lab=GND}
N 535 -340 605 -340 {lab=GND}
N 535 -340 535 -130 {lab=GND}
N 345 -340 535 -340 {lab=GND}
N 475 -130 535 -130 {lab=GND}
N 645 -340 715 -340 {lab=Vin}
N 425 -510 475 -510 {lab=#net3}
N 475 -590 970 -590 {lab=#net1}
N 475 -640 475 -590 {lab=#net1}
N 385 -640 475 -640 {lab=#net1}
N 475 -510 475 -420 {lab=#net3}
N 225 -340 305 -340 {lab=Vip}
N 135 -130 475 -130 {lab=GND}
N 605 -510 735 -510 {lab=Vo1}
N 135 -730 345 -730 {lab=VDD}
N 970 -590 970 -545 {lab=#net1}
N 970 -485 970 -130 {lab=GND}
N 535 -130 970 -130 {lab=GND}
N 930 -495 930 -350 {lab=V1_CM}
N 840 -535 930 -535 {lab=#net3}
N 840 -535 840 -420 {lab=#net3}
N 475 -420 840 -420 {lab=#net3}
N 870 -350 930 -350 {lab=V1_CM}
N 605 -730 970 -730 {lab=VDD}
C {res.sym} 395 -510 1 0 {name=R1
value=100k
footprint=1206
device=resistor
m=1}
C {res.sym} 555 -510 3 1 {name=R3
value=100k
footprint=1206
device=resistor
m=1}
C {sg13g2_pr/sg13_lv_nmos.sym} 325 -340 0 0 {name=MN_STG1_IP_N1
l=0.5u
w=1.563u
ng=1
m=2
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 625 -340 0 1 {name=MN_STG1_IP_N2
l=0.5u
w=1.563u
ng=1
m=2
model=sg13_lv_nmos
spiceprefix=X
}
C {isource.sym} 475 -190 0 0 {name=I0 value=10u}
C {ngspice_probe.sym} 475 -340 0 0 {name=r2}
C {ngspice_probe.sym} 475 -510 0 0 {name=r4}
C {ngspice_probe.sym} 475 -640 0 0 {name=r5}
C {ngspice_probe.sym} 715 -340 0 0 {name=r7}
C {ngspice_probe.sym} 605 -460 0 0 {name=r8}
C {ngspice_probe.sym} 345 -460 0 1 {name=r9}
C {iopin.sym} 135 -730 0 1 {name=p1 lab=VDD}
C {iopin.sym} 135 -130 0 1 {name=p2 lab=GND}
C {opin.sym} 735 -510 0 0 {name=p3 lab=Vo1}
C {ipin.sym} 225 -340 0 0 {name=p4 lab=Vip}
C {ipin.sym} 715 -340 0 1 {name=p5 lab=Vin}
C {title.sym} 160 -40 0 0 {name=l1 author="Nithin Purushothama"}
C {/foss/designs/fd_pr/sg13_hv_pmos.sym} 365 -640 0 1 {name=MP_STG1_CL_P1
l=1u
w=0.5u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {/foss/designs/fd_pr/sg13_hv_pmos.sym} 585 -640 0 0 {name=MP_STG1_CL_P2
l=1u
w=0.5u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {vcvs.sym} 970 -515 0 0 {name=E1 value=10k}
C {ipin.sym} 870 -350 0 0 {name=p6 lab=V1_CM}
