"""
SAMSARA: Journey to the Triple Gem
Configuration File

This file contains all game constants and settings.
Customize these values to adjust game behavior.
"""

# Screen Settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
import sys
FPS = 30 if sys.platform == 'emscripten' else 60
TITLE = "Samsara: Journey to the Triple Gem"

# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
BLUE = (100, 149, 237)
RED = (220, 20, 60)
GREEN = (34, 139, 34)
PURPLE = (138, 43, 226)
ORANGE = (255, 140, 0)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)

# Realm Colors - Moderate brightness, obscured by "dust in eyes" overlay
REALM_COLORS = {
    'hell': (120, 0, 0),          # Medium dark red (suffering)
    'hungry_ghost': (140, 60, 0), # Dark orange (craving)
    'animal': (100, 65, 30),      # Medium brown (ignorance)
    'human': (80, 100, 120),      # Medium steel blue (struggle)
    'asura': (110, 0, 110),       # Medium purple (jealousy)
    'deva': (140, 130, 0),        # Medium gold (false happiness)
    'temple': (200, 200, 200)     # Light gray (hope!)
}

# Player Settings
PLAYER_SIZE = 32
PLAYER_SPEED = 4
PLAYER_COLOR = (100, 200, 255)  # Light blue

# Stats Settings
STARTING_MERIT = 0
STARTING_KARMA = 0
STARTING_WISDOM = 0

# ENLIGHTENMENT REQUIREMENTS - Made MUCH harder!
ENLIGHTENMENT_WISDOM = 200   # Was 80 - now 2.5x harder!
ENLIGHTENMENT_MERIT = 150    # Was 60 - now 2.5x harder!
ENLIGHTENMENT_KARMA = 120    # Was 50 - now 2.4x harder!

# REALM BARRIER REQUIREMENTS - PROGRESSIVE! Harder as you approach Triple Gem!
# Progressive difficulty: outer realms (easy) → inner realms (very hard)
REALM_REQUIREMENTS = {
    'hell': {'wisdom': -999, 'merit': -999, 'karma': -999},  # ANYONE can enter (it's Hell!)
    'hungry_ghost': {'wisdom': 5, 'merit': 5, 'karma': 5},   # Just need to start growing
    'animal': {'wisdom': 20, 'merit': 15, 'karma': 15},      # Some real growth
    'human': {'wisdom': 50, 'merit': 35, 'karma': 30},       # Significant growth (HARDER!)
    'asura': {'wisdom': 90, 'merit': 65, 'karma': 55},       # Advanced progress (MUCH HARDER!)
    'deva': {'wisdom': 140, 'merit': 100, 'karma': 85},      # Major achievement (VERY HARD!)
    'temple': {'wisdom': 200, 'merit': 150, 'karma': 120}    # Full enlightenment required!
}

# Clarity/Vision System - "Dust in Your Eyes" 
# As wisdom grows, the dust slowly clears and you see more clearly
MIN_CLARITY = 0.1    # Starting clarity (10% - VERY dusty vision!)
MAX_CLARITY = 1.0    # Maximum clarity (100% - completely clear)
WISDOM_FOR_MAX_CLARITY = 250  # Wisdom points needed for full clarity (MUCH HARDER!)

# World Settings
TILE_SIZE = 32
WORLD_WIDTH = 3200   # 100 tiles wide
WORLD_HEIGHT = 3200  # 100 tiles tall

# Realm boundaries (concentric circles from center)
# Temple is at center: (1600, 1600)
TEMPLE_CENTER = (1600, 1600)
TEMPLE_RADIUS = 200

# Realm radii (from center outward)
DEVA_RADIUS = 400
ASURA_RADIUS = 600
HUMAN_RADIUS = 900
ANIMAL_RADIUS = 1200
HUNGRY_GHOST_RADIUS = 1500
HELL_RADIUS = 1600  # Outermost

# HELL REALM SUFFERING MECHANICS
HELL_STAT_DRAIN_RATE = 0.1  # Points lost per second in Hell realm
VOID_STAT_DRAIN_RATE = 2.0   # Points lost per second in black void (RAPID!)
HELL_DRAIN_INTERVAL = 60     # Apply drain every 60 frames (1 second @ 60fps)

# Void boundary (beyond Hell = eternal torture!)
VOID_BOUNDARY = 1600  # Distance from center where void begins

# UI Settings
FONT_SIZE_SMALL = 20 if sys.platform == 'emscripten' else 16
FONT_SIZE_MEDIUM = 26 if sys.platform == 'emscripten' else 24
FONT_SIZE_LARGE = 38 if sys.platform == 'emscripten' else 36

def make_font(size):
    """Return a clean-rendering font for the current platform."""
    import pygame
    if sys.platform == 'emscripten':
        return pygame.font.SysFont('freesansbold', size)
    return pygame.font.Font(None, size)
DIALOGUE_BOX_HEIGHT = 250
CHOICE_BUTTON_HEIGHT = 50
CHOICE_BUTTON_MARGIN = 10

# File Paths
ENCOUNTERS_FILE = "content/encounters.json"
NPCS_FILE = "content/npcs.json"
REALMS_FILE = "content/realm_data.json"
BALANCE_FILE = "content/balance.json"
SAVE_FILE = "save_game.json"

# Past Life Scenarios (determines starting realm)
PAST_LIFE_SCENARIOS = {
    'warrior': {
        'title': 'The Angry Warrior',
        'description': 'Your sword dripped with blood. Enemies fell before you. But rage consumed your heart, and vengeance was your only truth. You died in battle, hatred still burning in your chest.',
        'full_story': (
            'Your sword dripped with blood. Enemies fell before you. But rage consumed your heart, and vengeance was your only truth. You died in battle, hatred still burning in your chest.\n\n'
            'You were General Kenshin, feared across the land. Every slight demanded revenge. Every insult required bloodshed. Your family begged you to stop. Your soldiers wept at what they were ordered to do. But fury was your master, not you.\n\n'
            'In your final battle, surrounded by the corpses you had created, a strange stillness fell. You realized: this anger had never brought peace. Only more suffering, rippling outward forever.\n\n'
            'With your dying breath, you whispered, "I was wrong..."\n\n'
            'Now you wake in Hell — the realm of your own making. The flames you see are your rage, reflected back at you.'
        ),
        'starting_realm': 'hell',
        'starting_stats': {'merit': 0, 'karma': -10, 'wisdom': 0}
    },
    'merchant': {
        'title': 'The Greedy Merchant',
        'description': 'Gold coins clinked in your hands. More, more, always more! You hoarded wealth while others starved. Profit was your god. You died clutching your money bag, still wanting one more coin.',
        'full_story': (
            'Gold coins clinked in your hands. More, more, always more! You hoarded wealth while others starved. Profit was your god. You died clutching your money bag, still wanting one more coin.\n\n'
            'You were Merchant Zhao, the richest in the province. But no amount was ever enough. You charged desperate families triple for rice. You turned away the sick at your door. You counted coins by candlelight while children outside went hungry.\n\n'
            'On your deathbed, surrounded by chests of gold, no friend sat beside you. No child held your hand. Only servants, waiting to see what you would leave them.\n\n'
            'You tried to take the gold with you. You could not. You died alone, still craving one more coin.\n\n'
            'Now you wake as a Hungry Ghost — forever craving what can never, ever satisfy.'
        ),
        'starting_realm': 'hungry_ghost',
        'starting_stats': {'merit': 5, 'karma': -5, 'wisdom': 0}
    },
    'farmer': {
        'title': 'The Simple Farmer',
        'description': 'You worked the land from dawn to dusk. Eat, sleep, work. Follow the seasons, follow the herd. Never question, never think deeply. You died as you lived - unconscious and unaware.',
        'full_story': (
            'You worked the land from dawn to dusk. Eat, sleep, work. Follow the seasons, follow the herd. Never question, never think deeply. You died as you lived — unconscious and unaware.\n\n'
            'You were Farmer Chen, tending the same fields for sixty years. You were not cruel. You were kind to your animals and fair to your neighbours. But life was only: plant, grow, harvest, survive. You never asked why.\n\n'
            'When the drought came, you followed the crowd\'s panic. When they said "sacrifice," you sacrificed. When they said "flee," you fled. You moved through life like water, taking the shape of whatever container held you.\n\n'
            'You died quietly in your sleep. It was a gentle death. But you had never truly been awake to receive it.\n\n'
            'Now you wake in the Animal Realm — where instinct rules and awareness sleeps, and the first stirrings of questioning begin.'
        ),
        'starting_realm': 'animal',
        'starting_stats': {'merit': 10, 'karma': 0, 'wisdom': 0}
    },
    'scholar': {
        'title': 'The Ordinary Scholar',
        'description': 'Books were your world. You sought knowledge, taught students, lived a decent life. You experienced love and loss, joy and pain. You died peacefully, knowing you lived well - but not deeply.',
        'full_story': (
            'Books were your world. You sought knowledge, taught students, lived a decent life. You experienced love and loss, joy and pain. You died peacefully, knowing you lived well — but not deeply.\n\n'
            'You were Scholar Liu, a respected teacher for forty years. You taught reading, writing, philosophy. You loved your family. You helped your village. By every worldly measure, you were a success.\n\n'
            'But you never questioned suffering itself. Never looked past the words to the silence between them. You lived well inside the dream — never once realising you were dreaming.\n\n'
            'On your deathbed, your students gathered. You felt proud. But underneath the pride was something else — a quiet ache, a sense of something important you had somehow missed.\n\n'
            'Now you wake in the Human Realm — the precious middle path, where awakening is possible. But you must choose to walk it.'
        ),
        'starting_realm': 'human',
        'starting_stats': {'merit': 15, 'karma': 10, 'wisdom': 5}
    },
    'noble': {
        'title': 'The Envious Noble',
        'description': 'You had rank, title, servants — but it was never enough. Those with higher rank consumed your thoughts. Jealousy was your constant companion. You died bitter, comparing yourself to the end.',
        'full_story': (
            'You had rank, title, servants — but it was never enough. Those with higher rank consumed your thoughts. Jealousy was your constant companion. You died bitter, comparing yourself to the end.\n\n'
            'You were Lord Takeshi. You had land, soldiers, a fine house. But the Duke had more land. The Prince had the King\'s ear. The King had everything. Your eyes were always on the rung above you, never on what you held.\n\n'
            'You schemed and backstabbed your way upward. Each prize felt hollow the moment you grasped it, because someone else always had something better.\n\n'
            'Your last words, whispered to your horrified heir: "Never let anyone surpass you." You passed your poison forward like a gift.\n\n'
            'Now you wake in the Asura Realm — where proud titans war without end, each striving to surpass the other, none ever satisfied.'
        ),
        'starting_realm': 'asura',
        'starting_stats': {'merit': 10, 'karma': 5, 'wisdom': 0}
    },
    'prince': {
        'title': 'The Privileged Prince',
        'description': "Silk cushions, the finest foods, perfect entertainment. You lived in paradise, sheltered from all suffering. Why think of death or pain? They didn't exist in your world. Until suddenly, they did.",
        'full_story': (
            "Silk cushions, the finest foods, perfect entertainment. You lived in paradise, sheltered from all suffering. Why think of death or pain? They didn't exist in your world. Until suddenly, they did.\n\n"
            'Your father, the King, loved you so fiercely he hid the world from you. No sick people near the palace. No old age visible. No funerals, no grief, no decay. Only music, feasting, and the illusion of endless youth.\n\n'
            'You believed it. You thought you were special — exempt from the ordinary rules of existence.\n\n'
            'Then one morning, walking in the garden, you found the gardener dead beneath a tree. "What is this?" you asked. Your attendant bowed his head. "Death, my lord. It comes for all — even you."\n\n'
            'That night, you died in your sleep. Gently, peacefully. But you had spent a whole life thinking you had forever.\n\n'
            'Now you wake in the Deva Realm — beautiful, blissful, and utterly impermanent. Paradise is the most seductive trap of all.'
        ),
        'starting_realm': 'deva',
        'starting_stats': {'merit': 20, 'karma': 15, 'wisdom': 0}
    }
}

# Game States
STATE_MENU = 'menu'
STATE_PAST_LIFE_SELECTION = 'past_life_selection'
STATE_PAST_LIFE_STORY = 'past_life_story'  # Reading full story
STATE_EXPLORATION = 'exploration'
STATE_ENCOUNTER = 'encounter'
STATE_DIALOGUE = 'dialogue'
STATE_PAUSE = 'pause'
STATE_GAME_OVER = 'game_over'
STATE_VICTORY = 'victory'
STATE_JOURNAL = 'journal'            # Quest/progress journal & achievements
STATE_GLOSSARY = 'glossary'          # Buddhist terms glossary
STATE_HELP = 'help'                  # Controls & how to play
STATE_MEDITATION = 'meditation'      # Meditation mini-game
STATE_LOAD_MENU = 'load_menu'        # Choose a save slot to continue
STATE_TUTORIAL = 'tutorial'          # First-time tutorial overlay
