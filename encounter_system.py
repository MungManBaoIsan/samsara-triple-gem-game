"""
Encounter System
Manages NPC encounters, dialogue, choices, and consequences
"""

import sys
import pygame
import json
import config

IS_WEB = sys.platform == 'emscripten'

class Encounter:
    """Represents a single encounter with choices and consequences"""
    
    def __init__(self, encounter_data):
        """
        Initialize encounter from data
        
        Args:
            encounter_data: Dict with encounter information
        """
        self.id = encounter_data.get('id', '')
        self.realm = encounter_data.get('realm', '')
        self.title = encounter_data.get('title', '')
        self.description = encounter_data.get('description', '')
        self.choices = encounter_data.get('choices', [])
        self.completed = False
        
    def get_choice_count(self):
        """Get number of choices available"""
        return len(self.choices)
        
    def get_choice_text(self, index):
        """Get text for a specific choice"""
        if 0 <= index < len(self.choices):
            return self.choices[index].get('text', '')
        return ''
        
    def get_consequences(self, choice_index):
        """
        Get consequences for a choice
        
        Args:
            choice_index: Index of chosen option
            
        Returns:
            Dict with consequences
        """
        if 0 <= choice_index < len(self.choices):
            return self.choices[choice_index].get('consequences', {})
        return {}
        
    def mark_completed(self):
        """Mark this encounter as completed"""
        self.completed = True


class EncounterSystem:
    """Manages all encounters and the encounter UI"""
    
    def __init__(self):
        """Initialize encounter system"""
        self.encounters = {}
        self.active_encounter = None
        self.selected_choice = 0
        self.showing_result = False
        self.result_message = ""
        self.result_timer = 0
        
        # Track previous stats for change display
        self.previous_merit = 0
        self.previous_karma = 0
        self.previous_wisdom = 0
        
        # Load encounters from file
        self.load_encounters()
        
    def load_encounters(self):
        """Load encounters from JSON file"""
        try:
            with open(config.ENCOUNTERS_FILE, 'r') as f:
                data = json.load(f)
                for encounter_id, encounter_data in data.items():
                    encounter_data['id'] = encounter_id
                    self.encounters[encounter_id] = Encounter(encounter_data)
        except FileNotFoundError:
            # Create default test encounter if file doesn't exist
            self.create_default_encounters()
            
    def create_default_encounters(self):
        """Create a default test encounter for Phase 1"""
        test_encounter_data = {
            'id': 'test_encounter_anger',
            'realm': 'hell',
            'title': 'The Angry Bully',
            'description': 'You encounter someone spreading cruel rumors about you. Others are laughing. Your face burns with humiliation and anger rises in your chest.',
            'choices': [
                {
                    'text': "I'll spread even worse rumors about them!",
                    'consequences': {
                        'merit': -5,
                        'karma': -10,
                        'wisdom': 0,
                        'message': 'Revenge only creates more suffering. You feel the poison of hatred burning in your own heart.'
                    }
                },
                {
                    'text': 'This hurts, but revenge will not heal me.',
                    'consequences': {
                        'merit': 5,
                        'karma': 5,
                        'wisdom': 10,
                        'message': 'You recognized the cycle of hatred. The pain remains, but you chose not to add fuel to the fire.'
                    }
                },
                {
                    'text': 'What pain are they carrying that makes them act this way?',
                    'consequences': {
                        'merit': 10,
                        'karma': 10,
                        'wisdom': 15,
                        'message': 'Deep wisdom arises. Hurt people hurt people. You see the bully is also suffering, trapped in their own anger.'
                    }
                }
            ]
        }
        
        self.encounters['test_encounter_anger'] = Encounter(test_encounter_data)
        
    def start_encounter(self, encounter_id):
        """
        Start a specific encounter
        
        Args:
            encounter_id: ID of encounter to start
            
        Returns:
            bool: True if encounter started successfully
        """
        if encounter_id in self.encounters:
            encounter = self.encounters[encounter_id]
            if not encounter.completed:
                self.active_encounter = encounter
                self.selected_choice = 0
                self.showing_result = False
                return True
        return False
        
    def handle_input(self, event):
        """
        Handle input during encounter
        
        Args:
            event: Pygame event
            
        Returns:
            Dict with consequences if choice made, None otherwise
        """
        if not self.active_encounter or self.showing_result:
            return None
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_choice = max(0, self.selected_choice - 1)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                max_choice = self.active_encounter.get_choice_count() - 1
                self.selected_choice = min(max_choice, self.selected_choice + 1)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Player made a choice
                return self.make_choice(self.selected_choice)
                
        return None
        
    def make_choice(self, choice_index):
        """
        Make a choice and get consequences
        
        Args:
            choice_index: Index of chosen option
            
        Returns:
            Dict with consequences
        """
        if not self.active_encounter:
            return None
            
        consequences = self.active_encounter.get_consequences(choice_index)
        self.result_message = consequences.get('message', '')
        self.showing_result = True
        
        # Check if this is a special NPC with longer reflection time
        encounter_id = self.active_encounter.id
        if 'evil_mara' in encounter_id:
            self.result_timer = 900  # 15 seconds for Mara (intense!)
        elif 'the_buddha' in encounter_id:
            self.result_timer = 1200  # 20 seconds for Buddha (sacred!)
        else:
            self.result_timer = 600  # 10 seconds for regular NPCs
        
        self.active_encounter.mark_completed()
        
        return consequences
        
    def update(self):
        """Update encounter state"""
        if self.showing_result:
            self.result_timer -= 1
            if self.result_timer <= 0:
                self.showing_result = False
                self.active_encounter = None
                
    def draw(self, surface, font_large, font_medium, player_stats=None):
        """
        Draw encounter UI
        
        Args:
            surface: Surface to draw on
            font_large: Large font for title
            font_medium: Medium font for text
            player_stats: PlayerStats object (optional) to show current stats
        """
        if not self.active_encounter:
            return
            
        # Dark background — alpha surface is expensive on web so use solid fill there
        if IS_WEB:
            surface.fill((10, 10, 10))
        else:
            overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(config.BLACK)
            surface.blit(overlay, (0, 0))
        
        # Draw dialogue box with YELLOW BORDER LINES
        box_width = 1000
        box_height = 500
        box_x = (config.SCREEN_WIDTH - box_width) // 2
        box_y = (config.SCREEN_HEIGHT - box_height) // 2
        
        # Main box background
        pygame.draw.rect(surface, config.DARK_GRAY, 
                        (box_x, box_y, box_width, box_height))
        
        # THICK YELLOW TOP LINE
        pygame.draw.rect(surface, (255, 255, 0), 
                        (box_x, box_y, box_width, 6))
        
        # THICK YELLOW BOTTOM LINE
        pygame.draw.rect(surface, (255, 255, 0), 
                        (box_x, box_y + box_height - 6, box_width, 6))
        
        # Thin gold outline around whole box
        pygame.draw.rect(surface, config.GOLD, 
                        (box_x, box_y, box_width, box_height), 2)
        
        if self.showing_result:
            # Show result message
            self.draw_result(surface, font_large, font_medium, 
                           box_x, box_y, box_width, box_height, player_stats)
        else:
            # Show choices
            self.draw_choices(surface, font_large, font_medium,
                            box_x, box_y, box_width, box_height)
                            
    def draw_choices(self, surface, font_large, font_medium, box_x, box_y, box_width, box_height):
        """Draw the encounter choices with dynamic description area."""
        font_small = config.make_font(config.FONT_SIZE_SMALL)

        # ── Title — split name and subtitle (get_display_name uses \n) ───────
        title_parts = self.active_encounter.title.split('\n')
        name_line     = title_parts[0]
        subtitle_line = title_parts[1] if len(title_parts) > 1 else None

        name_surf = font_large.render(name_line, True, config.GOLD)
        name_x = box_x + (box_width - name_surf.get_width()) // 2
        surface.blit(name_surf, (name_x, box_y + 12))
        title_bottom = box_y + 12 + name_surf.get_height() + 4

        if subtitle_line:
            sub_surf = font_medium.render(subtitle_line, True, config.GOLD)
            sub_x = box_x + (box_width - sub_surf.get_width()) // 2
            surface.blit(sub_surf, (sub_x, title_bottom))
            title_bottom += sub_surf.get_height() + 4

        title_bottom += 6  # breathing room before description

        # ── Work out how many lines the description needs ─────────────────
        desc_text = self.active_encounter.description
        padding  = 30
        text_w   = box_width - padding * 2
        line_h   = font_small.get_height() + 4

        desc_lines = self._wrap_lines(desc_text, font_small, text_w)

        # How many choices? Use taller rows on web (larger fonts + wrapping)
        n_choices  = self.active_encounter.get_choice_count()
        choice_row = 64 if IS_WEB else 50
        choice_h   = n_choices * choice_row
        footer_h   = 40                       # instruction line
        bottom_limit  = box_y + box_height - footer_h - choice_h - 10
        max_desc_h    = bottom_limit - title_bottom - 10

        # How many lines fit?
        max_lines = max(1, int(max_desc_h // line_h))
        visible   = desc_lines[:max_lines]
        overflow  = len(desc_lines) > max_lines

        # ── Draw description ──────────────────────────────────────────────
        text_y = title_bottom
        for line in visible:
            surf = font_small.render(line, True, config.WHITE)
            surface.blit(surf, (box_x + padding, text_y))
            text_y += line_h

        if overflow:
            more = font_small.render("▼ (scroll down to see more)", True, config.LIGHT_GRAY)
            surface.blit(more, (box_x + padding, text_y))
            text_y += line_h

        # ── Choices ───────────────────────────────────────────────────────
        choice_y = box_y + box_height - footer_h - choice_h
        for i in range(n_choices):
            choice_text = self.active_encounter.get_choice_text(i)
            if i == self.selected_choice:
                choice_color = config.GOLD
                prefix = "→ "
                # Subtle highlight bar
                bar = pygame.Surface((box_width - 60, 36), pygame.SRCALPHA)
                bar.fill((255, 215, 0, 28))
                surface.blit(bar, (box_x + 30, choice_y - 4))
            else:
                choice_color = config.LIGHT_GRAY
                prefix = "  "

            # Word-wrap choice text so long options don't overflow right edge
            choice_lines = self._wrap_lines(prefix + choice_text, font_medium, text_w - 20)
            for j, cl in enumerate(choice_lines[:2]):   # max 2 lines per choice
                cs = font_medium.render(cl, True, choice_color)
                surface.blit(cs, (box_x + 40, choice_y + j * (font_medium.get_height() + 2)))
            choice_y += choice_row

        # ── Instructions ──────────────────────────────────────────────────
        instr = font_medium.render("↑↓ Select  |  ENTER Choose", True, config.LIGHT_GRAY)
        surface.blit(instr, (box_x + padding, box_y + box_height - 35))

    def draw_result(self, surface, font_large, font_medium, box_x, box_y, box_width, box_height, player_stats=None):
        """Draw the result of a choice with CURRENT TOTAL stats and PROGRESS ARROWS"""
        font_small = config.make_font(config.FONT_SIZE_SMALL)
        padding = 30
        text_w  = box_width - padding * 2

        # Result message — word-wrapped with newline support
        result_lines = self._wrap_lines(self.result_message, font_medium, text_w)
        line_h = font_medium.get_height() + 4
        result_y = box_y + 30
        for line in result_lines[:8]:        # cap at 8 lines
            surf = font_medium.render(line, True, config.GOLD)
            surface.blit(surf, (box_x + padding, result_y))
            result_y += line_h
        
        # SHOW CURRENT TOTAL STATS WITH PROGRESS INDICATORS!
        if player_stats:
            stats_y = box_y + 260
            
            # Title
            stats_title = font_large.render("═══ YOUR PROGRESS ═══", True, config.WHITE)
            title_x = box_x + (box_width - stats_title.get_width()) // 2
            surface.blit(stats_title, (title_x, stats_y))
            
            stats_y += 50
            
            # MERIT
            merit_change = player_stats.merit - self.previous_merit
            arrow = "↑" if merit_change > 0 else ("↓" if merit_change < 0 else "→")
            arrow_color = (0,255,0) if merit_change > 0 else ((255,0,0) if merit_change < 0 else config.LIGHT_GRAY)
            merit_text = f"Merit: {self.previous_merit} {arrow} {player_stats.merit}"
            merit_surface = font_large.render(merit_text, True, config.GOLD)
            surface.blit(merit_surface, (box_x + 80, stats_y))
            if merit_change != 0:
                cs = font_medium.render(f"({merit_change:+d})", True, arrow_color)
                surface.blit(cs, (box_x + 80 + merit_surface.get_width() + 15, stats_y + 5))
            
            # KARMA
            karma_change = player_stats.karma - self.previous_karma
            arrow = "↑" if karma_change > 0 else ("↓" if karma_change < 0 else "→")
            arrow_color = (0,255,0) if karma_change > 0 else ((255,0,0) if karma_change < 0 else config.LIGHT_GRAY)
            karma_text = f"Karma: {self.previous_karma} {arrow} {player_stats.karma}"
            karma_main_color = config.BLUE if player_stats.karma >= 0 else config.RED
            karma_surface = font_large.render(karma_text, True, karma_main_color)
            surface.blit(karma_surface, (box_x + 80, stats_y + 45))
            if karma_change != 0:
                cs = font_medium.render(f"({karma_change:+d})", True, arrow_color)
                surface.blit(cs, (box_x + 80 + karma_surface.get_width() + 15, stats_y + 50))
            
            # WISDOM
            wisdom_change = player_stats.wisdom - self.previous_wisdom
            arrow = "↑" if wisdom_change > 0 else ("↓" if wisdom_change < 0 else "→")
            arrow_color = (0,255,0) if wisdom_change > 0 else ((255,0,0) if wisdom_change < 0 else config.LIGHT_GRAY)
            wisdom_text = f"Wisdom: {self.previous_wisdom} {arrow} {player_stats.wisdom}"
            wisdom_surface = font_large.render(wisdom_text, True, config.PURPLE)
            surface.blit(wisdom_surface, (box_x + 80, stats_y + 90))
            if wisdom_change != 0:
                cs = font_medium.render(f"({wisdom_change:+d})", True, arrow_color)
                surface.blit(cs, (box_x + 80 + wisdom_surface.get_width() + 15, stats_y + 95))
        
        # Instruction
        instruction_text = f"Reflecting... ({self.result_timer // 60}s remaining)"
        instruction_surface = font_medium.render(instruction_text, True, config.LIGHT_GRAY)
        surface.blit(instruction_surface,
                    (box_x + padding, box_y + box_height - 35))

    def _wrap_lines(self, text, font, max_width):
        """
        Word-wrap text respecting both soft wrapping (max_width) and
        hard line breaks (\\n). Returns a list of string lines.
        """
        result = []
        # Split on hard newlines first
        for paragraph in text.split('\n'):
            if paragraph.strip() == '':
                result.append('')   # keep blank lines as spacers
                continue
            words = paragraph.split(' ')
            current = []
            for word in words:
                test = ' '.join(current + [word])
                if font.size(test)[0] <= max_width:
                    current.append(word)
                else:
                    if current:
                        result.append(' '.join(current))
                    current = [word]
            if current:
                result.append(' '.join(current))
        return result

    def draw_wrapped_text(self, surface, text, font, color, x, y, max_width, max_height):
        """Legacy wrapper — now delegates to _wrap_lines."""
        lines = self._wrap_lines(text, font, max_width)
        line_height = font.get_height() + 5
        for i, line in enumerate(lines):
            if y + i * line_height > y + max_height:
                break
            surface.blit(font.render(line, True, color), (x, y + i * line_height))
            
    def is_active(self):
        """Check if an encounter is currently active"""
        return self.active_encounter is not None
        
    def get_nearby_encounter(self, player_x, player_y, player_realm):
        """
        Check if player is near any encounter trigger
        
        Args:
            player_x: Player x position
            player_y: Player y position
            player_realm: Current realm player is in
            
        Returns:
            str: Encounter ID if near one, None otherwise
        """
        # For Phase 1, simple test: trigger encounter if in hell realm
        # and player presses E key (checked elsewhere)
        for encounter_id, encounter in self.encounters.items():
            if encounter.realm == player_realm and not encounter.completed:
                return encounter_id
        return None
