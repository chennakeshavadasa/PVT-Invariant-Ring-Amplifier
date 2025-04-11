v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
B 4 95 -110 1505 -100 {}
B 4 95 -670 1505 -660 {}
T {RING AMPLIFIER STAGE-2 REPLICA} 565 -735 0 0 0.75 0.75 {}
N 315 -305 315 -255 {lab=#net1}
N 315 -225 315 -105 {lab=GND}
N 215 -225 275 -225 {lab=Vin_STG2}
N 215 -305 215 -225 {lab=Vin_STG2}
N 215 -395 275 -395 {lab=Vin_STG2}
N 315 -535 315 -425 {lab=#net2}
N 315 -395 355 -395 {lab=VDD}
N 355 -565 355 -395 {lab=VDD}
N 315 -565 355 -565 {lab=VDD}
N 155 -305 215 -305 {lab=Vin_STG2}
N 215 -395 215 -305 {lab=Vin_STG2}
N 315 -365 315 -305 {lab=#net1}
N 1015 -355 1015 -255 {lab=#net3}
N 915 -355 975 -355 {lab=Vin_STG2}
N 915 -435 915 -355 {lab=Vin_STG2}
N 915 -525 975 -525 {lab=Vin_STG2}
N 855 -435 915 -435 {lab=Vin_STG2}
N 915 -525 915 -435 {lab=Vin_STG2}
N 1015 -435 1015 -385 {lab=#net4}
N 1015 -225 1015 -105 {lab=GND}
N 725 -245 755 -245 {lab=GND}
N 755 -245 755 -195 {lab=GND}
N 725 -195 755 -195 {lab=GND}
N 725 -215 725 -195 {lab=GND}
N 615 -245 685 -245 {lab=#net5}
N 615 -305 615 -245 {lab=#net5}
N 615 -305 725 -305 {lab=#net5}
N 725 -305 725 -275 {lab=#net5}
N 725 -375 725 -305 {lab=#net5}
N 725 -195 725 -105 {lab=GND}
N 435 -425 465 -425 {lab=VDD}
N 615 -425 655 -425 {lab=GND}
N 565 -305 615 -305 {lab=#net5}
N 1425 -325 1465 -325 {lab=#net6}
N 1395 -325 1395 -255 {lab=#net6}
N 1395 -255 1505 -255 {lab=#net6}
N 1505 -295 1505 -255 {lab=#net6}
N 1505 -255 1505 -215 {lab=#net6}
N 1505 -155 1505 -105 {lab=GND}
N 1175 -405 1205 -405 {lab=VDD}
N 1345 -405 1365 -405 {lab=GND}
N 1295 -515 1295 -485 {lab=#net6}
N 1295 -515 1425 -515 {lab=#net6}
N 1425 -515 1425 -325 {lab=#net6}
N 1395 -325 1425 -325 {lab=#net6}
N 1275 -275 1275 -180 {lab=VCTRLN}
N 1145 -515 1255 -515 {lab=#net4}
N 1015 -495 1015 -435 {lab=#net4}
N 565 -355 565 -305 {lab=#net5}
N 505 -355 505 -305 {lab=#net1}
N 1255 -515 1255 -485 {lab=#net4}
N 1145 -515 1145 -435 {lab=#net4}
N 315 -665 315 -565 {lab=VDD}
N 725 -665 1015 -665 {lab=VDD}
N 1015 -665 1015 -525 {lab=VDD}
N 1505 -665 1505 -325 {lab=VDD}
N 1175 -665 1505 -665 {lab=VDD}
N 1365 -105 1505 -105 {lab=GND}
N 655 -105 725 -105 {lab=GND}
N 725 -105 1015 -105 {lab=GND}
N 435 -665 435 -425 {lab=VDD}
N 315 -665 435 -665 {lab=VDD}
N 655 -425 655 -105 {lab=GND}
N 315 -105 655 -105 {lab=GND}
N 725 -665 725 -435 {lab=VDD}
N 435 -665 725 -665 {lab=VDD}
N 1175 -665 1175 -405 {lab=VDD}
N 1015 -665 1175 -665 {lab=VDD}
N 1365 -405 1365 -105 {lab=GND}
N 1015 -105 1365 -105 {lab=GND}
N 95 -665 315 -665 {lab=VDD}
N 95 -105 315 -105 {lab=GND}
N 315 -305 505 -305 {lab=#net1}
N 1015 -435 1145 -435 {lab=#net4}
N 100 -565 275 -565 {lab=VCTRLP}
N 100 -610 100 -565 {lab=VCTRLP}
N 80 -610 100 -610 {lab=VCTRLP}
N 100 -610 535 -610 {lab=VCTRLP}
N 535 -610 535 -535 {lab=VCTRLP}
N 920 -225 975 -225 {lab=VCTRLN}
N 920 -225 920 -180 {lab=VCTRLN}
N 900 -225 920 -225 {lab=VCTRLN}
N 920 -180 1275 -180 {lab=VCTRLN}
C {sg13g2_pr/sg13_lv_nmos.sym} 295 -225 0 0 {name=MN_STG2_3N1
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 295 -395 0 0 {name=MN_STG2_3P1
l=0.13u
w=0.15u
ng=1
m=3
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 295 -565 0 0 {name=MP_DZ_STG2_3N
l=0.13u
w=0.15u
ng=1
m=5
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 995 -355 0 0 {name=MP_STG2_3P2
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 995 -525 0 0 {name=MP_STG2_3P1
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 995 -225 0 0 {name=MN_DZ_STG2_3P
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 705 -245 0 0 {name=MN_STG2_3N_R
l=1u
w=2.3u
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {isource.sym} 725 -405 0 0 {name=I0 value=1u}
C {ngspice_probe.sym} 615 -305 0 0 {name=r1}
C {/foss/designs/RAMP/OTA/POTA.sym} 685 125 3 0 {name=x1}
C {ngspice_probe.sym} 315 -305 0 0 {name=r2}
C {sg13g2_pr/sg13_hv_pmos.sym} 1485 -325 0 0 {name=MP_STG2_3P_R
l=0.5u
w=4.5u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {isource.sym} 1505 -185 0 0 {name=I1 value=1u}
C {ngspice_probe.sym} 1395 -285 0 0 {name=r3}
C {/foss/designs/RAMP/OTA/NOTA.sym} 1275 -685 3 1 {name=x2}
C {ngspice_probe.sym} 1015 -435 0 0 {name=r4}
C {ipin.sym} 155 -305 0 0 {name=p5 lab=Vin_STG2}
C {lab_pin.sym} 855 -435 0 0 {name=p6 sig_type=std_logic lab=Vin_STG2}
C {iopin.sym} 95 -665 0 1 {name=p7 lab=VDD}
C {iopin.sym} 95 -105 0 1 {name=p8 lab=GND}
C {title.sym} 365 -30 0 0 {name=l1 author="Nithin Purushothama"}
C {ngspice_probe.sym} 1015 -285 0 0 {name=r5}
C {ngspice_probe.sym} 315 -485 0 1 {name=r6}
C {opin.sym} 80 -610 0 1 {name=p9 lab=VCTRLP}
C {opin.sym} 900 -225 0 1 {name=p1 lab=VCTRLN}
