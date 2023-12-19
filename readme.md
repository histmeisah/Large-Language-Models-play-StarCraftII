# StarCraft II Environment Documentation

## Single Agent Environments

### Mix_STARCRAFTENV
This environment interacts with a single agent playing StarCraft II. It supports both Zerg and Protoss races and uses the mixed mode (a combination of scripted and machine learned behaviour).

**Parameters:**

- `map_pool`: A list of available maps for the game.
- `map_idx`: The index of the selected map in the map pool.
- `player_race`: The race of the player. Can be either 'Zerg' or 'Protoss'.
- `opposite_race`: The race of the opponent. Can be either 'Zerg' or 'Protoss'.

### Language_STARCRAFTENV
This environment interacts with a single agent playing StarCraft II. It supports both Zerg and Protoss races and uses the language mode (based on scripted behaviour with language input).

**Parameters:**

- `map_pool`: A list of available maps for the game.
- `map_idx`: The index of the selected map in the map pool.
- `player_race`: The race of the player. Can be either 'Zerg' or 'Protoss'.
- `opposite_race`: The race of the opponent. Can be either 'Zerg' or 'Protoss'.

## Two Agent Environments

### Mix_STARCRAFTENV_2
This environment interacts with two agents playing StarCraft II. It supports both Zerg and Protoss races for both players and uses the mixed mode.

**Parameters:**

- `map_pool`: A list of available maps for the game.
- `map_idx`: The index of the selected map in the map pool.
- `player1_race`: The race of the first player. Can be either 'Zerg' or 'Protoss'.
- `player2_race`: The race of the second player. Can be either 'Zerg' or 'Protoss'.

### Language_STARCRAFTENV_2
This environment interacts with two agents playing StarCraft II. It supports both Zerg and Protoss races for both players and uses the language mode.

**Parameters:**

- `map_pool`: A list of available maps for the game.
- `map_idx`: The index of the selected map in the map pool.
- `player1_race`: The race of the first player. Can be either 'Zerg' or 'Protoss'.
- `player2_race`: The race of the second p