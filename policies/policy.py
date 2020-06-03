from .processor import Processor
from termcolor import cprint

class Policy(object):
    def __init__(self, processors_count, tasks, name=None, process_arguments=()):
        if processors_count<=0:
            raise ValueError("processes_count needs to be greater than 0")
        self.processors=[Processor(*process_arguments) for _ in range(processors_count)]
        self.tasks=tasks
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
        return self.select_processor(task).add_task(task)

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

    def rejected(self):
        sum=0
        for processor in self.processors:
            sum+=processor.rejected
        return sum

    def summary(self):
        cprint(self.name, attrs=['underline'])
        average_usage=self.average_usage()
        average_deviation=self.average_deviation(average_usage)
        digits_shown=4
        print(f"average usage:\t\t{round(average_usage, digits_shown)}")
        print(f"average deviation:\t{round(average_deviation, digits_shown)}")
        print(f"usage queries:\t\t{round(self.usage_queries(), digits_shown)}")
        print(f"rejected:\t\t{round(self.rejected(), digits_shown)}")
        print(f"end time:\t\t{round(self.time, digits_shown)}")

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
                    new_tasks.append(task)
                #else delete the task by not appending it to new tasks
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