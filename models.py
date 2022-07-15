from dataclasses import dataclass
# Task model
@dataclass
class Task:
    name: str = None
    type: str = None
    taskstate: str = None
    excstate: str = None
    active: str = None
    motiontask: str = None

@dataclass
class TaskOptions:
    name: str

@dataclass
class Module:
    name: str = None
    type: str = None