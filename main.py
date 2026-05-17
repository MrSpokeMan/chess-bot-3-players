import multiprocessing as mp
import random
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm

from model import ChessNet
from policy import generate_game

NUM_GAMES = 200
EPOCHS = 15
CPUS = mp.cpu_count()


def train():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = ChessNet().to(device)

    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.MSELoss()

    for epoch in range(EPOCHS):
        print(f"\nEpoch {epoch + 1}")

        with mp.Pool(CPUS) as pool:
            results = list(
                tqdm(pool.imap(generate_game, range(NUM_GAMES)), total=NUM_GAMES)
            )

        dataset = []
        for states, reward in results:
            for tensor_np, score in states:
                tensor = torch.from_numpy(tensor_np)
                target = 0.7 * np.tanh(score) + 0.3 * reward
                dataset.append((tensor, target))

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
        
        Path("models").mkdir(exist_ok=True)

        torch.save(
            model.state_dict(),
            f"models/chess_model-life-board_{epoch + 1}_loss_{total_loss / len(batches):.4f}.pth"
        )
        print("Saved model!")


if __name__ == "__main__":
    train()
