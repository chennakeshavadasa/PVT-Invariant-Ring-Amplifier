v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 780 -280 860 -280 {lab=Vout}
N 500 -150 500 -130 {lab=GND}
N 1060 -350 1060 -325 {lab=GND}
N 1060 -430 1060 -410 {lab=VDD}
N 670 -370 670 -340 {lab=VDD}
N 670 -220 670 -200 {lab=GND}
N 860 -170 860 -150 {lab=GND}
N 860 -280 860 -230 {lab=Vout}
N 500 -260 600 -260 {lab=VICM}
N 500 -260 500 -210 {lab=VICM}
N 340 -300 340 -280 {lab=VICM}
N 500 -300 600 -300 {lab=VICM}
N 500 -300 500 -260 {lab=VICM}
N 340 -300 500 -300 {lab=VICM}
C {vsource.sym} 1060 -380 0 0 {name=V2 value="dc 1.65 ac 1" savecurrent=false}
C {vdd.sym} 1060 -430 0 0 {name=l1 lab=VDD}
C {gnd.sym} 1060 -325 0 0 {name=l2 lab=GND}
C {gnd.sym} 500 -130 0 0 {name=l3 lab=GND}
C {vdd.sym} 670 -370 0 0 {name=l4 lab=VDD}
C {gnd.sym} 670 -200 0 0 {name=l5 lab=GND}
C {capa.sym} 860 -200 0 0 {name=C1
m=1
value=50p
footprint=1206
device="ceramic capacitor"}
C {gnd.sym} 860 -150 0 0 {name=l6 lab=GND}
C {title.sym} 160 -30 0 0 {name=l7 author="Nithin Purushothama"}
C {devices/launcher.sym} 610 -90 0 0 {name=h1
descr="load op & annotate" 
tclcommand="xschem raw_read $netlist_dir/RamP_tb1_CP_FB1.raw; set show_hidden_texts 1; xschem annotate_op"}
C {ngspice_probe.sym} 500 -300 0 1 {name=r1}
C {code_shown.sym} 0 -190 0 0 {
name=TT_MODELS
only_toplevel=true
value="
** IHP models
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
"
spice_ignore=false
      }
C {lab_pin.sym} 500 -250 0 0 {name=p2 sig_type=std_logic lab=VICM}
C {ngspice_probe.sym} 860 -280 0 0 {name=r2}
C {lab_pin.sym} 860 -280 0 1 {name=p1 sig_type=std_logic lab=Vout}
C {/foss/designs/RAMP/Fully-Diff-RAMP/RAMP2.sym} 340 -280 0 0 {name=x1}
C {code.sym} 290 -500 0 0 {name=SAVE_COMMANDS only_toplevel=false value="
.save @n.x1.x2.xmn_stg2_3n1.nsg13_lv_nmos[gm]
.save @n.x1.x2.xmn_stg2_3n1.nsg13_lv_nmos[gds]
.save @n.x1.x2.xmn_stg2_3n1.nsg13_lv_nmos[vth]
.save @n.x1.x2.xmn_stg2_3n1.nsg13_lv_nmos[vdss]
.save @n.x1.x2.xmn_stg2_3n1.nsg13_lv_nmos[cgg]
.save @n.x1.x2.xmn_stg2_3n1.nsg13_lv_nmos[cgsol]
.save @n.x1.x2.xmn_stg2_3n1.nsg13_lv_nmos[cgdol]
.save @n.x1.x2.xmn_stg2_3p1.nsg13_lv_pmos[gm]
.save @n.x1.x2.xmn_stg2_3p1.nsg13_lv_pmos[gds]
.save @n.x1.x2.xmn_stg2_3p1.nsg13_lv_pmos[vth]
.save @n.x1.x2.xmn_stg2_3p1.nsg13_lv_pmos[vdss]
.save @n.x1.x2.xmn_stg2_3p1.nsg13_lv_pmos[cgg]
.save @n.x1.x2.xmn_stg2_3p1.nsg13_lv_pmos[cgsol]
.save @n.x1.x2.xmn_stg2_3p1.nsg13_lv_pmos[cgdol]
.save @n.x1.x2.xmp_dz_stg2_3n.nsg13_lv_pmos[gm]
.save @n.x1.x2.xmp_dz_stg2_3n.nsg13_lv_pmos[gds]
.save @n.x1.x2.xmp_dz_stg2_3n.nsg13_lv_pmos[vth]
.save @n.x1.x2.xmp_dz_stg2_3n.nsg13_lv_pmos[vdss]
.save @n.x1.x2.xmp_dz_stg2_3n.nsg13_lv_pmos[cgg]
.save @n.x1.x2.xmp_dz_stg2_3n.nsg13_lv_pmos[cgsol]
.save @n.x1.x2.xmp_dz_stg2_3n.nsg13_lv_pmos[cgdol]
.save @n.x1.x2.xmp_stg2_3p2.nsg13_lv_nmos[gm]
.save @n.x1.x2.xmp_stg2_3p2.nsg13_lv_nmos[gds]
.save @n.x1.x2.xmp_stg2_3p2.nsg13_lv_nmos[vth]
.save @n.x1.x2.xmp_stg2_3p2.nsg13_lv_nmos[vdss]
.save @n.x1.x2.xmp_stg2_3p2.nsg13_lv_nmos[cgg]
.save @n.x1.x2.xmp_stg2_3p2.nsg13_lv_nmos[cgsol]
.save @n.x1.x2.xmp_stg2_3p2.nsg13_lv_nmos[cgdol]
.save @n.x1.x2.xmp_stg2_3p1.nsg13_lv_pmos[gm]
.save @n.x1.x2.xmp_stg2_3p1.nsg13_lv_pmos[gds]
.save @n.x1.x2.xmp_stg2_3p1.nsg13_lv_pmos[vth]
.save @n.x1.x2.xmp_stg2_3p1.nsg13_lv_pmos[vdss]
.save @n.x1.x2.xmp_stg2_3p1.nsg13_lv_pmos[cgg]
.save @n.x1.x2.xmp_stg2_3p1.nsg13_lv_pmos[cgsol]
.save @n.x1.x2.xmp_stg2_3p1.nsg13_lv_pmos[cgdol]
.save @n.x1.x2.xmn_dz_stg2_3p.nsg13_lv_nmos[gm]
.save @n.x1.x2.xmn_dz_stg2_3p.nsg13_lv_nmos[gds]
.save @n.x1.x2.xmn_dz_stg2_3p.nsg13_lv_nmos[vth]
.save @n.x1.x2.xmn_dz_stg2_3p.nsg13_lv_nmos[vdss]
.save @n.x1.x2.xmn_dz_stg2_3p.nsg13_lv_nmos[cgg]
.save @n.x1.x2.xmn_dz_stg2_3p.nsg13_lv_nmos[cgsol]
.save @n.x1.x2.xmn_dz_stg2_3p.nsg13_lv_nmos[cgdol]
.save @n.x1.xm1.nsg13_hv_nmos[gm]
.save @n.x1.xm1.nsg13_hv_nmos[gds]
.save @n.x1.xm1.nsg13_hv_nmos[vth]
.save @n.x1.xm1.nsg13_hv_nmos[vdss]
.save @n.x1.xm1.nsg13_hv_nmos[cgg]
.save @n.x1.xm1.nsg13_hv_nmos[cgsol]
.save @n.x1.xm1.nsg13_hv_nmos[cgdol]
.save @n.x1.xm2.nsg13_hv_pmos[gm]
.save @n.x1.xm2.nsg13_hv_pmos[gds]
.save @n.x1.xm2.nsg13_hv_pmos[vth]
.save @n.x1.xm2.nsg13_hv_pmos[vdss]
.save @n.x1.xm2.nsg13_hv_pmos[cgg]
.save @n.x1.xm2.nsg13_hv_pmos[cgsol]
.save @n.x1.xm2.nsg13_hv_pmos[cgdol]
.save @n.x1.x3.xmn_stg2_3n1.nsg13_lv_nmos[gm]
.save @n.x1.x3.xmn_stg2_3n1.nsg13_lv_nmos[gds]
.save @n.x1.x3.xmn_stg2_3n1.nsg13_lv_nmos[vth]
.save @n.x1.x3.xmn_stg2_3n1.nsg13_lv_nmos[vdss]
.save @n.x1.x3.xmn_stg2_3n1.nsg13_lv_nmos[cgg]
.save @n.x1.x3.xmn_stg2_3n1.nsg13_lv_nmos[cgsol]
.save @n.x1.x3.xmn_stg2_3n1.nsg13_lv_nmos[cgdol]
.save @n.x1.x3.xmn_stg2_3p1.nsg13_lv_pmos[gm]
.save @n.x1.x3.xmn_stg2_3p1.nsg13_lv_pmos[gds]
.save @n.x1.x3.xmn_stg2_3p1.nsg13_lv_pmos[vth]
.save @n.x1.x3.xmn_stg2_3p1.nsg13_lv_pmos[vdss]
.save @n.x1.x3.xmn_stg2_3p1.nsg13_lv_pmos[cgg]
.save @n.x1.x3.xmn_stg2_3p1.nsg13_lv_pmos[cgsol]
.save @n.x1.x3.xmn_stg2_3p1.nsg13_lv_pmos[cgdol]
.save @n.x1.x3.xmp_dz_stg2_3n.nsg13_lv_pmos[gm]
.save @n.x1.x3.xmp_dz_stg2_3n.nsg13_lv_pmos[gds]
.save @n.x1.x3.xmp_dz_stg2_3n.nsg13_lv_pmos[vth]
.save @n.x1.x3.xmp_dz_stg2_3n.nsg13_lv_pmos[vdss]
.save @n.x1.x3.xmp_dz_stg2_3n.nsg13_lv_pmos[cgg]
.save @n.x1.x3.xmp_dz_stg2_3n.nsg13_lv_pmos[cgsol]
.save @n.x1.x3.xmp_dz_stg2_3n.nsg13_lv_pmos[cgdol]
.save @n.x1.x3.xmp_stg2_3p2.nsg13_lv_nmos[gm]
.save @n.x1.x3.xmp_stg2_3p2.nsg13_lv_nmos[gds]
.save @n.x1.x3.xmp_stg2_3p2.nsg13_lv_nmos[vth]
.save @n.x1.x3.xmp_stg2_3p2.nsg13_lv_nmos[vdss]
.save @n.x1.x3.xmp_stg2_3p2.nsg13_lv_nmos[cgg]
.save @n.x1.x3.xmp_stg2_3p2.nsg13_lv_nmos[cgsol]
.save @n.x1.x3.xmp_stg2_3p2.nsg13_lv_nmos[cgdol]
.save @n.x1.x3.xmp_stg2_3p1.nsg13_lv_pmos[gm]
.save @n.x1.x3.xmp_stg2_3p1.nsg13_lv_pmos[gds]
.save @n.x1.x3.xmp_stg2_3p1.nsg13_lv_pmos[vth]
.save @n.x1.x3.xmp_stg2_3p1.nsg13_lv_pmos[vdss]
.save @n.x1.x3.xmp_stg2_3p1.nsg13_lv_pmos[cgg]
.save @n.x1.x3.xmp_stg2_3p1.nsg13_lv_pmos[cgsol]
.save @n.x1.x3.xmp_stg2_3p1.nsg13_lv_pmos[cgdol]
.save @n.x1.x3.xmn_dz_stg2_3p.nsg13_lv_nmos[gm]
.save @n.x1.x3.xmn_dz_stg2_3p.nsg13_lv_nmos[gds]
.save @n.x1.x3.xmn_dz_stg2_3p.nsg13_lv_nmos[vth]
.save @n.x1.x3.xmn_dz_stg2_3p.nsg13_lv_nmos[vdss]
.save @n.x1.x3.xmn_dz_stg2_3p.nsg13_lv_nmos[cgg]
.save @n.x1.x3.xmn_dz_stg2_3p.nsg13_lv_nmos[cgsol]
.save @n.x1.x3.xmn_dz_stg2_3p.nsg13_lv_nmos[cgdol]
.save @n.x1.x3.xmn_stg2_3n_r.nsg13_hv_nmos[gm]
.save @n.x1.x3.xmn_stg2_3n_r.nsg13_hv_nmos[gds]
.save @n.x1.x3.xmn_stg2_3n_r.nsg13_hv_nmos[vth]
.save @n.x1.x3.xmn_stg2_3n_r.nsg13_hv_nmos[vdss]
.save @n.x1.x3.xmn_stg2_3n_r.nsg13_hv_nmos[cgg]
.save @n.x1.x3.xmn_stg2_3n_r.nsg13_hv_nmos[cgsol]
.save @n.x1.x3.xmn_stg2_3n_r.nsg13_hv_nmos[cgdol]
.save @n.x1.x3.x1.xm2.nsg13_lv_pmos[gm]
.save @n.x1.x3.x1.xm2.nsg13_lv_pmos[gds]
.save @n.x1.x3.x1.xm2.nsg13_lv_pmos[vth]
.save @n.x1.x3.x1.xm2.nsg13_lv_pmos[vdss]
.save @n.x1.x3.x1.xm2.nsg13_lv_pmos[cgg]
.save @n.x1.x3.x1.xm2.nsg13_lv_pmos[cgsol]
.save @n.x1.x3.x1.xm2.nsg13_lv_pmos[cgdol]
.save @n.x1.x3.x1.xm4.nsg13_hv_nmos[gm]
.save @n.x1.x3.x1.xm4.nsg13_hv_nmos[gds]
.save @n.x1.x3.x1.xm4.nsg13_hv_nmos[vth]
.save @n.x1.x3.x1.xm4.nsg13_hv_nmos[vdss]
.save @n.x1.x3.x1.xm4.nsg13_hv_nmos[cgg]
.save @n.x1.x3.x1.xm4.nsg13_hv_nmos[cgsol]
.save @n.x1.x3.x1.xm4.nsg13_hv_nmos[cgdol]
.save @n.x1.x3.x1.xm5.nsg13_hv_nmos[gm]
.save @n.x1.x3.x1.xm5.nsg13_hv_nmos[gds]
.save @n.x1.x3.x1.xm5.nsg13_hv_nmos[vth]
.save @n.x1.x3.x1.xm5.nsg13_hv_nmos[vdss]
.save @n.x1.x3.x1.xm5.nsg13_hv_nmos[cgg]
.save @n.x1.x3.x1.xm5.nsg13_hv_nmos[cgsol]
.save @n.x1.x3.x1.xm5.nsg13_hv_nmos[cgdol]
.save @n.x1.x3.x1.xm1.nsg13_lv_pmos[gm]
.save @n.x1.x3.x1.xm1.nsg13_lv_pmos[gds]
.save @n.x1.x3.x1.xm1.nsg13_lv_pmos[vth]
.save @n.x1.x3.x1.xm1.nsg13_lv_pmos[vdss]
.save @n.x1.x3.x1.xm1.nsg13_lv_pmos[cgg]
.save @n.x1.x3.x1.xm1.nsg13_lv_pmos[cgsol]
.save @n.x1.x3.x1.xm1.nsg13_lv_pmos[cgdol]
.save @n.x1.x3.xmp_stg2_3p_r.nsg13_hv_pmos[gm]
.save @n.x1.x3.xmp_stg2_3p_r.nsg13_hv_pmos[gds]
.save @n.x1.x3.xmp_stg2_3p_r.nsg13_hv_pmos[vth]
.save @n.x1.x3.xmp_stg2_3p_r.nsg13_hv_pmos[vdss]
.save @n.x1.x3.xmp_stg2_3p_r.nsg13_hv_pmos[cgg]
.save @n.x1.x3.xmp_stg2_3p_r.nsg13_hv_pmos[cgsol]
.save @n.x1.x3.xmp_stg2_3p_r.nsg13_hv_pmos[cgdol]
.save @n.x1.x3.x2.xm1.nsg13_hv_nmos[gm]
.save @n.x1.x3.x2.xm1.nsg13_hv_nmos[gds]
.save @n.x1.x3.x2.xm1.nsg13_hv_nmos[vth]
.save @n.x1.x3.x2.xm1.nsg13_hv_nmos[vdss]
.save @n.x1.x3.x2.xm1.nsg13_hv_nmos[cgg]
.save @n.x1.x3.x2.xm1.nsg13_hv_nmos[cgsol]
.save @n.x1.x3.x2.xm1.nsg13_hv_nmos[cgdol]
.save @n.x1.x3.x2.xm2.nsg13_hv_nmos[gm]
.save @n.x1.x3.x2.xm2.nsg13_hv_nmos[gds]
.save @n.x1.x3.x2.xm2.nsg13_hv_nmos[vth]
.save @n.x1.x3.x2.xm2.nsg13_hv_nmos[vdss]
.save @n.x1.x3.x2.xm2.nsg13_hv_nmos[cgg]
.save @n.x1.x3.x2.xm2.nsg13_hv_nmos[cgsol]
.save @n.x1.x3.x2.xm2.nsg13_hv_nmos[cgdol]
.save @n.x1.x3.x2.xm3.nsg13_hv_pmos[gm]
.save @n.x1.x3.x2.xm3.nsg13_hv_pmos[gds]
.save @n.x1.x3.x2.xm3.nsg13_hv_pmos[vth]
.save @n.x1.x3.x2.xm3.nsg13_hv_pmos[vdss]
.save @n.x1.x3.x2.xm3.nsg13_hv_pmos[cgg]
.save @n.x1.x3.x2.xm3.nsg13_hv_pmos[cgsol]
.save @n.x1.x3.x2.xm3.nsg13_hv_pmos[cgdol]
.save @n.x1.x3.x2.xm4.nsg13_hv_pmos[gm]
.save @n.x1.x3.x2.xm4.nsg13_hv_pmos[gds]
.save @n.x1.x3.x2.xm4.nsg13_hv_pmos[vth]
.save @n.x1.x3.x2.xm4.nsg13_hv_pmos[vdss]
.save @n.x1.x3.x2.xm4.nsg13_hv_pmos[cgg]
.save @n.x1.x3.x2.xm4.nsg13_hv_pmos[cgsol]
.save @n.x1.x3.x2.xm4.nsg13_hv_pmos[cgdol]
.save @n.x1.x4.xm9.nsg13_lv_nmos[gm]
.save @n.x1.x4.xm9.nsg13_lv_nmos[gds]
.save @n.x1.x4.xm9.nsg13_lv_nmos[vth]
.save @n.x1.x4.xm9.nsg13_lv_nmos[vdss]
.save @n.x1.x4.xm9.nsg13_lv_nmos[cgg]
.save @n.x1.x4.xm9.nsg13_lv_nmos[cgsol]
.save @n.x1.x4.xm9.nsg13_lv_nmos[cgdol]
.save @n.x1.x4.xm10.nsg13_lv_pmos[gm]
.save @n.x1.x4.xm10.nsg13_lv_pmos[gds]
.save @n.x1.x4.xm10.nsg13_lv_pmos[vth]
.save @n.x1.x4.xm10.nsg13_lv_pmos[vdss]
.save @n.x1.x4.xm10.nsg13_lv_pmos[cgg]
.save @n.x1.x4.xm10.nsg13_lv_pmos[cgsol]
.save @n.x1.x4.xm10.nsg13_lv_pmos[cgdol]
.save @n.x1.x4.xm11.nsg13_lv_pmos[gm]
.save @n.x1.x4.xm11.nsg13_lv_pmos[gds]
.save @n.x1.x4.xm11.nsg13_lv_pmos[vth]
.save @n.x1.x4.xm11.nsg13_lv_pmos[vdss]
.save @n.x1.x4.xm11.nsg13_lv_pmos[cgg]
.save @n.x1.x4.xm11.nsg13_lv_pmos[cgsol]
.save @n.x1.x4.xm11.nsg13_lv_pmos[cgdol]
.save @n.x1.x4.xm12.nsg13_lv_nmos[gm]
.save @n.x1.x4.xm12.nsg13_lv_nmos[gds]
.save @n.x1.x4.xm12.nsg13_lv_nmos[vth]
.save @n.x1.x4.xm12.nsg13_lv_nmos[vdss]
.save @n.x1.x4.xm12.nsg13_lv_nmos[cgg]
.save @n.x1.x4.xm12.nsg13_lv_nmos[cgsol]
.save @n.x1.x4.xm12.nsg13_lv_nmos[cgdol]
.save @n.x1.x4.xm13.nsg13_lv_pmos[gm]
.save @n.x1.x4.xm13.nsg13_lv_pmos[gds]
.save @n.x1.x4.xm13.nsg13_lv_pmos[vth]
.save @n.x1.x4.xm13.nsg13_lv_pmos[vdss]
.save @n.x1.x4.xm13.nsg13_lv_pmos[cgg]
.save @n.x1.x4.xm13.nsg13_lv_pmos[cgsol]
.save @n.x1.x4.xm13.nsg13_lv_pmos[cgdol]
.save @n.x1.x4.xm14.nsg13_lv_nmos[gm]
.save @n.x1.x4.xm14.nsg13_lv_nmos[gds]
.save @n.x1.x4.xm14.nsg13_lv_nmos[vth]
.save @n.x1.x4.xm14.nsg13_lv_nmos[vdss]
.save @n.x1.x4.xm14.nsg13_lv_nmos[cgg]
.save @n.x1.x4.xm14.nsg13_lv_nmos[cgsol]
.save @n.x1.x4.xm14.nsg13_lv_nmos[cgdol]
.save @n.x1.x5.xmn_stg1_ip_n1.nsg13_lv_nmos[gm]
.save @n.x1.x5.xmn_stg1_ip_n1.nsg13_lv_nmos[gds]
.save @n.x1.x5.xmn_stg1_ip_n1.nsg13_lv_nmos[vth]
.save @n.x1.x5.xmn_stg1_ip_n1.nsg13_lv_nmos[vdss]
.save @n.x1.x5.xmn_stg1_ip_n1.nsg13_lv_nmos[cgg]
.save @n.x1.x5.xmn_stg1_ip_n1.nsg13_lv_nmos[cgsol]
.save @n.x1.x5.xmn_stg1_ip_n1.nsg13_lv_nmos[cgdol]
.save @n.x1.x5.xmn_stg1_ip_n2.nsg13_lv_nmos[gm]
.save @n.x1.x5.xmn_stg1_ip_n2.nsg13_lv_nmos[gds]
.save @n.x1.x5.xmn_stg1_ip_n2.nsg13_lv_nmos[vth]
.save @n.x1.x5.xmn_stg1_ip_n2.nsg13_lv_nmos[vdss]
.save @n.x1.x5.xmn_stg1_ip_n2.nsg13_lv_nmos[cgg]
.save @n.x1.x5.xmn_stg1_ip_n2.nsg13_lv_nmos[cgsol]
.save @n.x1.x5.xmn_stg1_ip_n2.nsg13_lv_nmos[cgdol]
.save @n.x1.x5.xmp_stg1_cl_p1.nsg13_hv_pmos[gm]
.save @n.x1.x5.xmp_stg1_cl_p1.nsg13_hv_pmos[gds]
.save @n.x1.x5.xmp_stg1_cl_p1.nsg13_hv_pmos[vth]
.save @n.x1.x5.xmp_stg1_cl_p1.nsg13_hv_pmos[vdss]
.save @n.x1.x5.xmp_stg1_cl_p1.nsg13_hv_pmos[cgg]
.save @n.x1.x5.xmp_stg1_cl_p1.nsg13_hv_pmos[cgsol]
.save @n.x1.x5.xmp_stg1_cl_p1.nsg13_hv_pmos[cgdol]
.save @n.x1.x5.xmp_stg1_cl_p2.nsg13_hv_pmos[gm]
.save @n.x1.x5.xmp_stg1_cl_p2.nsg13_hv_pmos[gds]
.save @n.x1.x5.xmp_stg1_cl_p2.nsg13_hv_pmos[vth]
.save @n.x1.x5.xmp_stg1_cl_p2.nsg13_hv_pmos[vdss]
.save @n.x1.x5.xmp_stg1_cl_p2.nsg13_hv_pmos[cgg]
.save @n.x1.x5.xmp_stg1_cl_p2.nsg13_hv_pmos[cgsol]
.save @n.x1.x5.xmp_stg1_cl_p2.nsg13_hv_pmos[cgdol]"}
C {devices/code_shown.sym} 20 -510 0 0 {name=NGSPICE1 only_toplevel=true 
value="
.option wnflag=1
.option savecurrents
.temp 27
.control
save all
write RamP_tb1_OP_1.raw
set appendwrite 
op
write RamP_tb1_OP_1.raw
dc V1 0 1.65 1m
**tran 0.5m 10m  0.01m
**ac dec 20 1 1e10
plot v(vout)
.endc
"}
C {vsource.sym} 500 -180 0 0 {name=V1 value=0.825 savecurrent=false}
