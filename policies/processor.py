from enum import Enum, auto

class OnUsageExceeded:
    REJECT=auto()
    SPLIT=auto()

class Processor(object):
    def __init__(self, on_usage_exceeded=OnUsageExceeded.REJECT):
        self.tasks=[]
        self.usage_queries=0
        self.rejected=0
        self.on_usage_exceeded=on_usage_exceeded
    def most_used(self):
        result=(None, float("infinity"))
        for task in self.tasks:
            usage=task.usage
            if usage<result[1]:
                result=(task, usage)
        return result[0]
    def add_task_reject(self, task):
        available=1-self.usage
        if available>task.usage:
            self.tasks.append(task)
            return True
        else:
            self.rejected+=1
            return False
    def add_task_split(self, task):
        available=1-self.usage
        needed=task.usage
        if available==0 or available/needed<0.1:
            most_used=self.most_used()
            if most_used.assigned/most_used.usage<0.1:
                self.rejected+=1
                return False
            available=most_used.assigned/2
            most_used.assigned/=2
        if available<needed:
            task.assigned=available
        else:
            task.assigned=task.usage
        self.tasks.append(task)
        return True
    def add_task(self, task):
        if self.on_usage_exceeded==OnUsageExceeded.REJECT:
            return self.add_task_reject(task)
        elif self.on_usage_exceeded==OnUsageExceeded.SPLIT:
            return self.add_task_split(task)
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