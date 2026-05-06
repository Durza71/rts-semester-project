import time
import csv
import numpy as np
from scipy.integrate import quad

JOB_FINISHED = "job_finished"
END_OF_SIMULATION = "end_of_simulation"
LLF_PRIORITY_CHANGE = "thrashing"
RESOURCE_LIMIT = "resource_limit"

class Job:
    def __init__(self, task_name, job_name, C, release_time, deadline):
        self.task_name = task_name
        self.name = job_name
        self.execution_time = C
        self.deadline = deadline
        self.release_time = release_time

        self.complete = False
        self.met_deadline = None
        self.slack = 0
        self.completion_time = None

    def run_for(self, time_run, sim_time):
        self.execution_time -= time_run
        if self.execution_time <= 0.1:
            self.complete = True
            self.completion_time = sim_time

            self.slack = self.deadline - sim_time
            self.met_deadline = sim_time <= self.deadline

            print(f"{sim_time} - Finished Job {self.name}")


class Task:
    def __init__(self, N, T, P, C, D):
        self.name = N
        self.period = T
        self.phase = P
        self.execution_time = C
        self.deadline = D
        self.times_run = 0

    def create_job(self, time) -> Job:
        self.times_run += 1
        job_name = f"{self.name}_{self.times_run}"
        release_time = time
        deadline = self.phase + self.times_run * self.period + self.deadline

        print(f"{time} - Created Job {job_name}")

        return Job(self.name, job_name, self.execution_time, release_time, deadline)

    def get_next_release(self) -> int:
        return self.times_run * self.period + self.phase
    
class Resources():
    def __init__(self, squeezing = False):
        self.f = lambda x : (
            1 if x < 250
            else 0.7 if x < 500
            else 1
        )

        if not squeezing:
            self. f = lambda x : 1


    def get_resources(self, start, end):

        result, _ = quad(self.f, start, end)
        return result  # ~9.0

class Scheduler:
    def __init__(self, limit=1000):
        self.tasks = {}
        self.jobs = []
        self.time = 0
        self.job = None
        self.limit = limit

        self.utilization = 0
        self.completed_jobs = 0
        self.missed_deadlines = 0

        self.completed_job_data = []

        self.resources = Resources(True)

    def add_task(self, name, period, phase, execution_time, deadline):
        self.tasks[name] = Task(name, period, phase, execution_time, deadline)

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

        if min_time < self.time:
            min_time = self.time

        return cause, min_time

    def next_process(self):
        if len(self.jobs) == 0:
            return None
        return self.jobs[0]

    def run(self):
        while self.time < self.limit:
            cause, next_moment = self.get_next_moment()
                

            if next_moment != self.time and self.job is not None:
                print(f"{self.time} : {next_moment} - Running Job {self.job.name}")

            period = next_moment - self.time
            running_since = self.time
            self.time = next_moment

            # Run current job
            if self.job is not None and period != 0:
                self.job.run_for(self.resources.get_resources(running_since, self.time), self.time)
                self.utilization += period

                if self.job.complete:
                    self.completed_jobs += 1
                    if not self.job.met_deadline:
                        self.missed_deadlines += 1

                    # Save CSV data
                    self.completed_job_data.append([
                        self.job.name,
                        self.job.task_name,
                        self.job.release_time,
                        self.job.completion_time,
                        self.job.met_deadline,
                        self.job.slack
                    ])

                    self.jobs.remove(self.job)
                    self.job = None

            # Handle new job release
            if cause in self.tasks:
                self.jobs.append(self.tasks[cause].create_job(self.time))

            # Pick next job if idle
            if self.job is None or cause == LLF_PRIORITY_CHANGE:
                start = time.perf_counter_ns()
                self.job = self.next_process()
                end = time.perf_counter_ns()

                # convert ns → ms (optional, small effect)
                self.time += (end - start) / 1_000_000
        self.report()

    def report(self):
        # Write CSV
        with open("results.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Job Name",
                "Task Name",
                "Release Time",
                "Completion Time",
                "Met Deadline",
                "Slack"
            ])
            writer.writerows(self.completed_job_data)

        print("DONE!")
        print(f"{len(self.jobs)} not finished")
        print(f"{self.utilization / self.limit} utilization")
        print(f"{self.missed_deadlines} missed deadlines out of {self.completed_jobs} jobs")


if __name__ == "__main__":
    simulator = Scheduler()

    simulator.add_task("Ping", 20, 5, 8, 15)
    simulator.add_task("Pong", 35, 7, 14, 29)
    simulator.add_task("Hack", 330, 9, 70, 80)

    simulator.run()