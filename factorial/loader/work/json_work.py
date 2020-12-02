import json
from typing import List

from .abstract_work import AbstractWork
from .work_break import WorkBreak


class JsonWork(AbstractWork):

    def __init__(self, filename: str):
        super().__init__()

        self.filename = filename
        with open(filename, "r") as f:
            settings = json.load(f)

            context = settings.get('work', {})
            self.start_hour = context.get('start')
            self.end_hour = context.get('end')
            self.minutes_variation = context.get('minutes_variation')
            self.resave = context.get('resave')

            self.breaks = [
                WorkBreak(
                    start_hour=work_break.get('start'),
                    end_hour=work_break.get('end'),
                    minutes_variation=work_break.get('minutes_variation')
                )
                for work_break in context.get('breaks', [])
            ]

    def get_start_hour(self) -> str:
        """Get the start hour to work

        :return: str eg: "7:30"
        """
        return self.start_hour

    def get_end_hour(self) -> str:
        """Get the end hour to work

        :return: str eg: "15:30"
        """
        return self.end_hour

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
        return self.minutes_variation

    def get_resave(self) -> bool:
        """Can the work be overwrite

        :return: bool
        """
        return self.resave

    def get_breaks(self) -> List[WorkBreak]:
        """List of breaks to take, for example to breakfast

        :return: list of WorkBreak
        """
        return self.breaks
