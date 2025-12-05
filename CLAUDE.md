# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**DyberPet AI Desktop Companion** - An AI-powered desktop pet application based on DyberPet, focused on AI conversation and interaction experience. The app creates an interactive desktop character with emotions, animations, and intelligent responses.

**Tech Stack**: Python 3.9+, PySide6 (Qt), qfluentwidgets, APScheduler
**Supported Platforms**: Windows, macOS, Linux

## Running the Application

### Start Application
```bash
# Primary method (recommended)
python main.py

# Alternative with uv
uv sync
uv run python main.py
```

### Run Tests
```bash
# Run comprehensive test suite (10 tests covering core functionality)
python test_complete.py

# Run basic tests
python test_basic.py
```

### Dependencies
Dependencies are managed in `pyproject.toml`:
- PySide6 with qfluentwidgets (UI framework)
- APScheduler (task scheduling)
- dashscope (Qwen AI API)
- psutil (system monitoring)
- pynput (input control)
- requests, tendo

Install via: `uv sync` or by reading pyproject.toml dependencies

## Architecture Overview

### Core Application Flow

```
main.py
  → run_DyberPet.py (DyberPetApp)
    → DyberPet/DyberPet.py (PetWidget) - Main desktop pet window
    → DyberPet/DyberSettings/DyberControlPanel.py - System settings
    → DyberPet/Dashboard/DashboardUI.py - Pet status dashboard
    → DyberPet/llm/ - AI integration (currently disabled)
```

**Entry Point**: `main.py` initializes the Qt application and launches `DyberPetApp` from `run_DyberPet.py`

**Single Instance**: Uses `tendo.singleton` to prevent multiple instances

**Settings Management**: `DyberPet/settings.py` initializes global settings, `DyberPet/conf.py` defines configuration classes

### Key Components

#### 1. **PetWidget** (`DyberPet/DyberPet.py`)
The main desktop character window. Core responsibilities:
- Renders pet animations with transparency
- Handles drag-and-drop physics (falling, bouncing)
- Manages status bars (HP, FV/favorability levels)
- Processes click interactions and context menus
- Coordinates with Animation_worker for character animations

**Important Classes**:
- `PetWidget`: Main window with frameless, always-on-top display
- `DP_HpBar`: Custom HP progress bar with tier-based colors
- `MouseMoveManager`: Handles drag movement and physics

#### 2. **Animation System** (`DyberPet/modules.py`)
Event-driven animation controller running in a separate thread.

**Core Classes**:
- `Animation_worker`: Main animation loop with probability-based action selection
- Animations are defined in `data/act_data.json` with status requirements and probabilities
- Supports HP tiers (0-50-80-100) affecting animation selection

#### 3. **LLM Integration** (`DyberPet/llm/`)
**STATUS**: Currently disabled in code (see lines 30-34 in DyberPet.py)

Modular AI system with clean separation of concerns:
- `llm_client.py`: Manages LLM API communication via worker threads
- `llm_request_manager.py`: Event queue, throttling, retry logic, structured response handling
- `api_factory.py`: Factory pattern for different API providers (Qwen/DashScope, OpenAI-compatible)
- `chatai.py`: Chat window UI with message bubbles
- `types.py`: TypedDict definitions for events, responses, pet status
- `event_queue.py`: Priority queue for AI events
- `throttle_manager.py`: Request rate limiting
- `conversation_manager.py`: Chat history management
- `software_monitor.py`: Monitors active applications for context-aware AI

**Event Flow**: User action → EventType (USER_INTERACTION, STATUS_CHANGE, etc.) → EventQueue (priority-based) → LLMClient → Structured JSON response → Action execution

**To Re-enable**: Uncomment imports in `DyberPet.py` and `run_DyberPet.py`, then connect signals

#### 4. **Dashboard** (`DyberPet/Dashboard/`)
Multi-tab interface for pet management:
- `DashboardUI.py`: Main window with tab navigation
- `statusUI.py`: HP/FV display, level progression
- `inventoryUI.py`: Item management and usage
- `animationUI.py`: Animation playlist configuration
- `buffModule.py`: Active effects/buffs display

#### 5. **Settings Panel** (`DyberPet/DyberSettings/`)
Fluent-style settings interface:
- `DyberControlPanel.py`: Main settings window with navigation
- `BasicSettingUI.py`: General settings including LLM configuration
- `PetCardUI.py`, `ItemCardUI.py`, `CharCardUI.py`: Resource management
- `GameSaveUI.py`: Save/load game state

### Data Storage

All persistent data in `data/` directory:
- `settings.json`: App configuration, window positions, LLM settings
- `pet_data.json`: HP, FV, coins, level, experience
- `act_data.json`: Animation definitions per pet character
- `task_data.json`: Task system data (feature removed but file may exist)

**Resource Structure**:
- `res/pet/[PetName]/`: Pet-specific animations and config
  - `pet_conf.json`: Pet metadata (size, physics)
  - `action/[ActionName]/`: Frame sequences for animations
- `res/items/[ItemName]/`: Item assets and definitions
- `res/icons/`: UI icons

### Platform-Specific Notes

**Path Handling** (`settings.py`, `conf.py`):
- Windows: Uses relative paths (`basedir = ''`)
- macOS/Linux: Resolves absolute paths dynamically
- Linux: Config directory at `~/.config/DyberPet/DyberPet`

**Dependencies**:
- Platform-specific pynput imports required for packaging:
  - Windows: `pynput.mouse._win32`, `pynput.keyboard._win32`
  - macOS: `pynput.mouse._darwin`, `pynput.keyboard._darwin`

## Development Patterns

### Adding New Features

1. **New Animations**: Add to pet's `act_data.json` with probability, status requirements, frame paths
2. **New Items**: Create folder in `res/items/` with `info.json` defining HP/FV effects
3. **LLM Events**: Create `StandardEvent` with `EventType` and `EventPriority`, emit via `LLMRequestManager`
4. **UI Extensions**: Use qfluentwidgets components, follow existing card-based layouts

### Signal/Slot Architecture

Heavy use of Qt signals for component communication:
- `PetWidget` emits: `hp_changed`, `fv_changed`, `note_sig` (notifications)
- `LLMRequestManager` emits: `register_bubble`, `execute_actions`, `add_chatai_response`
- Cross-component: DyberPetApp connects components (pet ↔ dashboard ↔ settings)

### Configuration Access

Settings accessed via singleton pattern:
```python
import DyberPet.settings as settings
settings.pet_data.hp  # Current HP value
settings.llm_config   # LLM configuration dict
settings.BASEDIR      # Project base directory
```

## Removed Features

The following systems have been deliberately removed to simplify focus on AI interaction:
- **Shop System** (`shopUI.py`) - No commerce/purchasing
- **Task System** (`taskUI.py`) - No quest/checklist management
- **Accessory System** (`Accessory.py`) - No character customization items

Do NOT reference these in new code. Tests verify removal (see `test_complete.py::TestFeatureCleanup`).

## Testing Philosophy

Tests focus on:
1. **File Structure**: Verifying required files exist, removed files are gone
2. **Code Quality**: Syntax validation, import checks
3. **LLM Module**: Constants and type definitions integrity
4. **Feature Cleanup**: No references to removed systems

Run `python test_complete.py` before commits to ensure 10/10 tests pass.

## Git Workflow

**Current Branch**: `cl-dev`
**No Main Branch**: PR creation may require specifying base branch manually

## Language/Localization

- Primary language: Chinese (Simplified)
- Translation files: `res/language/` (Qt .ts/.qm files)
- UI strings should support i18n via `settings.translator`

## Performance Notes

- **Startup Optimization**: Recent improvements achieved 30% faster launch (see README performance section)
- **Memory**: Reduced by 25% through cleanup
- Animation workers run in separate QThreads to avoid blocking UI
- LLM requests use worker threads with queue management to prevent freezing

## Common Debugging

**Application Won't Start**:
- Check `tendo.singleton` - only one instance allowed
- Verify PySide6 installation: `python -c "from PySide6.QtWidgets import QApplication"`

**LLM Not Responding** (when enabled):
- Check `data/settings.json` → `llm_config.enabled = true`
- Verify API key configured in settings
- Enable `debug_mode` in LLM config for verbose logging

**Animations Not Playing**:
- Verify `data/act_data.json` has entries for current pet
- Check HP tier - some animations require minimum HP
- Confirm animation frames exist in `res/pet/[PetName]/action/`

## Code Style

- Uses PySide6 (Qt6), not PyQt
- Signal naming: `sig_*` or `*_changed` patterns
- Class naming: `PascalCase` for widgets, `snake_case` for functions
- Imports: Group by stdlib → third-party → local
