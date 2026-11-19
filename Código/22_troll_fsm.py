"""
Exemplo de FSM / State Pattern: Troll
Tradução didática do projeto C++ recebido em FSMBase.zip.

Execute este arquivo com:
    python 22_troll_fsm.py
"""


class State:
    """Classe-base para os estados do Troll."""

    def execute(self, agent):
        """Cada estado concreto deve implementar este método."""
        raise NotImplementedError("O estado precisa implementar execute().")


class StateSleep(State):
    """Estado em que o Troll está dormindo."""

    def execute(self, agent):
        print("Sleeping")
        print(f"Fome: {agent.fome}")
        agent.fome += 1


class Troll:
    def __init__(self, initial_state):
        # O Troll começa no estado recebido como argumento.
        self.current_state = initial_state

        self.vida = 10
        self.fome = 0

    def update(self):
        # O Troll delega o comportamento ao estado atual.
        self.current_state.execute(self)

    def change_state(self, state):
        # Troca o objeto que representa o estado atual.
        self.current_state = state


def main():
    # Cria o estado e passa esse estado para o Troll.
    sleep = StateSleep()
    troll = Troll(sleep)

    game_on = True

    while game_on:
        troll.update()

        print("Digite 0 para sair, 1 para avancar o turno")
        try:
            user_input = int(input())
        except ValueError:
            print("Entrada inválida. Digite 0 ou 1.")
            continue

        if user_input == 0:
            game_on = False

    print("End game")


if __name__ == "__main__":
    main()
