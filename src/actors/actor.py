class Actor:
    def __init__(self, name):
        self.name = name
        self.abilities = {}

    def can(self, ability):
        self.abilities[type(ability)] = ability
        return self

    def ability_to(self, ability_class):
        return self.abilities[ability_class]

    def attempts_to(self, *tasks):
        for task in tasks:
            task.perform_as(self)
        return self

    def asks(self, question):
        return question.answered_by(self)
