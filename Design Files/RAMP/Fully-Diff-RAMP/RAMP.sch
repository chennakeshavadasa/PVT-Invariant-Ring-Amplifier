v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
B 4 280 -125 1180 -120 {}
B 4 280 -120 1180 -115 {}
B 4 280 -485 1180 -480 {}
B 4 580 -485 1480 -480 {}
B 4 280 -480 1180 -475 {}
B 4 580 -480 1480 -475 {}
B 4 580 -125 1480 -120 {}
B 4 580 -120 1480 -115 {}
B 4 740 -485 1640 -480 {}
B 4 740 -480 1640 -475 {}
B 4 730 -125 1630 -120 {}
B 4 730 -120 1630 -115 {}
B 4 60 -480 960 -475 {}
B 4 60 -485 960 -480 {}
B 4 60 -120 960 -115 {}
B 4 60 -125 960 -120 {}
T {SINGLE ENDED RING AMPLIFIER } 510 -550 0 0 0.75 0.75 {}
N 1380 -410 1440 -410 {lab=mp_dz}
N 1480 -480 1480 -410 {lab=VDD}
N 1380 -200 1440 -200 {lab=mn_dz}
N 1480 -300 1480 -230 {lab=Vout}
N 1480 -200 1480 -120 {lab=GND}
N 350 -325 460 -325 {lab=plus}
N 350 -400 350 -325 {lab=plus}
N 350 -285 350 -205 {lab=minus}
N 1480 -300 1620 -300 {lab=Vout}
N 1480 -380 1480 -300 {lab=Vout}
N 1290 -330 1380 -330 {lab=mp_dz}
N 1380 -410 1380 -330 {lab=mp_dz}
N 640 -280 755 -280 {lab=V1_CM}
N 955 -225 1050 -225 {lab=#net1}
N 955 -350 1050 -350 {lab=#net2}
N 1170 -120 1480 -120 {lab=GND}
N 1290 -270 1380 -270 {lab=mn_dz}
N 1380 -270 1380 -200 {lab=mn_dz}
N 1170 -480 1480 -480 {lab=VDD}
N 855 -180 855 -120 {lab=GND}
N 1170 -160 1170 -120 {lab=GND}
N 855 -120 1170 -120 {lab=GND}
N 855 -480 855 -395 {lab=VDD}
N 1170 -480 1170 -415 {lab=VDD}
N 855 -480 1170 -480 {lab=VDD}
N 320 -305 460 -305 {lab=V1_CM}
N 200 -480 200 -365 {lab=VDD}
N 60 -480 200 -480 {lab=VDD}
N 200 -245 200 -120 {lab=GND}
N 60 -120 200 -120 {lab=GND}
N 80 -400 350 -400 {lab=plus}
N 350 -285 460 -285 {lab=minus}
N 80 -205 350 -205 {lab=minus}
N 320 -305 320 -240 {lab=V1_CM}
N 280 -305 320 -305 {lab=V1_CM}
N 320 -240 640 -240 {lab=V1_CM}
N 640 -280 640 -240 {lab=V1_CM}
N 530 -480 530 -360 {lab=VDD}
N 530 -480 855 -480 {lab=VDD}
N 530 -120 855 -120 {lab=GND}
N 620 -305 1050 -305 {lab=Vo_STG1}
N 200 -120 530 -120 {lab=GND}
N 530 -250 530 -120 {lab=GND}
N 200 -480 530 -480 {lab=VDD}
C {/foss/designs/RAMP/Fully-Diff-RAMP/STG2.sym} 830 -290 0 0 {name=x2}
C {sg13g2_pr/sg13_hv_nmos.sym} 1460 -200 0 0 {name=M1
l=1u
w=2.3u
ng=1
m=4
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_pmos.sym} 1460 -410 0 0 {name=M2
l=0.5u
w=4.5u
ng=1
m=4
model=sg13_hv_pmos
spiceprefix=X
}
C {iopin.sym} 60 -120 0 1 {name=p1 lab=GND}
C {iopin.sym} 80 -400 0 1 {name=p3 lab=plus}
C {iopin.sym} 80 -205 0 1 {name=p4 lab=minus}
C {iopin.sym} 1620 -300 0 0 {name=p5 lab=Vout}
C {title.sym} 385 -35 0 0 {name=l1 author="Nithin Purushothama"}
C {lab_pin.sym} 700 -305 1 0 {name=p6 sig_type=std_logic lab=Vo_STG1}
C {lab_pin.sym} 1380 -200 0 0 {name=p7 sig_type=std_logic lab=mn_dz}
C {lab_pin.sym} 1380 -410 0 0 {name=p8 sig_type=std_logic lab=mp_dz}
C {/foss/designs/RAMP/Fully-Diff-RAMP/STG2_Replica.sym} 255 -285 0 0 {name=x3}
C {iopin.sym} 60 -480 0 1 {name=p2 lab=VDD}
C {lab_pin.sym} 640 -240 3 0 {name=p9 sig_type=std_logic lab=V1_CM}
C {/foss/designs/RAMP/Fully-Diff-RAMP/STG1-CM.sym} -80 -305 0 0 {name=x4}
C {/foss/designs/RAMP/Fully-Diff-RAMP/STG1.sym} 240 -305 0 0 {name=x1}
