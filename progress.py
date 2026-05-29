"""
Journal & Achievements System for Samsara
Tracks player progress: NPCs helped, obstacles destroyed, realms visited,
and unlockable achievements. Also holds the goal logic for the journal screen.
"""

import config


# All achievements: id -> (title, description, hidden)
ACHIEVEMENTS = {
    'first_help': ('First Compassion', 'Help your first suffering being', False),
    'hell_cleared': ('Through the Flames', 'Help every being in the Hell realm', False),
    'obstacle_5': ('Clearing the Path', 'Destroy 5 obstacles of delusion', False),
    'obstacle_25': ('Defiler of Defilements', 'Destroy 25 obstacles', False),
    'obstacle_50': ('Mind Like Diamond', 'Destroy 50 obstacles', False),
    'all_realms': ('Wheel Walker', 'Visit all six realms of Samsara', False),
    'clarity_50': ('Clearing Vision', 'Reach 50% clarity', False),
    'clarity_100': ('Crystal Clear', 'Reach 100% clarity', False),
    'precepts': ('The Five Precepts', 'Help all five Precept teachers', False),
    'half_npcs': ('Bodhisattva Heart', 'Help half of all beings', False),
    'all_npcs': ('Boundless Compassion', 'Help every being you meet', False),
    'face_mara': ('Facing the Tempter', 'Reach Mara at the temple', False),
    'enlightened': ('The Triple Gem', 'Attain liberation', False),
}

# NPC ids that teach the Five Precepts (matches content/npcs.json)
PRECEPT_NPC_IDS = {'swatter', 'thief', 'heartbreaker', 'drinker', 'liar'}


class ProgressTracker:
    """Tracks all progress metrics and unlocked achievements."""

    def __init__(self):
        self.npcs_helped = set()          # ids of helped NPCs
        self.obstacles_destroyed = 0
        self.realms_visited = set()
        self.unlocked = set()             # achievement ids
        self.newly_unlocked = []          # queue for notifications

    # ----- Recording events -----

    def record_npc_helped(self, npc_id, total_npcs):
        self.npcs_helped.add(npc_id)
        self._check_npc_achievements(total_npcs)

    def record_obstacle_destroyed(self):
        self.obstacles_destroyed += 1
        if self.obstacles_destroyed >= 5:
            self._unlock('obstacle_5')
        if self.obstacles_destroyed >= 25:
            self._unlock('obstacle_25')
        if self.obstacles_destroyed >= 50:
            self._unlock('obstacle_50')

    def record_realm_visited(self, realm):
        if realm and realm != 'temple':
            self.realms_visited.add(realm)
            six = {'hell', 'hungry_ghost', 'animal', 'human', 'asura', 'deva'}
            if six.issubset(self.realms_visited):
                self._unlock('all_realms')

    def record_clarity(self, clarity):
        if clarity >= 0.5:
            self._unlock('clarity_50')
        if clarity >= 0.999:
            self._unlock('clarity_100')

    def record_face_mara(self):
        self._unlock('face_mara')

    def record_enlightened(self):
        self._unlock('enlightened')

    # ----- Achievement checks -----

    def _check_npc_achievements(self, total_npcs):
        if len(self.npcs_helped) >= 1:
            self._unlock('first_help')
        # Precepts
        if PRECEPT_NPC_IDS.issubset(self.npcs_helped):
            self._unlock('precepts')
        # Half / all (exclude Mara and Buddha from "all helpable" count is
        # handled by caller passing the right total)
        if total_npcs > 0:
            if len(self.npcs_helped) >= total_npcs / 2:
                self._unlock('half_npcs')
            if len(self.npcs_helped) >= total_npcs:
                self._unlock('all_npcs')

    def check_hell_cleared(self, hell_npc_ids):
        """Caller passes the set of all hell NPC ids to check completion."""
        if hell_npc_ids and hell_npc_ids.issubset(self.npcs_helped):
            self._unlock('hell_cleared')

    def _unlock(self, achievement_id):
        if achievement_id not in self.unlocked and achievement_id in ACHIEVEMENTS:
            self.unlocked.add(achievement_id)
            self.newly_unlocked.append(achievement_id)

    def pop_notification(self):
        """Return the next freshly-unlocked achievement title, or None."""
        if self.newly_unlocked:
            aid = self.newly_unlocked.pop(0)
            return ACHIEVEMENTS[aid][0]
        return None

    # ----- Save/load -----

    def to_dict(self):
        return {
            'npcs_helped': list(self.npcs_helped),
            'obstacles_destroyed': self.obstacles_destroyed,
            'realms_visited': list(self.realms_visited),
            'unlocked': list(self.unlocked),
        }

    def from_dict(self, data):
        self.npcs_helped = set(data.get('npcs_helped', []))
        self.obstacles_destroyed = data.get('obstacles_destroyed', 0)
        self.realms_visited = set(data.get('realms_visited', []))
        self.unlocked = set(data.get('unlocked', []))
