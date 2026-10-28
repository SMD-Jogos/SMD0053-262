# Pong em Godot — Observer com sinais (Aula 19)

O mesmo Pong de `18_pong_conquistas.py`, montado no Godot 4.7.

## Como abrir

1. Abra o Godot 4.7 e escolha **Importar**.
2. Selecione o arquivo `project.godot` desta pasta.
3. Rode com **F5**. Setas ↑/↓ movem a raquete do jogador.

Para ver as áreas de colisão durante o jogo: **Depurar → Formas de Colisão Visíveis**.

## O que olhar

- `scenes/mundo.tscn`: a cena principal. O nó `World` declara os sinais `ponto(autor)`, `rebatida(autor)` e `saque()`.
- `scenes/raquete.tscn`: uma só cena para as duas raquetes; muda só o nó filho de controle (`ControleTeclado` ou `ControleSeguidor`).
- `scripts/mundo/world.gd`: recebe `area_entered` das raquetes, gols e paredes e emite os eventos do jogo.
- `scripts/conquistas/`: nove conquistas com seis scripts. Elas são conectadas por código no `_ready()` do World; o Placar é conectado pelo editor (aba Nó → Sinais).
- Camadas de colisão: `cenario` (raquetes, gols, paredes) só enxerga a camada `bola`.
