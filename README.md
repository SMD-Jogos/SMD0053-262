# SMD0053 — Programação para Jogos I (2026.2)

Material de referência da disciplina **Programação para Jogos I** (SMD0053), oferecida pelo curso de Sistemas e Mídias Digitais (SMD) da UFC, semestre 2026.2.

## Conteúdo

| Aula | Tema | Material |
|---|---|---|
| 01 | Apresentação da Disciplina | [PDF](./Aula_01_-_Apresentacao_da_Disciplina.pdf) |
| 02 | Diversão, Frustração e Flow | [PDF](./Aula_02_-_Diversao_Frustracao_e_Flow.pdf) |
| 03 | SGDD e Trabalho Final | [PDF](./Aula_03_-_SGDD_e_Trabalho_Final.pdf) |
| 04 | Setup GitHub Copilot | [PDF](./Aula_04_-_Setup_GitHub_Copilot.pdf) |
| 05 | Game Loop | [PDF](./Aula_05_-_Game_Loop.pdf) |
| 06 | Dissecando o Pong da IA | [PDF](./Aula_06_-_Dissecando_o_Pong_da_IA.pdf) |
| 07 | Quem controla o tempo do jogo | [PDF](./Aula_07_-_Quem_controla_o_tempo_do_jogo.pdf) |
| 08 | Colisão | [PDF](./Aula_08_-_Colisao.pdf) |
| 09 | Quatro jeitos de controlar o tempo | [PDF](./Aula_09_-_Quatro_jeitos_de_controlar_o_tempo.pdf) |

Código de exemplo usado em aula está em [`Código/`](./Código):

| Aula | Código | O que demonstra |
|---|---|---|
| 05 | [`05_game_loop_minimo.py`](./Código/05_game_loop_minimo.py) | O ciclo mínimo: escutar, mover, desenhar. `W`/`S` movem a raquete |
| 05 | [`05_demo_interruptores.py`](./Código/05_demo_interruptores.py) | Desliga cada etapa do ciclo ao vivo: `E` escutar, `M` mover, `D` desenhar |
| 06 | [`06_pong_da_ia.py`](./Código/06_pong_da_ia.py) | O Pong gerado pela IA, com placar e oponente automático. `↑`/`↓` |
| 07 | [`07_demo_maquinas_diferentes.py`](./Código/07_demo_maquinas_diferentes.py) | O problema: `x += 5` por frame roda em velocidades diferentes em cada máquina. `1`-`4` trocam o FPS-alvo, `0` desliga o freio (vsync) |
| 07 | [`07_pong_loop_em_funcoes.py`](./Código/07_pong_loop_em_funcoes.py) | O mesmo jogo separado em `inputs()`, `update()` e `draw()` |
| 07 | [`07_pong_delta_time.py`](./Código/07_pong_delta_time.py) | Velocidade em pixels por segundo, independente da taxa de quadros |
| 08 | [`08_pong_tunelamento.py`](./Código/08_pong_tunelamento.py) | Bola veloz atravessa a raquete; `T` engasga o quadro e força o bug |
| 08 | [`08_demo_volumes_colisao.py`](./Código/08_demo_volumes_colisao.py) | Círculo, AABB, OBB, fecho convexo e malha lado a lado. `←`/`→` gira, `T`, `R` |
| 09 | [`09_demo_nao_determinismo.py`](./Código/09_demo_nao_determinismo.py) | Mesmo código, mesma jogada: `dt` fixo vs. irregular divergem a cada quique. `1`-`4` trocam o modo, `R` reinicia, `P` pausa |
| 09 | [`09_demo_movimento_fixo_desenho_variavel.py`](./Código/09_demo_movimento_fixo_desenho_variavel.py) | Movimento em passos fixos de 16ms, desenho quando a máquina consegue. `ESPAÇO` avança um passo, `T` engasga o desenho, `A` automático |

O plano de ensino completo está em [`Plano_de_Ensino_2026_2.pdf`](./Plano_de_Ensino_2026_2.pdf).

Artigo de apoio ao tema SGDD, publicado no SBGames: [`paper_SGDD.pdf`](./paper_SGDD.pdf).

## Bibliografia recomendada

- **[Game Programming Patterns](https://gameprogrammingpatterns.com/)** — Robert Nystrom. Leitura gratuita online (também disponível impresso). Referência central para os padrões de arquitetura de jogos discutidos na disciplina (Game Loop, Update Method, Component, entre outros).
- **Game Programming Algorithms and Techniques: A Platform-Agnostic Approach** — Sanjay Madhav, Addison-Wesley Professional, 2013. *(livro comercial — não distribuído neste repositório; consulte a edição impressa/digital adquirida pela biblioteca ou individualmente)*.
- **[Hands-On Intro to Game Programming](https://gamkedo.gumroad.com/l/hands-on-game-programming)** — Christer Kaitila (Gamkedo), 2019. *(livro comercial — não distribuído neste repositório; disponível para compra no Gumroad)*.

## Vídeos recomendados

- **[Botão turbo: a maior mentira do PC](https://www.youtube.com/shorts/DTsg4h-X_Kg)** — curiosidade sobre o "botão turbo" dos PCs antigos.

## Uso do material

Este material é disponibilizado para fins educacionais aos alunos da disciplina. Os slides e códigos aqui publicados são de autoria do professor, salvo quando indicada a fonte. Direitos sobre obras de terceiros citadas na bibliografia pertencem aos respectivos autores/editoras.

## Contato

- Prof. George Gomes — george@virtual.ufc.br
- Prof. Alysson Diniz — alysson@virtual.ufc.br
