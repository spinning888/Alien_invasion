# 🚀 Alien Invasion Game

# 🏆 News
[Nov.20] First release : Base Version.

## 📋 Project Overview

Alien Invasion is a lightweight and ez game written in Python, also a friendly python project for beginners.

#  Background story
Pilot your spaceship left, and right to fire bullets and shoot down alien named Taffy to protect our homeland!

Try your best to eliminate the entire alien fleet to progress to the next level, with difficulty gradually increasing. You have 3 lives per game: you’ll lose one if aliens reach the bottom, collide with your spaceship, or hit you with their bombs. Survive more waves and earn a higher score to claim victory!

## 🔧 Tech Stack

| Technology | Description |
|------------|-------------|
| python | 3.12+ |
| pygame | 2.6+ |
| VSCode | Best editor ever in the world|

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

## ✨ Contacts

Any issues, feel free to contact the author:

📧 **Email:** [2024150065@mails.szu.edu.cn](mailto:2024150065@mails.szu.edu.cn)

🎮 **Enjoy the game and challenge your high score!** 🚀
