import json
import random
import numpy
from random import randint

from clients.client_abstract_class import Player


class SubmarineCaptain(Player):
    def __init__(self, name):
        super(SubmarineCaptain, self).__init__(name=name, is_trench_manager=False)
        game_info = json.loads(self.client.receive_data())
        print('sub', game_info)
        self.m = game_info['m']
        self.L = game_info['L']
        self.position = game_info['pos']

        self.probetime_arr = []
        for i in range(0, 100):
            self.probetime_arr.append([])
        self.score_arr = numpy.zeros(100)
        self.direction = 1
        self.t = 0
        self.curloc = 0
        self.last_probed = (0, 0, 0)

    def play_game(self):
        response = {}
        while True:
            move = self.your_algorithm(0 if not response else response['times_probed'])
            self.client.send_data(json.dumps({"move": move}))
            self.position += move
            response = json.loads(self.client.receive_data())
            if 'game_over' in response:
                print(f"The trench manager's final cost is: {response['trench_cost']}. " +
                      f"The safety condition {'was' if response['was_condition_achieved'] else 'was not'} satisfied.")
                exit(0)
            self.m -= 1

    def calculate_score(self):
        for i in range(0, 100):
            self.score_arr[i] = 0
            for j in range((self.curloc - self.L) % 100, (self.curloc + self.L) % 100):
                score = 0
                for k in range(0, len(self.probetime_arr[j])):
                    (t, n) = self.probetime_arr[j][k]
                    score += t * pow(n, 1 / 2)
                self.score_arr[i] += score

    def move_to_max(self):
        cmax = 0
        for i in range(0, 100):
            if (self.score_arr[cmax] > self.score_arr[i]):
                cmax = i
        if (self.curloc - cmax) % 100 < 50:
            return -1
        else:
            return 1

    def move_to_lastprob(self):
        (l, to, n) = self.last_probed
        if (l - self.curloc) % 100 < 50:
            return 1
        else:
            return -1

    def your_algorithm(self, times_probed):

        if (self.t < (self.m / 10)):
            self.probetime_arr[self.curloc].append((self.t, times_probed))
            if (times_probed > 0):
                last_probed = (self.curloc, self.t, times_probed)
            self.t += 1
            self.curloc += self.direction % 100
            return self.direction

        else:
            self.probetime_arr[self.curloc].append((self.t, times_probed))
            self.calculate_score()
            r = random.random()
            s = random.random()
            w = random.random()
            v = random.random()
            q = randint(-1, 1)
            if s < 0.5:
                q = 1
            else:
                q = -1

            (lp, tp, np) = self.last_probed
            consm=self.m/200
            if (times_probed == 0 and v < consm * np * (self.t - tp) / self.m):
                self.direction = self.move_to_lastprob()
                self.t += 1
                self.curloc += self.direction
                self.curloc = self.curloc % 100
                if (times_probed > 0):
                    self.last_probed = (self.curloc, self.t, times_probed)
                return self.direction

            if (r < 0.05):
                self.direction = self.move_to_max()
            else:
                if (self.score_arr[(self.curloc + q) % 100] > self.score_arr[self.curloc]):
                    self.direction = q
                else:
                    if (w > (self.t / self.m)):
                        self.direction = q
                    else:
                        self.direction = 0

            self.t += 1
            self.curloc += self.direction
            self.curloc = self.curloc % 100
            if (times_probed > 0):
                self.last_probed = (self.curloc, self.t, times_probed)
            return self.direction
        """
        PLACE YOUR ALGORITHM HERE
        As the submarine captain, you only ever have access to your position (self.position),
        the amount of times you were successfully probed (times_probed), how long is the game
        (self.m), and the range of the probes(self.L).
        You must return an integer between [-1, 1]
        """
        return randint(-1, 1)
