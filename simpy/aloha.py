# Original: https://heather.cs.ucdavis.edu/matloff/public_html/SimCourse/PLN/SimIntro.pdf
# Aloha.py, Python simulation example: a form of slotted ALOHA
# Here, we will look finite time, finding the probability that there are
# k active nodes at the end of epoch m
# usage: python Aloha.py s_num_nodes p_backoff q_message_arrival m_epoch k_active_nodes
#
# For example:
# aloha.py 3 0.5 0.2 100 3
# P(k active at time m) = 0.061


import random
import sys
import argparse

class Node: # one object of this class models one network node
    # some class variables
    p = 0.1
    q = 0.3
    r = random.Random(98765) # set seed
    active_set = [] # which nodes are active now
    inactive_set = [] # which nodes are inactive now

    @classmethod
    def init(cls, n):
        # start this node in inactive mode
        cls.inactive_set.append(n)

    @classmethod
    def checkgoactive(cls): # determine which nodes will go active
        for n in cls.inactive_set:
            if cls.r.uniform(0,1) < cls.q:
                cls.inactive_set.remove(n)
                cls.active_set.append(n)

    @classmethod
    def trysend(cls):
        '''
            During the current epoch, determine which nodes try to send
        '''
        numnodestried = 0 # number of nodes which have tried to send
        whotried = None # which node tried to send (last)
        for n in cls.active_set:
            if cls.r.uniform(0,1) < cls.p:
                whotried = n
                numnodestried += 1

        # We have a successful transmission if and only if exactly one
        # node has tried to send:
        if numnodestried == 1:
            cls.active_set.remove(whotried)
            cls.inactive_set.append(whotried)

    @classmethod
    def reset(cls):
        '''
            Makes all nodes inactive after a repetition of the experiment
        '''
        for n in cls.active_set:
            cls.active_set.remove(n)
            cls.inactive_set.append(n)

def main():
    parser = argparse.ArgumentParser(description="Parses Aloha parameters")
    parser.add_argument("s", type=int, help="Number of nodes that are communicating")
    parser.add_argument("p", type=float, help="The transmit probability (backoff scheme)")
    parser.add_argument("q", type=float, help="The arrival (message creation) probability")
    parser.add_argument("m", type=int, help="The number of epochs (discrete time units)")
    parser.add_argument("k", type=int, help="The number of active nodes (our measurement)")

    args = parser.parse_args()

    Node.s = args.s
    Node.p = args.p
    Node.q = args.q

    # set up the s nodes
    for i in range(args.s):
        Node.init(i) # ith node enters the simulation

    count = 0
    for _ in range(10000):
        # run the process for m epochs
        for epoch in range(args.m):
            Node.checkgoactive()
            Node.trysend()
        # len() gives the length of an object
        if len(Node.active_set) == args.k:
            count += 1

        Node.reset()

    print(f'P(k active at time m) = {count/10000.0}')

if __name__ == "__main__":
    main()