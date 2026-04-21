# Installation
```bash
python3 -m venv .venv
```
albo uv albo co używacie


```bash
pip install -r requirements.txt
```
alsbo `uv sync` albo `pdm install`, chatgpt/google do pomocy


potem aktywacja venv-a, albo uv
```bash
# dla venv
source .venv/bin/activate
```
# Treningu

```python
python3 train.py
```
W `train.py` są również parametry configuracji: ile epok, ile gier per epokę do generacji, ile CPU


# Gra

```python
python3 play.py
```



# Notatki odnośnie modelu
W botach do szachów bardzo jest ważne na czym jest bot trenowany. Istnieją różne strategie: trening na ruchach w grach które już byli zebrane (pobiera się ogromny dataset róchów i jest robiony trening per ruch), boty grają tylko sami ze sobą (styl AlphaZero) itd.

Nasze podejście jest takie że generujemy grę, maksymalnie 240 ruchów (ruchy wybieramy jako najleprzy przy pomocy [MCTS](https://en.wikipedia.org/wiki/Monte_Carlo_tree_search) i [AlphaBetaPruning](https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning) z głębokością 3 (im większa tym lepsza)), później patrzymy kto wygrał (białe, czarne), wtedy reward jest liczony jako:
```python
result = board.result()

if result == "1-0":
    reward = 1.0
elif result == "0-1":
    reward = -1.0
else:
    print("We are here")
    reward = -0.5  # penalize draws also
```
to jest w `policy.py`. Ważną częścią wyboru ruchu jest tak zwane `policy`, czyli oceniamy liczbowo stan gry teraz i jak zrobimy ruch `n`, wtedy wybieramy który ruch zwiększy najbardziej dla nas policy. Jako policy dla tego treningu są oceniane 3 rzeczy (plik `policy.py` funkcja `evaluate`):
1. Każda figura (królowa +9, pionek +1 itd.)
2. Jakie pola zajmujemy (bliżej centra jest więcej)
3. Ile możliwych ruchów możemy wykonać (mobility) (im więcej tym lepiej)


Trenujemy model na podstawie każdego ruchu i rewardu z dodanym szumem. Generujemy 200 gier na każdą epokę, to zajmuję najwięcej czasu, bo gry są generowane wyłącznie na CPU a nie na GPU (GPU w zasadzie tu odgrywa małą role). Z racji że to jest wolne generujemy w multiprocessingu.

Model po 14 epokach jest zamieszczony także w tym repo i można z nim zagrać, nawet nie wyszedł najgorszy biorąc pod uwagę mały trening i proste `policy`. Umie bić figury wtedy gdy to jest możliwe (nawet czasami nie odrazu bie figurę, tylko czeka na najlepszy moment), nie poddaje się na [mat dziecięcy](https://babynow.decorexpro.com/pl/razvivayushchie-igry/detskij-mat-v-shahmatah/). Aczkolwiek nadal czasami wykonuje ruchy wątpliwej jakości. Być może lepsze `policy` i dłuższy trening mogą dać zysk, ponadto, jest to uczenie nadzorowane, bez RL.