# Etap 05: Weryfikacja efektów (Model w pełni zoptymalizowany)

Finalna wersja symulacji z kompletem dobranych parametrów dla wszystkich badanych populacji.

### Instrukcja uruchomienia
1. Uruchom interfejs: `python -m solara run app.py`
2. Aby sprawdzić finalne wyniki, podmień treść pliku `config` na wartości zoptymalizowane w Etapie 04:
   * **Arima1:** 
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

  "female_pref_orange": 0.757303,
  "female_pref_black": 0.325120,
  "female_pref_body_size": 0.056161,
  "female_pref_N_orange": 0.305952,
  "female_pref_N_black": 0.249290,

  "pred_pref_orange": 0.653827,
  "pred_pref_black": 0.587406,
  "pred_pref_body_size": 0.280541,
  "pred_pref_N_orange": 0.837673,
  "pred_pref_N_black": 0.801709
  }

   * **Arima5:**
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

   * **Aripo1:**
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

   * **Aripo6:**
   {
  "n_agents": 20,
  "width": 10,
  "height": 10,
  "reproduction_prob": 0.292293,
  "env_death_prob": 0.028424,
  "max_age": 85.880205,

  "n_predators": 5,
  "predator_hunt_threshold": 33.060247,
  "predator_energy_decay": 2.173306,
  "predator_energy_gain": 9.231773,
  "predator_start_energy": 29.592789,

  "food_max": 56.019542,
  "food_regen": 5.529098,
  "food_eat": 11.302161,
  "food_regen_empty_multiplier": 2.711092,

  "guppy_start_energy": 35.698481,
  "guppy_energy_decay": 2.531543,
  "guppy_energy_gain_per_food": 10.452061,

  "female_pref_orange": 0.118503,
  "female_pref_black": 0.978972,
  "female_pref_body_size": 0.002508,
  "female_pref_N_orange": 0.260603,
  "female_pref_N_black": 0.621340,

  "pred_pref_orange": 0.590633,
  "pred_pref_black": 0.981495,
  "pred_pref_body_size": 0.037637,
  "pred_pref_N_orange": 0.468329,
  "pred_pref_N_black": 0.992262
  }