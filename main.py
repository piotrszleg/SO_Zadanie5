from dataclasses import dataclass
import random

@dataclass
class task(object):
    processor:int
    time:int
    requirement:float

@dataclass
class between(object):
    start:object
    end:object
    @property
    def length(self):
        return self.end-self.start
    def random(self):
        self.start.__class__
        # cast to start class
        return self.start.__class__(self.start+random.random()*self.length)

def random_tasks(seed, processors_count, count, requirement, time_skip):
    random.seed(seed)
    time=0
    result=[]
    for _ in range(count):
        result.append(task(random.randrange(0, processors_count), time, requirement.random()))
        time+=time_skip.random()
    return result

@dataclass
class Process(object):
    tasks:list
    def add_task(self, task):
        self.tasks.append(task)
    @property
    def usage(self):
        usage=0
        for task in self.tasks:
            usage+=task
        return usage

class Policy(object):
    def __init__(self, processors_count, tasks):
        self.processors=[Process([])]*processors_count
        self.tasks=tasks.copy()
        self.time=0

    def assign_task(self, task):
        raise NotImplementedError()

    def update(self):
        new_tasks=[]
        for task in self.tasks:
            if task.time==self.time:
                self.assign_task(task)
            else:
                new_tasks.append(task)
        self.tasks=new_tasks
        self.time+=1

    def run(self):
        while len(self.tasks)>0:
            self.update()

class FirstPolicy(Policy):
    def __init__(self, processors_count, tasks, threshold, checked):
        super().__init__(processors_count, tasks)
        self.threshold=threshold
        self.checked=checked

    def assign_task(self, task):
        indexes=[i for i in range(len(self.processors))]
        for _ in range(self.checked):
            if len(indexes)==0:
                self.processors[task.processor].add_task(task.requirement)
                break
            index=random.choice(indexes)
            if self.processors[index].usage<self.threshold:
                self.processors[index].add_task(task.requirement)
                break
            else:
                del index
                
class SecondPolicy(Policy):
    def __init__(self, processors_count, tasks, threshold):
        super().__init__(processors_count, tasks)
        self.threshold=threshold

    def assign_task(self, task):
        if self.processors[task.processor].usage<self.threshold:
            self.processors[task.processor].add_task(task.requirement)
        indexes=[i for i in range(len(self.processors))]
        index=0
        while len(indexes)==0:
            index=random.choice(indexes)
            if self.processors[index].usage<self.threshold:
                self.processors[index].add_task(task.requirement)
                break
            else:
                del indexes[index]
        self.processors[index].add_task(task.requirement)

class ThirdPolicy(SecondPolicy):
    def __init__(self, processors_count, tasks, threshold, minimal_threshold, moved):
        super().__init__(processors_count, tasks, threshold)
        self.minimal_threshold=minimal_threshold
        self.moved=moved

    def transfer_tasks(self, source, destination):
        moved=int(len(source.tasks)*self.moved)
        tasks=source.tasks
        destination.tasks=tasks[moved:]
        rest=len(tasks)-moved
        source.tasks=tasks[:rest]

    def update(self):
        for processor in self.processors:
            if processor.usage<self.minimal_threshold:
                chosen=random.choice(self.processors)
                if chosen.usage>self.threshold:
                    self.transfer_tasks(chosen, processor)
        super().update()

PROCESSORS_COUNT=5
tasks=random_tasks(123, PROCESSORS_COUNT, 10, between(0.01, 0.4), between(1, 5))
FirstPolicy(PROCESSORS_COUNT, tasks, 0.2, 3).run()
SecondPolicy(PROCESSORS_COUNT, tasks, 0.2).run()
ThirdPolicy(PROCESSORS_COUNT, tasks, 0.2, 0.1, 0.3).run()