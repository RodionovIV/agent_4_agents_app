from abc import ABC, abstractmethod


class AbstractAgent:
    @abstractmethod
    def create_agent(self):
        pass

    @abstractmethod
    def run_agent(self, *args, **kwargs):
        pass

    @abstractmethod
    def run(self, *args, **kwargs):
        pass
