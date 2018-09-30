import json
from random import randint, choice

from clients.client_abstract_class import Player

class TrenchManager(Player):
    def __init__(self, name):
        super(TrenchManager, self).__init__(name=name, is_trench_manager=True)
        game_info = json.loads(self.client.receive_data())
        print('trench', game_info)
        self.d = game_info['d']
        self.y = game_info['y']
        self.r = game_info['r']
        self.m = game_info['m']
        self.L = game_info['L']
        self.p = game_info['p']
        self.firstTurn = True
        self.lastProbesSent = []
        self.isProbed = False
        self.submarineLocationRange = (0, 0)
        self.timeLapsed = 0
        self.nextProbeTime = 0

    def play_game(self):
        while True:
            probes_to_send = self.send_probes()
            self.client.send_data(json.dumps({"probes": probes_to_send}))
            response = json.loads(self.client.receive_data())
            alert = self.choose_alert(probes_to_send, response['probe_results'])
            self.client.send_data(json.dumps({"region": alert}))
            response = json.loads(self.client.receive_data())
            if 'game_over' in response:
                print(f"Your final cost is: {response['trench_cost']}. " +
                      f"The safety condition {'was' if response['was_condition_achieved'] else 'was not'} satisfied.")
                exit(0)
            self.m -= 1

    def send_probes(self):
        """
        PLACE YOUR PROBE ALGORITHM HERE

        As the trench manager, you have access to the start of the red alert region (self.d),
        the cost for yellow alerts (self.y), the cost for red alerts (self.r), how long is
        the game (self.m), the range of the probes (self.L), and the cost to deploy a probe (self.p)

        For this function, you must return an array of integers between 0 and 99 determining the
        location you would like to send the probes
        """
        probesToBeSent = []
        self.timeLapsed += 1

        if self.firstTurn:
            self.firstTurn = False
            midRed = (self.d + 2)%100
            if self.L == 2:
                probesToBeSent = [midRed, (midRed+5)%100, (midRed+51)%100]

            else:
                probesToBeSent = [midRed, (midRed+51)%100]

        elif self.isProbed:
            self.isProbed = False
            a, b = self.d, (self.d+5)%100
            c, d = self.submarineLocationRange
            d1 = a-d
            d2 = c-b
            if(d1<0):
                d1 = 100 + d1
            if(d2<0):
                d2 = 100 + d2
            shortestPathToDanger = min(d1, d2)
            self.nextProbeTime = self.timeLapsed + shortestPathToDanger

        else:
            if self.timeLapsed < self.nextProbeTime - 1:
                probesToBeSent = []
            elif self.timeLapsed == self.nextProbeTime - 1:
                self.firstTurn = True
                probesToBeSent = []
            elif self.lastProbesSent.__len__() == 3:
                p1 = (self.lastProbesSent[0] - 2 * self.L) % 100 if (self.lastProbesSent[0] - 2 * self.L) % 100 >= 0 \
                    else 100 + (self.lastProbesSent[0] - 2 * self.L) % 100
                p2 = (self.lastProbesSent[0] + 2 * self.L) % 100
                p3 = (self.lastProbesSent[2] - 2 * self.L) % 100 if (self.lastProbesSent[2] - 2 * self.L) % 100 >= 0 \
                    else 100 + (self.lastProbesSent[2] - 2 * self.L) % 100
                p4 = (self.lastProbesSent[2] + 2 * self.L) % 100
                probesToBeSent = [p1, p2, p3, p4]
            elif self.lastProbesSent.__len__() == 2:
                p1 = (self.lastProbesSent[0] - 2 * self.L) % 100 if (self.lastProbesSent[0] - 2 * self.L) % 100 >= 0 \
                    else 100 + (self.lastProbesSent[0] - 2 * self.L) % 100
                p2 = (self.lastProbesSent[0] + 2 * self.L) % 100
                p3 = (self.lastProbesSent[1] - 2 * self.L) % 100 if (self.lastProbesSent[1] - 2 * self.L) % 100 >= 0 \
                    else 100 + (self.lastProbesSent[1] - 2 * self.L) % 100
                p4 = (self.lastProbesSent[1] + 2 * self.L) % 100
                probesToBeSent = [p1, p2, p3, p4]

            else:
                p1 = (self.lastProbesSent[0]-2*self.L)%100 if (self.lastProbesSent[0]-2*self.L)%100>0 else 100+(self.lastProbesSent[0]-2*self.L)%100
                p2 = (self.lastProbesSent[1]+2*self.L)%100
                p3 = (self.lastProbesSent[2]-2*self.L)%100 if (self.lastProbesSent[2]-2*self.L)%100>0 else 100+(
                                                                                                                   self.lastProbesSent[2]-2*self.L)%100
                p4 = (self.lastProbesSent[3]+2*self.L)%100
                probesToBeSent = [p1, p2, p3, p4]

        self.lastProbesSent = probesToBeSent
        return probesToBeSent




    def choose_alert(self, sent_probes, results):
        """
        PLACE YOUR ALERT-CHOOSING ALGORITHM HERE

        This function has access to the probes you just sent and the results. They look like:

        sent_probes: [x, y, z]
        results: [True, False, False]

        This means that deploying the probe x returned True, y returned False, and z returned False

        You must return one of two options: 'red' or 'yellow'
        """
        for ele in results:
            if ele:
                self.isProbed = True
                index = results.index(ele)
                c = (index - self.L)%100
                d = (index + self.L)%100
                if(c < 0):
                    c = 100 + c
                elif(d < 0):
                    d = 100+d
                self.submarineLocationRange = c, d
                for ele in range(c, c+2*self.L+1):
                    if ele in range(self.d, (self.d + 5) % 100):
                        return 'red'
                return 'yellow'
        return 'yellow'
