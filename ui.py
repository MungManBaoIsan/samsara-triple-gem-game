"""
UI System
Manages user interface, HUD, and stats display
"""

import pygame
import config

class UI:
    """Handles all user interface elements"""
    
    def __init__(self):
        """Initialize UI system"""
        pass
        
    def draw_stats_panel(self, surface, stats, font_medium, font_small):
        """
        Draw the stats panel showing Merit, Karma, Wisdom, and Clarity
        
        Args:
            surface: Surface to draw on
            stats: PlayerStats object
            font_medium: Medium font
            font_small: Small font
        """
        panel_width = 300
        panel_height = 180
        panel_x = config.SCREEN_WIDTH - panel_width - 10
        panel_y = 10
        
        # Draw panel background
        panel_surface = pygame.Surface((panel_width, panel_height))
        panel_surface.set_alpha(220)
        panel_surface.fill(config.DARK_GRAY)
        surface.blit(panel_surface, (panel_x, panel_y))
        
        # Draw border
        pygame.draw.rect(surface, config.GOLD, 
                        (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Title
        title_surface = font_medium.render("Spiritual Progress", True, config.GOLD)
        surface.blit(title_surface, (panel_x + 10, panel_y + 10))
        
        # Stats
        y_offset = panel_y + 45
        
        # Merit
        merit_text = f"Merit: {stats.merit}"
        merit_surface = font_small.render(merit_text, True, config.GOLD)
        surface.blit(merit_surface, (panel_x + 20, y_offset))
        
        # Karma
        karma_color = config.BLUE if stats.karma >= 0 else config.RED
        karma_text = f"Karma: {stats.karma}"
        karma_surface = font_small.render(karma_text, True, karma_color)
        surface.blit(karma_surface, (panel_x + 20, y_offset + 30))
        
        # Wisdom
        wisdom_text = f"Wisdom: {stats.wisdom}"
        wisdom_surface = font_small.render(wisdom_text, True, config.PURPLE)
        surface.blit(wisdom_surface, (panel_x + 20, y_offset + 60))
        
        # Clarity
        clarity_percent = int(stats.clarity * 100)
        clarity_text = f"Clarity: {clarity_percent}%"
        clarity_surface = font_small.render(clarity_text, True, config.WHITE)
        surface.blit(clarity_surface, (panel_x + 20, y_offset + 90))
        
        # Clarity bar
        bar_width = 260
        bar_height = 20
        bar_x = panel_x + 20
        bar_y = y_offset + 118
        
        # Background
        pygame.draw.rect(surface, config.BLACK, 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # Fill (based on clarity)
        fill_width = int(bar_width * stats.clarity)
        if fill_width > 0:
            # Color gradient from red to gold based on clarity
            if stats.clarity < 0.5:
                fill_color = config.RED
            elif stats.clarity < 0.8:
                fill_color = config.ORANGE
            else:
                fill_color = config.GOLD
                
            pygame.draw.rect(surface, fill_color,
                           (bar_x, bar_y, fill_width, bar_height))
        
        # Border
        pygame.draw.rect(surface, config.WHITE,
                        (bar_x, bar_y, bar_width, bar_height), 2)
                        
    def draw_controls_hint(self, surface, font_small, in_encounter=False):
        """
        Draw control hints at bottom of screen
        
        Args:
            surface: Surface to draw on
            font_small: Small font
            in_encounter: Whether player is in an encounter
        """
        if in_encounter:
            hints = "↑↓ Select | ENTER Choose"
        else:
            hints = ("WASD Move | E Talk | X Strike | M Meditate | "
                     "J Journal | G Glossary | H Help | ESC Pause")
            
        hint_surface = font_small.render(hints, True, config.LIGHT_GRAY)
        hint_x = 10
        hint_y = config.SCREEN_HEIGHT - 25
        
        # Draw background for readability
        bg_rect = hint_surface.get_rect()
        bg_rect.x = hint_x - 5
        bg_rect.y = hint_y - 5
        bg_rect.width += 10
        bg_rect.height += 10
        
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(180)
        bg_surface.fill(config.BLACK)
        surface.blit(bg_surface, (bg_rect.x, bg_rect.y))
        
        surface.blit(hint_surface, (hint_x, hint_y))
        
    def draw_notification(self, surface, message, font_medium, y_position=None):
        """
        Draw a notification message
        
        Args:
            surface: Surface to draw on
            message: Message to display
            font_medium: Medium font
            y_position: Y position (default: center of screen)
        """
        if y_position is None:
            y_position = config.SCREEN_HEIGHT // 2
            
        text_surface = font_medium.render(message, True, config.GOLD)
        text_x = (config.SCREEN_WIDTH - text_surface.get_width()) // 2
        
        # Background
        bg_width = text_surface.get_width() + 40
        bg_height = text_surface.get_height() + 20
        bg_x = text_x - 20
        bg_y = y_position - 10
        
        bg_surface = pygame.Surface((bg_width, bg_height))
        bg_surface.set_alpha(200)
        bg_surface.fill(config.DARK_GRAY)
        surface.blit(bg_surface, (bg_x, bg_y))
        
        pygame.draw.rect(surface, config.GOLD,
                        (bg_x, bg_y, bg_width, bg_height), 2)
        
        surface.blit(text_surface, (text_x, y_position))
        
    def draw_past_life_selection(self, surface, font_large, font_medium, selected_index):
        """Draw past life selection - clean layout, no overlaps."""
        surface.fill(config.BLACK)

        # ── TITLE ──────────────────────────────────────────── y=30
        title_surf = font_large.render("Choose Your Past Life", True, config.GOLD)
        surface.blit(title_surf,
                     ((config.SCREEN_WIDTH - title_surf.get_width()) // 2, 30))

        sub_surf = font_medium.render(
            "Your karma from past actions determines where you begin...",
            True, config.LIGHT_GRAY)
        surface.blit(sub_surf,
                     ((config.SCREEN_WIDTH - sub_surf.get_width()) // 2, 78))

        pygame.draw.line(surface, config.GOLD, (80, 110),
                         (config.SCREEN_WIDTH - 80, 110), 1)

        # ── SCENARIO LIST ──────────────────────────────────── y=120
        scenarios = list(config.PAST_LIFE_SCENARIOS.items())
        font_small = config.make_font(config.FONT_SIZE_SMALL)

        # 6 items in 590px (720 - 110 title - 60 instructions = 550 → use 90px each)
        item_h = 88
        start_y = 118

        for i, (key, scenario) in enumerate(scenarios):
            y = start_y + i * item_h
            selected = (i == selected_index)

            if selected:
                bg = pygame.Rect(60, y + 2, config.SCREEN_WIDTH - 120, item_h - 6)
                pygame.draw.rect(surface, config.DARK_GRAY, bg)
                pygame.draw.rect(surface, config.GOLD, bg, 2)
                title_color = config.GOLD
                desc_color  = config.WHITE
                arrow = "▶ "
            else:
                title_color = config.LIGHT_GRAY
                desc_color  = (150, 150, 150)
                arrow = "  "

            # Title line
            t_surf = font_medium.render(arrow + scenario['title'],
                                        True, title_color)
            surface.blit(t_surf, (80, y + 10))

            # Description — show full text, word-wrapped to one line at small size
            desc = scenario['description']
            # Truncate to fit one line at font_small width
            max_w = config.SCREEN_WIDTH - 200
            while font_small.size(desc)[0] > max_w and len(desc) > 20:
                desc = desc[:desc.rfind(' ', 0, -1)]
            if desc != scenario['description']:
                desc += '...'
            d_surf = font_small.render(desc, True, desc_color)
            surface.blit(d_surf, (90, y + 42))

            # "Press SPACE" hint for selected
            if selected:
                hint = font_small.render("SPACE to read full story",
                                         True, (180, 180, 80))
                surface.blit(hint, (config.SCREEN_WIDTH - hint.get_width() - 80,
                                    y + 42))

        # ── INSTRUCTIONS ───────────────────────────────────── y=660
        inst = font_medium.render(
            "↑↓ Select  |  SPACE Read Full Story  |  ENTER Begin",
            True, config.LIGHT_GRAY)
        surface.blit(inst,
                     ((config.SCREEN_WIDTH - inst.get_width()) // 2,
                      config.SCREEN_HEIGHT - 48))
    
    def draw_past_life_story(self, surface, font_large, font_medium, scenario_key):
        """
        Draw full past life story for selected scenario
        
        Args:
            surface: Surface to draw on
            font_large: Large font for title
            font_medium: Medium font for text
            scenario_key: Key of scenario to display
        """
        surface.fill(config.BLACK)
        
        scenario = config.PAST_LIFE_SCENARIOS[scenario_key]
        
        # Title
        title_surface = font_large.render(scenario['title'], True, config.GOLD)
        title_x = (config.SCREEN_WIDTH - title_surface.get_width()) // 2
        surface.blit(title_surface, (title_x, 40))
        
        # Draw decorative line under title
        line_y = 85
        pygame.draw.line(surface, config.GOLD, (200, line_y), (config.SCREEN_WIDTH - 200, line_y), 2)
        
        # Story box with yellow borders (like dialogue!)
        box_width = 1100
        box_height = 600
        box_x = (config.SCREEN_WIDTH - box_width) // 2
        box_y = 110
        
        # Main box background
        pygame.draw.rect(surface, config.DARK_GRAY, (box_x, box_y, box_width, box_height))
        
        # THICK YELLOW TOP LINE
        pygame.draw.rect(surface, (255, 255, 0), (box_x, box_y, box_width, 6))
        
        # THICK YELLOW BOTTOM LINE
        pygame.draw.rect(surface, (255, 255, 0), (box_x, box_y + box_height - 6, box_width, 6))
        
        # Thin gold outline
        pygame.draw.rect(surface, config.GOLD, (box_x, box_y, box_width, box_height), 2)
        
        # Get full story text
        full_story = scenario.get('full_story', scenario['description'])
        
        # Word wrap the story text - USE MEDIUM FONT FOR READABILITY!
        story_font = config.make_font(config.FONT_SIZE_MEDIUM)
        words = full_story.split()
        lines = []
        current_line = ""
        max_width = box_width - 80  # Padding
        
        for word in words:
            test_line = current_line + word + " "
            test_surface = story_font.render(test_line, True, config.WHITE)
            
            if test_surface.get_width() > max_width:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
            else:
                current_line = test_line

        if current_line:
            lines.append(current_line.strip())

        # Draw story text with proper line spacing
        text_y = box_y + 30
        line_height = 35

        for line in lines:
            if text_y + line_height > box_y + box_height - 40:
                break
            line_surface = story_font.render(line, True, config.WHITE)
            surface.blit(line_surface, (box_x + 40, text_y))
            text_y += line_height
        
        # Starting stats display
        stats_y = box_y + box_height + 20
        stats_text = f"Starting Stats: Merit {scenario['starting_stats']['merit']}, " \
                    f"Karma {scenario['starting_stats']['karma']}, " \
                    f"Wisdom {scenario['starting_stats']['wisdom']}"
        stats_surface = font_medium.render(stats_text, True, config.LIGHT_GRAY)
        stats_x = (config.SCREEN_WIDTH - stats_surface.get_width()) // 2
        surface.blit(stats_surface, (stats_x, stats_y))
        
        # Instructions
        instructions = "Press any key to return to selection"
        inst_surface = font_medium.render(instructions, True, config.GOLD)
        inst_x = (config.SCREEN_WIDTH - inst_surface.get_width()) // 2
        surface.blit(inst_surface, (inst_x, config.SCREEN_HEIGHT - 60))
        
    def draw_title_screen(self, surface, font_large, font_medium):
        """Draw the opening title screen with no overlapping elements."""
        surface.fill(config.BLACK)

        # ── TITLE ───────────────────────────────────────────  y=120
        title_font = config.make_font(72)
        title_surf = title_font.render("SAMSARA", True, config.GOLD)
        surface.blit(title_surf,
                     ((config.SCREEN_WIDTH - title_surf.get_width()) // 2, 80))

        # ── SUBTITLE ────────────────────────────────────────  y=170
        subtitle_surf = font_large.render("Journey to the Triple Gem",
                                          True, config.LIGHT_GRAY)
        surface.blit(subtitle_surf,
                     ((config.SCREEN_WIDTH - subtitle_surf.get_width()) // 2, 160))

        # ── GOLD DIVIDER ────────────────────────────────────  y=210
        pygame.draw.line(surface, config.GOLD,
                         (300, 210), (config.SCREEN_WIDTH - 300, 210), 2)

        # ── DESCRIPTION LINES ──────────────────────────────  y=230..330
        desc_lines = [
            "Navigate through the six realms of existence.",
            "Make choices that shape your karma.",
            "Find refuge in the Triple Gem.",
            "Escape the cycle of suffering.",
        ]
        y = 235
        for line in desc_lines:
            surf = font_medium.render(line, True, config.LIGHT_GRAY)
            surface.blit(surf,
                         ((config.SCREEN_WIDTH - surf.get_width()) // 2, y))
            y += 34

        # ── GOLD DIVIDER ────────────────────────────────────  y=360
        pygame.draw.line(surface, config.GOLD,
                         (300, 375), (config.SCREEN_WIDTH - 300, 375), 2)

        # ── MENU OPTIONS ───────────────────────────────────  drawn by main.py
        # (main.py calls render_menu which draws options below this y=400 area)

        # ── VERSION LABEL ──────────────────────────────────  bottom-right
        ver_font = config.make_font(22)
        ver_surf = ver_font.render("v1.0", True, (120, 120, 80))
        surface.blit(ver_surf,
                     (config.SCREEN_WIDTH - ver_surf.get_width() - 12,
                      config.SCREEN_HEIGHT - 24))
