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

    # spliting the assigning process into two functions ensures
    # that only one processor becomes assigned to the task
    def select_processor(self, task):
        raise NotImplementedError()

    def assign_task(self, task):
        self.select_processor(task).add_task(task)

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
    def __init__(self, processors_count, tasks, threshold, tries):
        super().__init__(processors_count, tasks)
        self.threshold=threshold
        self.tries=tries

    def select_processor(self, task):
        processors=self.processors.copy()
        # don't allow task.processor to be checked
        # TODO: ask if it's valid
        del processors[task.processor]
        for _ in range(self.tries):
            if len(processors)==0:
                # no more processors to check
                break
            processor=random.choice(processors)
            if processor.usage<self.threshold:
                # found a processor
                return processor
            else:
                processors.remove(processor)
        # finding other processor failed, assign to processor where it ocurred
        return self.processors[task.processor]
                
class SecondPolicy(Policy):
    def __init__(self, processors_count, tasks, threshold):
        super().__init__(processors_count, tasks)
        self.threshold=threshold

    def select_processor(self, task):
        if self.processors[task.processor].usage<self.threshold:
            return self.processors[task.processor]
        
        processors=self.processors.copy()
         # don't allow task.processor to be check
        del processors[task.processor]
        
        while len(processors)>0:
            processor=random.choice(processors)
            if processor.usage<self.threshold:
                return processor
            else:
                processors.remove(processor)
        # TODO: ask if it should be task.processor or last_processor
        return processor

class ThirdPolicy(SecondPolicy):
    def __init__(self, processors_count, tasks, threshold, transfer_treshold, moved):
        super().__init__(processors_count, tasks, threshold)
        self.transfer_treshold=transfer_treshold
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
            if processor.usage<self.transfer_treshold:
                chosen=random.choice(self.processors)
                if chosen.usage>self.threshold:
                    self.transfer_tasks(chosen, processor)
        super().update()

PROCESSORS_COUNT=20
tasks=random_tasks(123, PROCESSORS_COUNT, 1000, between(0.01, 1), between(1, 5), between(1, 7))
plot_tasks(tasks, PROCESSORS_COUNT)
FirstPolicy(PROCESSORS_COUNT, tasks, threshold=0.3, tries=3).run()
SecondPolicy(PROCESSORS_COUNT, tasks, threshold=0.3).run()
ThirdPolicy(PROCESSORS_COUNT, tasks, threshold=0.3, transfer_treshold=0.2, moved=0.5).run()