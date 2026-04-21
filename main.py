import multiprocessing as mp
import random

import chess
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm

from model import ChessNet
from policy import generate_game

# ==========================================
# Config
# ==========================================

NUM_GAMES = 200  # ile gier per epoka
EPOCHS = 15
CPUS = 16  # dla multiprocessingu


def board_to_tensor(board):
    pieces = ["P", "N", "B", "R", "Q", "K", "p", "n", "b", "r", "q", "k"]
    tensor = np.zeros((13, 8, 8), dtype=np.float32)

    for i in range(64):
        piece = board.piece_at(i)
        if piece:
            r, c = divmod(i, 8)
            tensor[pieces.index(piece.symbol())][r][c] = 1.0

    tensor[12].fill(1.0 if board.turn else -1.0)
    return torch.from_numpy(tensor)


# ==========================================
# Training Loop
# ==========================================
def train():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = ChessNet().to(device)

    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.MSELoss()

    for epoch in range(EPOCHS):
        print(f"\nEpoch {epoch + 1}")

        dataset = []

        with mp.Pool(CPUS) as pool:
            results = list(
                tqdm(pool.imap(generate_game, range(NUM_GAMES)), total=NUM_GAMES)
            )

        for states, reward in results:
            for fen, score in states:
                board = chess.Board(fen)
                tensor = board_to_tensor(board)

                # mix heuristic + outcome
                target = 0.7 * np.tanh(score) + 0.3 * reward
                dataset.append((tensor, target))

        # training
        model.train()
        batch_size = 256

        random.shuffle(dataset)
        batches = [
            dataset[i : i + batch_size] for i in range(0, len(dataset), batch_size)
        ]

        total_loss = 0

        for batch in tqdm(batches):
            states = torch.stack([x[0] for x in batch]).to(device)
            targets = (
                torch.tensor([x[1] for x in batch], dtype=torch.float32)
                .unsqueeze(1)
                .to(device)
            )

            optimizer.zero_grad()
            preds = model(states)
            loss = loss_fn(preds, targets)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print("Loss:", total_loss / len(batches))

        torch.save(model.state_dict(), "chess_model.pth")
        print("Saved model!")


if __name__ == "__main__":
    train()
