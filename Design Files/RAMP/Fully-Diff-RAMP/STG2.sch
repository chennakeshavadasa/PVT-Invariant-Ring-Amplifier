v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
B 4 120 -685 1105 -675 {}
B 4 120 -125 1105 -115 {}
T {RING AMPLIFIER STAGE-2} 335 -755 0 0 0.75 0.75 {}
N 440 -240 440 -120 {lab=GND}
N 340 -240 400 -240 {lab=Vin_2}
N 340 -320 340 -240 {lab=Vin_2}
N 340 -410 400 -410 {lab=Vin_2}
N 440 -550 440 -440 {lab=#net1}
N 440 -410 480 -410 {lab=VDD}
N 480 -580 480 -410 {lab=VDD}
N 440 -580 480 -580 {lab=VDD}
N 340 -410 340 -320 {lab=Vin_2}
N 440 -320 440 -270 {lab=VDZN}
N 440 -680 440 -580 {lab=VDD}
N 895 -370 895 -270 {lab=#net2}
N 795 -370 855 -370 {lab=Vin_2}
N 795 -450 795 -370 {lab=Vin_2}
N 795 -540 855 -540 {lab=Vin_2}
N 795 -540 795 -450 {lab=Vin_2}
N 895 -240 895 -120 {lab=GND}
N 895 -450 895 -400 {lab=VDZP}
N 895 -680 895 -540 {lab=VDD}
N 440 -680 895 -680 {lab=VDD}
N 440 -120 895 -120 {lab=GND}
N 260 -450 795 -450 {lab=Vin_2}
N 260 -450 260 -320 {lab=Vin_2}
N 260 -320 340 -320 {lab=Vin_2}
N 120 -320 260 -320 {lab=Vin_2}
N 120 -680 440 -680 {lab=VDD}
N 120 -120 440 -120 {lab=GND}
N 180 -580 400 -580 {lab=VCTRL_P}
N 660 -240 855 -240 {lab=VCTRL_N}
N 440 -320 585 -320 {lab=VDZN}
N 440 -380 440 -320 {lab=VDZN}
N 895 -450 1040 -450 {lab=VDZP}
N 895 -510 895 -450 {lab=VDZP}
C {sg13g2_pr/sg13_lv_nmos.sym} 420 -240 0 0 {name=MN_STG2_3N1
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 420 -410 0 0 {name=MN_STG2_3P1
l=0.13u
w=0.15u
ng=1
m=3
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 420 -580 0 0 {name=MP_DZ_STG2_3N
l=0.13u
w=0.15u
ng=1
m=5
model=sg13_lv_pmos
spiceprefix=X
}
C {ngspice_probe.sym} 440 -500 0 1 {name=r6}
C {sg13g2_pr/sg13_lv_nmos.sym} 875 -370 0 0 {name=MP_STG2_3P2
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 875 -540 0 0 {name=MP_STG2_3P1
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 875 -240 0 0 {name=MN_DZ_STG2_3P
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {ngspice_probe.sym} 895 -450 0 0 {name=r4}
C {ngspice_probe.sym} 895 -300 0 0 {name=r5}
C {ipin.sym} 120 -320 0 0 {name=p1 lab=Vin_2}
C {ipin.sym} 120 -680 0 0 {name=p3 lab=VDD}
C {ipin.sym} 120 -120 0 0 {name=p5 lab=GND}
C {ipin.sym} 180 -580 0 0 {name=p2 lab=VCTRL_P}
C {ipin.sym} 660 -240 0 0 {name=p4 lab=VCTRL_N}
C {opin.sym} 585 -320 0 0 {name=p9 lab=VDZN}
C {opin.sym} 1040 -450 0 0 {name=p6 lab=VDZP}
C {title.sym} 160 -30 0 0 {name=l1 author="Nithin Purushothama"}
C {sg13g2_pr/annotate_fet_params.sym} -30 -650 0 0 {name=annot1 ref=MP_DZ_STG2_3N}
C {sg13g2_pr/annotate_fet_params.sym} 60 -480 0 0 {name=annot2 ref=MN_STG2_3P1}
C {sg13g2_pr/annotate_fet_params.sym} 60 -280 0 0 {name=annot3 ref=MN_STG2_3N1}
C {sg13g2_pr/annotate_fet_params.sym} 1020 -620 0 0 {name=annot4 ref=MP_STG2_3P1}
C {sg13g2_pr/annotate_fet_params.sym} 1010 -400 0 0 {name=annot5 ref=MP_STG2_3P2}
C {sg13g2_pr/annotate_fet_params.sym} 1000 -260 0 0 {name=annot6 ref=MN_DZ_STG2_3P}
