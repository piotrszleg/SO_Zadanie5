from dataclasses import dataclass
import random
import matplotlib.pyplot as plt
import colorsys

@dataclass
class task(object):
    processor:int
    time:int
    usage:float
    duration:int
    def copy(self):
        return task(**self.__dict__)

@dataclass
class between(object):
    start:object
    end:object
    @property
    def length(self):
        return self.end-self.start
    def random(self):
        # cast to start class
        return_type=self.start.__class__
        return return_type(self.start+random.random()*self.length)

def random_tasks(seed, processors_count, count, usage, time_skip, duration):
    random.seed(seed)
    time=0
    result=[]
    for _ in range(count):
        result.append(task(random.randrange(0, processors_count), time, usage.random(), duration.random()))
        time+=time_skip.random()
    return result

def plot_tasks(tasks, processors_count):
    X=[task.time for task in tasks]
    Y=[task.processor for task in tasks]
    sizes=[task.usage*100 for task in tasks]
    step=1/processors_count
    processors_colors=[colorsys.hls_to_rgb(step*index, 0.8, 1) for index in range(processors_count)]
    random.shuffle(processors_colors)
    colors=[processors_colors[task.processor] for task in tasks]
    plt.scatter(X, Y, c=colors, s=sizes)
    plt.show()

@dataclass
class Processor(object):
    tasks:list
    usage_asks:int=0
    def add_task(self, task):
        self.tasks.append(task.copy())
    @property
    def usage(self):
        self.usage_asks+=1
        usage=0
        for task in self.tasks:
            usage+=task.usage
        return usage
    def update(self):
        new_tasks=[]
        for task in self.tasks:
            if task.duration>0:
                task.duration-=1
                new_tasks.append(task)
        self.tasks=new_tasks

class Policy(object):
    def __init__(self, processors_count, tasks):
        self.processors=[Processor([]) for _ in range(processors_count)]
        self.tasks=tasks.copy()
        self.time=0
        self.usages=[]

    def assign_task(self, task):
        raise NotImplementedError()

    def update_usages(self):
        for processor in self.processors:
            self.usages.append(processor.usage)

    def average_usage(self):
        sum=0
        for usage in self.usages:
            sum+=usage
        return sum/len(self.usages)

    def average_deviation(self, average):
        sum=0
        for usage in self.usages:
            sum+=abs(usage-average)
        return sum/len(self.usages)

    def usage_asks(self):
        sum=0
        for processor in self.processors:
            sum+=processor.usage_asks
        return sum

    def summary(self):
        print(self.__class__.__name__)
        average_usage=self.average_usage()
        print(f"average usage: {average_usage}")
        print(f"average deviation: {self.average_deviation(average_usage)}")
        print(f"usage asks: {self.usage_asks()}")

    def update(self):
        for processor in self.processors:
            processor.update()
        new_tasks=[]
        for task in self.tasks:
            if task.time==self.time:
                self.assign_task(task)
            else:
                new_tasks.append(task)
        self.tasks=new_tasks
        self.update_usages()
        self.time+=1

    def run(self):
        while len(self.tasks)>0:
            self.update()
        self.summary()

class FirstPolicy(Policy):
    def __init__(self, processors_count, tasks, threshold, checked):
        super().__init__(processors_count, tasks)
        self.threshold=threshold
        self.checked=checked

    def assign_task(self, task):
        indexes=[i for i in range(len(self.processors))]
        for _ in range(self.checked):
            if len(indexes)==0:
                break
            index=random.choice(indexes)
            if self.processors[index].usage<self.threshold:
                self.processors[index].add_task(task)
                return
            else:
                indexes.remove(index)
        self.processors[task.processor].add_task(task)
                
class SecondPolicy(Policy):
    def __init__(self, processors_count, tasks, threshold):
        super().__init__(processors_count, tasks)
        self.threshold=threshold

    def assign_task(self, task):
        if self.processors[task.processor].usage<self.threshold:
            self.processors[task.processor].add_task(task)
        indexes=[i for i in range(len(self.processors))]
        index=0
        while len(indexes)==0:
            index=random.choice(indexes)
            if self.processors[index].usage<self.threshold:
                self.processors[index].add_task(task)
                break
            else:
                indexes.remove(index)
        self.processors[index].add_task(task)

class ThirdPolicy(SecondPolicy):
    def __init__(self, processors_count, tasks, threshold, minimal_threshold, moved):
        super().__init__(processors_count, tasks, threshold)
        self.minimal_threshold=minimal_threshold
        self.moved=moved
        self.migrations=0

    def transfer_tasks(self, source, destination):
        moved=int(len(source.tasks)*self.moved)
        tasks=source.tasks
        destination.tasks=tasks[moved:]
        rest=len(tasks)-moved
        source.tasks=tasks[:rest]
        self.migrations+=moved

    def summary(self):
        super().summary()
        print(f"migrations: {self.migrations}")

    def update(self):
        for processor in self.processors:
            if processor.usage<self.minimal_threshold:
                chosen=random.choice(self.processors)
                if chosen.usage>self.threshold:
                    self.transfer_tasks(chosen, processor)
        super().update()

PROCESSORS_COUNT=20
tasks=random_tasks(123, PROCESSORS_COUNT, 1000, between(0.01, 1), between(1, 5), between(1, 7))
plot_tasks(tasks, PROCESSORS_COUNT)
FirstPolicy(PROCESSORS_COUNT, tasks, 0.3, 3).run()
SecondPolicy(PROCESSORS_COUNT, tasks, 0.3).run()
ThirdPolicy(PROCESSORS_COUNT, tasks, 0.3, 0.2, 0.5).run()
