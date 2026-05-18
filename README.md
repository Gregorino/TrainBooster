# TrainBooster

Are you stuck at 0.96 accuracy and want to achieve 1.0?

## Installation

```bash
pip install git+https://github.com/Gregorino/TrainBooster.git
```

Make sure you have `ffmpeg` installed:
- **macOS:** `brew install ffmpeg`
- **Ubuntu/Debian:** `apt-get install ffmpeg`
- **Windows:** `choco install ffmpeg`

## Usage

### Quick boost (one-time)
Play a motivational sound once without blocking your code:

```python
from TrainBooster import boost

boost()
train_model()  # Your training continues while audio plays
```

### Continuous boost (context manager)
Play motivational audio continuously throughout your training:

```python
from TrainBooster import booster

with booster():
    for epoch in range(100):
        train()
    # Audio stops automatically when training is done
```

**Result:** 1.0 accuracy or above is guaranteed! 🚀
