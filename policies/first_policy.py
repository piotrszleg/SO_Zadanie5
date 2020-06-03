import random

from .policy import Policy

class FirstPolicy(Policy):
    def __init__(self, processors_count, tasks, threshold, tries, process_arguments=(), allow_self_check=False, name=None):
        super().__init__(processors_count, tasks, name=name, process_arguments=process_arguments)
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