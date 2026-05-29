"""
Main Game Engine
Handles game loop, state management, and coordinates all systems
"""

import asyncio
import pygame
import sys
import time
import config
from player import Player
from stats import PlayerStats
from world import World
from visual_effects import VisualEffects
from encounter_system import EncounterSystem
from npc import NPCManager
from ui import UI
from obstacles import ObstacleManager
from audio import AudioManager
from save_system import SaveManager
from progress import ProgressTracker
from screens import Screens
from glossary import GLOSSARY

class Game:
    """Main game class that manages everything"""
    
    def __init__(self):
        """Initialize game"""
        import sys
        _is_web = sys.platform == 'emscripten'
        if not _is_web:
            # pre_init MUST happen before pygame.init() so the mixer
            # is created with the correct sample rate and buffer size.
            pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        if _is_web:
            pygame.mixer.quit()
        
        self._is_web = _is_web

        # On web: render internally at full res, display at 960x540 (fits any screen)
        if _is_web:
            self._window = pygame.display.set_mode((960, 540))
            self.screen = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            self._scaled = pygame.Surface((960, 540))  # pre-allocated, reused every frame
        else:
            self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            self._scaled = None
        pygame.display.set_caption(config.TITLE)

        # Clock for FPS
        self.clock = pygame.time.Clock()

        # Fonts — SysFont on web avoids the glyph-substitution (i→I) bug
        if _is_web:
            self.font_large  = pygame.font.SysFont('freesansbold', config.FONT_SIZE_LARGE)
            self.font_medium = pygame.font.SysFont('freesansbold', config.FONT_SIZE_MEDIUM)
            self.font_small  = pygame.font.SysFont('freesansbold', config.FONT_SIZE_SMALL)
        else:
            self.font_large  = pygame.font.Font(None, config.FONT_SIZE_LARGE)
            self.font_medium = pygame.font.Font(None, config.FONT_SIZE_MEDIUM)
            self.font_small  = pygame.font.Font(None, config.FONT_SIZE_SMALL)
        
        # Game state
        self.state = config.STATE_MENU
        self.running = True
        
        # Past life selection
        self.past_life_index = 0
        self.past_life_keys = list(config.PAST_LIFE_SCENARIOS.keys())
        
        # UI system (needed for menus)
        self.ui = UI()
        self.screens = Screens()

        # Persistent / cross-session systems
        self.audio = AudioManager(verbose=True)   # prints status at launch
        self.save_manager = SaveManager()

        # Menu navigation
        self.menu_index = 0          # main menu selection
        self.load_slot_index = 1     # load menu selection
        self.glossary_scroll = 0     # glossary scroll position
        self.has_save = any(self.save_manager.slot_exists(s)
                            for s in range(1, SaveManager.NUM_SLOTS + 1))

        # State to return to after closing an overlay
        self.return_state = config.STATE_EXPLORATION

        # Pre-allocated aura surfaces — reused each frame to avoid per-frame allocation
        self._mara_aura_surfs = None
        self._buddha_aura_surfs = None

        # Game systems (initialized when game starts)
        self.player = None
        self.stats = None
        self.world = None
        self.visual_effects = None
        self.encounter_system = None
        self.npc_manager = None
        self.obstacle_manager = None  # Mini-Mara obstacles!
        self.progress = None          # journal/achievement tracker

        # Progress / session tracking
        self.current_past_life_key = None
        self.current_realm_name = 'human'
        self.play_time = 0.0          # seconds played this save
        self.obstacles_destroyed = 0
        self.npcs_helped_count = 0
        self.active_slot = 1          # slot used for autosave
        self.autosave_timer = 0.0     # seconds since last autosave
        self._first_npc_hint_shown = False
        self._first_obstacle_hint_shown = False

        # Meditation mini-game state
        self.med_breath = 0.0
        self.med_focus = 0.0
        self.med_time_left = 0.0
        self.med_distraction_timer = 0.0

        # Notification system
        self.notification_message = ""
        self.notification_timer = 0

        # Current NPC being interacted with
        self.current_npc = None
        
    def initialize_game(self, starting_realm, starting_stats):
        """
        Initialize game systems with starting conditions
        
        Args:
            starting_realm: Which realm to spawn in
            starting_stats: Initial stat values
        """
        # Create game systems - pass starting_realm for clarity adjustment
        self.stats = PlayerStats(starting_realm=starting_realm)
        self.stats.set_starting_stats(starting_stats)
        
    def initialize_game(self, starting_realm, starting_stats, past_life_key=None):
        """
        Initialize game systems with starting conditions
        
        Args:
            starting_realm: Which realm to spawn in
            starting_stats: Initial stat values
            past_life_key: Key of chosen past life (for saving)
        """
        # Create game systems - pass starting_realm for clarity adjustment
        self.stats = PlayerStats(starting_realm=starting_realm)
        self.stats.set_starting_stats(starting_stats)
        
        self.world = World()
        self.visual_effects = VisualEffects()
        self.encounter_system = EncounterSystem()
        self.npc_manager = NPCManager()
        self.obstacle_manager = ObstacleManager()
        self.progress = ProgressTracker()
        
        # Session tracking
        self.current_past_life_key = past_life_key
        self.current_realm_name = starting_realm
        self.play_time = 0.0
        self.obstacles_destroyed = 0
        self.npcs_helped_count = 0
        self.autosave_timer = 0.0
        self._first_npc_hint_shown = False
        self._first_obstacle_hint_shown = False
        
        # Spawn initial mini-Mara obstacles
        self.obstacle_manager.spawn_obstacles(15)
        
        # Create player at spawn position for realm
        self.player = Player(0, 0)
        spawn_x, spawn_y = self.player.get_spawn_position_for_realm(starting_realm)
        self.player.set_position(spawn_x, spawn_y)
        
        # Update camera
        self.world.update_camera(self.player.x, self.player.y)
        
        # Record starting realm and set ambient sound
        self.progress.record_realm_visited(starting_realm)
        self.audio.set_ambient(starting_realm)
        
        # Show welcome notification
        realm_names = {
            'hell': 'Hell Realm',
            'hungry_ghost': 'Hungry Ghost Realm',
            'animal': 'Animal Realm',
            'human': 'Human Realm',
            'asura': 'Asura Realm',
            'deva': 'Deva Realm'
        }
        realm_name = realm_names.get(starting_realm, starting_realm)
        self.show_notification(f"You have been born into the {realm_name}", 240)
        
    async def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(config.FPS)

            self.handle_events()
            self.update()
            self.render()
            await asyncio.sleep(0)

        pygame.quit()
        
    def handle_events(self):
        """Handle all input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            if self.state == config.STATE_MENU:
                self.handle_menu_input(event)
            elif self.state == config.STATE_LOAD_MENU:
                self.handle_load_menu_input(event)
            elif self.state == config.STATE_PAST_LIFE_SELECTION:
                self.handle_past_life_input(event)
            elif self.state == config.STATE_PAST_LIFE_STORY:
                self.handle_past_life_story_input(event)
            elif self.state == config.STATE_TUTORIAL:
                self.handle_tutorial_input(event)
            elif self.state == config.STATE_EXPLORATION:
                self.handle_exploration_input(event)
            elif self.state == config.STATE_ENCOUNTER:
                self.handle_encounter_input(event)
            elif self.state == config.STATE_PAUSE:
                self.handle_pause_input(event)
            elif self.state == config.STATE_JOURNAL:
                self.handle_journal_input(event)
            elif self.state == config.STATE_GLOSSARY:
                self.handle_glossary_input(event)
            elif self.state == config.STATE_HELP:
                self.handle_help_input(event)
            elif self.state == config.STATE_MEDITATION:
                self.handle_meditation_input(event)
            elif self.state == config.STATE_VICTORY:
                self.handle_victory_input(event)
                
    def handle_menu_input(self, event):
        """Handle input on menu screen"""
        if event.type == pygame.KEYDOWN:
            # Build menu options dynamically (Continue only if a save exists)
            options = self._menu_options()
            if event.key in (pygame.K_UP, pygame.K_w):
                self.menu_index = (self.menu_index - 1) % len(options)
                self.audio.play('select')
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.menu_index = (self.menu_index + 1) % len(options)
                self.audio.play('select')
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.audio.play('confirm')
                choice = options[self.menu_index]
                if choice == 'New Journey':
                    self.state = config.STATE_PAST_LIFE_SELECTION
                elif choice == 'Continue':
                    self.load_slot_index = 1
                    self.state = config.STATE_LOAD_MENU
                elif choice == 'How to Play':
                    self.return_state = config.STATE_MENU
                    self.state = config.STATE_HELP
                elif choice == 'Glossary':
                    self.return_state = config.STATE_MENU
                    self.glossary_scroll = 0
                    self.state = config.STATE_GLOSSARY

    def _menu_options(self):
        """Return current main-menu options."""
        self.has_save = any(self.save_manager.slot_exists(s)
                            for s in range(1, SaveManager.NUM_SLOTS + 1))
        options = ['New Journey']
        if self.has_save:
            options.append('Continue')
        options += ['How to Play', 'Glossary']
        return options

    def handle_load_menu_input(self, event):
        """Handle input on the load/continue menu."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.load_slot_index = max(1, self.load_slot_index - 1)
                self.audio.play('select')
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.load_slot_index = min(SaveManager.NUM_SLOTS,
                                           self.load_slot_index + 1)
                self.audio.play('select')
            elif event.key == pygame.K_RETURN:
                if self.save_manager.slot_exists(self.load_slot_index):
                    self.audio.play('confirm')
                    self.load_into_game(self.load_slot_index)
            elif event.key == pygame.K_ESCAPE:
                self.state = config.STATE_MENU
                self.menu_index = 0
                
    def handle_past_life_input(self, event):
        """Handle input on past life selection screen"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.past_life_index = (self.past_life_index - 1) % len(self.past_life_keys)
                self.audio.play('select')
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.past_life_index = (self.past_life_index + 1) % len(self.past_life_keys)
                self.audio.play('select')
            elif event.key == pygame.K_SPACE:
                # View full story for selected past life
                self.state = config.STATE_PAST_LIFE_STORY
            elif event.key == pygame.K_RETURN:
                # Start game with selected past life
                self.audio.play('confirm')
                selected_key = self.past_life_keys[self.past_life_index]
                scenario = config.PAST_LIFE_SCENARIOS[selected_key]
                
                starting_realm = scenario['starting_realm']
                starting_stats = scenario['starting_stats']
                
                self.initialize_game(starting_realm, starting_stats,
                                     past_life_key=selected_key)
                # Show tutorial on first ever play (no saves existed)
                if not self.has_save:
                    self.state = config.STATE_TUTORIAL
                else:
                    self.state = config.STATE_EXPLORATION
    
    def handle_past_life_story_input(self, event):
        """Handle input while viewing past life story"""
        if event.type == pygame.KEYDOWN:
            # Any key returns to selection
            self.state = config.STATE_PAST_LIFE_SELECTION

    def handle_tutorial_input(self, event):
        """Dismiss the first-time tutorial."""
        if event.type == pygame.KEYDOWN:
            self.state = config.STATE_EXPLORATION

    def handle_pause_input(self, event):
        """Handle the pause menu: resume, save, glossary, help, quit."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = config.STATE_EXPLORATION
            elif event.key == pygame.K_s:
                # Manual save to the active slot
                if self.save_manager.save_game(self.active_slot, self):
                    self.show_notification(
                        f"Game saved to Slot {self.active_slot}", 150)
                self.state = config.STATE_EXPLORATION
            elif event.key == pygame.K_h:
                self.return_state = config.STATE_PAUSE
                self.state = config.STATE_HELP
            elif event.key == pygame.K_g:
                self.return_state = config.STATE_PAUSE
                self.glossary_scroll = 0
                self.state = config.STATE_GLOSSARY
            elif event.key == pygame.K_q:
                # Save and quit to menu
                self.save_manager.save_game(self.active_slot, self, auto=True)
                self.audio.stop_ambient()
                self.state = config.STATE_MENU
                self.menu_index = 0

    def handle_journal_input(self, event):
        """Close the journal."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_j, pygame.K_ESCAPE):
                self.state = config.STATE_EXPLORATION

    def handle_glossary_input(self, event):
        """Scroll or close the glossary."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_g, pygame.K_ESCAPE):
                self.state = self.return_state
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                if self.glossary_scroll + 4 < len(GLOSSARY):
                    self.glossary_scroll += 4
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.glossary_scroll = max(0, self.glossary_scroll - 4)

    def handle_help_input(self, event):
        """Close the help screen."""
        if event.type == pygame.KEYDOWN:
            self.state = self.return_state

    def handle_meditation_input(self, event):
        """Handle meditation mini-game input."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._end_meditation()
            elif event.key == pygame.K_SPACE:
                # Noting a distraction builds focus (mindfulness practice)
                if self.med_distraction_timer <= 0:
                    self.med_focus = min(1.0, self.med_focus + 0.08)

    def handle_victory_input(self, event):
        """Allow returning to menu from victory screen."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_SPACE):
                self.audio.stop_ambient()
                self.state = config.STATE_MENU
                self.menu_index = 0
                
    def handle_exploration_input(self, event):
        """Handle input during exploration"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = config.STATE_PAUSE
            elif event.key == pygame.K_e:
                # Try to interact with NPC first, then encounters
                self.try_interact()
            elif event.key == pygame.K_x:
                # Attack nearby mini-Mara obstacle!
                self.try_attack_obstacle()
            elif event.key == pygame.K_j:
                self.state = config.STATE_JOURNAL
            elif event.key == pygame.K_g:
                self.return_state = config.STATE_EXPLORATION
                self.glossary_scroll = 0
                self.state = config.STATE_GLOSSARY
            elif event.key == pygame.K_h:
                self.return_state = config.STATE_EXPLORATION
                self.state = config.STATE_HELP
            elif event.key == pygame.K_m:
                self._start_meditation()
            elif event.key == pygame.K_p:
                muted = self.audio.toggle_mute()
                self.show_notification(
                    "Sound muted" if muted else "Sound on", 90)
                if not muted:
                    self.audio.set_ambient(self.current_realm_name)
            elif event.key == pygame.K_F1:
                # Audio diagnostic — prints to terminal
                print("\n── Audio Diagnostic ──────────────────────")
                print(f"  pygame mixer init : {pygame.mixer.get_init()}")
                print(f"  AudioManager.enabled : {self.audio.enabled}")
                print(f"  AudioManager.muted   : {self.audio.muted}")
                print(f"  Sounds loaded : {list(self.audio.sounds.keys())}")
                print(f"  Current ambient : {self.audio.current_ambient}")
                print("───────────────────────────────────────────\n")
                
    def handle_encounter_input(self, event):
        """Handle input during encounter"""
        consequences = self.encounter_system.handle_input(event)
        
        if consequences:
            # Check if Buddha gave final teaching (GAME WON!)
            if 'game_won' in consequences and consequences['game_won']:
                self.state = config.STATE_VICTORY
                return
            
            # SAVE PREVIOUS STATS before applying changes (for progress display!)
            self.encounter_system.previous_merit = self.stats.merit
            self.encounter_system.previous_karma = self.stats.karma
            self.encounter_system.previous_wisdom = self.stats.wisdom
            
            # Apply consequences to stats
            self.stats.apply_consequences(consequences)
            
            # If this was an NPC interaction, update NPC state
            if self.current_npc:
                if 'npc_state' in consequences:
                    self.current_npc.update_state(consequences['npc_state'])
                    if consequences['npc_state'] in ['helped_once', 'transformed', 'enlightened']:
                        self.current_npc.mark_helped()
                        # Record helping this being for journal/achievements
                        npc_id = getattr(self.current_npc, 'id', None)
                        if npc_id and self.progress:
                            already = npc_id in self.progress.npcs_helped
                            helpable = max(1, len(self.npc_manager.npcs) - 2)
                            self.progress.record_npc_helped(npc_id, helpable)
                            if not already:
                                self.npcs_helped_count = len(self.progress.npcs_helped)
                            # Check hell-cleared achievement
                            hell_ids = {nid for nid, n in self.npc_manager.npcs.items()
                                        if n.realm == 'hell'}
                            self.progress.check_hell_cleared(hell_ids)
                self.current_npc.advance_dialogue()
            
            # Play a sound matching the dominant stat change
            self._play_consequence_sound(consequences)
            
            # Show stat change particles - SPREAD OUT for dramatic effect!
            screen_center_x = config.SCREEN_WIDTH // 2
            screen_center_y = config.SCREEN_HEIGHT // 2
            
            # Merit on LEFT side
            if 'merit' in consequences and consequences['merit'] != 0:
                self.visual_effects.add_stat_particle(
                    screen_center_x - 250,  # Far left
                    screen_center_y - 50,   # Slightly up
                    'merit', consequences['merit']
                )
                
            # Karma in CENTER
            if 'karma' in consequences and consequences['karma'] != 0:
                self.visual_effects.add_stat_particle(
                    screen_center_x,        # Center
                    screen_center_y - 50,   # Slightly up
                    'karma', consequences['karma']
                )
                
            # Wisdom on RIGHT side
            if 'wisdom' in consequences and consequences['wisdom'] != 0:
                self.visual_effects.add_stat_particle(
                    screen_center_x + 250,  # Far right
                    screen_center_y - 50,   # Slightly up
                    'wisdom', consequences['wisdom']
                )
            
            # Track clarity-based achievements
            if self.progress:
                self.progress.record_clarity(self.stats.clarity)
            self._flush_achievement_notifications()

    def _play_consequence_sound(self, consequences):
        """Pick a sound based on the largest stat change."""
        changes = {k: consequences.get(k, 0) for k in ('merit', 'karma', 'wisdom')}
        # If anything went notably negative, play the negative tone
        if any(v < 0 for v in changes.values()):
            self.audio.play('negative')
            return
        # Otherwise play the sound for the biggest positive gain
        biggest = max(changes, key=lambda k: changes[k])
        if changes[biggest] > 0:
            self.audio.play(biggest)
        else:
            self.audio.play('confirm')

    def _flush_achievement_notifications(self):
        """Show a notification (and bell) for any newly unlocked achievements."""
        if not self.progress:
            return
        title = self.progress.pop_notification()
        if title:
            self.show_notification(f"Achievement unlocked: {title}", 200)
            self.audio.play('bell')
                
    def update(self):
        """Update game state"""
        # Track play time and autosave only while actively playing
        in_game = self.state in (
            config.STATE_EXPLORATION, config.STATE_ENCOUNTER,
            config.STATE_JOURNAL, config.STATE_GLOSSARY,
            config.STATE_HELP, config.STATE_MEDITATION, config.STATE_PAUSE
        )
        if in_game and self.stats is not None:
            dt = self.clock.get_time() / 1000.0
            self.play_time += dt
            self.autosave_timer += dt
            # Autosave every 2 minutes during exploration
            if self.autosave_timer >= 120 and self.state == config.STATE_EXPLORATION:
                self.autosave_timer = 0.0
                self.save_manager.save_game(self.active_slot, self, auto=True)
                self.show_notification("Auto-saved", 80)

        if self.state == config.STATE_EXPLORATION:
            self.update_exploration()
        elif self.state == config.STATE_ENCOUNTER:
            self.update_encounter()
        elif self.state == config.STATE_MEDITATION:
            self.update_meditation()
        elif self.state == config.STATE_VICTORY:
            # Record enlightenment once
            if self.progress and 'enlightened' not in self.progress.unlocked:
                self.progress.record_enlightened()
                self.audio.play('bell')
            
        # Update notifications
        if self.notification_timer > 0:
            self.notification_timer -= 1
            
    def update_exploration(self):
        """Update during exploration"""
        # Get keyboard state
        keys = pygame.key.get_pressed()
        
        # Store old position
        old_x = self.player.x
        old_y = self.player.y
        old_realm = self.player.get_current_realm()
        
        # Update player
        self.player.handle_input(keys)
        self.player.update()
        
        # Update obstacles (spawn new ones, remove dead)
        self.obstacle_manager.update()
        
        # HELL SUFFERING - Stats drain over time in Hell!
        drain_message = self.player.apply_hell_suffering(self.stats)
        if drain_message:
            self.show_notification(drain_message, 120)
        
        # DEATH ZONE CHECK - Beyond Hell = Eternal Torture!
        distance_from_center = self.player.get_distance_from_temple()
        if distance_from_center > config.HELL_RADIUS:
            # PLAYER TOUCHED THE OUTER VOID - Push back!
            self.player.x = old_x
            self.player.y = old_y
            self.player.rect.x = int(old_x)
            self.player.rect.y = int(old_y)
            return
        
        # Check new realm
        new_realm = self.player.get_current_realm()
        
        # REALM BARRIER SYSTEM - Check if player can enter new realm!
        if new_realm != old_realm:
            can_enter, missing_stats = self.stats.can_enter_realm(new_realm)
            
            if not can_enter:
                # BLOCKED! Push player back
                self.player.x = old_x
                self.player.y = old_y
                self.player.rect.x = int(old_x)
                self.player.rect.y = int(old_y)
                
                # Show barrier message
                realm_names = {
                    'temple': 'Temple',
                    'deva': 'Deva Realm',
                    'asura': 'Asura Realm', 
                    'human': 'Human Realm',
                    'animal': 'Animal Realm',
                    'hungry_ghost': 'Hungry Ghost Realm',
                    'hell': 'Hell Realm'
                }
                
                # Build message showing what's missing
                missing_parts = []
                if 'wisdom' in missing_stats:
                    missing_parts.append(f"{missing_stats['wisdom']} more Wisdom")
                if 'merit' in missing_stats:
                    missing_parts.append(f"{missing_stats['merit']} more Merit")
                if 'karma' in missing_stats:
                    missing_parts.append(f"{missing_stats['karma']} more Karma")
                    
                missing_text = ", ".join(missing_parts)
                message = f"⚠️ BARRIER! Need {missing_text} to enter {realm_names.get(new_realm, new_realm)}!"
                self.show_notification(message, 180)
        
        # Update camera
        self.world.update_camera(self.player.x, self.player.y)
        
        # Update visual effects
        self.visual_effects.update_particles()
        
        # Track realm changes: update ambient sound and journal
        current_realm = self.player.get_current_realm()
        if current_realm and current_realm != self.current_realm_name:
            self.current_realm_name = current_realm
            self.audio.set_ambient(current_realm)
            if self.progress:
                self.progress.record_realm_visited(current_realm)
                self._flush_achievement_notifications()
        
        # Contextual first-time hints
        self._maybe_show_hints()
        
        # Victory is now ONLY achieved through Buddha's final teaching!
        # No automatic win - must defeat Mara AND complete Buddha dialogue

    def _maybe_show_hints(self):
        """Show a one-time hint the first time the player is near an NPC/obstacle."""
        if not self._first_npc_hint_shown:
            npc = self.npc_manager.get_nearby_npc(
                self.player.x, self.player.y, max_distance=100)
            if npc:
                self._first_npc_hint_shown = True
                self.show_notification("Press E to speak with this being", 150)
                return
        if not self._first_obstacle_hint_shown:
            obs = self.obstacle_manager.get_nearby_obstacle(
                self.player.x, self.player.y)
            if obs:
                self._first_obstacle_hint_shown = True
                self.show_notification(
                    "Press X to strike this obstacle of delusion", 150)
            
    def update_encounter(self):
        """Update during encounter"""
        self.encounter_system.update()
        
        # Check if encounter finished
        if not self.encounter_system.is_active():
            self.state = config.STATE_EXPLORATION
            
        # Update particles
        self.visual_effects.update_particles()

    # ---------------- MEDITATION MINI-GAME ----------------

    def _start_meditation(self):
        """Begin a short breath-focused meditation session."""
        self.med_breath = 0.0
        self.med_focus = 0.0
        self.med_time_left = 20.0  # 20 second session
        self.med_distraction_timer = 0.0
        self.state = config.STATE_MEDITATION
        self.audio.play('bell')

    def update_meditation(self):
        """Advance the meditation timer, breath cycle, and focus."""
        dt = self.clock.get_time() / 1000.0
        self.med_time_left -= dt
        # Breath cycle: one full in/out every ~8 seconds
        self.med_breath = (self.med_breath + dt / 8.0) % 1.0
        # Focus slowly builds just by staying present
        self.med_focus = min(1.0, self.med_focus + dt * 0.02)
        if self.med_distraction_timer > 0:
            self.med_distraction_timer -= dt

        if self.med_time_left <= 0:
            self._end_meditation()

    def _end_meditation(self):
        """Finish meditation and grant rewards based on focus achieved."""
        # Reward scales with focus: a little wisdom + clarity, restore calm
        wisdom_gain = int(5 + self.med_focus * 15)   # 5..20
        self.stats.add_wisdom(wisdom_gain)
        # Small clarity bump
        self.stats.clarity = min(1.0, self.stats.clarity + 0.03 + self.med_focus * 0.05)
        self.audio.play('clarity')
        self.show_notification(
            f"Meditation complete. +{wisdom_gain} Wisdom, clearer mind.", 180)
        if self.progress:
            self.progress.record_clarity(self.stats.clarity)
            self._flush_achievement_notifications()
        self.state = config.STATE_EXPLORATION

    # ---------------- LOAD GAME ----------------

    def load_into_game(self, slot):
        """Load a saved slot and resume play."""
        data = self.save_manager.load_game(slot, prefer_auto=True)
        if not data:
            self.show_notification("Could not load that slot", 150)
            return

        past_life_key = data.get('past_life_key')
        scenario = config.PAST_LIFE_SCENARIOS.get(
            past_life_key, list(config.PAST_LIFE_SCENARIOS.values())[0])
        starting_realm = data.get('current_realm', scenario['starting_realm'])

        # Initialize fresh, then overwrite with saved values
        self.initialize_game(starting_realm, scenario['starting_stats'],
                             past_life_key=past_life_key)
        self.active_slot = slot

        s = data.get('stats', {})
        self.stats.merit = s.get('merit', self.stats.merit)
        self.stats.karma = s.get('karma', self.stats.karma)
        self.stats.wisdom = s.get('wisdom', self.stats.wisdom)
        self.stats.clarity = s.get('clarity', self.stats.clarity)

        p = data.get('player', {})
        if 'x' in p and 'y' in p:
            self.player.set_position(p['x'], p['y'])
            self.world.update_camera(self.player.x, self.player.y)

        # Restore NPC states
        if 'npcs' in data:
            self.npc_manager.from_dict(data['npcs'])

        # Restore progress / journal
        self.obstacles_destroyed = data.get('obstacles_destroyed', 0)
        self.npcs_helped_count = data.get('npcs_helped_count', 0)
        self.play_time = data.get('play_time', 0.0)
        self.progress.obstacles_destroyed = self.obstacles_destroyed
        # Rebuild helped set from NPC states
        for nid, npc in self.npc_manager.npcs.items():
            if getattr(npc, 'player_helped', False):
                self.progress.npcs_helped.add(nid)

        self.current_realm_name = starting_realm
        self.audio.set_ambient(starting_realm)
        self.state = config.STATE_EXPLORATION
        self.show_notification("Journey resumed", 150)

    # ---------------- JOURNAL GOAL LOGIC ----------------

    def _compute_next_goal(self):
        """Produce a human-readable 'next goal' string for the journal."""
        if not self.stats:
            return "Begin your journey."
        # If Mara not yet enlightened, point toward his requirements
        mara = self.npc_manager.npcs.get('evil_mara')
        if mara and mara.state != 'enlightened':
            # Find Mara's first dialogue requirement
            try:
                req = mara.dialogues[mara.current_dialogue_index]['requirements']
            except (IndexError, KeyError, AttributeError):
                req = {'wisdom': 220, 'merit': 180, 'karma': 150}
            needs = []
            if self.stats.wisdom < req.get('wisdom', 0):
                needs.append(f"{req['wisdom'] - self.stats.wisdom} more Wisdom")
            if self.stats.merit < req.get('merit', 0):
                needs.append(f"{req['merit'] - self.stats.merit} more Merit")
            if self.stats.karma < req.get('karma', 0):
                needs.append(f"{req['karma'] - self.stats.karma} more Karma")
            if needs:
                return ("Grow toward facing Mara: " + ", ".join(needs) +
                        ". Help beings and clear obstacles.")
            return "You are ready to face Mara at the temple. Seek him out."
        return "Overcome Mara, then approach the Buddha to reach the Triple Gem."
        
    def try_interact(self):
        """Try to interact with NPC (encounters disabled - NPCs only)"""
        # Check for nearby NPCs (100px for special NPCs, 60px for regular)
        nearby_npc = self.npc_manager.get_nearby_npc(
            self.player.x, self.player.y, max_distance=100
        )
        
        if nearby_npc:
            # SPECIAL CHECK: Can't talk to Buddha until Mara is defeated!
            if hasattr(nearby_npc, 'id') and nearby_npc.id == 'the_buddha':
                # Check if Mara has been defeated
                mara = self.npc_manager.npcs.get('evil_mara')
                if mara and mara.state != 'enlightened':
                    self.show_notification("⚠️ You must first overcome Mara before approaching the Buddha!", 180)
                    return
            
            # Reaching Mara is an achievement
            if hasattr(nearby_npc, 'id') and nearby_npc.id == 'evil_mara':
                if self.progress:
                    self.progress.record_face_mara()
                    self._flush_achievement_notifications()
            
            # Start NPC dialogue
            self.audio.play('dialogue_open')
            self.start_npc_dialogue(nearby_npc)
        else:
            # No NPC nearby
            self.show_notification("No one nearby to talk to", 120)
    
    def try_attack_obstacle(self):
        """Try to attack nearby mini-Mara obstacle"""
        nearby_obstacle = self.obstacle_manager.get_nearby_obstacle(
            self.player.x, self.player.y
        )
        
        if nearby_obstacle:
            # Attack the obstacle!
            rewards = nearby_obstacle.take_damage()
            
            if rewards:
                # Obstacle destroyed! Give rewards
                self.stats.add_merit(rewards['merit'])
                self.stats.add_karma(rewards['karma'])
                self.stats.add_wisdom(rewards['wisdom'])
                self.show_notification(rewards['message'], 120)
                self.audio.play('destroy')
                # Track for journal & achievements
                self.obstacles_destroyed += 1
                if self.progress:
                    self.progress.record_obstacle_destroyed()
                    self.progress.record_clarity(self.stats.clarity)
                    self._flush_achievement_notifications()
            else:
                # Just damaged it
                self.show_notification(f"⚔️ Hit! {nearby_obstacle.health} HP remaining", 60)
                self.audio.play('hit')
        else:
            self.show_notification("No obstacle nearby to attack", 60)
            
    def start_npc_dialogue(self, npc):
        """
        Start dialogue with an NPC
        
        Args:
            npc: NPC object to interact with
        """
        dialogue = npc.get_current_dialogue(self.stats)
        
        if not dialogue['choices']:
            # No choices - just showing a message
            self.show_notification(dialogue['text'], 240)
            return
            
        # Convert NPC dialogue to encounter format
        encounter_data = {
            'id': f'npc_{npc.id}',
            'realm': npc.realm,
            'title': npc.get_display_name(),
            'description': dialogue['text'],
            'choices': dialogue['choices']
        }
        
        # Store current NPC for later
        self.current_npc = npc
        
        # Create a simple encounter object for NPC dialogue
        class NPCEncounter:
            def __init__(self, data):
                self.id = data['id']
                self.realm = data['realm']
                self.title = data['title']
                self.description = data['description']
                self.choices = data['choices']
                self.completed = False
                
            def get_choice_count(self):
                return len(self.choices)
                
            def get_choice_text(self, idx):
                if 0 <= idx < len(self.choices):
                    return self.choices[idx]['text']
                return ''
                
            def get_consequences(self, idx):
                if 0 <= idx < len(self.choices):
                    return self.choices[idx]['consequences']
                return {}
                
            def mark_completed(self):
                pass
        
        # Start as encounter
        self.encounter_system.active_encounter = NPCEncounter(encounter_data)
        self.encounter_system.selected_choice = 0
        self.encounter_system.showing_result = False
        self.state = config.STATE_ENCOUNTER
        
    # OLD ENCOUNTER SYSTEM - Disabled (NPCs only now)
    # Uncomment this method and call it from try_interact() if you want
    # to re-enable abstract encounters alongside NPCs
    """
    def try_start_encounter(self):
        '''Try to start an encounter if player is near one'''
        current_realm = self.player.get_current_realm()
        
        if current_realm != 'temple':  # No encounters in temple
            encounter_id = self.encounter_system.get_nearby_encounter(
                self.player.x, self.player.y, current_realm
            )
            
            if encounter_id:
                if self.encounter_system.start_encounter(encounter_id):
                    self.current_npc = None  # Not an NPC encounter
                    self.state = config.STATE_ENCOUNTER
                else:
                    self.show_notification("No encounters here right now", 120)
            else:
                self.show_notification("Press E near NPCs", 120)
    """
                
    def render(self):
        """Render everything"""
        if self.state == config.STATE_MENU:
            self.render_menu()
        elif self.state == config.STATE_LOAD_MENU:
            self.screens.draw_load_menu(
                self.screen, self.font_large, self.font_medium,
                self.font_small, self.load_slot_index)
        elif self.state == config.STATE_PAST_LIFE_SELECTION:
            self.render_past_life_selection()
        elif self.state == config.STATE_PAST_LIFE_STORY:
            self.render_past_life_story()
        elif self.state == config.STATE_TUTORIAL:
            self.render_tutorial()
        elif self.state == config.STATE_EXPLORATION:
            self.render_exploration()
        elif self.state == config.STATE_ENCOUNTER:
            self.render_encounter()
        elif self.state == config.STATE_PAUSE:
            self.render_pause()
        elif self.state == config.STATE_JOURNAL:
            self.render_exploration()  # draw world behind
            self.screens.draw_journal(
                self.screen, self.font_large, self.font_medium,
                self.font_small, self.progress, self.npc_manager,
                self.stats, self._compute_next_goal())
        elif self.state == config.STATE_GLOSSARY:
            self.screens.draw_glossary(
                self.screen, self.font_large, self.font_medium,
                self.font_small, self.glossary_scroll)
        elif self.state == config.STATE_HELP:
            self.screens.draw_help(
                self.screen, self.font_large, self.font_medium, self.font_small)
        elif self.state == config.STATE_MEDITATION:
            self.render_exploration()  # draw world behind dim overlay
            self.screens.draw_meditation(
                self.screen, self.font_large, self.font_medium,
                self.font_small, self.med_breath, self.med_focus,
                self.med_time_left)
        elif self.state == config.STATE_VICTORY:
            self.render_victory()

        if self._is_web:
            pygame.transform.scale(self.screen, (960, 540), self._scaled)
            self._window.blit(self._scaled, (0, 0))
        pygame.display.flip()
        
    def render_menu(self):
        """Render menu screen with selectable options."""
        self.ui.draw_title_screen(self.screen, self.font_large, self.font_medium)
        # Menu options start just below the divider line (~y=395)
        options = self._menu_options()
        start_y = 400
        for i, option in enumerate(options):
            selected = (i == self.menu_index)
            color = config.GOLD if selected else config.LIGHT_GRAY
            prefix = "> " if selected else "  "
            surf = self.font_medium.render(prefix + option, True, color)
            x = (config.SCREEN_WIDTH - surf.get_width()) // 2
            self.screen.blit(surf, (x, start_y + i * 46))
        # Press-ENTER prompt sits 20px below the last option, never below y=660
        prompt_y = min(start_y + len(options) * 46 + 20, 660)
        prompt = self.font_small.render("↑↓ Navigate  |  ENTER Select",
                                        True, (130, 130, 130))
        self.screen.blit(prompt,
                         ((config.SCREEN_WIDTH - prompt.get_width()) // 2,
                          prompt_y))

    def render_tutorial(self):
        """Render the first-time tutorial overlay on top of the world."""
        self.render_exploration()
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT),
                                 pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        box_w, box_h = 900, 460
        box_x = (config.SCREEN_WIDTH - box_w) // 2
        box_y = (config.SCREEN_HEIGHT - box_h) // 2
        pygame.draw.rect(self.screen, config.DARK_GRAY, (box_x, box_y, box_w, box_h))
        pygame.draw.rect(self.screen, (255, 255, 0), (box_x, box_y, box_w, 6))
        pygame.draw.rect(self.screen, (255, 255, 0),
                         (box_x, box_y + box_h - 6, box_w, 6))
        pygame.draw.rect(self.screen, config.GOLD, (box_x, box_y, box_w, box_h), 2)

        title = self.font_large.render("Your Journey Begins", True, config.GOLD)
        self.screen.blit(title, ((config.SCREEN_WIDTH - title.get_width()) // 2,
                                 box_y + 30))

        lines = [
            "You are reborn in Samsara, the wheel of suffering.",
            "Your vision is clouded by the dust of ignorance.",
            "",
            "Move with WASD or the arrow keys.",
            "Press E to speak with the suffering beings you meet.",
            "Press X to strike the obstacles of delusion.",
            "Press M to meditate and clear your mind.",
            "",
            "Grow in Merit, Karma, and Wisdom to clear your sight,",
            "pass between realms, and reach the temple at the center.",
            "",
            "Press J for your journal, G for the glossary, H for help.",
        ]
        y = box_y + 95
        for line in lines:
            surf = self.font_small.render(line, True, config.WHITE)
            self.screen.blit(surf, (box_x + 50, y))
            y += 27

        hint = self.font_medium.render("Press any key to begin", True, config.GOLD)
        self.screen.blit(hint, ((config.SCREEN_WIDTH - hint.get_width()) // 2,
                                box_y + box_h - 45))

    def render_pause(self):
        """Render the pause menu overlay."""
        self.render_exploration()
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT),
                                 pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        self.screen.blit(overlay, (0, 0))

        title = self.font_large.render("Paused", True, config.GOLD)
        self.screen.blit(title, ((config.SCREEN_WIDTH - title.get_width()) // 2,
                                 config.SCREEN_HEIGHT // 2 - 160))

        options = [
            "ESC  -  Resume",
            "S  -  Save game",
            "G  -  Glossary",
            "H  -  How to Play",
            "Q  -  Save & Quit to Menu",
        ]
        y = config.SCREEN_HEIGHT // 2 - 80
        for line in options:
            surf = self.font_medium.render(line, True, config.LIGHT_GRAY)
            self.screen.blit(surf, ((config.SCREEN_WIDTH - surf.get_width()) // 2, y))
            y += 46
        
    def render_past_life_selection(self):
        """Render past life selection screen"""
        self.ui.draw_past_life_selection(
            self.screen, self.font_large, self.font_medium, 
            self.past_life_index
        )
    
    def render_past_life_story(self):
        """Render full past life story"""
        selected_key = self.past_life_keys[self.past_life_index]
        self.ui.draw_past_life_story(
            self.screen, self.font_large, self.font_medium,
            selected_key
        )
        
    def render_exploration(self):
        """Render exploration view"""
        # Draw world
        self.world.draw_world(self.screen, self.player)
        
        # Draw NPCs
        camera_x, camera_y = self.world.get_camera_offset()
        self.draw_npcs(camera_x, camera_y)
        
        # Draw mini-Mara obstacles
        self.obstacle_manager.draw(self.screen, camera_x, camera_y)
        
        # Draw player
        self.player.draw(self.screen, camera_x, camera_y)
        
        # DEATH ZONE WARNING - Red vignette if approaching edge
        distance_from_center = self.player.get_distance_from_temple()
        if distance_from_center > config.HELL_RADIUS - 100:  # Within 100px of death
            # Calculate danger level (0 to 1)
            danger = (distance_from_center - (config.HELL_RADIUS - 100)) / 100
            danger = min(1.0, max(0.0, danger))
            
            # Draw red warning overlay
            warning_alpha = int(danger * 150)
            warning_surf = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
            warning_surf.fill((255, 0, 0, warning_alpha))
            self.screen.blit(warning_surf, (0, 0))
            
            # Show warning text
            if danger > 0.5:
                warning_text = "⚠️ DANGER! Outer darkness ahead! ⚠️"
                warning_surface = self.font_large.render(warning_text, True, (255, 0, 0))
                text_x = (config.SCREEN_WIDTH - warning_surface.get_width()) // 2
                self.screen.blit(warning_surface, (text_x, 50))
        
        # Apply fog of ignorance
        self.visual_effects.create_fog_overlay(self.screen, self.stats.clarity)
        
        # Draw temple glow (if visible)
        self.visual_effects.draw_temple_glow(
            self.screen, self.player.x, self.player.y,
            camera_x, camera_y, self.stats.clarity
        )
        
        # Draw wisdom rays (if clarity high enough)
        self.visual_effects.draw_wisdom_rays(
            self.screen, self.player.x, self.player.y,
            camera_x, camera_y, self.stats.clarity
        )
        
        # Draw UI
        self.ui.draw_stats_panel(self.screen, self.stats, 
                                 self.font_medium, self.font_small)
        
        # Draw realm indicator
        current_realm = self.player.get_current_realm()
        self.visual_effects.draw_realm_indicator(self.screen, current_realm, 
                                                self.font_medium)
        
        # Draw controls
        self.ui.draw_controls_hint(self.screen, self.font_small, False)
        
        # Draw particles
        self.visual_effects.draw_particles(self.screen, self.font_small)
        
        # Draw notification
        if self.notification_timer > 0:
            self.ui.draw_notification(self.screen, self.notification_message,
                                     self.font_medium)
                                     
    def render_encounter(self):
        """Render encounter view"""
        # Draw world in background (frozen)
        self.world.draw_world(self.screen, self.player)
        camera_x, camera_y = self.world.get_camera_offset()
        self.player.draw(self.screen, camera_x, camera_y)
        
        # Draw encounter UI
        self.encounter_system.draw(self.screen, self.font_large, self.font_medium, self.stats)
        
        # Draw particles (for stat gains)
        self.visual_effects.draw_particles(self.screen, self.font_small)
        
        # Draw controls
        self.ui.draw_controls_hint(self.screen, self.font_small, True)
        
    def render_victory(self):
        """Render victory screen"""
        self.screen.fill(config.BLACK)
        
        # Draw golden glow background
        for i in range(10):
            alpha = int(50 - (i * 4))
            glow_surf = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
            glow_surf.fill((255, 215, 0, alpha))
            self.screen.blit(glow_surf, (0, 0))
        
        # Victory message
        victory_text = "⛩️ WELCOME TO THE TRIPLE GEM ⛩️"
        subtitle1 = "You have found refuge in Buddha, Dhamma, and Sangha"
        subtitle2 = "You have left the cruel world of suffering behind"
        subtitle3 = "The right path to Nibbana awaits you"
        
        victory_surface = self.font_large.render(victory_text, True, config.GOLD)
        subtitle1_surface = self.font_medium.render(subtitle1, True, config.WHITE)
        subtitle2_surface = self.font_medium.render(subtitle2, True, (100, 200, 255))  # Light blue
        subtitle3_surface = self.font_medium.render(subtitle3, True, config.GOLD)
        
        victory_x = (config.SCREEN_WIDTH - victory_surface.get_width()) // 2
        subtitle1_x = (config.SCREEN_WIDTH - subtitle1_surface.get_width()) // 2
        subtitle2_x = (config.SCREEN_WIDTH - subtitle2_surface.get_width()) // 2
        subtitle3_x = (config.SCREEN_WIDTH - subtitle3_surface.get_width()) // 2
        
        self.screen.blit(victory_surface, (victory_x, 160))
        self.screen.blit(subtitle1_surface, (subtitle1_x, 220))
        self.screen.blit(subtitle2_surface, (subtitle2_x, 255))
        self.screen.blit(subtitle3_surface, (subtitle3_x, 290))
        
        # Show final stats
        stats_y = 360
        stats_title = self.font_large.render("Your Journey Complete:", True, config.GOLD)
        stats_title_x = (config.SCREEN_WIDTH - stats_title.get_width()) // 2
        self.screen.blit(stats_title, (stats_title_x, stats_y))
        
        stats_y += 50
        stats_lines = [
            f"🪙 Merit: {self.stats.merit}",
            f"☸ Karma: {self.stats.karma}",
            f"📜 Wisdom: {self.stats.wisdom}",
            f"✨ Clarity: {int(self.stats.clarity * 100)}%"
        ]
        
        for line in stats_lines:
            line_surface = self.font_medium.render(line, True, config.LIGHT_GRAY)
            line_x = (config.SCREEN_WIDTH - line_surface.get_width()) // 2
            self.screen.blit(line_surface, (line_x, stats_y))
            stats_y += 40
            
        # Final blessings
        final_msg1 = "Sadhu! Sadhu! Sadhu!"
        final_msg2 = "May all beings be free from suffering"
        final_msg3 = "May all beings find the path to liberation"
        
        msg1_surface = self.font_large.render(final_msg1, True, config.WHITE)
        msg2_surface = self.font_medium.render(final_msg2, True, config.GOLD)
        msg3_surface = self.font_medium.render(final_msg3, True, config.GOLD)
        
        msg1_x = (config.SCREEN_WIDTH - msg1_surface.get_width()) // 2
        msg2_x = (config.SCREEN_WIDTH - msg2_surface.get_width()) // 2
        msg3_x = (config.SCREEN_WIDTH - msg3_surface.get_width()) // 2
        
        self.screen.blit(msg1_surface, (msg1_x, 580))
        self.screen.blit(msg2_surface, (msg2_x, 635))
        self.screen.blit(msg3_surface, (msg3_x, 670))
            
    def draw_npcs(self, camera_x, camera_y):
        """
        Draw all NPCs on the map
        
        Args:
            camera_x: Camera x offset
            camera_y: Camera y offset
        """
        import math
        
        for npc in self.npc_manager.get_all_npcs():
            # Calculate screen position
            screen_x = npc.x - camera_x
            screen_y = npc.y - camera_y
            
            # Only draw if on screen
            if -100 < screen_x < config.SCREEN_WIDTH + 100 and -100 < screen_y < config.SCREEN_HEIGHT + 100:
                # Check if this is a special NPC
                is_mara = hasattr(npc, 'id') and npc.id == 'evil_mara'
                is_buddha = hasattr(npc, 'id') and npc.id == 'the_buddha'
                
                # SPECIAL: Mara - MASSIVE, pulsing dark red with INTENSE aura
                if is_mara:
                    npc_size = 120  # EVEN LARGER! (was 80)
                    # Intense pulsing effect
                    pulse = abs(math.sin(pygame.time.get_ticks() / 400))  # Faster pulse
                    dark_red = (int(139 + pulse * 100), int(pulse * 50), 0)  # More dramatic color shift
                    
                    # Mara aura — pre-allocated surfaces, fewer rings on web
                    num_rings = 3 if self._is_web else 5
                    if self._mara_aura_surfs is None:
                        self._mara_aura_surfs = [
                            pygame.Surface((npc_size + i * 25, npc_size + i * 25), pygame.SRCALPHA)
                            for i in range(num_rings)]
                    for i, aura_surf in enumerate(self._mara_aura_surfs):
                        aura_size = npc_size + (i * 25)
                        aura_surf.fill((0, 0, 0, 0))
                        aura_alpha = int(70 - (i * 15))
                        pygame.draw.circle(aura_surf, (*dark_red, aura_alpha),
                                         (aura_size//2, aura_size//2), aura_size//2)
                        self.screen.blit(aura_surf, (screen_x - aura_size//2, screen_y - aura_size//2))
                    
                    # Main body - LARGE diamond shape
                    points = [
                        (screen_x, screen_y - npc_size//2),  # Top
                        (screen_x + npc_size//2, screen_y),  # Right
                        (screen_x, screen_y + npc_size//2),  # Bottom
                        (screen_x - npc_size//2, screen_y)   # Left
                    ]
                    pygame.draw.polygon(self.screen, dark_red, points)
                    pygame.draw.polygon(self.screen, (255, 0, 0), points, 5)  # THICK bright red outline
                    
                    # Evil eye symbol in center
                    eye_radius = 15
                    pygame.draw.circle(self.screen, (255, 0, 0), (int(screen_x), int(screen_y)), eye_radius)
                    pygame.draw.circle(self.screen, config.BLACK, (int(screen_x), int(screen_y)), eye_radius//2)
                    
                # SPECIAL: Buddha - MASSIVE, glowing gold with DIVINE radiant aura
                elif is_buddha:
                    npc_size = 140  # LARGEST! (was 90)
                    # Gentle divine glow
                    glow = abs(math.sin(pygame.time.get_ticks() / 600)) * 0.4 + 0.6  # Brighter base
                    gold = (255, int(215 * glow), 0)  # Pure gold
                    
                    # Buddha aura — pre-allocated surfaces, fewer rings on web
                    num_rings = 4 if self._is_web else 7
                    if self._buddha_aura_surfs is None:
                        self._buddha_aura_surfs = [
                            pygame.Surface((npc_size + i * 30, npc_size + i * 30), pygame.SRCALPHA)
                            for i in range(num_rings)]
                    for i, aura_surf in enumerate(self._buddha_aura_surfs):
                        aura_size = npc_size + (i * 30)
                        aura_surf.fill((0, 0, 0, 0))
                        aura_alpha = int(80 - (i * 15))
                        pygame.draw.circle(aura_surf, (255, 215, 0, aura_alpha),
                                         (aura_size//2, aura_size//2), aura_size//2)
                        self.screen.blit(aura_surf, (screen_x - aura_size//2, screen_y - aura_size//2))
                    
                    # Main body - LARGE octagon (8-sided for Noble Eightfold Path)
                    points = []
                    for i in range(8):
                        angle = (i * 45) * (math.pi / 180)
                        px = screen_x + math.cos(angle) * npc_size // 2
                        py = screen_y + math.sin(angle) * npc_size // 2
                        points.append((px, py))
                    pygame.draw.polygon(self.screen, gold, points)
                    pygame.draw.polygon(self.screen, config.WHITE, points, 6)  # VERY thick white outline
                    
                    # Draw LARGE dharma wheel symbol in center
                    wheel_radius = 25  # Bigger wheel
                    pygame.draw.circle(self.screen, config.WHITE, (int(screen_x), int(screen_y)), wheel_radius, 4)
                    for spoke in range(8):
                        angle = spoke * 45 * (math.pi / 180)
                        end_x = screen_x + math.cos(angle) * wheel_radius
                        end_y = screen_y + math.sin(angle) * wheel_radius
                        pygame.draw.line(self.screen, config.WHITE, 
                                       (screen_x, screen_y), (end_x, end_y), 3)
                    
                    # Sacred lotus petals around Buddha
                    petal_distance = npc_size // 2 + 20
                    for i in range(8):
                        angle = (i * 45 + 22.5) * (math.pi / 180)
                        petal_x = screen_x + math.cos(angle) * petal_distance
                        petal_y = screen_y + math.sin(angle) * petal_distance
                        pygame.draw.circle(self.screen, (255, 192, 203), (int(petal_x), int(petal_y)), 12)
                        pygame.draw.circle(self.screen, config.WHITE, (int(petal_x), int(petal_y)), 12, 2)
                
                # Regular NPCs
                else:
                    npc_size = 40
                    pygame.draw.rect(self.screen, npc.color,
                                   (screen_x - npc_size//2, screen_y - npc_size//2,
                                    npc_size, npc_size))
                    pygame.draw.rect(self.screen, config.WHITE,
                                   (screen_x - npc_size//2, screen_y - npc_size//2,
                                    npc_size, npc_size), 2)
                
                # Draw name above NPC
                name_font = self.font_medium if (is_mara or is_buddha) else self.font_small
                name_color = config.RED if is_mara else (config.GOLD if is_buddha else config.WHITE)
                name_surface = name_font.render(npc.name, True, name_color)
                name_x = screen_x - name_surface.get_width() // 2
                name_y = screen_y - npc_size//2 - 25 if (is_mara or is_buddha) else screen_y - npc_size//2 - 20
                
                # Background for readability
                bg_rect = name_surface.get_rect()
                bg_rect.x = name_x - 2
                bg_rect.y = name_y - 2
                bg_rect.width += 4
                bg_rect.height += 4
                pygame.draw.rect(self.screen, config.BLACK, bg_rect)
                
                self.screen.blit(name_surface, (name_x, name_y))
                
                # Draw title for special NPCs
                if is_mara or is_buddha:
                    title_surface = self.font_small.render(npc.title, True, name_color)
                    title_x = screen_x - title_surface.get_width() // 2
                    title_y = name_y + 20
                    
                    bg_rect = title_surface.get_rect()
                    bg_rect.x = title_x - 2
                    bg_rect.y = title_y - 2
                    bg_rect.width += 4
                    bg_rect.height += 4
                    pygame.draw.rect(self.screen, config.BLACK, bg_rect)
                    
                    self.screen.blit(title_surface, (title_x, title_y))
                
                # Draw interaction indicator if player is nearby
                distance = npc.get_distance_from_player(self.player.x, self.player.y)
                interaction_distance = 100 if (is_mara or is_buddha) else 60
                if distance <= interaction_distance:
                    # Special check for Buddha - show if blocked
                    if is_buddha:
                        mara = self.npc_manager.npcs.get('evil_mara')
                        if mara and mara.state != 'enlightened':
                            indicator = "🔒 DEFEAT MARA FIRST 🔒"
                            indicator_color = config.RED
                        else:
                            indicator = "✨ Press E ✨"
                            indicator_color = config.GOLD
                    elif is_mara:
                        indicator = "⚠️ Press E ⚠️"
                        indicator_color = config.GOLD
                    else:
                        indicator = "Press E"
                        indicator_color = config.GOLD
                        
                    indicator_surface = self.font_small.render(indicator, True, indicator_color)
                    indicator_x = screen_x - indicator_surface.get_width() // 2
                    indicator_y = screen_y + npc_size//2 + 10
                    self.screen.blit(indicator_surface, (indicator_x, indicator_y))
            
    def show_notification(self, message, duration):
        """
        Show a notification message
        
        Args:
            message: Message to show
            duration: Duration in frames
        """
        self.notification_message = message
        self.notification_timer = duration


async def main():
    """Entry point"""
    game = Game()
    await game.run()


if __name__ == '__main__':
    asyncio.run(main())
