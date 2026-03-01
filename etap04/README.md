# Etap 04: Drugi etap parametryzacji

optymalizacja parametrów preferencji i selekcji

### Instrukcja
1. W pliku `parametryzacja2.py` ustaw `TARGET_POPULATION` (np. `Arima1`).
2. Podmień treść pliku `config` na wartości z Etapu 02 (fizjologia/środowisko) dla wybranej populacji:
<details>
  <summary>▶ Kliknij, aby zobaczyć parametry dla <b>Arima1</b></summary>

  ```json
  {
    "n_agents": 20,
    "width": 10,
    "height": 10,
    "reproduction_prob": 0.278935,
    "env_death_prob": 0.013652,
    "max_age": 105.503065,

    "n_predators": 5,
    "predator_hunt_threshold": 34.232825,
    "predator_energy_decay": 2.543465,
    "predator_energy_gain": 8.224903,
    "predator_start_energy": 22.091489,

    "food_max": 25.101250,
    "food_regen": 7.770476,
    "food_eat": 8.976971,
    "food_regen_empty_multiplier": 1.434243,

    "guppy_start_energy": 23.830070,
    "guppy_energy_decay": 4.109367,
    "guppy_energy_gain_per_food": 11.725148,

    "female_pref_orange": 0.2,
    "female_pref_black": 0.2,
    "female_pref_body_size": 0.2,
    "female_pref_N_orange": 0.2,
    "female_pref_N_black": 0.2,

    "pred_pref_orange": 0.001,
    "pred_pref_black": 0.001,
    "pred_pref_body_size": 0.001,
    "pred_pref_N_orange": 0.001,
    "pred_pref_N_black": 0.001
  }

</details>

<details>
<summary>▶ Kliknij, aby zobaczyć parametry dla <b>Arima5</b></summary>
 {
  "n_agents": 20,
  "width": 10,
  "height": 10,
  "reproduction_prob": 0.343517,
  "env_death_prob": 0.015319,
  "max_age": 98.818863,

  "n_predators": 5,
  "predator_hunt_threshold": 30.495078,
  "predator_energy_decay": 1.926174,
  "predator_energy_gain": 6.258830,
  "predator_start_energy": 26.093109,

  "food_max": 29.613076,
  "food_regen": 5.895126,
  "food_eat": 17.442263,
  "food_regen_empty_multiplier": 2.252399,

  "guppy_start_energy": 29.458932,
  "guppy_energy_decay": 3.807996,
  "guppy_energy_gain_per_food": 11.363268,

  "female_pref_orange": 0.636795,
  "female_pref_black": 0.082827,
  "female_pref_body_size": 0.209370,
  "female_pref_N_orange": 0.620886,
  "female_pref_N_black": 0.156024,

  "pred_pref_orange": 0.355255,
  "pred_pref_black": 0.175370,
  "pred_pref_body_size": 0.174405,
  "pred_pref_N_orange": 0.612798,
  "pred_pref_N_black": 0.490272
}

</details>

<details>
<summary>▶ Kliknij, aby zobaczyć parametry dla <b>Aripo1</b></summary>

 {
  "n_agents": 20,
  "width": 10,
  "height": 10,
  "reproduction_prob": 0.557892,
  "env_death_prob": 0.073379,
  "max_age": 59.761692,

  "n_predators": 5,
  "predator_hunt_threshold": 28.433234,
  "predator_energy_decay": 2.310085,
  "predator_energy_gain": 7.750989,
  "predator_start_energy": 27.174907,

  "food_max": 15.343571,
  "food_regen": 3.700458,
  "food_eat": 11.566006,
  "food_regen_empty_multiplier": 1.893308,

  "guppy_start_energy": 18.530527,
  "guppy_energy_decay": 7.533253,
  "guppy_energy_gain_per_food": 5.065457,

  "female_pref_orange": 0.564057,
  "female_pref_black": 0.354362,
  "female_pref_body_size": 0.278560,
  "female_pref_N_orange": 0.397121,
  "female_pref_N_black": 0.519694,

  "pred_pref_orange": 0.141690,
  "pred_pref_black": 0.189557,
  "pred_pref_body_size": 0.227941,
  "pred_pref_N_orange": 0.621921,
  "pred_pref_N_black": 0.381606
}
</details>

<details>
<summary>▶ Kliknij, aby zobaczyć parametry dla <b>Aripo6</b></summary>
{
  "n_agents": 20,
  "width": 10,
  "height": 10,
  "reproduction_prob": 0.319652,
  "env_death_prob": 0.025331,
  "max_age": 72.800183,

  "n_predators": 5,
  "predator_hunt_threshold": 30.148245,
  "predator_energy_decay": 1.990026,
  "predator_energy_gain": 3.954136,
  "predator_start_energy": 32.187707,

  "food_max": 8.752360,
  "food_regen": 2.004740,
  "food_eat": 10.694467,
  "food_regen_empty_multiplier": 3.335146,

  "guppy_start_energy": 31.484270,
  "guppy_energy_decay": 2.325307,
  "guppy_energy_gain_per_food": 6.502142,

  "female_pref_orange": 0.2,
  "female_pref_black": 0.2,
  "female_pref_body_size": 0.2,
  "female_pref_N_orange": 0.2,
  "female_pref_N_black": 0.2,

  "pred_pref_orange": 0.001,
  "pred_pref_black": 0.001,
  "pred_pref_body_size": 0.001,
  "pred_pref_N_orange": 0.001,
  "pred_pref_N_black": 0.001
}
</details>

3. Uruchom proces:
   ```bash
   python parametryzacja2.py