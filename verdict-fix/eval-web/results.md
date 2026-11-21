# Web test set - measurements (NOT accuracy claims)

Denominators locked first (`denominators-locked.json`). Labels = source captions. Hand-cut crops. Tiny n.

## 1. Paired look-closer flags (reference = genuine from the same photo / session)

| set | pairs | capture judged SAME | any look-closer flag |
|---|---|---|---|
| same_photo | 12 | 7/12 [32.0-80.7%] | 4/12 [13.8-60.9%] |
| same_photo_genuine_control | 4 | 2/4 [15.0-85.0%] | 0/4 [0.0-49.0%] |
| same_session_not_same_photo | 6 | 5/6 [43.6-97.0%] | 1/6 [3.0-56.4%] |

Same-photo G->F: a flag = catch. Genuine controls (two real copies in one photo): a flag = false flag.

| pair | ref | cand | cand label | capture same? | flags | dL cand-ref |
|---|---|---|---|---|---|---|
| SP01 | ef17741_3270_L | ef17741_3270_R | FAKE | yes | softer_small_print | -49.2 |
| SP02 | ef17741_3275_L | ef17741_3275_R | FAKE | yes | - | 0.18 |
| SP03 | ef17741_3277_L | ef17741_3277_R | FAKE | NO: framing card_in_scene vs fills_frame (photo of a card in a scene vs a scan/render/tight crop); on-ca | - | 15.61 |
| SP04 | ef17741_3279_L | ef17741_3279_R | FAKE | yes | - | -13.5 |
| SP05 | ef17741_3280_L | ef17741_3280_R | FAKE | yes | - | -10.72 |
| SP06 | ef17741_3283_L | ef17741_3283_R | FAKE | NO: framing fills_frame vs card_in_scene (photo of a card in a scene vs a scan/render/tight crop); on-ca | - | -18.51 |
| SP07 | ef17741_3286_L | ef17741_3286_R | FAKE | yes | - | 1.08 |
| SP08 | ef17741_3288_L | ef17741_3288_R | FAKE | yes | - | -2.92 |
| SP09 | ef17741_3292_L | ef17741_3292_R | FAKE | yes | softer_small_print | -12.74 |
| SP10 | ef17741_3296_L | ef17741_3296_R | FAKE | NO: framing fills_frame vs card_in_scene (photo of a card in a scene vs a scan/render/tight crop) | - | -9.16 |
| SP12 | ef13268_d_R | ef13268_d_L | FAKE | NO: framing card_in_scene vs fills_frame (photo of a card in a scene vs a scan/render/tight crop); on-ca | softer_small_print, flatter_back_blue | 6.21 |
| SP13 | ef23015_68c_L | ef23015_68c_M | FAKE | NO: framing card_in_scene vs fills_frame (photo of a card in a scene vs a scan/render/tight crop); on-ca | softer_small_print | -24.7 |
| GG01 | ef17741_3283_L | ef17741_3283_LB | GENUINE | NO: framing fills_frame vs card_in_scene (photo of a card in a scene vs a scan/render/tight crop) | - | 10.18 |
| GG02 | ef17741_3288_L | ef17741_3288_LB | GENUINE | yes | - | 6.25 |
| GG03 | ef17741_3296_L | ef17741_3296_LB | GENUINE | NO: framing fills_frame vs card_in_scene (photo of a card in a scene vs a scan/render/tight crop) | - | -9.68 |
| GG04 | ef17741_3277_L | ef17741_3277_LT | GENUINE | yes | - | 10.03 |
| SS01 | cgcd_machreal | cgcd_machfake | FAKE | NO: on-card sharpness 131.38 vs 73.01 (x1.8) | - | -0.27 |
| SS02 | cgcd_backreal | cgcd_backfake | FAKE | yes | - | -9.69 |
| SS04 | cgcd_czreal | cgcd_czfake | FAKE | yes | - | -0.01 |
| SS05 | cgcu_obvreal | cgcu_obvfake | FAKE | yes | - | 8.02 |
| SS06 | flip_regreal | flip_regfake | FAKE | yes | - | -22.62 |
| SS07 | flip_backreal | flip_backfake | FAKE | yes | flatter_back_blue | -18.48 |

### Paired direction per feature (same-photo G->F fronts): how often the fake reads LOWER than its genuine twin

50% = coin flip. Genuine controls show the same count for 2nd real copy vs 1st.

| feature | fake lower than twin | controls: 2nd genuine lower |
|---|---|---|
| capture_profile.blown_share | 8/11 [43.4-90.3%] | 1/4 [4.6-69.9%] |
| capture_profile.card_fine_noise | 1/11 [1.6-37.7%] | 0/4 [0.0-49.0%] |
| capture_profile.card_sharpness | 6/11 [28.0-78.7%] | 2/4 [15.0-85.0%] |
| capture_profile.edge_ring_texture | 5/11 [21.3-72.0%] | 3/4 [30.1-95.4%] |
| capture_profile.laplacian_var | 5/11 [21.3-72.0%] | 4/4 [51.0-100.0%] |
| halftone_periodicity.band_power_frac | 0/1 [0.0-79.3%] | 0/0 |
| halftone_periodicity.patches | 1/1 [20.7-100.0%] | 0/0 |
| halftone_periodicity.peak_to_median | 0/1 [0.0-79.3%] | 0/0 |
| halftone_periodicity.px_per_mm | 0/1 [0.0-79.3%] | 0/0 |
| small_text_edges.edge_p99_over_contrast | 8/10 [49.0-94.3%] | 2/4 [15.0-85.0%] |
| lightness_delta_L | 8/11 [43.4-90.3%] | 1/4 [4.6-69.9%] |

## 2. Unpaired single-image features, split by photo type (top 6 by separation)

**lab_scan_or_photo|back**: genuine 1, fake 1
  - too few in a class to compute anything
**lab_scan_or_photo|front**: genuine 3, fake 3
  - capture_profile.width (CAPTURE descriptor - confound, not a tell): sep 1.00; LOO catch 3/3 [43.8-100.0%]; false-flag 1/3 [6.1-79.2%]
  - capture_profile.px_per_mm (CAPTURE descriptor - confound, not a tell): sep 1.00; LOO catch 3/3 [43.8-100.0%]; false-flag 1/3 [6.1-79.2%]
  - capture_profile.laplacian_var (CAPTURE descriptor - confound, not a tell): sep 1.00; LOO catch 3/3 [43.8-100.0%]; false-flag 1/3 [6.1-79.2%]
  - capture_profile.height (CAPTURE descriptor - confound, not a tell): sep 1.00; LOO catch 3/3 [43.8-100.0%]; false-flag 1/3 [6.1-79.2%]
  - capture_profile.card_fine_noise (CAPTURE descriptor - confound, not a tell): sep 0.83; LOO catch 3/3 [43.8-100.0%]; false-flag 1/3 [6.1-79.2%]
  - capture_profile.card_fill (CAPTURE descriptor - confound, not a tell): sep 0.78; LOO catch 2/3 [20.8-93.9%]; false-flag 1/3 [6.1-79.2%]
**phone_photo_scene|back**: genuine 2, fake 2
  - too few in a class to compute anything
**phone_photo_scene|front**: genuine 16, fake 12
  - capture_profile.blown_share (CAPTURE descriptor - confound, not a tell): sep 0.84; LOO catch 0/12 [0.0-24.3%]; false-flag 0/16 [0.0-19.4%]
  - small_text_edges.edge_p99_over_contrast: sep 0.79; LOO catch 2/11 [5.1-47.7%]; false-flag 2/14 [4.0-39.9%]
  - capture_profile.height (CAPTURE descriptor - confound, not a tell): sep 0.61; LOO catch 1/12 [1.5-35.4%]; false-flag 1/16 [1.1-28.3%]
  - capture_profile.edge_ring_texture (CAPTURE descriptor - confound, not a tell): sep 0.57; LOO catch 1/12 [1.5-35.4%]; false-flag 2/16 [3.5-36.0%]
  - capture_profile.card_sharpness (CAPTURE descriptor - confound, not a tell): sep 0.54; LOO catch 0/12 [0.0-24.3%]; false-flag 2/16 [3.5-36.0%]
  - capture_profile.card_fill (CAPTURE descriptor - confound, not a tell): sep 0.54; LOO catch 0/12 [0.0-24.3%]; false-flag 1/16 [1.1-28.3%]
**scan_or_flat_photo|front**: genuine 0, fake 1
  - too few in a class to compute anything

## 3. Screen-periodicity (rosette) lane on images at >= 15 px/mm (estimated scale)

| image | label | photo type | est px/mm | status | peak_to_median | band_power_frac |
|---|---|---|---|---|---|---|
| ef23015_realstamp | GENUINE | microscope | 190.0 | ran | 320.21 | 0.6461 |
| ef23015_fakestamp | FAKE | microscope | 190.0 | ran | 305.35 | 0.6613 |
| ef23015_phonefake | FAKE | phone_closeup | 60.0 | could_not_run (region_unreadable) |  |  |
| ef64743_b01 | GENUINE | microscope | 615.0 | ran | 59.18 | 0.8081 |
| ef64743_b02 | GENUINE | microscope | 615.0 | ran | 50.72 | 0.787 |
| ef64743_b03 | GENUINE | microscope | 615.0 | ran | 42.98 | 0.7613 |
| ef64743_b04 | GENUINE | microscope | 615.0 | ran | 39.07 | 0.7537 |
| ef64743_b05 | GENUINE | microscope | 615.0 | ran | 39.08 | 0.7483 |
| ef64743_b06 | GENUINE | microscope | 615.0 | ran | 48.07 | 0.7496 |
| cgcl_starng | FAKE | lab_macro | 100.0 | ran | 18.02 | 0.2867 |
| cgcl_star1 | GENUINE | lab_macro | 100.0 | ran | 107.51 | 0.4195 |
| cgcl_star2 | GENUINE | lab_macro | 300.0 | ran | 5.46 | 0.2866 |
| cgcd_taxireal | GENUINE | lab_macro | 60.0 | ran | 201.6 | 0.2447 |
| cgcd_taxifake | FAKE | lab_macro | 60.0 | ran | 211.61 | 0.1354 |
| poki_c1 | FAKE | loupe_phone | 230.0 | ran | 423.04 | 0.3902 |
| poki_c2 | FAKE | loupe_phone | 230.0 | ran | 551.23 | 0.5454 |
| poki_c3 | FAKE | loupe_phone | 230.0 | ran | 672.56 | 0.5968 |
| poki_c4 | FAKE | loupe_phone | 230.0 | ran | 2502.94 | 0.8095 |
| ef13268_d_R | GENUINE | phone_photo_scene | 20.8 | ran | 215.16 | 0.1071 |
| ef13268_d_L | FAKE | phone_photo_scene | 23.6 | ran | 135.48 | 0.1602 |
| ef23015_68c_L | GENUINE | phone_photo_scene | 18.4 | ran | 110.02 | 0.045 |
| ef23015_68c_M | FAKE | phone_photo_scene | 22.0 | ran | 542.21 | 0.0706 |
| tci_phole_L | GENUINE | composite_graphic | 100.0 | ran | 143.97 | 0.362 |
| tci_phole_R | FAKE | composite_graphic | 100.0 | ran | 72.51 | 0.4443 |

Ran on 23/24. Genuine n=13, fake n=10.
AUC (fake reads LESS periodic) = 0.19. Fakes below the lowest genuine (5.46): 0/10 [0.0-27.8%].
