from brain.router import Router


class Brain:

    def __init__(self):
        self.router = Router()

    def process(self, message: str):

        return self.router.route(message)