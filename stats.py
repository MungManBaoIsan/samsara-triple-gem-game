"""
Player Stats System
Tracks Merit, Karma, and Dharma Wisdom

The Three Treasures that lead to seeing the Triple Gem clearly:
- Merit (Dana/Generosity): Earned through helping, sharing, selfless acts
- Karma (Ethical Action): Earned through right speech, right action, non-harm
- Dharma Wisdom (Understanding): Earned through recognizing truth, wise choices
"""

import config

class PlayerStats:
    """Manages player's spiritual progress statistics"""
    
    def __init__(self, starting_realm=None):
        """
        Initialize with starting stats
        
        Args:
            starting_realm: The realm player starts in (affects initial clarity)
        """
        self.merit = config.STARTING_MERIT
        self.karma = config.STARTING_KARMA
        self.wisdom = config.STARTING_WISDOM
        
        # Deva realm starts with clearer vision (privileged birth!)
        if starting_realm == 'deva':
            self.clarity = 0.7  # 70% clarity - much clearer! (was 10%)
        else:
            self.clarity = config.MIN_CLARITY  # 10% - dusty vision
        
    def add_merit(self, amount):
        """
        Add merit (generosity/selflessness)
        
        Args:
            amount: Amount of merit to add (can be negative)
        """
        self.merit += amount
        self.merit = max(0, self.merit)  # Can't go below 0
        self._update_clarity()
        
    def add_karma(self, amount):
        """
        Add karma points (ethical action)
        
        Args:
            amount: Number of karma points to add (can be negative)
        """
        self.karma += amount
        # Karma can be negative (bad karma)
        self._update_clarity()
        
    def add_wisdom(self, amount):
        """
        Add dharma wisdom (understanding/insight)
        
        Args:
            amount: Number of wisdom points to add (can be negative)
        """
        self.wisdom += amount
        self.wisdom = max(0, self.wisdom)  # Can't go below 0
        self._update_clarity()
        
    def apply_consequences(self, consequences):
        """
        Apply consequences from a choice
        
        Args:
            consequences: Dict with 'merit', 'karma', 'wisdom' keys
        """
        if 'merit' in consequences:
            self.add_merit(consequences['merit'])
        if 'karma' in consequences:
            self.add_karma(consequences['karma'])
        if 'wisdom' in consequences:
            self.add_wisdom(consequences['wisdom'])
            
    def _update_clarity(self):
        """
        Update clarity level based on wisdom - "Clearing the Dust from Your Eyes"
        
        Clarity represents how clearly you can see through the dust.
        Higher wisdom = less dust = clearer vision (but HARD to achieve!)
        """
        # Clarity is primarily based on wisdom (MUCH HARDER NOW!)
        wisdom_factor = min(self.wisdom / config.WISDOM_FOR_MAX_CLARITY, 1.0)
        
        # Merit and positive karma help slightly (but need MORE now!)
        bonus_clarity = 0
        if self.merit > 50:  # Was 20 - now MUCH harder!
            bonus_clarity += 0.03  # Was 0.05 - now smaller bonus!
        if self.karma > 50:  # Was 20 - now MUCH harder!
            bonus_clarity += 0.03  # Was 0.05 - now smaller bonus!
            
        # Calculate total clarity - dust slowly clears
        self.clarity = config.MIN_CLARITY + (wisdom_factor * (config.MAX_CLARITY - config.MIN_CLARITY))
        self.clarity = min(self.clarity + bonus_clarity, config.MAX_CLARITY)
        
    def get_stats_summary(self):
        """
        Get a summary of current stats
        
        Returns:
            Dict with all stat information
        """
        return {
            'merit': self.merit,
            'karma': self.karma,
            'wisdom': self.wisdom,
            'clarity': self.clarity,
            'clarity_percent': int(self.clarity * 100)
        }
        
    def can_see_temple(self):
        """
        Check if player has enough wisdom to see the temple
        
        Returns:
            bool: True if clarity is high enough to see temple
        """
        return self.clarity >= 0.5  # Need 50% clarity to start seeing temple
        
    def is_enlightened(self):
        """
        Check if player has reached enlightenment (won the game)
        
        Returns:
            bool: True if player has enough wisdom/merit/karma for enlightenment
        """
        import config
        # Requires high levels in all three aspects - MUCH HARDER NOW!
        return (self.wisdom >= config.ENLIGHTENMENT_WISDOM and 
                self.merit >= config.ENLIGHTENMENT_MERIT and 
                self.karma >= config.ENLIGHTENMENT_KARMA)
    
    def can_enter_realm(self, realm_name):
        """
        Check if player has sufficient stats to enter a realm
        
        Args:
            realm_name: Name of realm to check
            
        Returns:
            tuple: (can_enter: bool, missing_stats: dict)
        """
        import config
        
        if realm_name not in config.REALM_REQUIREMENTS:
            return True, {}
            
        requirements = config.REALM_REQUIREMENTS[realm_name]
        missing = {}
        
        if self.wisdom < requirements['wisdom']:
            missing['wisdom'] = requirements['wisdom'] - self.wisdom
        if self.merit < requirements['merit']:
            missing['merit'] = requirements['merit'] - self.merit
        if self.karma < requirements['karma']:
            missing['karma'] = requirements['karma'] - self.karma
            
        can_enter = len(missing) == 0
        return can_enter, missing
    
    def get_requirements_for_realm(self, realm_name):
        """
        Get stat requirements for a realm
        
        Args:
            realm_name: Name of realm
            
        Returns:
            dict: Requirements or empty dict
        """
        import config
        return config.REALM_REQUIREMENTS.get(realm_name, {})
                
    def set_starting_stats(self, stats_dict):
        """
        Set starting stats from past life selection
        
        Args:
            stats_dict: Dict with 'merit', 'karma', 'wisdom' keys
        """
        self.merit = stats_dict.get('merit', 0)
        self.karma = stats_dict.get('karma', 0)
        self.wisdom = stats_dict.get('wisdom', 0)
        self._update_clarity()
        
    def to_dict(self):
        """
        Convert stats to dictionary for saving
        
        Returns:
            Dict representation of stats
        """
        return {
            'merit': self.merit,
            'karma': self.karma,
            'wisdom': self.wisdom
        }
        
    def from_dict(self, data):
        """
        Load stats from dictionary
        
        Args:
            data: Dict with saved stat data
        """
        self.merit = data.get('merit', 0)
        self.karma = data.get('karma', 0)
        self.wisdom = data.get('wisdom', 0)
        self._update_clarity()
