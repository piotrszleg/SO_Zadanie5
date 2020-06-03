from enum import Enum, auto
import random

from .policy import Policy

class OnFindingFailure:
    TASK=auto()
    LAST=auto()
    MIN_USAGE=auto()

class SecondPolicy(Policy):
    def __init__(self, processors_count, tasks, threshold, process_arguments=(), on_finding_failure=OnFindingFailure.MIN_USAGE, allow_self_check=False, name=None):
        super().__init__(processors_count, tasks, name=name, process_arguments=process_arguments)
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