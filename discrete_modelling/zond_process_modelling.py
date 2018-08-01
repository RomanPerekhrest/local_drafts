import collections
import queue
import re
import random

Event = collections.namedtuple('Event', 'time procid action')

# Corouting representing space zond activities
def zond_process(zond_id, max_trips, start_time = 0):
    time = yield Event(start_time, zond_id, 'leave the base ... ')

    for i in range(max_trips):
        time = yield Event(time, zond_id, 'pick up an oar piece')
        time = yield Event(time, zond_id, 'perform the primary analysis of the picked oar piece')
        time = yield Event(time, zond_id, 'transfer the oar piece to central lab')

    yield Event(time, zond_id, 'going home ...')


class Modeller:

    DEPARTURE_INTERVAL = 5

    TIME_RANGE = [3, 7, 2, 10, 5]

    def __init__(self, processes):
        self.procs = dict(processes)
        self.events = queue.PriorityQueue()

    def run(self, end_time):
        for _, proc in self.procs.items():
            event = next(proc)
            self.events.put(event)

        sim_time = 0
        while (sim_time < end_time):
            if self.events.empty():
                print('all events were finished ...')
                break

            current_event = self.events.get()
            next_time, proc_id, action = current_event
            print('zond: ', proc_id, proc_id * ' ', current_event)

            active_proc = self.procs[proc_id]
            sim_time += next_time

            try:
                next_event = active_proc.send(next_time + random.choice(Modeller.TIME_RANGE))
            except StopIteration:
                del self.procs[proc_id]
            else:
                self.events.put(next_event)
        else:
            print('The end of modelling: modelling time limit exceeded ...')
            print('events pending:', self.events.qsize())



processes = { i: zond_process(i, i * 2, i * Modeller.DEPARTURE_INTERVAL) for i in range(1,4) }
modeller = Modeller(processes)
modeller.run(1000)


