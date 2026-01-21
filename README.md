# Steam Sentimental

Steam game and review data collection tool.

## Project Structure

```
SteamSentimental/
├── data/                      # All JSON data files
│   ├── steam_app_list.json    # Steam app list
│   ├── game_player_data.json  # Current player counts
│   ├── reviews_data.json      # Review data
│   └── last_timestamps.json   # Tracking last fetch timestamps
├── src/                       # Python source files
│   ├── Get-SteamGames.py     # Main script
│   └── config.py             # Configuration (API token)
└── README.md                 # This file
```

## Usage

Run the main script from the project root:
```bash
python src/Get-SteamGames.py
```

## Configuration

Edit `src/config.py` to set your Steam API access token.
