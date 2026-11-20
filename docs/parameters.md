# Input generator parameter rules

A task change rebuilds its descendants. Formula defaults follow their dependencies until edited.

| Parameter | Parent | Visible when | Default in the generator | Constraints |
| --- | --- | --- | --- | --- |
| `calculation` | - | always | scf | scf, relax, md, cell-relax, nscf, get_s, get_wf, get_pchg, gen_bessel, gen_opt_abfs, test_memory, test_neighbour |
| `esolver_type` | calculation | always | ksdft | ksdft, sdft, ofdft, tdofdft, tddft, lj, dp, nep, snap, lr, ks-lr, dfpt and `esolver_type != 'tddft' or calculation == 'md'` |
| `basis_type` | esolver_type | esolver_type not in ('dp','lj','nep','snap') | calculation in ('get_wf','get_pchg','get_s','test_neighbour') or esolver_type in ('lr','ks-lr'): lcao / otherwise: pw | pw, lcao, lcao_in_pw |
| `ecutwfc` | basis_type | basis_type != None | given('ecutrho'): ecutrho / 4.0 / basis_type == 'lcao': 100.0 / otherwise: 50.0 | > 0 |
| `ecutrho` | basis_type | basis_type != None | otherwise: 4.0 * ecutwfc | > 0 and `ecutrho / ecutwfc >= 4.0 - 1e-8 and (basis_type != 'lcao' or ecutrho / ecutwfc <= 4.0 + 1e-8)` |
| `scf_thr` | basis_type | basis_type != None | basis_type == 'lcao' or basis_type == 'lcao_in_pw': 1e-07 / calculation == 'nscf': 1e-06 / otherwise: 1e-09 | >= 0 |
| `scf_nmax` | basis_type | basis_type != None | calculation == 'nscf': 1 / otherwise: 100 | >= 1 and `calculation != 'nscf' or scf_nmax == 1` |
| `nspin` | basis_type | basis_type != None | 1 | 1, 2, 4 |
| `sc_mag_switch` | nspin | nspin in (2,4) and esolver_type == 'ksdft' | False |  |
| `sc_scf_thr` | sc_mag_switch | sc_mag_switch == True | 0.0001 | > 0 |
| `mixing_restart` | basis_type | esolver_type == 'ksdft' | not sc_mag_switch: 0.0 / sc_scf_thr == 10: scf_thr / 10.0 / otherwise: sc_scf_thr |  |
| `relax_nmax` | calculation | calculation in ('relax', 'cell-relax') | 50 | >= 1 |
| `force_thr_ev` | calculation | calculation in ('relax', 'cell-relax') | 0.0257112 | > 0 |
| `md_type` | calculation | calculation == 'md' | nvt | fire, nve, nvt, npt, langevin, msst |
| `md_nstep` | calculation | calculation == 'md' | 10 | >= 1 |
| `md_dt` | calculation | calculation == 'md' | 1.0 | > 0 |
| `md_tfirst` | calculation | calculation == 'md' | 300.0 | > 0 |
| `md_tlast` | md_type | md_type in ('nvt', 'npt') | otherwise: md_tfirst | > 0 |
| `md_thermostat` | md_type | md_type == 'nvt' | nhc | nhc, anderson, berendsen, rescaling, rescale_v, csvr |
| `md_tfreq` | md_type | md_type == 'npt' or md_thermostat == 'nhc' | otherwise: 1.0 / (40.0 * md_dt) | > 0 |
| `md_csvr_tau` | md_thermostat | md_thermostat == 'csvr' | otherwise: 100.0 * md_dt | > 0 |
| `md_pmode` | md_type | md_type == 'npt' | iso | iso, aniso, tri |
| `md_pfirst` | md_type | md_type == 'npt' | 1.0 |  |
| `md_plast` | md_type | md_type == 'npt' | otherwise: md_pfirst |  |
| `md_pfreq` | md_type | md_type == 'npt' | otherwise: 1.0 / (400.0 * md_dt) | > 0 |
| `cal_force` | calculation | always | otherwise: calculation in ('relax', 'cell-relax', 'md') | `(calculation not in ('relax','cell-relax','md') or cal_force) and (calculation not in ('get_s','get_pchg','get_wf') or not cal_force)` |
| `cal_stress` | calculation | always | otherwise: calculation == 'cell-relax' or (calculation == 'md' and (md_type in ('npt', 'msst') or esolver_type in ('lj', 'dp'))) | `(calculation != 'cell-relax' and md_type not in ('npt','msst')) or cal_stress` |
| `pot_file` | esolver_type | esolver_type in ('dp','nep','snap') | graph.pb |  |
| `dp_rescaling` | esolver_type | esolver_type == 'dp' | 1.0 |  |
| `dp_fparam` | pot_file | esolver_type == 'dp' and dim_fparam > 0 | [] |  |
| `dp_aparam` | pot_file | esolver_type == 'dp' and dim_aparam > 0 | [] |  |

## ABACUS input catalogue

ABACUS revision `eba09c937c734f3f4da52cbdbb9c55504846921a` registers 637 keywords. Unselected catalogue entries are omitted from INPUT. The reader default column reproduces the native documentation. A callback can also set internal state.

### Additional registered inputs

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `relax` | bool | false |  |  |  |  |
| `cond_mgga_vel` | bool | true |  |  |  |  |
| `out_unshrinked_v` | bool | false |  |  |  |  |
| `exx_coul_moment` | bool | false |  |  |  |  |
| `exx_rotate_abfs` | bool | false |  |  |  |  |
| `exx_multip_moments_threshold` | real | 1e-10 |  |  |  |  |
| `shrink_abfs_pca_thr` | real | -1 |  |  |  |  |
| `shrink_lu_inv_thr` | real | 9.9999999999999995e-07 |  |  |  |  |

### Berry phase and wannier90 interface

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `berry_phase` | Boolean | false |  |  |  |  |
| `gdir` | Integer | 3 |  |  |  |  |
| `towannier90` | Boolean | 0 |  |  |  |  |
| `nnkpfile` | String | seedname.nnkp |  |  |  |  |
| `wannier_method` | Integer | 1 |  |  |  | yes |
| `wannier_spin` | String | up |  |  |  |  |
| `out_wannier_mmn` | Boolean | 1 |  |  |  |  |
| `out_wannier_amn` | Boolean | 1 |  |  |  |  |
| `out_wannier_eig` | Boolean | 1 |  |  |  |  |
| `out_wannier_spn` | Boolean | 1 when the output requirements are met, 0 otherwise |  |  | When out_wannier_spn==true: require towannier90==true and calculation==nscf and basis_type==lcao and wannier_method==2 and nspin==4 | yes |
| `out_wannier_unk` | Boolean | 0 |  |  |  |  |
| `out_wannier_wvfn_formatted` | Boolean | 1 |  |  |  |  |

### Bethe-Salpeter Equation

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `bse_tda` | String | tda |  |  |  |  |
| `bse_spin_types` | Vector of String (>=1 values) | singlet triplet |  |  |  | yes |
| `bse_mem_save` | Boolean | false |  |  |  | yes |
| `bse_ri_hartree` | Boolean | true |  |  |  |  |
| `bse_use_fine_kgrid` | Integer | 0 |  |  |  |  |
| `bse_q_approx_mode` | Integer | 0 |  |  |  |  |
| `bse_q_approx_threshold` | Real | 0.1 |  |  |  |  |
| `out_bse_ab` | Boolean | false |  |  |  |  |
| `bse_continue` | Integer | 0 |  |  |  |  |

### DFT+U correction

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `dft_plus_u` | Integer | 0 |  |  |  | yes |
| `dft_plus_dmft` | Boolean | False |  | basis_type==lcao |  |  |
| `orbital_corr` | Vector of Integer (n values where n is the number of atomic types) | -1 |  |  |  |  |
| `hubbard_u` | Vector of Real (n values where n is the number of atomic types) | 0.0 |  |  |  |  |
| `yukawa_potential` | Boolean | False |  |  |  |  |
| `yukawa_lambda` | Real | Calculated on the fly. |  | dft_plus_u==1 and yukawa_potential==true |  |  |
| `uramping` | Real | -1.0. | eV | dft_plus_u==1 and mixing_restart>0 |  | yes |
| `init_occ_mat` | Integer | 0 |  |  |  |  |
| `omc` | Integer | 0 |  |  |  |  |
| `onsite_radius` | Real | `3.0` for `dft_plus_u=1`, `sc_mag_switch=true`, or `nspin=4` PW RT-TDDFT with `td_out_mag=onsite`; `0.0` otherwise | Bohr | basis_type in [pw, lcao] | value>0 | yes |

### DeePKS

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `deepks_out_labels` | Integer | 0 |  | basis_type==lcao |  |  |
| `deepks_out_freq_elec` | Integer | 0 |  | basis_type==lcao | value>=0 When deepks_out_freq_elec>0: require deepks_out_base!=none |  |
| `deepks_out_base` | String | None |  | basis_type==lcao and deepks_out_freq_elec>0 | When deepks_out_base!=none: require deepks_out_labels>0 and deepks_bandgap==0 |  |
| `deepks_scf` | Boolean | False |  | basis_type==lcao |  |  |
| `deepks_equiv` | Boolean | False |  | basis_type==lcao |  | yes |
| `deepks_model` | String | None |  | basis_type==lcao and deepks_scf==true |  |  |
| `bessel_descriptor_lmax` | Integer | 2 |  | calculation==gen_bessel |  |  |
| `bessel_descriptor_ecut` | String | same as ecutwfc | Ry | calculation==gen_bessel |  | yes |
| `bessel_descriptor_tolerence` | Real | 1.0e-12 |  | calculation==gen_bessel |  |  |
| `bessel_descriptor_rcut` | Real | 6.0 | Bohr | calculation==gen_bessel | value>=0 |  |
| `bessel_descriptor_smooth` | Boolean | False |  | calculation==gen_bessel |  |  |
| `bessel_descriptor_sigma` | Real | 0.1 | Bohr | calculation==gen_bessel |  |  |
| `deepks_bandgap` | Integer | 0 |  | basis_type==lcao and deepks_scf==true | [0, 1, 2, 3] |  |
| `deepks_band_range` | Integer*2 | -1 0 |  | basis_type==lcao and deepks_scf==true and deepks_bandgap in [1, 2] |  |  |
| `deepks_v_delta` | Integer | 0 |  | basis_type==lcao | [-2, -1, 0, 1, 2] |  |
| `deepks_out_unittest` | Boolean | False |  |  |  | yes |

### Density functional perturbation theory

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `dfpt_qmesh` | Vector of Int (1 or 3 values) | 1 1 1 |  |  |  |  |
| `dfpt_qfile` | String | "" |  |  |  |  |
| `dfpt_compute_q0` | Boolean | false |  |  |  |  |
| `dfpt_loto` | Boolean | false |  |  |  |  |
| `dfpt_out_dyn` | Boolean | false |  |  |  |  |
| `dfpt_conv_thr` | Real | 1.0e-8 |  |  |  |  |
| `dfpt_max_iter` | Integer | 100 |  |  | value>=1 |  |
| `dfpt_lin_conv_thr` | Real | -1.0 (inherit dfpt_conv_thr) |  |  |  |  |
| `dfpt_lin_max_iter` | Integer | 0 (inherit dfpt_max_iter) |  |  |  |  |
| `dfpt_mix_beta` | Real | 0.4 |  |  |  |  |
| `dfpt_asr` | String | no |  |  |  |  |
| `dfpt_mix_type` | String | v_sc_broyden |  |  | ['rho_plain', 'rho_kerker', 'rho_broyden', 'v_sc_plain', 'v_sc_broyden'] |  |
| `dfpt_kerker_a2` | Real | 1.0 |  |  | value>0 |  |
| `dfpt_broyden_ndim` | Integer | 8 |  |  | value>=1 |  |

### Density of states

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `dos_edelta_ev` | Real | 0.03 | eV |  |  |  |
| `dos_sigma` | Real | 0.07 | eV |  |  |  |
| `dos_scale` | Real | 0.01 | eV |  |  |  |
| `dos_emin_ev` | Real | Minimal eigenenergy of | eV |  |  |  |
| `dos_emax_ev` | Real | Maximal eigenenergy of | eV |  |  |  |
| `dos_nche` | Integer | 100 |  |  |  |  |
| `stm_bias` | Real Real(optional) Integer(optional) | 1.0 | V |  |  |  |
| `ldos_line` | Real*6 Integer(optional) | 0.0 0.0 0.0 0.0 0.0 1.0 100 |  |  |  |  |

### Electric field and dipole correction

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `efield_flag` | Boolean | False |  |  |  |  |
| `dip_cor_flag` | Boolean | False |  | efield_flag==true | When dip_cor_flag==true: require efield_flag==true |  |
| `efield_dir` | Integer | 2 |  | efield_flag==true | When gate_flag==true and efield_flag==true: require dip_cor_flag==true |  |
| `efield_pos_max` | Real | Autoset to center of vacuum - width of vacuum / 20 |  | efield_flag==true |  |  |
| `efield_pos_dec` | Real | Autoset to width of vacuum / 10 |  | efield_flag==true |  |  |
| `efield_amp` | Real | 0.0 | a.u., 1 a.u. = 51.4220632*10^10 V/m. | efield_flag==true |  |  |

### Electronic conductivities

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `cal_cond` | Boolean | False |  | basis_type==pw |  |  |
| `cond_che_thr` | Real | 1e-8 |  | esolver_type==sdft |  |  |
| `cond_dw` | Real | 0.1 | eV | basis_type==pw |  |  |
| `cond_wcut` | Real | 10.0 | eV | basis_type==pw |  |  |
| `cond_dt` | Real | 0.02 | a.u. | basis_type==pw |  |  |
| `cond_dtbatch` | Integer | 0 |  | esolver_type==sdft |  |  |
| `cond_smear` | Integer | 1 |  |  |  |  |
| `cond_fwhm` | Real | 0.4 | eV | basis_type==pw |  |  |
| `cond_nonlocal` | Boolean | True |  | basis_type==pw |  |  |

### Electronic structure

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `basis_type` | String | pw |  |  | ['pw', 'lcao', 'lcao_in_pw'] | yes |
| `ks_solver` | String | - PW basis: cg. - LCAO basis: - genelpa (if compiling option `ENABLE_ELPA` has been set) - lapack (if compiling option `ENABLE_MPI` has not been set) - scalapack_gvx (if compiling option `ENABLE_ELPA` has not been set and compiling option `ENABLE_MPI` has been set) - cusolver (if compiling option `USE_CUDA` has been set) |  |  | ['cg', 'dav', 'bpcg', 'dav_subspace', 'genelpa', 'elpa', 'lapack', 'scalapack_gvx', 'cusolver', 'cusolvermp', 'pexsi'] When basis_type==pw: require ks_solver in [cg, dav, bpcg, dav_subspace]; When basis_type==lcao: require ks_solver in [genelpa, elpa, lapack, scalapack_gvx, cusolver, cusolvermp, pexsi]; When ks_solver==genelpa: require device==cpu | yes |
| `nbands` | Integer |  |  |  | value>=0 |  |
| `nelec` | Real | 0.0 |  |  | value>=0 |  |
| `nelec_delta` | Real | 0.0 |  |  |  |  |
| `nupdown` | Real | 0.0 |  |  | When nspin==1: require nupdown==0 | yes |
| `dft_functional` | String | Used the same as DFT functional as specified in the pseudopotential files. |  |  |  |  |
| `xc_temperature` | Real | 0.0 | Ry |  |  |  |
| `xc_exch_ext` | Integer followed by Real values |  |  |  |  |  |
| `xc_corr_ext` | Integer followed by Real values |  |  |  |  |  |
| `pseudo_rcut` | Real | 15 | Bohr |  |  |  |
| `pseudo_mesh` | Boolean | 0 |  |  |  |  |
| `nspin` | Integer | 1 |  |  | [1, 2, 4] When noncolin==true or lspinorb==true: require nspin==4 |  |
| `gga_grad` | Integer | `2` for `esolver_type=tddft`; `0` otherwise |  |  | [0, 1, 2] | yes |
| `smearing_method` | String | gauss |  |  |  |  |
| `smearing_sigma` | Real | 0.015 | Ry |  |  |  |
| `smearing_sigma_temp` | Real | 2 * smearing_sigma / kB. | K |  |  |  |
| `mixing_type` | String | broyden |  |  |  |  |
| `mixing_beta` | Real | 0.8 for nspin=1, 0.4 for nspin=2 and nspin=4. |  |  | value>=0 | yes |
| `mixing_beta_mag` | Real | 4*mixing_beta, but the maximum value is 1.6. |  |  | value>=0 | yes |
| `mixing_ndim` | Integer | 8 |  |  |  |  |
| `mixing_restart` | Real | 0 |  |  |  | yes |
| `mixing_dmr` | Boolean | false |  | mixing_restart>0 |  |  |
| `mixing_gg0` | Real | 1.0 |  |  |  |  |
| `mixing_gg0_mag` | Real | 0.0 |  |  |  |  |
| `mixing_gg0_min` | Real | 0.1 |  |  |  |  |
| `mixing_angle` | Real | -10.0 |  | nspin==4 |  |  |
| `mixing_tau` | Boolean | False |  |  |  |  |
| `mixing_dftu` | Boolean | False |  | dft_plus_u==1 |  |  |
| `gamma_only` | Boolean | 0 |  | basis_type==lcao |  | yes |
| `scf_nmax` | Integer | 100 |  |  |  | yes |
| `scf_thr` | Real | 1.0e-9 (plane-wave basis), or 1.0e-7 (localized atomic orbital basis). | Ry if scf_thr_type=1, dimensionless if scf_thr_type=2 |  | value>=0 | yes |
| `scf_ene_thr` | Real | -1.0. If the user does not set this parameter, it will not take effect. | eV |  |  |  |
| `scf_thr_type` | Integer | 1 (plane-wave basis), or 2 (localized atomic orbital basis). |  |  | [1, 2] | yes |
| `scf_os_stop` | Boolean | false |  |  |  |  |
| `scf_os_thr` | Real | -0.01 |  |  | value<0 |  |
| `scf_os_ndim` | Integer | mixing_ndim |  |  |  | yes |
| `sc_os_ndim` | Integer | 5 |  |  |  |  |
| `lspinorb` | Boolean | False |  |  |  |  |
| `noncolin` | Boolean | False |  |  |  |  |
| `soc_lambda` | Real | 1.0 |  | lspinorb==true |  |  |
| `dfthalf_type` | Integer | 0 |  |  | [0, 1] |  |

### Electronic structure (SDFT)

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `method_sto` | Integer | 2 |  | esolver_type==sdft | [1, 2] |  |
| `nbands_sto` | Integer or string | 256 |  | esolver_type==sdft |  |  |
| `nche_sto` | Integer | 100 |  | esolver_type==sdft |  |  |
| `emin_sto` | Real | 0.0 | Ry | esolver_type==sdft |  |  |
| `emax_sto` | Real | 0.0 | Ry | esolver_type==sdft |  |  |
| `seed_sto` | Integer | 0 |  | esolver_type==sdft |  |  |
| `initsto_ecut` | Real | 0.0 | Ry | esolver_type==sdft |  |  |
| `initsto_freq` | Integer | 0 |  | esolver_type==sdft |  |  |
| `npart_sto` | Integer | 1 |  | esolver_type==sdft and ((method_sto==2 and out_dos==1) or (basis_type==pw and cal_cond==true)) |  |  |

### Exact Exchange (Common)

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `exx_fock_alpha` | Real | see hybrid_func_params |  |  |  | yes |
| `exx_erfc_alpha` | Real | see hybrid_func_params |  |  |  | yes |
| `exx_erfc_omega` | Real | see hybrid_func_params |  |  |  | yes |
| `exx_separate_loop` | Boolean | True |  |  |  | yes |
| `exx_hybrid_step` | Integer | 100 |  | exx_separate_loop==1 |  |  |
| `exx_mixing_beta` | Real | 1.0 |  | exx_separate_loop==1 |  |  |
| `exx_singularity_correction` | String | default |  |  |  | yes |

### Exact Exchange (LCAO in PW)

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `exx_fock_lambda` | Real | 0.3 |  | basis_type==lcao_in_pw |  | yes |

### Exact Exchange (LCAO)

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `exx_pca_threshold` | Real | 1E-4 |  |  |  |  |
| `exx_c_threshold` | Real | 1E-4 |  |  |  |  |
| `exx_cs_inv_thr` | Real | -1 |  |  |  |  |
| `exx_v_threshold` | Real | 1E-1 |  |  |  |  |
| `exx_dm_threshold` | Real | 1E-4 |  |  |  |  |
| `exx_c_grad_threshold` | Real | 1E-4 |  |  |  |  |
| `exx_v_grad_threshold` | Real | 1E-1 |  |  |  |  |
| `exx_c_grad_r_threshold` | Real | 1E-4 |  |  |  |  |
| `exx_v_grad_r_threshold` | Real | 1E-1 |  |  |  |  |
| `exx_ccp_rmesh_times` | String |  |  |  |  | yes |
| `exx_opt_orb_lmax` | Integer | 0 |  | calculation==gen_opt_abfs |  |  |
| `exx_opt_orb_ecut` | Real | 0 | Ry | calculation==gen_opt_abfs |  |  |
| `exx_opt_orb_tolerence` | Real | 1E-12 |  | calculation==gen_opt_abfs |  |  |
| `exx_real_number` | String | depends on the gamma_only option |  |  |  | yes |
| `rpa_ccp_rmesh_times` | Real | 10 |  |  |  |  |
| `rpa_cut_coulomb` | String | hard |  |  | ['hard', 'log_erfc'] |  |
| `rpa_cut_radius` | String | legacy |  |  | ['legacy', 'inscribed'] |  |
| `rpa_cut_width` | Real | 1.091868692359 |  |  | value>1 and value<=1.25 |  |
| `exx_symmetry_realspace` | Boolean | True |  | symmetry==1 and (dft_functional in [hse, hf, pbe0, scan0] or (basis_type==lcao and rpa==true)) |  | yes |
| `out_ri_cv` | Boolean | false |  |  |  |  |

### Exact Exchange (PW)

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `exxace` | Boolean | True |  | exx_separate_loop==true |  |  |
| `exx_gamma_extra` | Boolean | False for PW limits; True otherwise |  |  |  |  |
| `ecutexx` | Real | same as ecutrho | Ry |  | value>=0 |  |
| `exx_batch_size` | Integer | 0 |  |  | value>=0 |  |
| `exx_thr_type` | String | density |  |  |  |  |
| `exx_ene_thr` | Real | 1e-5 | Ry | exx_thr_type==energy | value>0 |  |

### Gate field (compensating charge)

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `gate_flag` | Boolean | false |  |  |  |  |
| `zgate` | Real | 0.5 | Unit cell size |  |  |  |
| `block` | Boolean | false |  |  |  |  |
| `block_down` | Real | 0.45 | Unit cell size |  |  |  |
| `block_up` | Real | 0.55 | Unit cell size |  |  |  |
| `block_height` | Real | 0.1 | Rydberg |  |  |  |

### Geometry relaxation

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `relax_method` | String | cg |  |  | ['cg', 'cg_trad', 'bfgs', 'bfgs_trad', 'sd', 'cg_bfgs', 'lbfgs'] |  |
| `relax_scale_force` | Real | 0.5 |  | relax_method==cg |  |  |
| `relax_nmax` | Integer | 1 for SCF, 50 for relax and cell-relax calcualtions |  |  |  | yes |
| `relax_cg_thr` | Real | 0.5 | eV/Angstrom | relax_method==cg_bfgs |  |  |
| `force_thr` | Real | 0.001 | Ry/Bohr (25.7112 eV/Angstrom) |  | value>=0 | yes |
| `force_thr_ev` | Real | 0.0257112 | eV/Angstrom (0.03889 Ry/Bohr) |  | value>=0 |  |
| `force_zero_out` | Real | 0.0 | eV/Angstrom |  |  |  |
| `relax_bfgs_w1` | Real | 0.01 |  | relax_method in [bfgs, bfgs_trad, cg_bfgs] |  |  |
| `relax_bfgs_w2` | Real | 0.5 |  | relax_method in [bfgs, bfgs_trad, cg_bfgs] |  |  |
| `relax_bfgs_rmax` | Real | 0.8 | Bohr | relax_method in [bfgs, bfgs_trad, cg_bfgs] |  |  |
| `relax_bfgs_rmin` | Real | 1e-5 | Bohr | relax_method==bfgs_trad |  |  |
| `relax_bfgs_init` | Real | 0.5 | Bohr | relax_method in [bfgs, bfgs_trad, cg_bfgs] |  |  |
| `stress_thr` | Real | 0.5 | kbar |  |  |  |
| `press1` | Real | 0 | kbar |  |  |  |
| `press2` | Real | 0 | kbar |  |  |  |
| `press3` | Real | 0 | kbar |  |  |  |
| `fixed_axes` | String | None |  | calculation==cell-relax | When fixed_axes in [shape, volume]: require relax_method==cg |  |
| `fixed_ibrav` | Boolean | False |  | relax_method==cg and latname!=none | When fixed_ibrav==true: require relax_method==cg and latname!=none |  |
| `fixed_atoms` | Boolean | False |  |  | When fixed_atoms==true: require calculation!=relax |  |

### Implicit solvation model

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `imp_sol` | Integer | 0 |  |  |  |  |
| `eb_k` | Real | 80 |  | imp_sol==1 |  |  |
| `tau` | Real | 1.0798e-05 |  |  |  |  |
| `sigma_k` | Real | 0.6 |  |  |  |  |
| `nc_k` | Real | 0.00037 |  |  |  |  |
| `sccs_preset` | String | custom |  | imp_sol==2 |  |  |
| `sccs_epsilon` | Real | 1.0 |  | imp_sol==2 |  |  |
| `sccs_rho_min` | Real | 1e-4 | e/bohr^3 | imp_sol==2 |  |  |
| `sccs_rho_max` | Real | 5e-3 | e/bohr^3 | imp_sol==2 |  |  |
| `sccs_gamma` | Real | 0.0 | dyn/cm | imp_sol==2 |  |  |
| `sccs_pressure` | Real | 0.0 | GPa | imp_sol==2 |  |  |
| `sccs_maxiter` | Integer | 200 |  | imp_sol==2 |  |  |
| `sccs_tol_rms` | Real | 1e-10 | e/bohr^3 | imp_sol==2 |  |  |
| `sccs_tol_max` | Real | 1e-8 | e/bohr^3 | imp_sol==2 |  |  |
| `sccs_surface_eta` | Real | 1e-8 | bohr^-1 | imp_sol==2 |  |  |
| `sccs_lowpass_p1` | Real | -1 |  | imp_sol==2 |  |  |
| `sccs_lowpass_p2` | Real | -1 |  | imp_sol==2 |  |  |
| `sccs_solvent_mode` | String | electronic |  | imp_sol==2 |  |  |
| `sccs_corespread` | Vector of Real | 0.5 | bohr | imp_sol==2 |  |  |
| `sccs_solvent_radius` | Real | 0.0 | bohr | imp_sol==2 |  |  |
| `sccs_radial_scale` | Real | 2.0 |  | imp_sol==2 |  |  |
| `sccs_radial_spread` | Real | 0.5 | bohr | imp_sol==2 |  |  |
| `sccs_filling_thr` | Real | 0.825 |  | imp_sol==2 |  |  |
| `sccs_filling_spread` | Real | 0.02 |  | imp_sol==2 |  |  |
| `sccs_start_drho` | Real | 0.0 |  | imp_sol==2 |  |  |
| `sccs_start_nmax` | Integer | 30 |  | imp_sol==2 |  |  |
| `sccs_debug` | Integer | 0 |  |  |  |  |

### Input files

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `stru_file` | String | STRU |  |  |  |  |
| `kpoint_file` | String | KPT |  |  |  | yes |
| `pseudo_dir` | String | "" |  |  |  |  |
| `orbital_dir` | String | "" |  |  |  |  |
| `read_file_dir` | String | OUT.$suffix |  |  |  | yes |
| `restart_load` | Boolean | False |  | basis_type==lcao |  |  |
| `spillage_outdir` | String | "./" |  | basis_type==pw |  |  |

### Linear Response TDDFT

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `xc_kernel` | String | LDA |  |  |  |  |
| `lr_init_xc_kernel` | Vector of String (>=1 values) | "default" |  |  |  | yes |
| `lr_solver` | String | dav |  |  |  |  |
| `lr_thr` | Real | 1e-2 |  |  |  |  |
| `nocc` | Integer | all occupied orbitals |  |  |  |  |
| `nvirt` | Integer | 1 |  |  |  |  |
| `lr_nstates` | Integer | 0 |  |  |  |  |
| `lr_target_state` | Integer | 0 |  |  |  |  |
| `lr_degen_thr` | Real | 0 | Ry |  |  |  |
| `lr_degen_mode` | String | state |  |  |  |  |
| `lr_grad_solver` | String | cg |  |  |  |  |
| `lr_target_spin` | String | singlet |  |  |  |  |
| `lr_unrestricted` | Boolean | False |  |  |  |  |
| `abs_wavelen_range` | Real Real | 0.0 0.0 | nm |  |  |  |
| `out_wfc_lr` | Boolean | False |  |  |  |  |
| `abs_gauge` | String | velocity |  |  |  |  |
| `abs_broadening` | Real | 0.01 |  |  |  |  |
| `plot_istate` | Integer | 0 |  |  |  |  |
| `exciton_plot_type` | String | average |  |  |  |  |
| `exciton_plot_format` | String | cube |  | lr_solver==plot |  |  |
| `exciton_fixed_coordinate` | Vector of Real (6 values) | 0.0 0.0 0.0 0.0 0.0 0.0 |  |  |  |  |
| `exciton_slice_plane` | String | ab |  |  |  |  |
| `exciton_slice_pos` | Real | 0.0 |  |  |  |  |
| `exciton_slice_npoints` | Integer | 200 |  |  |  |  |
| `exciton_slice_range` | Vector of Integer (4 values) | -1 2 -1 2 | primitive cells | lr_solver==plot and exciton_plot_format in [slice, both] |  |  |
| `ri_hartree_benchmark` | String | none |  |  |  |  |
| `aims_nbasis` | A number(ntype) of Integers | {} (empty list, where ABACUS use its own basis set size) |  | ri_hartree_benchmark==aims |  |  |

### ML-KEDF: machine learning based kinetic energy density functional for OFDFT

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `of_ml_gene_data` | Boolean | False |  | esolver_type==ksdft and basis_type==pw |  |  |
| `of_ml_device` | String | cpu |  | esolver_type==ofdft |  |  |
| `of_ml_feg` | Integer | 0 |  | esolver_type==ofdft |  |  |
| `of_ml_nkernel` | Integer | 1 |  | esolver_type==ofdft |  | yes |
| `of_ml_kernel` | Vector of Integer | 1 |  | esolver_type==ofdft |  |  |
| `of_ml_kernel_scaling` | Vector of Real | 1.0 |  | esolver_type==ofdft |  |  |
| `of_ml_yukawa_alpha` | Vector of Real | 1.0 |  | esolver_type==ofdft |  |  |
| `of_ml_kernel_file` | Vector of String | none |  | esolver_type==ofdft |  |  |
| `of_ml_gamma` | Boolean | False |  | esolver_type==ofdft |  |  |
| `of_ml_p` | Boolean | False |  | esolver_type==ofdft |  |  |
| `of_ml_q` | Boolean | False |  | esolver_type==ofdft |  |  |
| `of_ml_tanhp` | Boolean | False |  | esolver_type==ofdft |  |  |
| `of_ml_tanhq` | Boolean | False |  | esolver_type==ofdft |  |  |
| `of_ml_chi_p` | Real | 1.0 |  | esolver_type==ofdft |  |  |
| `of_ml_chi_q` | Real | 1.0 |  | esolver_type==ofdft |  |  |
| `of_ml_gammanl` | Vector of Integer | 0 |  | esolver_type==ofdft |  |  |
| `of_ml_pnl` | Vector of Integer | 0 |  | esolver_type==ofdft |  |  |
| `of_ml_qnl` | Vector of Integer | 0 |  | esolver_type==ofdft |  |  |
| `of_ml_xi` | Vector of Integer | 0 |  | esolver_type==ofdft |  |  |
| `of_ml_tanhxi` | Vector of Integer | 0 |  | esolver_type==ofdft |  |  |
| `of_ml_tanhxi_nl` | Vector of Integer | 0 |  | esolver_type==ofdft |  |  |
| `of_ml_tanh_pnl` | Vector of Integer | 0 |  | esolver_type==ofdft |  |  |
| `of_ml_tanh_qnl` | Vector of Integer | 0 |  | esolver_type==ofdft |  |  |
| `of_ml_tanhp_nl` | Vector of Integer | 0 |  | esolver_type==ofdft |  |  |
| `of_ml_tanhq_nl` | Vector of Integer | 0 |  | esolver_type==ofdft |  |  |
| `of_ml_chi_xi` | Vector of Real | 1.0 |  | esolver_type==ofdft |  |  |
| `of_ml_chi_pnl` | Vector of Real | 1.0 |  | esolver_type==ofdft |  |  |
| `of_ml_chi_qnl` | Vector of Real | 1.0 |  | esolver_type==ofdft |  |  |
| `of_ml_local_test` | Boolean | False |  | esolver_type==ofdft |  |  |
| `ml_exx` | Boolean | False |  |  |  |  |

### Molecular dynamics

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `md_type` | String | nvt |  |  | ['fire', 'nve', 'nvt', 'npt', 'langevin', 'msst'] |  |
| `md_nstep` | Integer | 10 |  |  |  | yes |
| `md_dt` | Real | 1.0 | fs |  |  | yes |
| `md_thermostat` | String | nhc |  |  | ['nhc', 'anderson', 'berendsen', 'rescaling', 'rescale_v', 'csvr'] |  |
| `md_tfirst` | Real | No default | K |  |  |  |
| `md_tlast` | Real | No default | K |  |  | yes |
| `md_prec_level` | Integer | 0 |  |  |  | yes |
| `md_restart` | Boolean | False |  |  |  |  |
| `md_restartfreq` | Integer | 5 |  |  |  |  |
| `md_dumpfreq` | Integer | 1 |  |  |  |  |
| `md_thermo_freq` | Integer | 1 |  |  |  |  |
| `md_neighbor_skin` | Real | 0.0 | Angstrom |  |  |  |
| `dump_force` | Boolean | True |  |  |  |  |
| `dump_vel` | Boolean | True |  |  |  |  |
| `dump_virial` | Boolean | True |  |  |  |  |
| `md_seed` | Integer | -1 |  |  |  |  |
| `md_tfreq` | Real | 1/40/md_dt |  |  |  | yes |
| `md_tchain` | Integer | 1 |  |  |  |  |
| `md_pmode` | String | iso |  |  |  |  |
| `ref_cell_factor` | Real | 1.0 |  |  |  | yes |
| `md_pcouple` | String | none |  |  | ['none', 'xyz', 'xy', 'xz', 'yz'] | yes |
| `md_pfirst` | Real | -1.0 | kbar |  |  |  |
| `md_plast` | Real | -1.0 | kbar |  |  | yes |
| `md_pfreq` | Real | 1/400/md_dt |  |  |  | yes |
| `md_pchain` | Integer | 1 |  |  |  |  |
| `lj_rule` | Integer | 2 |  |  |  |  |
| `lj_eshift` | Boolean | False |  |  |  |  |
| `lj_rcut` | Real | No default | Angstrom |  |  |  |
| `lj_epsilon` | Real | No default | eV |  |  |  |
| `lj_sigma` | Real | No default | Angstrom |  |  |  |
| `pot_file` | String | graph.pb |  |  |  |  |
| `snap_param_file` | String | snap.param |  | esolver_type==snap |  |  |
| `dp_rescaling` | Real | 1.0 |  | esolver_type==dp |  |  |
| `dp_fparam` | Real | {} |  | esolver_type==dp |  |  |
| `dp_aparam` | Real | {} |  | esolver_type==dp |  |  |
| `msst_direction` | Integer | 2 |  |  |  |  |
| `msst_vel` | Real | 0.0 | Angstrom/fs |  |  |  |
| `msst_vis` | Real | 0.0 | g/(mol*Angstrom*fs) |  |  |  |
| `msst_tscale` | Real | 0.01 |  |  |  |  |
| `msst_qmass` | Real | No default |  |  | value>0 |  |
| `md_damp` | Real | 1.0 | fs |  |  |  |
| `md_csvr_tau` | Real | 100.0 | fs | md_thermostat==csvr |  |  |
| `md_tolerance` | Real | 100.0 | K |  |  |  |
| `md_nraise` | Integer | 1 |  |  |  |  |
| `cal_syns` | Boolean \[Integer\](optional) | False |  |  |  |  |
| `dmax` | Real | 0.01 | bohr |  |  |  |
| `plumed` | Boolean | False |  |  |  |  |
| `plumed_file` | String | plumed.dat |  | plumed==true |  |  |

### NAOs

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `bessel_nao_ecut` | String | ecutwfc |  |  |  | yes |
| `bessel_nao_tolerence` | Real | 1.0e-12 |  |  |  |  |
| `bessel_nao_rcut` | Vector of Real (N values) | 6.0 |  |  |  |  |
| `bessel_nao_smooth` | Boolean | True |  |  |  |  |
| `bessel_nao_sigma` | Real | 0.1 |  |  |  |  |

### Numerical atomic orbitals related variables

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `lmaxmax` | Integer | 2. |  |  |  |  |
| `lcao_ecut` | Real | ecutwfc |  |  |  | yes |
| `lcao_dk` | Real | 0.01 | Bohr |  |  |  |
| `lcao_dr` | Real | 0.01 | Bohr |  |  |  |
| `lcao_rmax` | Real | 30 | Bohr |  |  |  |
| `search_radius` | Real | -1 | Bohr |  |  |  |
| `bx` | Integer | 0 |  |  | value>=0 and value<=10 | yes |
| `by` | Integer | 0 |  |  | value>=0 and value<=10 |  |
| `bz` | Integer | 0 |  |  | value>=0 and value<=10 |  |
| `elpa_num_thread` | Integer | -1 |  |  |  |  |
| `num_stream` | Integer | 4 |  |  |  |  |

### OFDFT: orbital free density functional theory

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `of_kinetic` | String | wt |  | esolver_type==ofdft |  | yes |
| `of_method` | String | tn |  | esolver_type==ofdft |  |  |
| `of_conv` | String | energy |  | esolver_type==ofdft |  |  |
| `of_tole` | Real | 2e-6 | Ry | esolver_type==ofdft |  |  |
| `of_tolp` | Real | 1e-5 | Ry | esolver_type==ofdft |  |  |
| `of_tf_weight` | Real | 1.0 |  | esolver_type==ofdft and of_kinetic in [tf, tf+, wt, ext-wt, xwm] |  |  |
| `of_vw_weight` | Real | 1.0 |  | esolver_type==ofdft and of_kinetic in [vw, tf+, wt, ext-wt, lkt, xwm] |  |  |
| `of_wt_alpha` | Real |  |  | esolver_type==ofdft and of_kinetic in [wt, ext-wt] |  |  |
| `of_wt_beta` | Real |  |  | esolver_type==ofdft and of_kinetic in [wt, ext-wt] |  |  |
| `of_extwt_kappa` | Real | 1.0 / (2.0 * std::pow(4./3., 1./3.) - 1.0) |  | esolver_type==ofdft and of_kinetic==ext-wt |  |  |
| `of_wt_rho0` | Real | 0.0 | Bohr^-3 | esolver_type==ofdft and of_kinetic==wt |  |  |
| `of_hold_rho0` | Boolean | False |  | esolver_type==ofdft and of_kinetic==wt |  | yes |
| `of_lkt_a` | Real | 1.3 |  | esolver_type==ofdft and of_kinetic==lkt |  |  |
| `of_xwm_rho_ref` | Real | 0.0 |  | esolver_type==ofdft and of_kinetic==xwm |  |  |
| `of_xwm_kappa` | Real | 0.0 |  | esolver_type==ofdft and of_kinetic==xwm |  |  |
| `of_read_kernel` | Boolean | False |  | esolver_type==ofdft and of_kinetic==wt |  | yes |
| `of_kernel_file` | String | WTkernel.txt |  | esolver_type==ofdft and of_kinetic==wt and of_read_kernel==true |  |  |
| `of_full_pw` | Boolean | True |  | esolver_type==ofdft |  |  |
| `of_full_pw_dim` | Integer | 0 |  | esolver_type==ofdft and of_full_pw==true |  | yes |

### Output information

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `out_freq_ion` | Integer | 0 |  |  |  | yes |
| `out_freq_elec` | Integer | scf_nmax |  |  |  | yes |
| `out_chg` | Integer \[Integer\](optional) | 0 3 |  |  |  | yes |
| `out_occ_mat` | Boolean | True |  |  |  |  |
| `out_pot` | Integer \[Integer\](optional) | 0 |  |  |  | yes |
| `out_sol` | Integer \[Integer\](optional) | 0 |  |  |  |  |
| `out_dmk` | Boolean \[Integer\](optional) | False |  | basis_type==lcao |  | yes |
| `out_dmr` | Boolean \[Integer\](optional) | False |  | basis_type==lcao and gamma_only==0 |  | yes |
| `out_wfc_pw` | Integer | 0 |  | basis_type==pw and esolver_type==ksdft | [0, 1, 2] When out_wfc_pw!=0: require basis_type==pw |  |
| `out_wfc_lcao` | Integer | 0 |  | basis_type==lcao | [0, 1, 2] When out_wfc_lcao!=0: require basis_type==lcao | yes |
| `out_dos` | Integer | 0 |  |  |  | yes |
| `out_ldos` | Integer \[Integer\](optional) | 0 |  |  |  |  |
| `out_band` | Boolean \[Integer\](optional) | False |  |  |  | yes |
| `out_proj_band` | Boolean | False |  |  |  | yes |
| `out_stru` | Integer | 1 |  |  |  | yes |
| `out_level` | String | ie |  |  |  | yes |
| `out_hsk` | Integer \[Integer\](optional) | 0 8 | Ry | basis_type==lcao |  |  |
| `out_mat_hs` | Boolean \[Integer\](optional) | False 8 | Ry | basis_type==lcao |  |  |
| `out_hsr` | Integer \[Integer\](optional) | 0 8 | Ry | basis_type==lcao |  |  |
| `out_mat_hs2` | Boolean \[Integer\](optional) | False 8 | Ry | basis_type==lcao |  |  |
| `out_mat_tk` | Boolean \[Integer\](optional) | False [8] | Ry | basis_type==lcao |  |  |
| `out_mat_r` | Boolean \[Integer\](optional) | False 8 | Bohr | basis_type==lcao and gamma_only==0 |  |  |
| `out_mat_t` | Boolean \[Integer\](optional) | False 8 | Ry | basis_type==lcao and gamma_only==0 |  |  |
| `out_mat_dh` | Integer | 0 8 | Ry/Bohr | basis_type==lcao and gamma_only==0 |  |  |
| `out_mat_dh_t` | Integer | 0 8 | Ry/Bohr |  |  |  |
| `out_mat_dh_vl` | Integer | 0 8 | Ry/Bohr |  |  |  |
| `out_mat_dh_vnl` | Integer | 0 8 | Ry/Bohr |  |  |  |
| `out_mat_dh_vh` | Integer | 0 8 | Ry/Bohr |  |  |  |
| `out_mat_dh_vxc` | Integer | 0 8 | Ry/Bohr |  |  |  |
| `out_mat_h_t` | Integer | 0 8 | Ry |  |  |  |
| `out_mat_vnlk` | Integer | 0 8 | Ry |  |  |  |
| `out_mat_h_vnl` | Integer | 0 8 | Ry |  |  |  |
| `out_mat_vlk` | Integer | 0 8 | Ry |  |  |  |
| `out_mat_h_vl` | Integer | 0 8 | Ry |  |  |  |
| `out_mat_vhk` | Integer | 0 8 | Ry |  |  |  |
| `out_mat_h_vh` | Integer | 0 8 | Ry |  |  |  |
| `out_mat_vxck` | Integer | 0 8 | Ry |  |  |  |
| `out_mat_h_vxc` | Integer | 0 8 | Ry |  |  |  |
| `out_mat_exxk` | Integer | 0 8 | Ry |  |  |  |
| `out_mat_h_exx` | Integer | 0 8 | Ry |  |  |  |
| `out_mat_ds` | Boolean \[Integer\](optional) | False 8 | Ry/Bohr | basis_type==lcao and gamma_only==0 |  |  |
| `out_mat_xc` | Boolean | False | Ry | basis_type in [lcao, lcao_in_pw] |  |  |
| `out_mat_xc2` | Boolean \[Integer\](optional) | False 8 | Ry | basis_type==lcao |  |  |
| `out_mat_l` | Boolean \[Integer\](optional) | False 8 |  | basis_type==lcao |  |  |
| `out_xc_r` | Integer \[Integer\](optional) | -1 3 |  |  |  |  |
| `out_eband` | Boolean | False |  | basis_type==lcao |  |  |
| `out_eband_terms` | Boolean | False |  | basis_type==lcao |  |  |
| `out_hr_npz` | Boolean | False | Ry | basis_type==lcao and gamma_only==0 |  |  |
| `out_hsr_npz` | Boolean | False | Ry | basis_type==lcao |  |  |
| `out_dm_npz` | Boolean | False |  | basis_type==lcao and gamma_only==0 |  |  |
| `out_mul` | Boolean | False |  | basis_type==lcao |  |  |
| `out_app_flag` | Integer | 0 |  |  |  |  |
| `out_ndigits` | Integer | 8 |  | basis_type==lcao and out_hsk==1 |  |  |
| `out_element_info` | Boolean | False |  |  |  |  |
| `restart_save` | Boolean | False |  | basis_type==lcao |  |  |
| `rpa` | Boolean | False |  | basis_type==lcao |  |  |
| `rpa_out_vel` | Boolean | False | eV * A | basis_type==lcao |  |  |
| `rpa_outdir` | String | "OUT.librpa" |  | basis_type==lcao |  | yes |
| `out_librpa_ver` | Integer | 0 |  | basis_type==lcao | [0, 1] |  |
| `out_pchg` | String | none |  | basis_type==pw or (basis_type==lcao and calculation==get_pchg) |  |  |
| `out_wfc_norm` | String | none |  | basis_type==pw or (basis_type==lcao and calculation==get_wf) |  |  |
| `out_wfc_re_im` | String | none |  | basis_type==pw or (basis_type==lcao and calculation==get_wf) |  |  |
| `if_separate_k` | Boolean | false |  | (basis_type==pw and out_pchg!=none) or (basis_type==lcao and calculation==get_pchg and gamma_only==0) |  |  |
| `out_elf` | Integer \[Integer\](optional) | 0 3 |  | esolver_type in [ksdft, ofdft] |  |  |
| `out_spillage` | Integer | 0 |  | esolver_type==ksdft and basis_type==pw |  |  |
| `out_alllog` | Boolean | False |  |  |  |  |

### PEXSI

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `pexsi_npole` | Integer | 40 |  |  |  |  |
| `pexsi_inertia` | Boolean | True |  |  |  |  |
| `pexsi_nmax` | Integer | 80 |  |  |  |  |
| `pexsi_comm` | Boolean | True |  |  |  |  |
| `pexsi_storage` | Boolean | True |  |  |  |  |
| `pexsi_ordering` | Integer | 0 |  |  |  |  |
| `pexsi_row_ordering` | Integer | 1 |  |  |  |  |
| `pexsi_nproc` | Integer | 1 |  |  |  |  |
| `pexsi_symm` | Boolean | True |  |  |  |  |
| `pexsi_trans` | Boolean | False |  |  |  |  |
| `pexsi_method` | Integer | 1 |  |  |  |  |
| `pexsi_nproc_pole` | Integer | 1 |  |  |  |  |
| `pexsi_temp` | Real | 0.015 |  |  |  |  |
| `pexsi_gap` | Real | 0 |  |  |  |  |
| `pexsi_delta_e` | Real | 20 |  |  |  |  |
| `pexsi_mu_lower` | Real | -10 |  |  |  |  |
| `pexsi_mu_upper` | Real | 10 |  |  |  |  |
| `pexsi_mu` | Real | 0 |  |  |  |  |
| `pexsi_mu_thr` | Real | 0.05 |  |  |  |  |
| `pexsi_mu_expand` | Real | 0.3 |  |  |  |  |
| `pexsi_mu_guard` | Real | 0.2 |  |  |  |  |
| `pexsi_elec_thr` | Real | 0.001 |  |  |  |  |
| `pexsi_zero_thr` | Real | 1e-10 |  |  |  |  |

### Plane wave related variables

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `ecutwfc` | Real | 50 for PW basis, 100 for LCAO basis | Ry |  | value>0 | yes |
| `ecutrho` | Real | 4*ecutwfc | Ry |  | value>0 | yes |
| `nx` | Integer | 0 |  |  |  |  |
| `ny` | Integer | 0 |  |  |  |  |
| `nz` | Integer | 0 |  |  |  |  |
| `ndx` | Integer | 0 |  |  |  | yes |
| `ndy` | Integer | 0 |  |  |  | yes |
| `ndz` | Integer | 0 |  |  |  | yes |
| `pw_seed` | Integer | 0 |  | basis_type==pw |  |  |
| `diag_subspace` | Integer | 0 |  | basis_type==pw and ks_solver==dav_subspace | [0, 1, 2] |  |
| `erf_ecut` | Real | 0.0 | Ry |  |  |  |
| `fft_mode` | Integer | 0 |  |  | [0, 1, 2, 3] |  |
| `erf_height` | Real | 0.0 | Ry |  |  |  |
| `erf_sigma` | Real | 0.1 | Ry |  |  |  |
| `pw_diag_thr` | Real | 0.01 |  |  |  | yes |
| `diago_smooth_ethr` | Boolean | false |  |  |  |  |
| `use_k_continuity` | Boolean | false |  | basis_type==pw | When use_k_continuity==true: require basis_type==pw and calculation!=nscf and kpar==1 and nspin!=2 and esolver_type!=sdft |  |
| `pw_diag_nmax` | Integer | 50 |  | basis_type==pw and ks_solver in [cg, dav, dav_subspace, bpcg] |  |  |
| `pw_diag_ndim` | Integer | 4 |  |  |  |  |
| `diago_cg_prec` | Integer | 1 |  |  |  |  |

### Quasiatomic Orbital (QO) analysis

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `qo_switch` | Boolean | False |  |  |  |  |
| `qo_basis` | String | szv |  |  |  |  |
| `qo_strategy` | Vector of String (1 or n values where n is the number of atomic types) | for hydrogen: energy-valence, for pswfc and szv: all |  |  |  | yes |
| `qo_screening_coeff` | Vector of Real (n values where n is the number of atomic types; 1 value allowed for qo_basis=pswfc) | 0.1 | Bohr^-1 |  |  | yes |
| `qo_thr` | Real | 1.0e-6 |  |  |  |  |

### Real-Time TDDFT (Common)

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `td_scf_nmax` | Integer | 100 |  | esolver_type==tddft and basis_type in [pw, lcao] | value>=2 |  |
| `estep_per_md` | Integer | 1 |  |  | value>0 |  |
| `td_dt` | Real | md_dt / estep_per_md | fs |  | value>0 | yes |
| `td_print_eij` | Real | -1 | Ry | basis_type in [pw, lcao] and esolver_type==tddft |  |  |
| `td_propagator` | Integer | 0 |  | (basis_type==pw or basis_type==lcao) and esolver_type==tddft | When basis_type==pw and esolver_type==tddft: require td_propagator in [0, 2] |  |
| `td_vext` | Boolean | False |  |  |  |  |
| `td_vext_dire` | Vector of Integer | 1 |  |  |  |  |
| `td_stype` | Integer | 0 |  |  | When init_vecpot==false: require td_stype in [0, 1, 2] |  |
| `td_ttype` | Vector of Integer | 0 |  |  |  |  |
| `td_tstart` | Integer | 1 |  |  |  |  |
| `td_tend` | Integer | 1000 |  |  |  |  |
| `td_lcut1` | Real | 0.05 |  |  |  |  |
| `td_lcut2` | Real | 0.95 |  |  |  |  |
| `td_gauss_freq` | Vector of Real | 22.13 | 1/fs | td_ttype contains 0 |  |  |
| `td_gauss_phase` | Vector of Real | 0.0 | rad | td_ttype contains 0 |  |  |
| `td_gauss_sigma` | Vector of Real | 30.0 | fs | td_ttype contains 0 |  |  |
| `td_gauss_t0` | Vector of Real | 100 |  | td_ttype contains 0 |  |  |
| `td_gauss_amp` | Vector of Real | 0.25 | V/Angstrom | td_ttype contains 0 |  |  |
| `td_trape_freq` | Vector of Real | 1.60 | 1/fs | td_ttype contains 1 |  |  |
| `td_trape_phase` | Vector of Real | 0.0 | rad | td_ttype contains 1 |  |  |
| `td_trape_t1` | Vector of Real | 1875 |  | td_ttype contains 1 |  |  |
| `td_trape_t2` | Vector of Real | 5625 |  | td_ttype contains 1 |  |  |
| `td_trape_t3` | Vector of Real | 7500 |  | td_ttype contains 1 |  |  |
| `td_trape_amp` | Vector of Real | 2.74 | V/Angstrom | td_ttype contains 1 |  |  |
| `td_trigo_freq1` | Vector of Real | 1.164656 | 1/fs | td_ttype contains 2 |  |  |
| `td_trigo_freq2` | Vector of Real | 0.029116 | 1/fs | td_ttype contains 2 |  |  |
| `td_trigo_phase1` | Vector of Real | 0.0 | rad | td_ttype contains 2 |  |  |
| `td_trigo_phase2` | Vector of Real | 0.0 | rad | td_ttype contains 2 |  |  |
| `td_trigo_amp` | Vector of Real | 2.74 | V/Angstrom | td_ttype contains 2 |  |  |
| `td_heavi_t0` | Vector of Real | 100 |  | td_ttype contains 3 |  |  |
| `td_heavi_amp` | Vector of Real | 1.0 | V/Angstrom | td_ttype contains 3 |  |  |
| `td_supsine_amp` | Vector of Real | 0.27 | V/Angstrom | td_ttype contains 4 |  |  |
| `td_supsine_freq` | Vector of Real | 0.18737028625 | 1/fs | td_ttype contains 4 |  |  |
| `td_supsine_phase` | Vector of Real | 0.0 | rad | td_ttype contains 4 |  |  |
| `td_supsine_sigma` | Vector of Real | 0.75 |  | td_ttype contains 4 |  |  |
| `td_supsine_tstart` | Vector of String | default |  | td_ttype contains 4 |  | yes |
| `td_supsine_tend` | Vector of String | default |  | td_ttype contains 4 |  | yes |
| `init_vecpot` | Boolean | False |  | esolver_type==tddft and ((basis_type==pw and td_stype==1) or (basis_type==lcao and td_stype in [1, 2])) | When init_vecpot==true: require esolver_type==tddft and ((basis_type==pw and td_stype==1) or (basis_type==lcao and td_stype in [1, 2])) |  |
| `ocp` | Boolean | False |  |  |  |  |
| `ocp_set` | String | None |  |  |  |  |
| `out_freq_td` | Integer | 0 |  |  |  | yes |
| `out_dipole` | Boolean | False |  |  |  |  |
| `out_current` | Integer | 0 |  | basis_type in [pw, lcao] and esolver_type==tddft |  |  |
| `out_current_k` | Boolean | False |  | basis_type in [pw, lcao] and esolver_type==tddft and out_current>0 |  |  |
| `out_efield` | Boolean | False |  | esolver_type==tddft |  |  |
| `out_vecpot` | Boolean | False |  | esolver_type==tddft and ((basis_type==pw and td_stype==1) or (basis_type==lcao and td_stype in [1, 2])) |  |  |

### Real-Time TDDFT (LCAO)

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `td_edm` | Integer | 0 |  | basis_type==lcao and esolver_type==tddft |  |  |

### Real-Time TDDFT (PW)

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `td_orthonormal` | String | cholesky |  | basis_type==pw and esolver_type==tddft | ['cholesky', 'lowdin', 'newton_schulz', 'none'] |  |
| `td_out_stat` | Boolean | false |  | basis_type==pw and esolver_type==tddft |  |  |
| `td_max_halvings` | Integer | 0 |  | basis_type==pw and esolver_type==tddft | value>=0 and value<31 |  |
| `td_out_mag` | String | voronoi |  | basis_type==pw and esolver_type==tddft and nspin==4 | ['voronoi', 'onsite', 'none'] |  |
| `td_out_torque` | Boolean | false |  | basis_type==pw and esolver_type==tddft and nspin==4 |  |  |
| `td_out_spincur` | Boolean | false |  | basis_type==pw and esolver_type==tddft and nspin==4 |  |  |
| `lin_solver` | String | gmres |  | basis_type==pw and esolver_type==tddft and td_propagator==0 | ['bicgstab', 'cgs', 'gmres'] |  |
| `lin_precond` | String | kinetic_recycle |  | basis_type==pw and esolver_type==tddft and td_propagator==0 | ['kinetic', 'kinetic_recycle', 'kinetic_subspace', 'none'] |  |
| `lin_thr` | Real | 0 |  | basis_type==pw and esolver_type==tddft and td_propagator==0 | value>=0 |  |
| `lin_maxiter` | Integer | 500 |  | basis_type==pw and esolver_type==tddft and td_propagator==0 | value>0 |  |
| `lin_gmres_restart` | Integer | 20 |  | basis_type==pw and esolver_type==tddft and td_propagator==0 and lin_solver==gmres | value>0 |  |
| `td_cn_init` | Boolean | true |  | basis_type==pw and esolver_type==tddft and td_propagator==0 |  |  |
| `lin_reconstruct` | Boolean | true |  | basis_type==pw and esolver_type==tddft and td_propagator==0 and lin_solver==gmres |  |  |
| `td_exp_method` | String | lanczos |  | basis_type==pw and esolver_type==tddft and td_propagator==2 | ['lanczos', 'taylor'] |  |
| `td_exp_order` | Integer | 4 |  | basis_type==pw and esolver_type==tddft and td_propagator==2 and td_exp_method==taylor | value>=2 |  |
| `td_exp_thr` | Real | 0 |  | basis_type==pw and esolver_type==tddft and td_propagator==2 and td_exp_method==lanczos | value>=0 |  |
| `td_exp_krylov_dim` | Integer | 32 |  | basis_type==pw and esolver_type==tddft and td_propagator==2 and td_exp_method==lanczos | value>=2 |  |

### Reduced Density Matrix Functional Theory

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `rdmft` | Boolean | false |  |  |  |  |
| `rdmft_power_alpha` | Real | 0.656 |  |  | value>=0 and value<=1 | yes |

### Spin-Constrained DFT

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `sc_mag_switch` | Boolean | False |  |  | When sc_mag_switch==true: require nspin in [2, 4] |  |
| `decay_grad_switch` | Boolean | False |  |  |  |  |
| `sc_thr` | Real | 1.0e-6 | uB | sc_mag_switch==true | value>=0 |  |
| `nsc` | Integer | 100 |  | sc_mag_switch==true | value>0 |  |
| `nsc_min` | Integer | 2 |  | sc_mag_switch==true | value>0 |  |
| `alpha_trial` | Real | 0.01 | eV/uB^2 | sc_mag_switch==true | value>0 |  |
| `sccut` | Real | 3.0 | eV/uB | sc_mag_switch==true | value>0 |  |
| `sc_drop_thr` | Real | 1.0e-2 |  | sc_mag_switch==true |  |  |
| `sc_scf_thr` | Real | 1.0e-4 |  | sc_mag_switch==true | value>0 |  |
| `sc_direction_only` | Boolean | False |  | sc_mag_switch==true |  |  |
| `sc_lambda_strategy` | String | bfgs |  | sc_mag_switch==true | ['bfgs', 'bfgs2', 'linear_response', 'augmented_lagrangian', 'hybrid_delayed', 'linear_scan'] |  |
| `sc_scan_lambda_start` | Float | 0.0 | eV/uB | sc_mag_switch==true and sc_lambda_strategy==linear_scan |  |  |
| `sc_scan_lambda_end` | Float | 1.0 | eV/uB | sc_mag_switch==true and sc_lambda_strategy==linear_scan |  |  |
| `sc_scan_steps` | Integer | 20 |  | sc_mag_switch==true and sc_lambda_strategy==linear_scan |  |  |

### System variables

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `suffix` | String | ABACUS |  |  |  |  |
| `ntype` | Integer | 0 |  |  |  |  |
| `cell_replica` | Three Integers | 1 1 1 |  |  |  |  |
| `calculation` | String | scf |  |  | ['scf', 'relax', 'md', 'cell-relax', 'nscf', 'get_s', 'get_wf', 'get_pchg', 'gen_bessel', 'gen_opt_abfs', 'test_memory', 'test_neighbour'] When calculation in [get_pchg, get_wf]: require basis_type!=pw; When calculation==gen_bessel: require basis_type==pw |  |
| `socket_driver` | Boolean | False |  |  |  |  |
| `esolver_type` | String | ksdft |  |  |  |  |
| `symmetry` | String | 1 normally; 0 or -1 depending on the calculation and enabled features. |  |  | ['-1', '0', '1'] | yes |
| `symmetry_prec` | Real | 1.0e-6 | Bohr |  |  |  |
| `symmetry_autoclose` | Boolean | True |  | symmetry==1 |  |  |
| `cal_force` | Boolean | False |  |  |  | yes |
| `kpar` | Integer | 1 |  |  |  | yes |
| `bndpar` | Integer | 1 |  | (basis_type==pw and esolver_type==sdft) or (basis_type==pw and esolver_type==ksdft and ks_solver==bpcg) |  |  |
| `latname` | String | none |  |  |  |  |
| `assume_isolated` | String | none |  |  |  | yes |
| `pcc_2d_axis` | Integer | 2 |  | assume_isolated==pcc_2d | [0, 1, 2] |  |
| `init_wfc` | Vector of string | atomic |  |  |  | yes |
| `init_chg` | String | atomic |  |  |  | yes |
| `init_vel` | Boolean | False |  |  |  | yes |
| `mem_saver` | Integer | 0 |  | calculation==nscf and basis_type==pw | [0, 1] When calculation in [scf, relax]: require mem_saver==0 |  |
| `cal_stress` | Boolean | False |  |  |  | yes |
| `diago_proc` | Integer | 0 |  | basis_type==pw |  | yes |
| `nbspline` | Integer | -1 |  |  |  |  |
| `kspacing` | Vector of Real (1 or 3 values) | 0.0 |  |  |  |  |
| `koffset` | Vector of Real (3 values) | 0.0 0.0 0.0 |  |  |  |  |
| `kmesh_type` | String | gamma |  |  |  |  |
| `min_dist_coef` | Real | 0.2 |  |  |  |  |
| `device` | String | cpu |  |  | ['cpu', 'gpu'] | yes |
| `precision` | String | double |  | basis_type==pw | ['single', 'double'] When precision==single: require basis_type!=lcao |  |
| `gint_precision` | String | double |  | basis_type==lcao | ['single', 'double', 'mix'] When gint_precision!=double: require basis_type==lcao and nspin!=4 |  |
| `timer_enable_nvtx` | Boolean | False |  |  |  |  |
| `cell_factor` | Real | 1.2 |  |  |  | yes |
| `dm_to_rho` | Boolean | False |  |  |  |  |
| `chg_extrap` | String | default |  |  |  | yes |
| `nb2d` | Integer | 0 |  |  | value>=0 |  |
| `cal_symm_repr` | Integer \[Integer\](optional) | 1 3 |  |  |  |  |

### TDOFDFT: time dependent orbital free density functional theory

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `of_cd` | Boolean | False |  | esolver_type==tdofdft |  |  |
| `of_mcd_alpha` | Real | 1.0 |  | esolver_type==tdofdft |  |  |

### Variables useful for debugging

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `nurse` | Integer | 0 |  |  |  |  |
| `t_in_h` | Boolean | 1 |  |  |  |  |
| `vl_in_h` | Boolean | 1 |  |  |  |  |
| `vnl_in_h` | Boolean | 1 |  |  |  |  |
| `vh_in_h` | Boolean | 1 |  |  |  |  |
| `vion_in_h` | Boolean | 1 |  |  |  |  |
| `test_force` | Boolean | 0 |  |  |  |  |
| `test_stress` | Boolean | 0 |  |  |  |  |
| `test_skip_ewald` | Boolean | 0 |  |  |  |  |

### vdW correction

| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |
| --- | --- | --- | --- | --- | --- | --- |
| `vdw_method` | String | none |  |  | ['none', 'd2', 'd3_0', 'd3_bj', 'd4'] |  |
| `vdw_d4_xc` | String | default |  | vdw_method==d4 |  |  |
| `vdw_d4_model` | String | d4 |  | vdw_method==d4 | ['d4', 'd4s', 'D4', 'D4S'] |  |
| `vdw_s6` | String |  |  | vdw_method in [d2, d3_0, d3_bj] |  | yes |
| `vdw_s8` | String |  |  | vdw_method in [d3_0, d3_bj] |  | yes |
| `vdw_a1` | String |  |  | vdw_method in [d3_0, d3_bj] |  | yes |
| `vdw_a2` | String |  |  | vdw_method in [d3_0, d3_bj] |  | yes |
| `vdw_d` | Real | 20 |  | vdw_method==d2 |  |  |
| `vdw_abc` | Boolean | False |  | vdw_method in [d3_0, d3_bj] |  |  |
| `vdw_c6_file` | String | default |  | vdw_method==d2 |  |  |
| `vdw_c6_unit` | String | Jnm6/mol |  | vdw_method==d2 and vdw_c6_file!=default | ['Jnm6/mol', 'eVA6'] |  |
| `vdw_r0_file` | String | default |  | vdw_method==d2 |  |  |
| `vdw_r0_unit` | String | A |  | vdw_method==d2 and vdw_r0_file!=default | ['A', 'Bohr'] |  |
| `vdw_cutoff_type` | String | radius |  |  | ['radius', 'period'] When vdw_method in [d3_0, d3_bj, d4]: require vdw_cutoff_type==radius |  |
| `vdw_cutoff_radius` | String |  | defined by vdw_radius_unit (default Bohr) | vdw_cutoff_type==radius |  | yes |
| `vdw_radius_unit` | String | Bohr |  | vdw_cutoff_type==radius | ['A', 'Bohr'] |  |
| `vdw_cutoff_width2` | Real | 0.05 | Bohr | vdw_method in [d3_0, d3_bj, d4] | value>=0 |  |
| `vdw_cutoff_width3` | Real | 0.0 | Bohr | vdw_method in [d3_0, d3_bj, d4] | value>=0 |  |
| `vdw_cutoff_period` | Integer Integer Integer | 3 3 3 |  | vdw_cutoff_type==period |  |  |
| `vdw_cn_thr` | Real | 40 | defined by vdw_cn_thr_unit (default: Bohr) | vdw_method in [d3_0, d3_bj, d4] | value>0 | yes |
| `vdw_cn_thr_unit` | String | Bohr |  |  | ['A', 'Bohr'] |  |
