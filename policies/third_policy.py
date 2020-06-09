from operator import attrgetter
from enum import Enum, auto
import random

from .second_policy import SecondPolicy

class ThirdPolicy(SecondPolicy):
    def __init__(self, processors_count, tasks, threshold, transfer_treshold, process_arguments=(), allow_self_check=False, name=None):
        super().__init__(processors_count, tasks, threshold=threshold, allow_self_check=allow_self_check, name=name, process_arguments=process_arguments)
        self.transfer_treshold=transfer_treshold
        self.migrations=0

    def transfer_tasks(self, source, destination, to_move):
        tasks=source.tasks.copy()
        tasks.sort(key=attrgetter("usage"))
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
                    self.transfer_tasks(chosen, processor, self.transfer_treshold-processor.usage)
        return super().update()
