import mesa
import json
from pathlib import Path

class Individual(mesa.Agent):
    def __init__(self, model, sex):
        super().__init__(model)
        self.sex = sex          # M/F
        self.age = 0
        self.alive = True
        self.energy = self.model.guppy_start_energy

        if self.sex == "M":
            self.N_orange = self.model.random.randint(0, 5)
            self.N_black = self.model.random.randint(0, 5)

    def step(self):
        if not self.alive:
            return

        # koszt życia
        self.energy -= self.model.guppy_energy_decay

        neighborhood = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False,
        )
        empty_neighbors = [pos for pos in neighborhood if self.model.grid.is_cell_empty(pos)]

        if empty_neighbors:
            # znajdź maksymalny food wśród pustych sąsiadów
            best_food = max(self.model.food[y][x] for (x, y) in empty_neighbors)

            # weź wszystkie kratki z tym maksymalnym food i wybierz losową
            best_positions = [(x, y) for (x, y) in empty_neighbors if self.model.food[y][x] == best_food]

            new_position = self.model.random.choice(best_positions)
            self.model.grid.move_agent(self, new_position)

        # === JEDZENIE ===
        x, y = self.pos
        available = self.model.food[y][x]
        eat = min(available, self.model.food_eat)
        self.model.food[y][x] -= eat
        self.energy += eat * self.model.guppy_energy_gain_per_food

        self.age += 1
        self.check_death()

    def check_death(self):
        if self.energy <= 0:
            self.alive = False
            return

        if self.model.random.random() < self.model.env_death_prob:
            self.alive = False
            return

        if self.age > self.model.max_age:
            self.alive = False
            return


class Predator(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.alive = True
        self.energy = self.model.predator_start_energy

    def step(self):
        if not self.alive:
            return

        # koszt życia
        self.energy -= self.model.predator_energy_decay
        if self.energy <= 0:
            self.alive = False
            return

        # ruch: może wejść na pustą kratkę ALBOR na kratkę z gupikiem
        neighborhood = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )

        candidates = []
        for pos in neighborhood:
            cell_agents = self.model.grid.get_cell_list_contents([pos])

            if not cell_agents:
                candidates.append(pos)
                continue

            if any(isinstance(a, Individual) for a in cell_agents):
                candidates.append(pos)

        if candidates:
            self.model.grid.move_agent(self, self.model.random.choice(candidates))

        # polowanie tylko gdy głodny
        if self.energy <= self.model.predator_hunt_threshold:
            self.hunt()

    def hunt(self):
        neighbors = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=True
        )
        males = [a for a in neighbors if isinstance(a, Individual) and a.sex == "M" and a.alive]
        females = [a for a in neighbors if isinstance(a, Individual) and a.sex == "F" and a.alive]

        if not males and not females:
            return

        # Nowa logika: 10% szans na zjedzenie losowej samicy, w innym wypadku wybór najlepszego samca
        x = self.model.random.random()
        if x <= 0.1 and females:
            victim = self.model.random.choice(females)
        else: 
            if not males:
                return # Jeśli nie wylosowano samicy i nie ma samców, drapieżnik nie je
            
            # W starej wersji wybieramy samca z największą liczbą plam N_orange
            victim = max(males, key=lambda m: m.N_orange)

        victim.alive = False
        self.energy += self.model.predator_energy_gain


class PopulationModel(mesa.Model):
    def __init__(self, config_path=None, **kwargs):
        if kwargs:
            bad = ", ".join(sorted(kwargs.keys()))
            raise TypeError(f"PopulationModel nie przyjmuje parametrów w kodzie. Nieobsługiwane: {bad}")

        default_path = Path(__file__).with_name("config.json")
        path = Path(config_path) if config_path is not None else default_path

        if not path.exists():
            raise FileNotFoundError(f"Brak pliku config.json: {path}")

        with path.open("r", encoding="utf-8") as f:
            cfg = json.load(f)

        # Wczytanie wartości
        n_agents = int(cfg["n_agents"])
        width = int(cfg["width"])
        height = int(cfg["height"])
        reproduction_prob = float(cfg["reproduction_prob"])
        env_death_prob = float(cfg["env_death_prob"])
        max_age = int(cfg["max_age"])
        seed = int(cfg.get("seed", 2137))

        n_predators = int(cfg["n_predators"])
        predator_start_energy = float(cfg["predator_start_energy"])
        predator_energy_decay = float(cfg["predator_energy_decay"])
        predator_hunt_threshold = float(cfg["predator_hunt_threshold"])
        predator_energy_gain = float(cfg["predator_energy_gain"])

        food_max = float(cfg["food_max"])
        food_regen = float(cfg["food_regen"])
        food_eat = float(cfg["food_eat"])
        food_regen_empty_multiplier = float(cfg["food_regen_empty_multiplier"])

        guppy_start_energy = float(cfg["guppy_start_energy"])
        guppy_energy_decay = float(cfg["guppy_energy_decay"])
        guppy_energy_gain_per_food = float(cfg["guppy_energy_gain_per_food"])

        super().__init__(seed=seed)

        if n_agents + n_predators > width * height:
            raise ValueError("Za dużo agentów na siatkę!")

        self.params = dict(cfg)
        self.reproduction_prob = reproduction_prob
        self.env_death_prob = env_death_prob
        self.max_age = max_age
        self.n_predators = n_predators
        self.predator_start_energy = predator_start_energy
        self.predator_energy_decay = predator_energy_decay
        self.predator_hunt_threshold = predator_hunt_threshold
        self.predator_energy_gain = predator_energy_gain
        self.food_max = food_max
        self.food_regen = food_regen
        self.food_eat = food_eat
        self.food_regen_empty_multiplier = food_regen_empty_multiplier
        self.guppy_start_energy = guppy_start_energy
        self.guppy_energy_decay = guppy_energy_decay
        self.guppy_energy_gain_per_food = guppy_energy_gain_per_food

        self.step_count = 0
        self.births_last_step = 0
        self.deaths_last_step = 0

        self.grid = mesa.space.MultiGrid(width, height, torus=True)
        self.food = [[self.food_max for _ in range(width)] for _ in range(height)]

        for _ in range(n_agents):
            sex = self.random.choice(["M", "F"])
            agent = Individual(self, sex)
            while True:
                x, y = self.random.randrange(width), self.random.randrange(height)
                if self.grid.is_cell_empty((x, y)):
                    self.grid.place_agent(agent, (x, y))
                    break

        for _ in range(n_predators):
            predator = Predator(self)
            while True:
                x, y = self.random.randrange(width), self.random.randrange(height)
                if self.grid.is_cell_empty((x, y)):
                    self.grid.place_agent(predator, (x, y))
                    break

    def regenerate_food(self):
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                cell_agents = self.grid.get_cell_list_contents([(x, y)])
                has_guppy = any(isinstance(a, Individual) for a in cell_agents)
                regen = self.food_regen if has_guppy else (self.food_regen_empty_multiplier * self.food_regen)
                self.food[y][x] = min(self.food_max, self.food[y][x] + regen)

    def step(self):
        self.step_count += 1
        self.births_last_step = 0
        self.deaths_last_step = 0
        self.regenerate_food()
        self.agents.shuffle_do("step")

        for agent in list(self.agents):
            if isinstance(agent, (Individual, Predator)) and not agent.alive:
                self.grid.remove_agent(agent)
                self.agents.remove(agent)
                if isinstance(agent, Individual):
                    self.deaths_last_step += 1

        self.reproduce()

    def reproduce(self):
        females = [a for a in self.agents if isinstance(a, Individual) and a.sex == "F"]
        for female in females:
            neighbors = self.grid.get_neighbors(female.pos, moore=True, include_center=False)
            males = [a for a in neighbors if isinstance(a, Individual) and a.sex == "M"]
            if not males:
                continue

            father = max(males, key=lambda m: m.N_orange)
            if self.random.random() >= self.reproduction_prob:
                continue

            possible_positions = set(self.grid.get_neighborhood(female.pos, moore=True, include_center=True))
            possible_positions |= set(self.grid.get_neighborhood(father.pos, moore=True, include_center=True))
            free_positions = [pos for pos in possible_positions if self.grid.is_cell_empty(pos)]
            
            if not free_positions:
                continue

            child_sex = self.random.choice(["M", "F"])
            child = Individual(self, child_sex)

            if child_sex == "M":
                child.N_orange = min(5, max(0, father.N_orange + self.random.choice([-1, 0, 1])))
                child.N_black = min(5, max(0, father.N_black + self.random.choice([-1, 0, 1])))

            self.grid.place_agent(child, self.random.choice(free_positions))
            self.births_last_step += 1