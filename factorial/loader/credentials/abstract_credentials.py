from abc import ABC, abstractmethod


class AbstractCredentials(ABC):

    @abstractmethod
    def get_email(self) -> str:
        """Get email to login to factorialhr

        :return: string
        """
        pass

    @abstractmethod
    def get_password(self) -> str:
        """Get password to login to factorialhr

        :return: string
        """
        pass
