v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
B 4 50 -125 950 -120 {}
B 4 50 -120 950 -115 {}
B 4 50 -485 950 -480 {}
B 4 350 -485 1250 -480 {}
B 4 50 -480 950 -475 {}
B 4 350 -480 1250 -475 {}
B 4 350 -125 1250 -120 {}
B 4 350 -120 1250 -115 {}
B 4 510 -485 1410 -480 {}
B 4 510 -480 1410 -475 {}
B 4 500 -125 1400 -120 {}
B 4 500 -120 1400 -115 {}
B 4 -170 -480 730 -475 {}
B 4 -170 -485 730 -480 {}
B 4 -170 -120 730 -115 {}
B 4 -170 -125 730 -120 {}
T {SINGLE ENDED RING AMPLIFIER } 280 -550 0 0 0.75 0.75 {}
N 1150 -410 1210 -410 {lab=mp_dz}
N 1250 -480 1250 -410 {lab=VDD}
N 1150 -200 1210 -200 {lab=mn_dz}
N 1250 -300 1250 -230 {lab=Vout}
N 1250 -200 1250 -120 {lab=GND}
N 120 -325 230 -325 {lab=plus}
N 120 -400 120 -325 {lab=plus}
N 120 -285 120 -205 {lab=minus}
N 1250 -300 1390 -300 {lab=Vout}
N 1250 -380 1250 -300 {lab=Vout}
N 1060 -330 1150 -330 {lab=mp_dz}
N 1150 -410 1150 -330 {lab=mp_dz}
N 410 -280 525 -280 {lab=V1_CM}
N 725 -225 820 -225 {lab=#net1}
N 725 -350 820 -350 {lab=#net2}
N 940 -120 1250 -120 {lab=GND}
N 1060 -270 1150 -270 {lab=mn_dz}
N 1150 -270 1150 -200 {lab=mn_dz}
N 940 -480 1250 -480 {lab=VDD}
N 625 -180 625 -120 {lab=GND}
N 940 -160 940 -120 {lab=GND}
N 625 -120 940 -120 {lab=GND}
N 625 -480 625 -395 {lab=VDD}
N 940 -480 940 -415 {lab=VDD}
N 625 -480 940 -480 {lab=VDD}
N 90 -305 230 -305 {lab=V1_CM}
N -30 -480 -30 -365 {lab=VDD}
N -170 -480 -30 -480 {lab=VDD}
N -30 -245 -30 -120 {lab=GND}
N -170 -120 -30 -120 {lab=GND}
N -150 -205 120 -205 {lab=minus}
N 120 -285 230 -285 {lab=minus}
N -150 -400 120 -400 {lab=plus}
N 310 -480 625 -480 {lab=VDD}
N 310 -120 625 -120 {lab=GND}
N 90 -305 90 -240 {lab=V1_CM}
N 50 -305 90 -305 {lab=V1_CM}
N 90 -240 410 -240 {lab=V1_CM}
N 410 -280 410 -240 {lab=V1_CM}
N 310 -235 310 -120 {lab=GND}
N -30 -120 310 -120 {lab=GND}
N 310 -480 310 -375 {lab=VDD}
N -30 -480 310 -480 {lab=VDD}
N 430 -305 820 -305 {lab=Vo_STG1}
C {/foss/designs/RAMP/Fully-Diff-RAMP/STG2.sym} 600 -290 0 0 {name=x2}
C {sg13g2_pr/sg13_hv_nmos.sym} 1230 -200 0 0 {name=M1
l=1u
w=2.3u
ng=1
m=4
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_pmos.sym} 1230 -410 0 0 {name=M2
l=0.5u
w=4.5u
ng=1
m=4
model=sg13_hv_pmos
spiceprefix=X
}
C {iopin.sym} -170 -120 0 1 {name=p1 lab=GND}
C {iopin.sym} -150 -400 0 1 {name=p3 lab=plus}
C {iopin.sym} -150 -205 0 1 {name=p4 lab=minus}
C {iopin.sym} 1390 -300 0 0 {name=p5 lab=Vout}
C {title.sym} 155 -35 0 0 {name=l1 author="Nithin Purushothama"}
C {lab_pin.sym} 470 -305 1 0 {name=p6 sig_type=std_logic lab=Vo_STG1}
C {lab_pin.sym} 1150 -200 0 0 {name=p7 sig_type=std_logic lab=mn_dz}
C {lab_pin.sym} 1150 -410 0 0 {name=p8 sig_type=std_logic lab=mp_dz}
C {/foss/designs/RAMP/Fully-Diff-RAMP/STG2_Replica.sym} 25 -285 0 0 {name=x3}
C {iopin.sym} -170 -480 0 1 {name=p2 lab=VDD}
C {lab_pin.sym} 410 -240 3 0 {name=p9 sig_type=std_logic lab=V1_CM}
C {/foss/designs/RAMP/Fully-Diff-RAMP/STG1-CM.sym} -310 -305 0 0 {name=x4}
C {/foss/designs/RAMP/Fully-Diff-RAMP/STG1_2.sym} 10 -305 0 0 {name=x5}
C {sg13g2_pr/annotate_fet_params.sym} 1360 -450 0 0 {name=annot1 ref=M1}
C {sg13g2_pr/annotate_fet_params.sym} 1350 -260 0 0 {name=annot2 ref=M2}
