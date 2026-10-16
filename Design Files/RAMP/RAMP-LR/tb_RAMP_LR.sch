v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
C {RAMP-LR/RAMP_LR.sym} 300 -300 0 0 {name=x1}
N 150 -320 110 -320 {lab=IBIAS}
C {lab_pin.sym} 110 -320 0 0 {name=l101 sig_type=std_logic lab=IBIAS}
N 150 -300 110 -300 {lab=VICM}
C {lab_pin.sym} 110 -300 0 0 {name=l102 sig_type=std_logic lab=VICM}
N 150 -280 110 -280 {lab=inp}
C {lab_pin.sym} 110 -280 0 0 {name=l103 sig_type=std_logic lab=inp}
N 450 -320 490 -320 {lab=VDD}
C {lab_pin.sym} 490 -320 0 1 {name=l104 sig_type=std_logic lab=VDD}
N 450 -300 490 -300 {lab=GND}
C {lab_pin.sym} 490 -300 0 1 {name=l105 sig_type=std_logic lab=GND}
N 450 -280 490 -280 {lab=out}
C {lab_pin.sym} 490 -280 0 1 {name=l106 sig_type=std_logic lab=out}
T {Unity-gain buffer, 50 pF load, Middlebrook double-injection loop gain (as RamP_tb1_CP_FB.sch)} -300 -760 0 0 0.4 0.4 {}
C {vsource.sym} 700 -300 0 0 {name=V2 value="dc 1.65 ac 0" savecurrent=false}
C {lab_pin.sym} 700 -330 0 0 {name=l7 sig_type=std_logic lab=VDD}
C {gnd.sym} 700 -270 0 0 {name=l8 lab=GND}
C {vsource.sym} 800 -300 0 0 {name=V1 value="dc 0.825 ac 0" savecurrent=false}
C {lab_pin.sym} 800 -330 0 0 {name=l9 sig_type=std_logic lab=VICM}
C {gnd.sym} 800 -270 0 0 {name=l10 lab=GND}
C {isource.sym} 900 -300 0 0 {name=I_BIAS value=1u}
C {lab_pin.sym} 900 -330 0 0 {name=l11 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 900 -270 0 0 {name=l12 sig_type=std_logic lab=IBIAS}
C {capa.sym} 1000 -300 0 0 {name=C1 m=1 value=50p footprint=1206 device="ceramic capacitor"}
C {lab_pin.sym} 1000 -330 0 0 {name=l13 sig_type=std_logic lab=out}
C {gnd.sym} 1000 -270 0 0 {name=l14 lab=GND}
C {vsource.sym} 1150 -420 1 1 {name=Vprobe2 value=0 savecurrent=false}
C {vsource.sym} 1290 -420 3 0 {name=Vprobe1 value="dc 0 ac 1" savecurrent=false}
C {isource.sym} 1220 -490 0 0 {name=Iprobe1 value="dc 0 ac 0"}
N 1120 -420 1080 -420 {lab=inp}
N 1180 -420 1260 -420 {lab=probe}
N 1320 -420 1360 -420 {lab=out}
N 1220 -460 1220 -420 {lab=probe}
C {lab_pin.sym} 1080 -420 0 0 {name=l15 sig_type=std_logic lab=inp}
C {lab_pin.sym} 1360 -420 0 1 {name=l16 sig_type=std_logic lab=out}
C {lab_pin.sym} 1220 -420 3 0 {name=l17 sig_type=std_logic lab=probe}
C {gnd.sym} 1220 -520 2 0 {name=l18 lab=GND}
C {code_shown.sym} -300 -660 0 0 {name=MODELS only_toplevel=true value="
** IHP SG13G2 models (TT)
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerRES.lib res_typ
.lib cornerCAP.lib cap_typ
"}
C {code_shown.sym} 300 -660 0 0 {name=NGSPICE only_toplevel=true value="
.control
ac dec 40 1 10G
alter @Vprobe1[acmag]=0
alter @Iprobe1[acmag]=1
ac dec 40 1 10G
let mb = 1/(ac1.v(probe) + ac2.i(Vprobe2)) - 1
let phase_mb = 180/PI*vp(mb)
meas ac ugf when vdb(mb)=0
meas ac pm_deg find phase_mb when vdb(mb)=0
meas ac loop_gain find vdb(mb) at=1
let phase_margin = 180 + pm_deg
print phase_margin
plot vdb(mb) phase_mb
.endc
"}
C {title.sym} -300 0 0 0 {name=l0 author="Nithin Purushothama"}
