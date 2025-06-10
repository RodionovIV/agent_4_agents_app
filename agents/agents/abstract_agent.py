from abc import ABC, abstractmethod

class Agent(ABC):
    @abstractmethod
    def create_agent(self, *args, **kwargs):
        pass

    @abstractmethod
    def run_qa_agent(self, *args, **kwargs):
        pass

