from simulation import Scheduler, END_OF_SIMULATION, JOB_FINISHED, LLF_PRIORITY_CHANGE, JOB_OVERRUN
import time 
import heapq

class EDF(Scheduler):
    def next_process(self):
        if len(self.jobs) == 0:
            return None
        return min(self.jobs, key=lambda j: j.deadline)
    
class RM(Scheduler):
    def __init__(self, limit=1000, name="scheduler", squeezing=False):
        super().__init__(limit, name, squeezing)

        self.priorities = {}

    def add_task(self, name, period, phase, execution_time, deadline):
        super().add_task(name, period, phase, execution_time, deadline)

        self.priorities[name] = 1 / period

    def next_process(self):
        if len(self.jobs) == 0:
            return None
        return min(self.jobs, key= lambda j : self.priorities[j.name.split("_")[0]])

class LLF(Scheduler):
    def __init__(self, limit=1000, name="scheduler", squeezing=False):
        super().__init__(limit, name, squeezing)

        self.thrashing_interrupt = limit


    def next_process(self):
        if len(self.jobs) == 0:
            return None
        values = heapq.nsmallest(2, self.jobs, key=lambda j: j.deadline - j.execution_time)
        
        if len(values) > 1:
            catchup_point = values[1].deadline - values[1].execution_time - (values[0].deadline - values[0].execution_time)

            self.thrashing_interrupt = max(self.time + 1, self.time + catchup_point)
            #print(f"At time {self.time} Compare {self.time + 1} and {self.time + catchup_point}")

        else: self.thrashing_interrupt = self.limit

        return values[0]
    
    def get_next_moment(self):
        min_time = self.limit
        cause = END_OF_SIMULATION

        for task in self.tasks.values():
            next_release = task.get_next_release()
            if next_release < min_time:
                min_time = next_release
                cause = task.name

        if self.job is not None:
            finish_time = self.time + self.job.execution_time
            if finish_time < min_time:
                min_time = finish_time
                cause = JOB_FINISHED

        for overrun in self.overruns:
            if overrun[0] < min_time:
                min_time = overrun[0]
                cause = JOB_OVERRUN

        if self.thrashing_interrupt < min_time:
            min_time = self.thrashing_interrupt
            cause = LLF_PRIORITY_CHANGE

        if min_time < self.time:
            min_time = self.time

        return cause, min_time