"""
Save/Load System for Samsara
Persists game progress to JSON files in the user's save directory.
Supports 3 save slots plus a separate autosave per slot.
"""

import json
import os
import sys
import time

IS_WEB = sys.platform == 'emscripten'


class SaveManager:
    """Handles saving and loading game state across sessions."""

    NUM_SLOTS = 3

    def __init__(self):
        if IS_WEB:
            self.save_dir = None
            return
        # Store saves next to the game files in a 'saves' folder
        self.save_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'saves')
        os.makedirs(self.save_dir, exist_ok=True)

    def _slot_path(self, slot, auto=False):
        suffix = '_auto' if auto else ''
        return os.path.join(self.save_dir, f'slot_{slot}{suffix}.json')

    def save_game(self, slot, game, auto=False):
        """
        Save the full game state to a slot.

        Args:
            slot: Slot number (1..NUM_SLOTS)
            game: The Game object to read state from
            auto: If True, write to the autosave file for the slot
        Returns:
            bool success
        """
        if IS_WEB:
            return False
        try:
            data = {
                'version': 1,
                'timestamp': time.time(),
                'play_time': game.play_time,
                'past_life_key': game.current_past_life_key,
                'stats': {
                    'merit': game.stats.merit,
                    'karma': game.stats.karma,
                    'wisdom': game.stats.wisdom,
                    'clarity': game.stats.clarity,
                },
                'player': {
                    'x': game.player.x,
                    'y': game.player.y,
                },
                'npcs': game.npc_manager.to_dict(),
                'obstacles_destroyed': game.obstacles_destroyed,
                'npcs_helped_count': game.npcs_helped_count,
                'current_realm': game.current_realm_name,
            }
            with open(self._slot_path(slot, auto), 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Save failed: {e}")
            return False

    def load_game(self, slot, prefer_auto=False):
        """
        Load saved data from a slot. Returns the data dict or None.
        If prefer_auto is True and an autosave is newer, load that instead.
        """
        if IS_WEB:
            return None
        manual_path = self._slot_path(slot, auto=False)
        auto_path = self._slot_path(slot, auto=True)

        path = manual_path
        if prefer_auto and os.path.exists(auto_path):
            # Pick whichever is newer
            auto_t = os.path.getmtime(auto_path) if os.path.exists(auto_path) else 0
            man_t = os.path.getmtime(manual_path) if os.path.exists(manual_path) else 0
            path = auto_path if auto_t >= man_t else manual_path

        if not os.path.exists(path):
            # Fall back to whichever exists
            if os.path.exists(auto_path):
                path = auto_path
            elif os.path.exists(manual_path):
                path = manual_path
            else:
                return None
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Load failed: {e}")
            return None

    def get_slot_info(self, slot):
        """
        Return a short summary of a slot for the load menu, or None if empty.
        """
        if IS_WEB:
            return None
        manual_path = self._slot_path(slot, auto=False)
        auto_path = self._slot_path(slot, auto=True)

        path = None
        if os.path.exists(manual_path) and os.path.exists(auto_path):
            path = manual_path if os.path.getmtime(manual_path) >= \
                os.path.getmtime(auto_path) else auto_path
        elif os.path.exists(manual_path):
            path = manual_path
        elif os.path.exists(auto_path):
            path = auto_path

        if not path:
            return None
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            return {
                'realm': data.get('current_realm', 'unknown'),
                'wisdom': data.get('stats', {}).get('wisdom', 0),
                'merit': data.get('stats', {}).get('merit', 0),
                'karma': data.get('stats', {}).get('karma', 0),
                'play_time': data.get('play_time', 0),
                'timestamp': data.get('timestamp', 0),
                'is_auto': path.endswith('_auto.json'),
            }
        except Exception:
            return None

    def slot_exists(self, slot):
        if IS_WEB:
            return False
        return (os.path.exists(self._slot_path(slot, False)) or
                os.path.exists(self._slot_path(slot, True)))

    def delete_slot(self, slot):
        if IS_WEB:
            return
        for auto in (False, True):
            p = self._slot_path(slot, auto)
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

    @staticmethod
    def format_play_time(seconds):
        """Format seconds as Hh Mm or Mm Ss."""
        seconds = int(seconds)
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        if h > 0:
            return f"{h}h {m}m"
        if m > 0:
            return f"{m}m {s}s"
        return f"{s}s"
