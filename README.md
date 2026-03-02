# Relic Reconstruction 🧩

Relic Reconstruction is a streamlined coding and debugging platform. This repository is designed to be ultra-clean, containing only the essential components for hosting and participating in coding challenges.

## 📁 Repository Structure

The repository is divided into two primary pillars:

### 1. Questions (`/questions`)
Contains the definitive metadata, problem statements, and **reference solutions** for all contest puzzles in a single JSON format.
- **Puzzles**: Difficulty-graded challenges (Easy, Medium, Hard).
- **Integrated Solutions**: Each JSON file includes validated solution code in multiple languages (C, C++, Java, Python).
- **Test Cases**: Definitive inputs and outputs for automated judging.

### 2. App (`/app`)
The self-contained Flask-based web application that serves the contest platform.
- **Features**: Real-time leaderboard, secure code execution, and user management.
- **Tech Stack**: Python, Flask, SQLite, SocketIO.

## 🚀 Quick Start

1. **Install Dependencies**:
   Navigate to the `app` directory and install the required Python packages:
   ```bash
   cd app
   pip install -r requirements.txt
   ```

2. **Run the Platform**:
   ```bash
   python3 app.py
   ```

---
*Relic Reconstruction: Focused on logic, debugging, and efficient algorithmic design.*
