"""
Additional UI Screens for Samsara
Journal, Achievements, Glossary, Help, Load Menu, and Meditation overlay.
Styled to match the existing yellow-bordered dialogue boxes.
"""

import pygame
import math
import config
from progress import ACHIEVEMENTS
from glossary import GLOSSARY
from save_system import SaveManager


def _draw_bordered_box(surface, x, y, w, h):
    """Draw the signature dark box with thick yellow top/bottom lines."""
    pygame.draw.rect(surface, config.DARK_GRAY, (x, y, w, h))
    pygame.draw.rect(surface, (255, 255, 0), (x, y, w, 6))
    pygame.draw.rect(surface, (255, 255, 0), (x, y + h - 6, w, 6))
    pygame.draw.rect(surface, config.GOLD, (x, y, w, h), 2)


def _wrap_text(text, font, max_width):
    """Word-wrap text to a pixel width, returning a list of lines."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = current + word + " "
        if font.size(test)[0] > max_width and current:
            lines.append(current.strip())
            current = word + " "
        else:
            current = test
    if current:
        lines.append(current.strip())
    return lines


class Screens:
    """Renders the full-screen menus and overlays."""

    def __init__(self):
        self.save_manager = SaveManager()

    # ---------------- HELP / CONTROLS ----------------

    def draw_help(self, surface, font_large, font_medium, font_small):
        surface.fill(config.BLACK)

        title = font_large.render("How to Play", True, config.GOLD)
        surface.blit(title, ((config.SCREEN_WIDTH - title.get_width()) // 2, 40))
        pygame.draw.line(surface, config.GOLD, (200, 90),
                         (config.SCREEN_WIDTH - 200, 90), 2)

        box_w, box_h = 1100, 640
        box_x = (config.SCREEN_WIDTH - box_w) // 2
        box_y = 110
        _draw_bordered_box(surface, box_x, box_y, box_w, box_h)

        sections = [
            ("CONTROLS", [
                "WASD / Arrow Keys  -  Move through the realms",
                "E  -  Talk to a nearby being",
                "X  -  Strike a nearby obstacle of delusion",
                "M  -  Meditate (restores a little, clears the mind)",
                "J  -  Open your Journal & Achievements",
                "G  -  Open the Glossary of Buddhist terms",
                "H  -  Open this Help screen",
                "P  -  Mute / unmute sound",
                "ESC  -  Pause menu (save & quit)",
            ]),
            ("YOUR PATH", [
                "Help suffering beings and strike obstacles to grow.",
                "Merit comes from generosity. Karma from right action.",
                "Wisdom from understanding. All three clear your vision.",
                "Dust clouds your sight until wisdom clears it.",
                "Reach the temple, face Mara, then meet the Buddha.",
            ]),
        ]

        y = box_y + 30
        for header, lines in sections:
            h_surf = font_medium.render(header, True, config.GOLD)
            surface.blit(h_surf, (box_x + 40, y))
            y += 38
            for line in lines:
                l_surf = font_small.render(line, True, config.WHITE)
                surface.blit(l_surf, (box_x + 60, y))
                y += 26
            y += 20

        hint = font_medium.render("Press any key to return", True, config.GOLD)
        surface.blit(hint, ((config.SCREEN_WIDTH - hint.get_width()) // 2,
                            config.SCREEN_HEIGHT - 55))

    # ---------------- JOURNAL / ACHIEVEMENTS ----------------

    def draw_journal(self, surface, font_large, font_medium, font_small,
                     tracker, npc_manager, stats, next_goal_text):
        surface.fill(config.BLACK)

        title = font_large.render("Journal", True, config.GOLD)
        surface.blit(title, ((config.SCREEN_WIDTH - title.get_width()) // 2, 30))
        pygame.draw.line(surface, config.GOLD, (200, 78),
                         (config.SCREEN_WIDTH - 200, 78), 2)

        # Left box: progress & goals
        left_w, left_h = 540, 620
        left_x = 120
        left_y = 95
        _draw_bordered_box(surface, left_x, left_y, left_w, left_h)

        y = left_y + 25
        header = font_medium.render("Progress", True, config.GOLD)
        surface.blit(header, (left_x + 30, y))
        y += 42

        total_npcs = len(npc_manager.npcs)
        helpable = max(0, total_npcs - 2)  # exclude Mara & Buddha
        rows = [
            f"Beings helped: {len(tracker.npcs_helped)} / {helpable}",
            f"Obstacles destroyed: {tracker.obstacles_destroyed}",
            f"Realms visited: {len(tracker.realms_visited)} / 6",
            f"Clarity: {int(stats.clarity * 100)}%",
            "",
            f"Merit: {stats.merit}    Karma: {stats.karma}    Wisdom: {stats.wisdom}",
        ]
        for row in rows:
            surface.blit(font_small.render(row, True, config.WHITE),
                         (left_x + 40, y))
            y += 30

        y += 15
        goal_header = font_medium.render("Next Goal", True, config.GOLD)
        surface.blit(goal_header, (left_x + 30, y))
        y += 38
        for line in _wrap_text(next_goal_text, font_small, left_w - 80):
            surface.blit(font_small.render(line, True, (180, 220, 180)),
                         (left_x + 40, y))
            y += 26

        # Right box: achievements
        right_w, right_h = 540, 620
        right_x = config.SCREEN_WIDTH - right_w - 120
        right_y = 95
        _draw_bordered_box(surface, right_x, right_y, right_w, right_h)

        y = right_y + 25
        ach_header = font_medium.render(
            f"Achievements  ({len(tracker.unlocked)}/{len(ACHIEVEMENTS)})",
            True, config.GOLD)
        surface.blit(ach_header, (right_x + 30, y))
        y += 42

        for aid, (a_title, a_desc, _hidden) in ACHIEVEMENTS.items():
            unlocked = aid in tracker.unlocked
            color = config.GOLD if unlocked else (110, 110, 110)
            mark = "✓ " if unlocked else "○ "
            surface.blit(font_small.render(mark + a_title, True, color),
                         (right_x + 40, y))
            y += 23
            desc_color = config.LIGHT_GRAY if unlocked else (90, 90, 90)
            shown_desc = a_desc if unlocked else "Locked"
            surface.blit(font_small.render("   " + shown_desc, True, desc_color),
                         (right_x + 40, y))
            y += 28

        hint = font_medium.render("Press J or ESC to return", True, config.GOLD)
        surface.blit(hint, ((config.SCREEN_WIDTH - hint.get_width()) // 2,
                            config.SCREEN_HEIGHT - 45))

    # ---------------- GLOSSARY ----------------

    def draw_glossary(self, surface, font_large, font_medium, font_small,
                      scroll_index):
        surface.fill(config.BLACK)

        title = font_large.render("Glossary", True, config.GOLD)
        surface.blit(title, ((config.SCREEN_WIDTH - title.get_width()) // 2, 30))
        pygame.draw.line(surface, config.GOLD, (200, 78),
                         (config.SCREEN_WIDTH - 200, 78), 2)

        box_w, box_h = 1100, 620
        box_x = (config.SCREEN_WIDTH - box_w) // 2
        box_y = 95
        _draw_bordered_box(surface, box_x, box_y, box_w, box_h)

        # Show a window of entries based on scroll_index
        per_page = 4
        start = scroll_index
        end = min(len(GLOSSARY), start + per_page)

        y = box_y + 30
        for entry in GLOSSARY[start:end]:
            term_line = f"{entry['term']}  ({entry['pron']})"
            surface.blit(font_medium.render(term_line, True, config.GOLD),
                         (box_x + 40, y))
            y += 36
            for line in _wrap_text(entry['def'], font_small, box_w - 90):
                surface.blit(font_small.render(line, True, config.WHITE),
                             (box_x + 55, y))
                y += 25
            for line in _wrap_text("In game: " + entry['game'],
                                   font_small, box_w - 90):
                surface.blit(font_small.render(line, True, (150, 190, 220)),
                             (box_x + 55, y))
                y += 25
            y += 18

        # Page indicator
        page = (scroll_index // per_page) + 1
        total_pages = (len(GLOSSARY) + per_page - 1) // per_page
        page_text = font_small.render(
            f"Page {page} / {total_pages}", True, config.LIGHT_GRAY)
        surface.blit(page_text, (box_x + box_w - 140, box_y + box_h - 30))

        hint = font_medium.render(
            "W/S or ↑↓ to Scroll  |  G or ESC to return", True, config.GOLD)
        surface.blit(hint, ((config.SCREEN_WIDTH - hint.get_width()) // 2,
                            config.SCREEN_HEIGHT - 45))

    # ---------------- LOAD MENU ----------------

    def draw_load_menu(self, surface, font_large, font_medium, font_small,
                       selected_slot):
        surface.fill(config.BLACK)

        title = font_large.render("Continue Journey", True, config.GOLD)
        surface.blit(title, ((config.SCREEN_WIDTH - title.get_width()) // 2, 60))
        pygame.draw.line(surface, config.GOLD, (200, 110),
                         (config.SCREEN_WIDTH - 200, 110), 2)

        slot_w, slot_h = 900, 130
        slot_x = (config.SCREEN_WIDTH - slot_w) // 2
        start_y = 170

        realm_names = {
            'hell': 'Hell Realm', 'hungry_ghost': 'Hungry Ghost Realm',
            'animal': 'Animal Realm', 'human': 'Human Realm',
            'asura': 'Asura Realm', 'deva': 'Deva Realm', 'temple': 'The Temple',
            'unknown': 'Unknown'
        }

        for i in range(1, SaveManager.NUM_SLOTS + 1):
            y = start_y + (i - 1) * (slot_h + 25)
            selected = (i == selected_slot)

            # Highlight selected
            bg = config.DARK_GRAY if not selected else (70, 65, 40)
            pygame.draw.rect(surface, bg, (slot_x, y, slot_w, slot_h))
            border_color = config.GOLD if selected else (120, 120, 120)
            border_w = 4 if selected else 2
            pygame.draw.rect(surface, border_color,
                             (slot_x, y, slot_w, slot_h), border_w)

            info = self.save_manager.get_slot_info(i)
            label = font_medium.render(f"Slot {i}", True, config.GOLD)
            surface.blit(label, (slot_x + 25, y + 15))

            if info:
                realm = realm_names.get(info['realm'], info['realm'])
                detail = (f"{realm}  -  Wisdom {info['wisdom']}, "
                          f"Merit {info['merit']}, Karma {info['karma']}")
                surface.blit(font_small.render(detail, True, config.WHITE),
                             (slot_x + 25, y + 58))
                playtime = SaveManager.format_play_time(info['play_time'])
                auto = "  (autosave)" if info['is_auto'] else ""
                surface.blit(font_small.render(
                    f"Time played: {playtime}{auto}", True, config.LIGHT_GRAY),
                    (slot_x + 25, y + 88))
            else:
                surface.blit(font_small.render("Empty", True, (120, 120, 120)),
                             (slot_x + 25, y + 60))

        hint = font_medium.render(
            "↑↓ Select  |  ENTER Load  |  ESC Back", True, config.GOLD)
        surface.blit(hint, ((config.SCREEN_WIDTH - hint.get_width()) // 2,
                            config.SCREEN_HEIGHT - 55))

    # ---------------- MEDITATION OVERLAY ----------------

    def draw_meditation(self, surface, font_large, font_medium, font_small,
                        breath_phase, focus_meter, time_left):
        # Dim the world behind
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT),
                                 pygame.SRCALPHA)
        overlay.fill((0, 0, 20, 210))
        surface.blit(overlay, (0, 0))

        title = font_large.render("Meditation", True, config.GOLD)
        surface.blit(title, ((config.SCREEN_WIDTH - title.get_width()) // 2, 70))

        # Breathing guide text
        # breath_phase in [0,1): 0-0.5 inhale, 0.5-1 exhale
        if breath_phase < 0.5:
            guide = "Breathe in..."
            scale = breath_phase * 2          # 0 -> 1
        else:
            guide = "Breathe out..."
            scale = 1 - (breath_phase - 0.5) * 2  # 1 -> 0

        guide_surf = font_medium.render(guide, True, config.WHITE)
        surface.blit(guide_surf,
                     ((config.SCREEN_WIDTH - guide_surf.get_width()) // 2, 140))

        # Expanding/contracting circle synced to breath
        cx, cy = config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2
        min_r, max_r = 60, 180
        radius = int(min_r + (max_r - min_r) * scale)

        for i in range(4):
            alpha = max(0, 120 - i * 30)
            ring = pygame.Surface((radius * 2 + i * 40, radius * 2 + i * 40),
                                  pygame.SRCALPHA)
            pygame.draw.circle(ring, (180, 200, 255, alpha),
                               (radius + i * 20, radius + i * 20),
                               radius + i * 20, 3)
            surface.blit(ring, (cx - radius - i * 20, cy - radius - i * 20))
        pygame.draw.circle(surface, (120, 160, 230), (cx, cy), radius)
        pygame.draw.circle(surface, config.GOLD, (cx, cy), radius, 2)

        # Focus meter
        meter_w = 400
        meter_x = (config.SCREEN_WIDTH - meter_w) // 2
        meter_y = config.SCREEN_HEIGHT - 150
        pygame.draw.rect(surface, (60, 60, 60), (meter_x, meter_y, meter_w, 24))
        fill = int(meter_w * min(1.0, focus_meter))
        pygame.draw.rect(surface, config.PURPLE, (meter_x, meter_y, fill, 24))
        pygame.draw.rect(surface, config.GOLD, (meter_x, meter_y, meter_w, 24), 2)
        focus_label = font_small.render("Focus", True, config.WHITE)
        surface.blit(focus_label, (meter_x, meter_y - 26))

        # Instructions
        inst = font_small.render(
            "Watch the breath. Press SPACE when your mind wanders to note it. "
            "ESC to stop.", True, config.LIGHT_GRAY)
        surface.blit(inst, ((config.SCREEN_WIDTH - inst.get_width()) // 2,
                            config.SCREEN_HEIGHT - 95))

        timer = font_small.render(f"{int(time_left)}s", True, config.LIGHT_GRAY)
        surface.blit(timer, (config.SCREEN_WIDTH - 80, 40))
