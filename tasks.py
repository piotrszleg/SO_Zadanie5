from dataclasses import dataclass
import random
from between import Between

@dataclass
class Task(object):
    processor:int
    time:int
    usage:float
    duration:int
    assigned:int=1
    def copy(self):
        return Task(**self.__dict__)

def random_tasks(seed, processors_count, count, usage, time_distance, duration):
    random.seed(seed)
    time=0
    result=[]
    for _ in range(count):
        result.append(Task(random.randrange(0, processors_count), time, usage.random(), duration.random()))
        time+=time_distance.random()
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