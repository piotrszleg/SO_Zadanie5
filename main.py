from dataclasses import dataclass
import random
import matplotlib.pyplot as plt
import colorsys
from enum import Enum, auto
from operator import attrgetter

@dataclass
class Task(object):
    processor:int
    time:int
    usage:float
    duration:int
    assigned:int=1
    def copy(self):
        return Task(**self.__dict__)

class Between(object):
    def __init__(self, start, end):
        if start.__class__!=end.__class__:
            raise ValueError("Start and end need to be of the same type")
        self.start=start
        self.end=end
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
        result.append(Task(random.randrange(0, processors_count), time, usage.random(), duration.random()))
        time+=time_skip.random()
    return result

def plot_durations(plt, tasks, processors_count, colors):
    for processor in range(processors_count):
        X=[]
        Y=[]
        for task in tasks:
            if task.processor!=processor:
                continue
            # start of the line
            X.append(task.time)
            Y.append(task.processor)
            # end of the line
            X.append(task.time+task.duration)
            Y.append(task.processor)
            # hole between lines
            X.append(float("NaN"))
            Y.append(float("NaN"))
        plt.plot(X, Y, c=colors[processor])
        

def plot_tasks(plt, tasks, processors_count, processors_colors):
    X=[task.time for task in tasks]
    Y=[task.processor for task in tasks]
    sizes=[task.usage*2000/processors_count for task in tasks]
    colors=[processors_colors[task.processor] for task in tasks]
    plt.scatter(X, Y, c=colors, s=sizes)
    plot_durations(plt, tasks, processors_count, processors_colors)
    plt.set_xlabel("time")
    plt.set_ylabel("processors tasks")

class OnUsageExceeded:
    REJECT=auto()
    SPLIT=auto()

class Processor(object):
    def __init__(self, tasks, on_usage_exceeded=OnUsageExceeded.SPLIT):
        self.tasks=tasks
        self.usage_queries=0
        self.on_usage_exceeded=on_usage_exceeded
    def most_used(self):
        result=(None, float("infinity"))
        for task in self.tasks:
            usage=task.usage
            if usage<result[1]:
                result=(task, usage)
        return result[0]
    def add_task_reject(self, task):
        copied=task.copy()
        available=1-self.usage
        if available>copied.usage:
            self.tasks.append(copied)
            return True
        else:
            return False
    def add_task_split(self, task):
        copied=task.copy()
        available=1-self.usage
        needed=copied.usage
        if available==0 or available/needed<0.1:
            most_used=self.most_used()
            if most_used.assigned/most_used.usage<0.1:
                return False
            available=most_used.assigned/2
            most_used.assigned/=2
        if available<needed:
            copied.assigned=available
        else:
            copied.assigned=copied.usage
        self.tasks.append(copied)
        return True
    def add_task(self, task):
        if self.on_usage_exceeded==OnUsageExceeded.REJECT:
            self.add_task_reject(task)
        elif self.on_usage_exceeded==OnUsageExceeded.SPLIT:
            self.add_task_split(task)
        else:
            raise ValueError("Incorrect enum value")
    @property
    def usage(self):
        self.usage_queries+=1
        usage=0
        for task in self.tasks:
            usage+=task.assigned
        return min(1, usage)
    def update_task(self, task):
        if task.assigned<1 and self.usage<1:
            task.assigned+=max(1-self.usage, task.usage)
        task.duration-=task.assigned/task.usage
    def update(self):
        new_tasks=[]
        for task in self.tasks:
            if task.duration>0:
                self.update_task(task)
                new_tasks.append(task)
        self.tasks=new_tasks
        return len(self.tasks)>0

class Policy(object):
    def __init__(self, processors_count, tasks, name=None):
        if processors_count<=0:
            raise ValueError("processes_count needs to be greater than 0")
        self.processors=[Processor([]) for _ in range(processors_count)]
        self.tasks=tasks.copy()
        self.time=0
        self.usages=[]
        self.plot_list=[[] for _ in range(processors_count)]
        if name!=None:
            self.name=name
        else:
            self.name=self.__class__.__name__

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

    def usage_queries(self):
        sum=0
        for processor in self.processors:
            sum+=processor.usage_queries
        return sum

    def summary(self):
        print(self.name)
        average_usage=self.average_usage()
        average_deviation=self.average_deviation(average_usage)
        print(f"average usage:\t\t{round(average_usage, 4)}")
        print(f"average deviation:\t{round(average_deviation, 4)}")
        print(f"usage queries:\t\t{round(self.usage_queries(), 4)}")
        print(f"end time:\t\t{round(self.time, 4)}")

    def update_plot(self):
        for processor_plot, processor in zip(self.plot_list, self.processors):
            processor_plot.append((self.time, processor.usage))

    def update(self):
        processors_need_updating=False
        for processor in self.processors:
            processors_need_updating=processors_need_updating or processor.update()
        new_tasks=[]
        for task in self.tasks:
            if task.time==self.time:
                if not self.assign_task(task):
                    task.time+=1
            else:
                new_tasks.append(task)
        self.tasks=new_tasks
        self.update_usages()
        self.update_plot()
        self.time+=1
        return len(self.tasks)>0 or processors_need_updating

    def run(self):
        while self.update():
            pass
        self.summary()
        return self

    def plot(self, plt, processors_colors):
        offset=0.5

        for index, process_plot in enumerate(self.plot_list):
            X=[element[0] for element in process_plot]
            Y=[index*(1+offset)+element[1] for element in process_plot]
            color=processors_colors[index]
            plt.plot(X, Y, '-', c=color)
            plt.set_xlabel("time")
            plt.set_ylabel("processors usage")
            plt.set_title(self.name)

class FirstPolicy(Policy):
    def __init__(self, processors_count, tasks, threshold, tries, allow_self_check=False, name=None):
        super().__init__(processors_count, tasks, name=name)
        self.threshold=threshold
        self.tries=tries
        self.allow_self_check=allow_self_check

    def select_processor(self, task):
        processors=self.processors.copy()
        if not self.allow_self_check:
            # don't allow task.processor to be checked
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

class OnFindingFailure:
    TASK=auto()
    LAST=auto()
    MIN_USAGE=auto()
                
class SecondPolicy(Policy):
    def __init__(self, processors_count, tasks, threshold, allow_self_check=False, on_finding_failure=OnFindingFailure.MIN_USAGE, name=None):
        super().__init__(processors_count, tasks, name=name)
        self.threshold=threshold
        self.allow_self_check=allow_self_check
        self.on_finding_failure=on_finding_failure

    def select_processor(self, task):
        if self.processors[task.processor].usage<self.threshold:
            return self.processors[task.processor]

        min_usage=(self.processors[task.processor], self.processors[task.processor].usage)
        
        processors=self.processors.copy()
        if not self.allow_self_check:
            # don't allow task.processor to be checked
            del processors[task.processor]
        
        while len(processors)>0:
            processor=random.choice(processors)
            usage=processor.usage
            if usage<min_usage[1]:
                min_usage=(processor, usage)
            if usage<self.threshold:
                return processor
            else:
                processors.remove(processor)
        if self.on_finding_failure==OnFindingFailure.TASK:
            return self.processors[task.processor]
        elif self.on_finding_failure==OnFindingFailure.LAST:
            return processor
        elif self.on_finding_failure==OnFindingFailure.MIN_USAGE:
            return min_usage[0]
        else:
            raise ValueError("Incorrect enum value")

class MovedType:
    COUNT=auto()
    USAGE=auto()

class ThirdPolicy(SecondPolicy):
    def __init__(self, processors_count, tasks, threshold, transfer_treshold, moved, moved_type=MovedType.COUNT, allow_self_check=False, name=None):
        super().__init__(processors_count, tasks, threshold=threshold, allow_self_check=allow_self_check, name=name)
        self.transfer_treshold=transfer_treshold
        self.moved=moved
        self.moved_type=moved_type
        self.migrations=0

    def transfer_tasks(self, source, destination):
        if self.moved_type==MovedType.COUNT:
            # self.moved is percentage of tasks moved from source to destination
            moved=int(len(source.tasks)*self.moved)
            tasks=source.tasks
            destination.tasks=tasks[moved:]
            rest=len(tasks)-moved
            source.tasks=tasks[:rest]
            self.migrations+=moved
        elif self.moved_type==MovedType.USAGE:
            tasks=source.tasks.copy()
            tasks.sort(key=attrgetter("usage"))
            to_move=source.usage*self.moved
            while to_move>0 and len(tasks)>0:
                task=tasks.pop(0)
                source.tasks.remove(task)
                destination.tasks.append(task)
                self.migrations+=1
                to_move-=task.usage

    def summary(self):
        super().summary()
        print(f"migrations:\t\t{self.migrations}")

    def update(self):
        for processor in self.processors:
            if processor.usage<self.transfer_treshold:
                chosen=random.choice(self.processors)
                if chosen.usage>self.threshold:
                    self.transfer_tasks(chosen, processor)
        return super().update()

fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3)

PROCESSORS_COUNT=20
step=1/PROCESSORS_COUNT
PROCESSORS_COLORS=[colorsys.hls_to_rgb(step*index, 0.8, 1) for index in range(PROCESSORS_COUNT)]
random.shuffle(PROCESSORS_COLORS)
tasks=random_tasks(123, PROCESSORS_COUNT, 200, Between(0.01, 0.4), Between(1, 5), Between(10, 100))
plot_tasks(ax1, tasks, PROCESSORS_COUNT, PROCESSORS_COLORS)
FirstPolicy(PROCESSORS_COUNT, tasks, threshold=0.3, tries=3).run().plot(ax2, PROCESSORS_COLORS)
SecondPolicy(PROCESSORS_COUNT, tasks, threshold=0.3).run().plot(ax3, PROCESSORS_COLORS)
ThirdPolicy(PROCESSORS_COUNT, tasks, threshold=0.3, transfer_treshold=0.2, moved=0.5, name="ThirdPolicy(MovedType.COUNT)").run().plot(ax4, PROCESSORS_COLORS)
ThirdPolicy(PROCESSORS_COUNT, tasks, threshold=0.3, transfer_treshold=0.2, moved=0.5, moved_type=MovedType.USAGE, name="ThirdPolicy(MovedType.USAGE)").run().plot(ax5, PROCESSORS_COLORS)

plt.show()