"""
NPC System
Manages non-player characters, their dialogues, and state progression
"""

import json
import config

class NPC:
    """Represents a single NPC with dialogue trees and state"""
    
    def __init__(self, npc_data):
        """
        Initialize NPC from data
        
        Args:
            npc_data: Dict with NPC information
        """
        self.id = npc_data.get('id', '')
        self.name = npc_data.get('name', 'Unnamed')
        self.title = npc_data.get('title', '')
        self.realm = npc_data.get('realm', '')
        self.x = npc_data.get('x', 0)
        self.y = npc_data.get('y', 0)
        self.color = tuple(npc_data.get('color', [200, 100, 200]))
        self.description = npc_data.get('description', '')
        self.npc_type = npc_data.get('type', 'suffering')  # 'suffering' or 'teacher' or 'mixed'
        
        # Dialogue system
        self.dialogues = npc_data.get('dialogues', [])
        self.current_dialogue_index = 0
        self.interaction_count = 0
        
        # State tracking
        self.state = 'initial'  # Can be: initial, helped_once, transformed, enlightened
        self.player_helped = False
        
    def can_interact(self):
        """
        Check if player can interact with this NPC
        
        Returns:
            bool: True if NPC has more dialogues available
        """
        return self.current_dialogue_index < len(self.dialogues)
        
    def get_current_dialogue(self, player_stats):
        """
        Get current dialogue based on NPC state and player stats
        
        Args:
            player_stats: PlayerStats object
            
        Returns:
            Dict with dialogue data or None if no dialogue available
        """
        if not self.can_interact():
            # Return a default "already talked" message
            return {
                'text': self.get_repeat_dialogue(),
                'choices': []
            }
            
        dialogue = self.dialogues[self.current_dialogue_index]
        
        # Check if player meets requirements for this dialogue
        requirements = dialogue.get('requirements', {})
        
        if not self.meets_requirements(player_stats, requirements):
            # Return a "not ready" message
            return {
                'text': self.get_not_ready_dialogue(requirements),
                'choices': []
            }
            
        return dialogue
        
    def meets_requirements(self, player_stats, requirements):
        """
        Check if player meets requirements for a dialogue
        
        Args:
            player_stats: PlayerStats object
            requirements: Dict with stat requirements
            
        Returns:
            bool: True if requirements met
        """
        if 'wisdom' in requirements:
            if player_stats.wisdom < requirements['wisdom']:
                return False
        if 'merit' in requirements:
            if player_stats.merit < requirements['merit']:
                return False
        if 'karma' in requirements:
            if player_stats.karma < requirements['karma']:
                return False
        if 'interaction_count' in requirements:
            if self.interaction_count < requirements['interaction_count']:
                return False
                
        return True
        
    def get_repeat_dialogue(self):
        """Get dialogue for when player talks to NPC again after exhausting dialogues"""
        repeat_messages = {
            'suffering': f"{self.name}: Thank you for your compassion. I'm still working on understanding what you taught me.",
            'teacher': f"{self.name}: You've learned what I have to teach. Continue on your path with wisdom.",
            'mixed': f"{self.name}: We've shared much. May your journey continue well."
        }
        return repeat_messages.get(self.npc_type, f"{self.name}: May you find peace.")
        
    def get_not_ready_dialogue(self, requirements):
        """Get dialogue when player doesn't meet requirements"""
        if 'wisdom' in requirements:
            return f"{self.name}: You're not ready to understand what I have to share yet. Cultivate more wisdom and return."
        if 'interaction_count' in requirements:
            return f"{self.name}: Give me time to reflect on our last conversation. Return later."
        return f"{self.name}: Come back when you've grown more on your path."
        
    def advance_dialogue(self):
        """Move to next dialogue in sequence"""
        self.current_dialogue_index += 1
        self.interaction_count += 1
        
    def update_state(self, new_state):
        """
        Update NPC's internal state
        
        Args:
            new_state: New state string
        """
        self.state = new_state
        
    def mark_helped(self):
        """Mark that player has helped this NPC"""
        self.player_helped = True
        
    def get_display_name(self):
        """
        Get display name for NPC
        
        Returns:
            str: Full name with title
        """
        if self.title:
            return f"{self.name}\n{self.title}"
        return self.name
        
    def get_distance_from_player(self, player_x, player_y):
        """
        Calculate distance from player
        
        Args:
            player_x: Player x position
            player_y: Player y position
            
        Returns:
            float: Distance in pixels
        """
        dx = self.x - player_x
        dy = self.y - player_y
        return (dx * dx + dy * dy) ** 0.5
        
    def to_dict(self):
        """
        Convert NPC state to dictionary for saving
        
        Returns:
            Dict with NPC state
        """
        return {
            'id': self.id,
            'current_dialogue_index': self.current_dialogue_index,
            'interaction_count': self.interaction_count,
            'state': self.state,
            'player_helped': self.player_helped
        }
        
    def from_dict(self, data):
        """
        Load NPC state from dictionary
        
        Args:
            data: Dict with saved NPC state
        """
        self.current_dialogue_index = data.get('current_dialogue_index', 0)
        self.interaction_count = data.get('interaction_count', 0)
        self.state = data.get('state', 'initial')
        self.player_helped = data.get('player_helped', False)


class NPCManager:
    """Manages all NPCs in the game"""
    
    def __init__(self):
        """Initialize NPC manager"""
        self.npcs = {}
        self.load_npcs()
        
    def load_npcs(self):
        """Load NPCs from JSON file"""
        try:
            with open(config.NPCS_FILE, 'r') as f:
                data = json.load(f)
                for npc_id, npc_data in data.items():
                    npc_data['id'] = npc_id
                    self.npcs[npc_id] = NPC(npc_data)
        except FileNotFoundError:
            # Create default NPCs if file doesn't exist
            self.create_default_npcs()
            
    def create_default_npcs(self):
        """Create default test NPCs"""
        # Hell Realm NPC - The Vengeful Warrior
        hell_npc_data = {
            'id': 'vengeful_warrior',
            'name': 'Kara',
            'title': 'The Vengeful Warrior',
            'realm': 'hell',
            'x': 2800,
            'y': 1600,
            'color': [255, 100, 100],
            'description': 'A warrior consumed by rage, seeking revenge for past betrayals.',
            'type': 'suffering',
            'dialogues': [
                {
                    'requirements': {},
                    'text': "Kara stands before you, fists clenched, jaw tight. Her eyes burn with rage.\n\n\"They BETRAYED me! After everything I did for them! I'll make them PAY for what they did. I'll destroy them like they destroyed me!\"\n\nShe's shaking with anger. What do you say?",
                    'choices': [
                        {
                            'text': 'You should destroy them! They deserve it!',
                            'consequences': {
                                'merit': -5,
                                'karma': -10,
                                'wisdom': 0,
                                'message': 'Kara nods grimly. \"Yes... revenge...\" But you both remain trapped in hatred. The poison spreads.',
                                'npc_state': 'initial'
                            }
                        },
                        {
                            'text': 'I understand your pain. Betrayal hurts deeply.',
                            'consequences': {
                                'merit': 5,
                                'karma': 5,
                                'wisdom': 10,
                                'message': 'Kara pauses. For a moment, the rage cracks and you see the hurt underneath. \"It does hurt... so much...\"',
                                'npc_state': 'helped_once'
                            }
                        },
                        {
                            'text': 'Hatred is like holding a hot coal. You\'re the one getting burned.',
                            'consequences': {
                                'merit': 10,
                                'karma': 10,
                                'wisdom': 15,
                                'message': 'Kara stops. Really stops. Her hands unclench slowly. \"I... I am burning, aren\'t I? This rage is destroying ME.\"',
                                'npc_state': 'helped_once'
                            }
                        }
                    ]
                },
                {
                    'requirements': {'wisdom': 10, 'interaction_count': 1},
                    'text': "Kara looks less tense than before. The fire in her eyes has dimmed slightly.\n\n\"I've been thinking about what you said. The anger... it's like a weight I carry everywhere. But I don't know how to let it go. They hurt me! Doesn't that mean they were wrong and I'm right to be angry?\"",
                    'choices': [
                        {
                            'text': 'Yes, you have every right to be angry!',
                            'consequences': {
                                'merit': 0,
                                'karma': -5,
                                'wisdom': 0,
                                'message': 'Kara\'s jaw tightens again. The progress fades. \"You\'re right. I DO have the right.\" The anger returns.',
                                'npc_state': 'helped_once'
                            }
                        },
                        {
                            'text': 'They were wrong. But holding anger only punishes YOU, not them.',
                            'consequences': {
                                'merit': 10,
                                'karma': 10,
                                'wisdom': 20,
                                'message': 'Kara nods slowly. \"They probably don\'t even think about me anymore. But I think about them every day. I\'m the prisoner here.\"',
                                'npc_state': 'transformed'
                            }
                        },
                        {
                            'text': 'Hurt people hurt people. Maybe they were suffering too.',
                            'consequences': {
                                'merit': 12,
                                'karma': 12,
                                'wisdom': 25,
                                'message': 'Kara\'s eyes widen. \"I... never thought about what pain they might have been in. Could my anger be the same as theirs?\"',
                                'npc_state': 'transformed'
                            }
                        }
                    ]
                },
                {
                    'requirements': {'wisdom': 30, 'interaction_count': 2},
                    'text': "Kara smiles when she sees you. There's peace in her face now.\n\n\"Friend, I wanted to thank you. I've been practicing letting go of the anger. Some days are harder than others, but... I'm free. The betrayal still happened, but it doesn't own me anymore. I hope you find your own freedom too.\"",
                    'choices': [
                        {
                            'text': 'I\'m so glad to hear this. You\'ve found real wisdom.',
                            'consequences': {
                                'merit': 5,
                                'karma': 5,
                                'wisdom': 10,
                                'message': 'Kara bows to you. \"We helped each other. May all beings find this peace.\"',
                                'npc_state': 'enlightened'
                            }
                        }
                    ]
                }
            ]
        }
        
        self.npcs['vengeful_warrior'] = NPC(hell_npc_data)
        
    def get_nearby_npc(self, player_x, player_y, max_distance=50):
        """
        Find NPC near player
        
        Args:
            player_x: Player x position
            player_y: Player y position
            max_distance: Maximum distance to consider "nearby"
            
        Returns:
            NPC object or None
        """
        for npc in self.npcs.values():
            distance = npc.get_distance_from_player(player_x, player_y)
            if distance <= max_distance:
                return npc
        return None
        
    def get_npcs_in_realm(self, realm_name):
        """
        Get all NPCs in a specific realm
        
        Args:
            realm_name: Name of realm
            
        Returns:
            List of NPC objects
        """
        return [npc for npc in self.npcs.values() if npc.realm == realm_name]
        
    def get_all_npcs(self):
        """
        Get all NPCs
        
        Returns:
            List of all NPC objects
        """
        return list(self.npcs.values())
        
    def to_dict(self):
        """
        Convert all NPC states to dictionary for saving
        
        Returns:
            Dict with all NPC states
        """
        return {npc_id: npc.to_dict() for npc_id, npc in self.npcs.items()}
        
    def from_dict(self, data):
        """
        Load all NPC states from dictionary
        
        Args:
            data: Dict with saved NPC states
        """
        for npc_id, npc_state in data.items():
            if npc_id in self.npcs:
                self.npcs[npc_id].from_dict(npc_state)
