from abc import ABC, abstractmethod
from typing import List
from .work_break import WorkBreak


class AbstractWork(ABC):

    @abstractmethod
    def get_start_hour(self) -> str:
        """Get the start hour to work

        :return: str eg: "7:30"
        """
        pass

    @abstractmethod
    def get_end_hour(self) -> str:
        """Get the end hour to work

        :return: str eg: "15:30"
        """
        pass

    @abstractmethod
    def get_minutes_variation(self) -> int:
        """Randomly variate the hour of start and end

        Eg:
        - start_hour: "7:30"
        - end_hour: "7:30"
        - minutes_variation: 10
        With a minimum of "7:20" - "15:20" and a max of "7:40" - "15:40"
        Possible outputs:
        · "7:32" - "15:32"
        · "7:26" - "15:26"
        ...


        :return: int eg: 10
        """
        pass

    @abstractmethod
    def get_resave(self) -> bool:
        """Can the work be overwrite

        :return: bool
        """
        pass

    @abstractmethod
    def get_breaks(self) -> List[WorkBreak]:
        """List of breaks to take, for example to breakfast

        :return: list of WorkBreak
        """
        pass
