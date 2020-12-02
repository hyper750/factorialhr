class WorkBreak:

    def __init__(self, start_hour: str, end_hour: str, minutes_variation: int):
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.minutes_variation = minutes_variation

    def get_start_hour(self) -> str:
        """Get the start hour of the break

        :return: str eg: "10:30"
        """
        return self.start_hour

    def get_end_hour(self) -> str:
        """Get the end hour of the break

        :return: str eg: "11:00"
        """
        return self.end_hour

    def get_minutes_variation(self) -> int:
        """Randomly variate the hour of start and end

        Eg:
        - start_hour: "10:30"
        - end_hour: "11:00"
        - minutes_variation: 15
        With a minimum of "10:15" - "10:45" and a max of "10:45" - "11:15"
        Possible outputs:
        · "10:35" - "11:05"
        · "10:40" - "11:10"
        ...

        :return: int eg: 15
        """
        return self.minutes_variation

    def __repr__(self) -> str:
        return f'{self.get_start_hour()} - {self.get_end_hour()} ~{self.get_minutes_variation()}m'
