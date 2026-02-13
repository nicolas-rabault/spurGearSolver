from dataclasses import dataclass


@dataclass(frozen=True)
class SingleGear:
    name: str
    teeth: int
    module: float

    def diameter(self) -> float:
        return self.teeth * self.module

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class CompoundGear:
    name: str
    big: SingleGear
    small: SingleGear

    def __str__(self) -> str:
        return self.name


@dataclass
class Stage:
    driver_teeth: int
    driven_teeth: int
    module: float
    ratio: float


@dataclass
class Solution:
    gears: list  # list[SingleGear | CompoundGear]
    ratio: float
    stages: list[Stage]
