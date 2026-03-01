import mesa
import json
from pathlib import Path

class Individual(mesa.Agent):
    def __init__(self, model, sex):
        super().__init__(model)
        self.sex = sex
        self.age = 0
        self.alive = True
        self.energy = self.model.guppy_start_energy

        # Nowe cechy fizyczne (bez parametrów preferencji)
        if self.sex == "M":
            self.N_orange = self.model.random.randint(0, 5)
            self.N_black = self.model.random.randint(0, 5)
            self.body_size = self.model.random.uniform(1.5, 4.0)
            self.orange_area = self.model.random.uniform(0, 0.5)
            self.black_area = self.model.random.uniform(0, 0.5)

    def step(self):
        if not self.alive: return
        self.energy -= self.model.guppy_energy_decay

        # Ruch w stronę jedzenia
        neighborhood = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        empty_neighbors = [pos for pos in neighborhood if self.model.grid.is_cell_empty(pos)]

        if empty_neighbors:
            best_food = max(self.model.food[y][x] for (x, y) in empty_neighbors)
            best_positions = [(x, y) for (x, y) in empty_neighbors if self.model.food[y][x] == best_food]
            self.model.grid.move_agent(self, self.model.random.choice(best_positions))

        # Konsumpcja
        x, y = self.pos
        eat = min(self.model.food[y][x], self.model.food_eat)
        self.model.food[y][x] -= eat
        self.energy += eat * self.model.guppy_energy_gain_per_food

        self.age += 1
        self.check_death()

    def check_death(self):
        if self.energy <= 0 or self.age > self.model.max_age or self.model.random.random() < self.model.env_death_prob:
            self.alive = False

class Predator(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.alive = True
        self.energy = self.model.predator_start_energy

    def step(self):
        if not self.alive: return
        self.energy -= self.model.predator_energy_decay
        if self.energy <= 0:
            self.alive = False
            return

        # Ruch
        neighborhood = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        candidates = [pos for pos in neighborhood if not any(isinstance(a, Predator) for a in self.model.grid.get_cell_list_contents([pos]))]
        
        if candidates:
            self.model.grid.move_agent(self, self.model.random.choice(candidates))

        if self.energy <= self.model.predator_hunt_threshold:
            self.hunt()

    def hunt(self):
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=True)
        males = [a for a in neighbors if isinstance(a, Individual) and a.sex == "M" and a.alive]
        females = [a for a in neighbors if isinstance(a, Individual) and a.sex == "F" and a.alive]

        if not males and not females: return

        # 10% szans na zjedzenie samicy, inaczej najatrakcyjniejszy samiec
        if self.model.random.random() <= 0.1 and females:
            victim = self.model.random.choice(females)
            self.energy += self.model.predator_energy_gain
        elif males:
            victim = max(males, key=lambda m: m.N_orange) # Uproszczony wybór bez parametrów pref.
            # Zysk energii skalowany rozmiarem: $$E_{gain} = P_{gain} \cdot \frac{S_{body}}{4}$$
            self.energy += self.model.predator_energy_gain * (victim.body_size / 4.0)
        else:
            return

        victim.alive = False

class PopulationModel(mesa.Model):
    def __init__(self, config_path=None):
        path = Path(config_path) if config_path else Path(__file__).with_name("config.json")
        with path.open("r", encoding="utf-8") as f:
            cfg = json.load(f)

        super().__init__(seed=cfg.get("seed"))
        self.params = cfg
        
        # Inicjalizacja atrybutów z configu (analogicznie do starej wersji)
        for key, value in cfg.items():
            setattr(self, key, value)

        self.step_count = 0
        self.births_last_step = 0
        self.deaths_last_step = 0
        self.predator_deaths_last_step = 0
        self.grid = mesa.space.MultiGrid(self.width, self.height, torus=True)
        self.food = [[self.food_max for _ in range(self.width)] for _ in range(self.height)]

        # Startowi agenci
        self._place_agents(Individual, self.n_agents)
        self._place_agents(Predator, self.n_predators)

    def _place_agents(self, agent_class, n):
        for _ in range(n):
            agent = agent_class(self, self.random.choice(["M", "F"])) if agent_class == Individual else agent_class(self)
            while True:
                pos = (self.random.randrange(self.width), self.random.randrange(self.height))
                if self.grid.is_cell_empty(pos):
                    self.grid.place_agent(agent, pos)
                    break

    def step(self):
        self.step_count += 1
        self.births_last_step = 0
        self.deaths_last_step = 0
        self.predator_deaths_last_step = 0

        # Stała regeneracja jedzenia
        regen = self.food_regen * self.food_regen_empty_multiplier
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                self.food[y][x] = min(self.food_max, self.food[y][x] + regen)

        self.agents.shuffle_do("step")

        # Usuwanie martwych i respawn drapieżników
        dead_predators = 0
        for agent in list(self.agents):
            if not agent.alive:
                if isinstance(agent, Predator):
                    dead_predators += 1
                    self.predator_deaths_last_step += 1
                else:
                    self.deaths_last_step += 1
                self.grid.remove_agent(agent)
                self.agents.remove(agent)

        for _ in range(dead_predators):
            self._place_agents(Predator, 1)

        self.reproduce()

    def reproduce(self):
        females = [a for a in self.agents if isinstance(a, Individual) and a.sex == "F"]
        for female in females:
            neighbors = self.grid.get_neighbors(female.pos, moore=True, include_center=False)
            males = [a for a in neighbors if isinstance(a, Individual) and a.sex == "M"]
            if not males or self.random.random() >= self.reproduction_prob: continue

            father = max(males, key=lambda m: m.N_orange)
            
            # Szukanie miejsca dla potomka
            possible_pos = [p for p in self.grid.get_neighborhood(female.pos, moore=True) if self.grid.is_cell_empty(p)]
            if not possible_pos: continue

            child = Individual(self, self.random.choice(["M", "F"]))
            if child.sex == "M": # Dziedziczenie cech fizycznych
                child.N_orange = min(5, max(0, father.N_orange + self.random.choice([-1, 0, 1])))
                child.body_size = min(4.0, max(1.5, father.body_size + self.random.choice([-0.5, 0, 0.5])))
            
            self.grid.place_agent(child, self.random.choice(possible_pos))
            self.births_last_step += 1