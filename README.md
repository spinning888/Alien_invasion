# 🚀 Alien Invasion Game

## 📋 Project Overview

Alien Invasion is a lightweight ez 2D shooting game written in Python, also a friendly python project for beginners.

#  Backgroud story
Pilot your spaceship up, down, left, and right to fire bullets and shoot down alien named Taffy to protect our homeland!

Try your best to clear an entire alien fleet to advance to the next level, with increasing difficulty. You have 3 lives per game: losing one when aliens reach the bottom, collide with your ship, or hit you with their bombs. Survive more waves and achieve a higher score to win!

## 🔧 Tech Stack

| Technology | Description |
|------------|-------------|
| python | 3.12+ |
| pygame | 2.6+ |
| VSCode | Bset editor ever in the world|

## ⚙️ Installation & Run

1. Install the pygame dependency

```bash
python -m pip install pygame
```

or use PyPI mirror

```bash
python3 -m pip install -i https://mirrors.aliyun.com/pypi/simple/ pygame
```

2. Run the game

```bash
python main.py
```

## 🎮 Game Controls

| Key | Function |
|-----|----------|
| `←` `→` | Move spaceship |
| `Space` | Fire bullets |
| `Ctrl` | Activate shield for ship |
| `Q` | Quit game |

## 🛡️ Features

- **Shield System** - Energy shield protection with 8s duration, 3s cooldown
- **Smart Taffy** - Aliens with burst shooting mode
- **Visual Effects** - Explosion animations and particle effects
- **Dynamic Difficulty** - Speed increases with each level
- **High Score all time** - Save and track your best performance, but only local

## 📁 Project Structure

```
alien_invasion/
├── main.py              # Main game loop
├── settings.py          # Game configuration
├── ship.py             # Player spaceship
├── alien.py            # Enemy aliens
├── bullet.py           # Player bullets
├── shield.py           # Shield system
├── images/             # Game sprites
└── sounds/             # Audio files 
```

---

🎮 **Enjoy the game and challenge your high score!** 🚀
