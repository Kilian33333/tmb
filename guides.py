import pygame
import sys
from modules.screenSet import *
from modules.music import play_menu_music
import json
import re
from modules.months import MONTHS

pygame.init()

guide_menu_font = pygame.font.Font("src/OleoScript-Regular.ttf", 40)
guide_content_font = pygame.font.Font("src/OleoScript-Regular.ttf", 28)
guide_small_font = pygame.font.Font("src/OleoScript-Regular.ttf", 14)

# Medal colors
MEDAL_COLORS = {
    1: (255, 215, 0),      # Gold
    2: (192, 192, 192),    # Silver
    3: (205, 127, 50),     # Bronze
    4: (190, 138, 80),     # Copper
    5: (128, 128, 128),    # Iron
    6: (128, 128, 128),    # Iron
    7: (128, 128, 128),    # Iron
    8: (128, 128, 128),    # Iron
    9: (128, 128, 128),    # Iron
    10: (128, 128, 128),   # Iron
}

MEDAL_NAMES = {
    1: "GOLD",
    2: "SILVER",
    3: "BRONZE",
    4: "COPPER",
    5: "IRON",
    6: "IRON",
    7: "IRON",
    8: "IRON",
    9: "IRON",
    10: "IRON"
}

# -------------------------------
# SORTING
# -------------------------------
def format_timestamp(timestamp_str):
    """Format timestamp to '4th Apr. 2026 at 00:49:31'"""
    try:
        from datetime import datetime

        dt = datetime.fromisoformat(timestamp_str)

        def ordinal(n):
            if 11 <= n % 100 <= 13:
                suffix = "th"
            else:
                suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
            return str(n) + suffix

        day = ordinal(dt.day)
        month = MONTHS[dt.month]
        year = dt.year

        time_str = dt.strftime("%H:%M:%S")  # no microseconds

        return f"{day} {month} {year} at {time_str}"

    except:
        return timestamp_str


def bubble_sort_time(records):
    return sorted(records, key=lambda r: (r["time_seconds"], r["damage_taken"]))


def bubble_sort_damage(records):
    return sorted(records, key=lambda r: (r["damage_taken"], r["time_seconds"]))


# -------------------------------
# JSON HELPERS
# -------------------------------
def load_data():
    try:
        with open("game_results.json", "r") as file:
            return json.load(file)
    except:
        return []


def get_top_10_time():
    data = load_data()
    sorted_data = bubble_sort_time(data)
    top_10 = sorted_data[:10]

    if not top_10:
        return [{"medal": "", "rank": "", "text": "No records yet", "color": GRAY}]

    result = []
    for i, r in enumerate(top_10, start=1):
        medal = MEDAL_NAMES.get(i, "")
        color = MEDAL_COLORS.get(i, GRAY)
        formatted_time = format_timestamp(r.get('timestamp', ''))
        text = f"{r['player_name']} - {r['time_seconds']}s"
        result.append({"medal": medal, "rank": str(i), "text": text, "timestamp": formatted_time, "color": color})
    return result


def get_top_10_damage():
    data = load_data()
    sorted_data = bubble_sort_damage(data)
    top_10 = sorted_data[:10]

    if not top_10:
        return [{"medal": "", "rank": "", "text": "No records yet", "color": GRAY}]

    result = []
    for i, r in enumerate(top_10, start=1):
        medal = MEDAL_NAMES.get(i, "")
        color = MEDAL_COLORS.get(i, GRAY)
        formatted_time = format_timestamp(r.get('timestamp', ''))
        text = f"{r['player_name']} - DMG: {r['damage_taken']}"
        result.append({"medal": medal, "rank": str(i), "text": text, "timestamp": formatted_time, "color": color})
    return result


# -------------------------------
# GUIDE DATA
# -------------------------------
guides_data = [
    {
        "title": "First Words",
        "content": [
            "Hi, my name is Kilian. Before you start playing or reading the guides,",
            "i wanna let you know, this was one of my biggest projects in a short period of time,",
            "especially in relation to the complexity.",
            "I mainly programmed this game, made artwork and design,",
            "made music, practiced and played hours of guitar,",
            "Buuuut i was not the only developer working on this game. Jannis was a help,",
            "especially in the cases of drawing enemies, sound effects and small codes and also background.",
            "If you wanna know more about us and my group (Bite the Byte Games),",
            "you can find more in 'Behind the scenes'.",
            "I know i was maybe talkin' a bit toooo much (it's 4am and i'm running on 160mg caffeine right now XD),",
            "but i just wanna say, that i hope you have fun playing this game :D"
        ]
    },
    {
        "title": "Controls",
        "content": [
            "Q - Front Kick",
            "E - High Kick",
            "R - Upward Swing",
            "C - Side Head Strike",
            "X - Direct Punch",
            "F - Ultimate Attack",
            "SPACE - Jump",
        ]
    },
    {
        "title": "Game Mechanics",
        "content": [
            "Defeat enemies in combat",
            "Build Ultimate meter",
            "Use combos effectively",
            "Dodge enemy attacks",
            "Level up difficulty"
        ]
    },
    {
        "title": "Best Players",
        "content": []
    },
    {
        "title": "Music and Artwork",
        "content": []
    },
    {
        "title": "Development",
        "content": []
    },
    {
        "title":"Behind the Scenes",
        "content": []
    },
    {
        "title": "Credits",
        "content": []
    },
    {
        "title": "Rights",
        "content": []
    },
    {
        "title": "Back to Menu",
        "content": ["Press ENTER to return", "to the main menu"]
    }
]


# -------------------------------
# GUIDE SCREEN
# -------------------------------
def guides():
    clock = pygame.time.Clock()
    selected_index = 0
    running = True

    menu_item_height = 60
    menu_x = 20
    menu_start_y = 40

    while running:
        clock.tick(60)
        screen.fill(BLACK)

        # MENU
        for i, guide in enumerate(guides_data):
            y_pos = menu_start_y + (i * menu_item_height)
            button_rect = pygame.Rect(menu_x, y_pos, 310, 50)

            if i == selected_index:
                pygame.draw.rect(screen, WHITE, button_rect, 3)
                color = WHITE
            else:
                pygame.draw.rect(screen, GRAY, button_rect, 1)
                color = GRAY

            label = guide_menu_font.render(guide["title"], True, color)
            label_rect = label.get_rect(center=button_rect.center)
            screen.blit(label, label_rect)

        # CONTENT AREA
        current_guide = guides_data[selected_index]


        # -------------------------------
        # Behind the Scenes
        # -------------------------------
        if current_guide["title"] == "Behind the Scenes":
            small_thx_text = guide_small_font.render("Special thx to my girlfriend, Emily, for helping me have fun, no matter what happened and keeping me motivated. ~Kilian ", True, WHITE)
            screen.blit(small_thx_text, (400, screen.get_height() - 75))
        
        # -------------------------------
        # HALL OF FAME (SPECIAL VIEW)
        # -------------------------------

        if current_guide["title"] == "Best Players":

            left_list = get_top_10_time()
            right_list = get_top_10_damage()

            left_title = guide_content_font.render("FASTEST TIMES", True, WHITE)
            right_title = guide_content_font.render("LOWEST DAMAGE", True, WHITE)

            screen.blit(left_title, (380, 150))
            screen.blit(right_title, (850, 150))

            pygame.draw.line(screen, WHITE, (800, 50), (800, 650), 2)

            y_offset = 210
            for entry in left_list:
                medal_text = f"{entry['medal']}" if entry['medal'] else ""
                rank_text = f"#{entry['rank']}" if entry['rank'] else ""
                main_text = entry['text']
                timestamp_text = entry.get('timestamp', '')

                if medal_text:
                    medal_surface = guide_content_font.render(medal_text, True, entry['color'])
                    medal_bg = pygame.Surface((110, 35))
                    medal_bg.fill(entry['color'])
                    medal_bg.set_alpha(40)
                    screen.blit(medal_bg, (385, y_offset+5))
                    medal_num = guide_content_font.render(rank_text, True, entry['color'])
                    screen.blit(medal_num, (340, y_offset))
                    screen.blit(medal_surface, (385, y_offset))

                    text_surface = guide_content_font.render(main_text, True, entry['color'])
                    screen.blit(text_surface, (500, y_offset))

                    if timestamp_text:
                        timestamp_surface = pygame.font.Font("src/Jacquard24-Regular.ttf", 25).render(timestamp_text, True, GRAY)
                        screen.blit(timestamp_surface, (500, y_offset + 25))
                else:
                    text_surface = guide_content_font.render(main_text, True, GRAY)
                    screen.blit(text_surface, (480, y_offset))

                y_offset += 50

            y_offset = 210
            for entry in right_list:
                medal_text = f"{entry['medal']}" if entry['medal'] else ""
                rank_text = f"#{entry['rank']}" if entry['rank'] else ""
                main_text = entry['text']
                timestamp_text = entry.get('timestamp', '')

                if medal_text:
                    medal_surface = guide_content_font.render(medal_text, True, entry['color'])
                    medal_num = guide_content_font.render(rank_text, True, entry['color'])
                    medal_bg = pygame.Surface((110, 35))
                    medal_bg.fill(entry['color'])
                    medal_bg.set_alpha(40)
                    screen.blit(medal_bg, (855, y_offset+5))
                    screen.blit(medal_num, (810, y_offset))
                    screen.blit(medal_surface, (855, y_offset))

                    text_surface = guide_content_font.render(main_text, True, entry['color'])
                    screen.blit(text_surface, (970, y_offset))

                    if timestamp_text:
                        timestamp_surface = pygame.font.Font("src/Jacquard24-Regular.ttf", 25).render(timestamp_text, True, GRAY)
                        screen.blit(timestamp_surface, (970, y_offset + 25))
                else:
                    text_surface = guide_content_font.render(main_text, True, GRAY)
                    screen.blit(text_surface, (850, y_offset))

                y_offset += 50

        else:
            content_x = 400
            content_y = 50

            title = guide_content_font.render(current_guide["title"], True, WHITE)
            screen.blit(title, (content_x, content_y))

            content_y += 80
            for line in current_guide["content"]:
                text = guide_content_font.render(line, True, GRAY)
                screen.blit(text, (content_x, content_y))
                content_y += 50

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(guides_data)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(guides_data)
                elif event.key == pygame.K_RETURN:
                    if selected_index == len(guides_data) - 1:
                        return

        pygame.display.flip()