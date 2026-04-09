import pygame
import sys
from modules.screenSet import *
from modules.music import play_menu_music
import json

pygame.init()

guide_menu_font = pygame.font.Font("src/DancingScript-VariableFont_wght.ttf", 40)
guide_content_font = pygame.font.Font("src/DancingScript-VariableFont_wght.ttf", 28)


# -------------------------------
# SORTING
# -------------------------------
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
        return ["No records yet"]

    return [
        f"{i}. {r['player_name']} - {r['time_seconds']}s"
        for i, r in enumerate(top_10, start=1)
    ]


def get_top_10_damage():
    data = load_data()
    sorted_data = bubble_sort_damage(data)
    top_10 = sorted_data[:10]

    if not top_10:
        return ["No records yet"]

    return [
        f"{i}. {r['player_name']} - DMG: {r['damage_taken']}"
        for i, r in enumerate(top_10, start=1)
    ]


# -------------------------------
# GUIDE DATA
# -------------------------------
guides_data = [
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
            button_rect = pygame.Rect(menu_x, y_pos, 300, 50)

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
        # HALL OF FAME (SPECIAL VIEW)
        # -------------------------------
        if current_guide["title"] == "Best Players":

            left_list = get_top_10_time()
            right_list = get_top_10_damage()

            # Titles
            left_title = guide_content_font.render("FASTEST TIMES", True, WHITE)
            right_title = guide_content_font.render("LOWEST DAMAGE", True, WHITE)

            screen.blit(left_title, (380, 50))
            screen.blit(right_title, (750, 50))

            # Divider
            pygame.draw.line(screen, WHITE, (700, 50), (700, 650), 2)

            # LEFT COLUMN
            y_offset = 130
            for i, line in enumerate(left_list):
                color = WHITE if i == 0 else GRAY  # highlight #1
                text = guide_content_font.render(line, True, color)
                screen.blit(text, (380, y_offset))
                y_offset += 45

            # RIGHT COLUMN
            y_offset = 130
            for i, line in enumerate(right_list):
                color = WHITE if i == 0 else GRAY
                text = guide_content_font.render(line, True, color)
                screen.blit(text, (750, y_offset))
                y_offset += 45

        # -------------------------------
        # NORMAL GUIDES
        # -------------------------------
        else:
            content_x = 350
            content_y = 50

            title = guide_content_font.render(current_guide["title"], True, WHITE)
            screen.blit(title, (content_x, content_y))

            content_y += 80
            for line in current_guide["content"]:
                text = guide_content_font.render(line, True, GRAY)
                screen.blit(text, (content_x, content_y))
                content_y += 50

        # INPUT
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