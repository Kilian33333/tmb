import pygame
import sys
from modules.screenSet import *
from modules.screenSet import update_display
from modules.music import play_menu_music
import json
import math
import re
from modules.months import MONTHS
from modules.guides_data import guides_data, MEDAL_COLORS, MEDAL_NAMES
from modules.sounds import *
from modules.settings_ui import settings_menu


pygame.init()

WIDTH = screen.get_width()
HEIGHT = screen.get_height()

guide_menu_font = pygame.font.Font("src/OleoScript-Regular.ttf", 40)
guide_content_font = pygame.font.Font("src/OleoScript-Regular.ttf", 22)
guide_small_font = pygame.font.Font("src/OleoScript-Regular.ttf", 14)


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


def tim_sort_time(records):
    return sorted(records, key=lambda r: (r["time_seconds"], r["damage_taken"]))


def tim_sort_damage(records):
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
    sorted_data = tim_sort_time(data)
    top_10 = sorted_data[:10]

    if not top_10:
        return [{"medal": "", "rank": "", "text": "No records yet", "color": GRAY}]

    result = []
    for i, r in enumerate(top_10, start=1):
        medal = MEDAL_NAMES.get(i, "")
        color = MEDAL_COLORS.get(i, GRAY)
        time_score = int(200 - ( 100 * math.pow(r['time_seconds'] / 370, 3))) if int(r['time_seconds']) < 370 else int(100 - math.pow((r['time_seconds'] - 370) / 370, 3))
        formatted_time = format_timestamp(r.get('timestamp', ''))
        text = f"{r['player_name']} - {r['time_seconds']}s  - Score: {time_score}"
        result.append({"medal": medal, "rank": str(i), "text": text, "timestamp": formatted_time, "color": color})
    return result


def get_top_10_damage():
    data = load_data()
    sorted_data = tim_sort_damage(data)
    top_10 = sorted_data[:10]

    if not top_10:
        return [{"medal": "", "rank": "", "text": "No records yet", "color": GRAY}]

    result = []
    for i, r in enumerate(top_10, start=1):
        medal = MEDAL_NAMES.get(i, "")
        color = MEDAL_COLORS.get(i, GRAY)
        dmg_score = int(200 - ( 100 * math.pow(r['damage_taken'] / 640, 3))) if int(r['damage_taken']) < 640 else int(100 - (100 * math.pow((r['damage_taken'] - 640) / 640, 3)))
        formatted_time = format_timestamp(r.get('timestamp', ''))
        text = f"{r['player_name']} - DMG: {r['damage_taken']} - Score: {dmg_score}"
        result.append({"medal": medal, "rank": str(i), "text": text, "timestamp": formatted_time, "color": color})
    return result


def get_top_10_total_score():
    data = load_data()
    
    if not data:
        return [{"medal": "", "rank": "", "text": "No records yet", "color": GRAY}]
    
    # Calculate total scores for each record
    records_with_scores = []
    for r in data:
        time_score = int(200 - ( 100 * math.pow(r['time_seconds'] / 370, 3))) if int(r['time_seconds']) < 370 else int(100 - math.pow((r['time_seconds'] - 370) / 370, 3))
        dmg_score = int(200 - ( 100 * math.pow(r['damage_taken'] / 640, 3))) if int(r['damage_taken']) < 640 else int(100 - (100 * math.pow((r['damage_taken'] - 640) / 640, 3)))
        total_score = time_score + dmg_score
        records_with_scores.append({
            **r,
            "time_score": time_score,
            "dmg_score": dmg_score,
            "total_score": total_score
        })
    
    # Sort by total score descending (highest first)
    sorted_data = sorted(records_with_scores, key=lambda r: r["total_score"], reverse=True)
    top_10 = sorted_data[:10]
    
    result = []
    for i, r in enumerate(top_10, start=1):
        medal = MEDAL_NAMES.get(i, "")
        color = MEDAL_COLORS.get(i, GRAY)
        formatted_time = format_timestamp(r.get('timestamp', ''))
        text = f"{r['player_name']} - Total Score: {r['total_score']}"
        result.append({"medal": medal, "rank": str(i), "text": text, "timestamp": formatted_time, "color": color})
    
    return result

# -------------------------------
# Images
# -------------------------------

# name: identifier for code
# text_placement: text_side = "left", "center", "right", "under", "over", x_fillout
# src: source image path
# size: (width, height) or None to keep original
# background: (r, g, b) color tuple or None for no background
# positionsyntax (a placeholder text between <> with an name that identifes the image)

imge_sets = [
    {
        "name": "player_example_texture_1",
        "text_placement": "left",
        "src": "src/player_ultimate_13.png",
        "size": (300, 300),
        "background": (50, 50, 50),
        "positionSyntax": "<player_example_texture_1>"
    },
    {
        "name": "behind_the_scenes_kilian_1",
        "text_placement": "right",
        "src": "src/behind_the_scenes_kilian_1.jpg",
        "size": (286, 200),
        "background": None,
        "positionSyntax": "<behind_the_scenes_kilian_1>"
    },
    {
        "name": "behind_the_scenes_kilian_2",
        "text_placement": "left",
        "src": "src/behind_the_scenes_kilian_2.jpg",
        "size": (400, 300),
        "background": None,
        "positionSyntax": "<behind_the_scenes_kilian_2>"
    }
]


# -------------------------------
# GUIDE SCREEN
# -------------------------------

def get_image_set(name):
    """Find and return image set by name, or None if not found"""
    for img in imge_sets:
        if img["name"] == name:
            return img
    return None

def load_image(src, size):
    """Load and scale image, handle errors gracefully"""
    try:
        img = pygame.image.load(src).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except:
        return None

def extract_image_from_line(line):
    """Check if line contains image syntax and extract it, return (image_name, line_without_syntax)"""
    import re
    match = re.search(r'<(\w+)>', line)
    if match:
        image_name = match.group(1)
        line_without_syntax = re.sub(r'<\w+>', '', line).strip()
        return image_name, line_without_syntax
    return None, line

def guides():
    clock = pygame.time.Clock()
    selected_index = 0
    current_page = 0  # Track current page for multi-page content
    running = True

    menu_item_height = 60
    menu_x = 20
    menu_start_y = 40

    # Constants for content pagination
    CONTENT_START_Y = 130
    LINE_HEIGHT = 35  # Reduced from 50 to fit more lines per page
    PAGES_MARGIN_TOP = 150  # Margin above pages section
    PAGES_MARGIN_BOTTOM = 20  # Margin below pages section
    PAGES_SECTION_HEIGHT = 60  # Height of pages section (arrows + text)
    
    # Calculate CONTENT_END_Y dynamically based on screen height
    CONTENT_END_Y = screen.get_height() - PAGES_MARGIN_BOTTOM - PAGES_SECTION_HEIGHT - PAGES_MARGIN_TOP
    MAX_LINES_PER_PAGE = (CONTENT_END_Y - CONTENT_START_Y) // LINE_HEIGHT

    def get_page_content(content_lines):
        """Split content into pages and return total pages needed"""
        if not content_lines:
            return [[]], 1
        
        total_pages = (len(content_lines) + MAX_LINES_PER_PAGE - 1) // MAX_LINES_PER_PAGE
        pages = []
        
        for page_num in range(total_pages):
            start_idx = page_num * MAX_LINES_PER_PAGE
            end_idx = min(start_idx + MAX_LINES_PER_PAGE, len(content_lines))
            pages.append(content_lines[start_idx:end_idx])
        
        return pages, total_pages

    while running:
        clock.tick(60)
        guides_background = pygame.image.load("src/guides_background.png").convert_alpha()
        guides_background = pygame.transform.scale(guides_background, (WIDTH, HEIGHT))
        screen.blit(guides_background, (0, 0))

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

        # Reset page when changing guides
        if selected_index != getattr(guides, 'prev_index', selected_index):
            current_page = 0
        guides.prev_index = selected_index

        # CONTENT AREA
        current_guide = guides_data[selected_index]

        # Behind the Scenes
        if current_guide["title"] == "Behind the Scenes":
            small_thx_text = guide_small_font.render("Special thx to my girlfriend, Emily, for helping me have fun, no matter what happened and keeping me motivated. ~Kilian ", True, WHITE)
            screen.blit(small_thx_text, (400, screen.get_height() - 75))
        
        # HALL OF FAME (SPECIAL VIEW)
        if current_guide["title"] == "Best Players":
            # Best Players has 2 pages
            best_players_total_pages = 2
            best_players_current_page = min(current_page, best_players_total_pages - 1)
            
            if best_players_current_page == 0:
                # Page 1: Fastest Times and Lowest Damage
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
                # Page 2: Highest Total Scores
                total_list = get_top_10_total_score()
                
                title = guide_content_font.render("HIGHEST TOTAL SCORES", True, WHITE)
                screen.blit(title, (500, 150))
                
                y_offset = 210
                for entry in total_list:
                    medal_text = f"{entry['medal']}" if entry['medal'] else ""
                    rank_text = f"#{entry['rank']}" if entry['rank'] else ""
                    main_text = entry['text']
                    timestamp_text = entry.get('timestamp', '')

                    if medal_text:
                        medal_surface = guide_content_font.render(medal_text, True, entry['color'])
                        medal_bg = pygame.Surface((110, 35))
                        medal_bg.fill(entry['color'])
                        medal_bg.set_alpha(40)
                        screen.blit(medal_bg, (480, y_offset+5))
                        medal_num = guide_content_font.render(rank_text, True, entry['color'])
                        screen.blit(medal_num, (435, y_offset))
                        screen.blit(medal_surface, (480, y_offset))

                        text_surface = guide_content_font.render(main_text, True, entry['color'])
                        screen.blit(text_surface, (595, y_offset))

                        if timestamp_text:
                            timestamp_surface = pygame.font.Font("src/Jacquard24-Regular.ttf", 25).render(timestamp_text, True, GRAY)
                            screen.blit(timestamp_surface, (595, y_offset + 25))
                    else:
                        text_surface = guide_content_font.render(main_text, True, GRAY)
                        screen.blit(text_surface, (480, y_offset))

                    y_offset += 50
            
            # Draw page indicator and navigation buttons for Best Players
            pages_y_position = screen.get_height() - 60
            page_text = guide_small_font.render(f"Page {best_players_current_page + 1} / {best_players_total_pages}", True, WHITE)
            page_text_rect = page_text.get_rect(center=(screen.get_width() // 2, pages_y_position))
            screen.blit(page_text, page_text_rect)
            
            # Left arrow button
            left_arrow_rect = pygame.Rect(380, pages_y_position - 20, 40, 40)
            if best_players_current_page > 0:
                pygame.draw.rect(screen, WHITE, left_arrow_rect, 2)
                arrow_left = guide_small_font.render("<", True, WHITE)
            else:
                pygame.draw.rect(screen, GRAY, left_arrow_rect, 1)
                arrow_left = guide_small_font.render("<", True, GRAY)
            arrow_left_rect = arrow_left.get_rect(center=left_arrow_rect.center)
            screen.blit(arrow_left, arrow_left_rect)
            
            # Right arrow button
            right_arrow_rect = pygame.Rect(screen.get_width() - 100, pages_y_position - 20, 40, 40)
            if best_players_current_page < best_players_total_pages - 1:
                pygame.draw.rect(screen, WHITE, right_arrow_rect, 2)
                arrow_right = guide_small_font.render(">", True, WHITE)
            else:
                pygame.draw.rect(screen, GRAY, right_arrow_rect, 1)
                arrow_right = guide_small_font.render(">", True, GRAY)
            arrow_right_rect = arrow_right.get_rect(center=right_arrow_rect.center)
            screen.blit(arrow_right, arrow_right_rect)

        else:
            content_x = 400
            content_y = CONTENT_START_Y

            title = guide_content_font.render(current_guide["title"], True, WHITE)
            screen.blit(title, (content_x, 50))

            # Get paginated content
            pages, total_pages = get_page_content(current_guide["content"])
            
            # Clamp current_page to valid range
            current_page = max(0, min(current_page, total_pages - 1))
            
            # Render current page content
            if pages and pages[current_page]:
                line_index = 0
                page_lines = pages[current_page]
                
                while line_index < len(page_lines):
                    line = page_lines[line_index]
                    image_name, text_without_syntax = extract_image_from_line(line)
                    
                    if image_name:
                        # This line contains an image
                        image_set = get_image_set(image_name)
                        if image_set:
                            img = load_image(image_set["src"], tuple(image_set["size"]) if image_set["size"] else None)
                            if img:
                                img_width, img_height = img.get_size()
                                placement = image_set["text_placement"]
                                background = image_set.get("background")
                                
                                # Draw background if specified
                                if background:
                                    bg_rect = pygame.Rect(content_x, content_y, img_width, img_height)
                                    pygame.draw.rect(screen, background, bg_rect)
                                
                                # Position based on text_placement
                                if placement == "left":
                                    # Image on left, text block on right
                                    screen.blit(img, (content_x, content_y))
                                    
                                    # Collect all following text lines for text block
                                    text_lines_to_render = []
                                    if text_without_syntax:
                                        text_lines_to_render.append(text_without_syntax)
                                    
                                    # Look ahead for more text lines (up to next image)
                                    next_line_idx = line_index + 1
                                    while next_line_idx < len(page_lines):
                                        next_line = page_lines[next_line_idx]
                                        if extract_image_from_line(next_line)[0]:  # Next image found
                                            break
                                        text_lines_to_render.append(next_line)
                                        next_line_idx += 1
                                    
                                    # Render text block on the right
                                    text_x = content_x + img_width + 20  # 20px padding after image
                                    text_y = content_y
                                    for text_line in text_lines_to_render:
                                        text_surface = guide_content_font.render(text_line, True, GRAY)
                                        screen.blit(text_surface, (text_x, text_y))
                                        text_y += guide_content_font.get_height() + 5
                                    
                                    content_y += max(img_height, (text_y - content_y)) + 15  # 15px bottom spacing
                                    line_index = next_line_idx
                                    continue
                                    
                                elif placement == "right":
                                    # Text block on left, image on right
                                    text_lines_to_render = []
                                    if text_without_syntax:
                                        text_lines_to_render.append(text_without_syntax)
                                    
                                    # Look ahead for more text lines (up to next image)
                                    next_line_idx = line_index + 1
                                    while next_line_idx < len(page_lines):
                                        next_line = page_lines[next_line_idx]
                                        if extract_image_from_line(next_line)[0]:  # Next image found
                                            break
                                        text_lines_to_render.append(next_line)
                                        next_line_idx += 1
                                    
                                    # Render text block on the left
                                    text_x = content_x
                                    text_y = content_y
                                    max_text_width = 0
                                    for text_line in text_lines_to_render:
                                        text_surface = guide_content_font.render(text_line, True, GRAY)
                                        screen.blit(text_surface, (text_x, text_y))
                                        max_text_width = max(max_text_width, text_surface.get_width())
                                        text_y += guide_content_font.get_height() + 5
                                    
                                    # Image on the right - position it after text block with padding
                                    img_x = text_x + max_text_width + 20  # 20px padding between text and image
                                    screen.blit(img, (img_x, content_y))
                                    
                                    # Ensure content_y advances by the larger of image height or text height
                                    content_y += max(img_height, (text_y - content_y)) + 15  # 15px bottom spacing
                                    line_index = next_line_idx
                                    continue
                                    
                                elif placement == "center":
                                    # Image centered, text below
                                    img_x = content_x + (400 - img_width) // 2
                                    screen.blit(img, (img_x, content_y))
                                    content_y += img_height + 15  # 15px spacing after image
                                    
                                    if text_without_syntax:
                                        text_surface = guide_content_font.render(text_without_syntax, True, GRAY)
                                        text_x = content_x + (400 - text_surface.get_width()) // 2
                                        screen.blit(text_surface, (text_x, content_y))
                                        content_y += text_surface.get_height() + 15  # 15px spacing after text
                                        
                                elif placement == "under":
                                    # Text above, image below
                                    if text_without_syntax:
                                        text_surface = guide_content_font.render(text_without_syntax, True, GRAY)
                                        screen.blit(text_surface, (content_x, content_y))
                                        content_y += text_surface.get_height() + 10  # 10px spacing
                                    screen.blit(img, (content_x, content_y))
                                    content_y += img_height + 15  # 15px bottom spacing
                                    
                                elif placement == "over":
                                    # Image above, text below
                                    screen.blit(img, (content_x, content_y))
                                    content_y += img_height + 10  # 10px spacing
                                    if text_without_syntax:
                                        text_surface = guide_content_font.render(text_without_syntax, True, GRAY)
                                        screen.blit(text_surface, (content_x, content_y))
                                        content_y += text_surface.get_height() + 15  # 15px bottom spacing
                            
                            line_index += 1
                    else:
                        # Regular text line without image
                        text = guide_content_font.render(line, True, GRAY)
                        screen.blit(text, (content_x, content_y))
                        content_y += LINE_HEIGHT
                        line_index += 1

            # Draw page indicator and navigation buttons if multiple pages
            if total_pages > 1:
                # Calculate pages section position
                pages_y_position = screen.get_height() - PAGES_MARGIN_BOTTOM - 60
                
                # Page indicator text at bottom
                page_text = guide_small_font.render(f"Page {current_page + 1} / {total_pages}", True, WHITE)
                page_text_rect = page_text.get_rect(center=(screen.get_width() // 2, pages_y_position + 0))
                screen.blit(page_text, page_text_rect)
                
                # Left arrow button at bottom left
                left_arrow_rect = pygame.Rect(content_x - 50, pages_y_position, 40, 40)
                if current_page > 0:
                    pygame.draw.rect(screen, WHITE, left_arrow_rect, 2)
                    arrow_left = guide_small_font.render("<", True, WHITE)
                else:
                    pygame.draw.rect(screen, GRAY, left_arrow_rect, 1)
                    arrow_left = guide_small_font.render("<", True, GRAY)
                arrow_left_rect = arrow_left.get_rect(center=left_arrow_rect.center)
                screen.blit(arrow_left, arrow_left_rect)
                
                # Right arrow button at bottom right
                right_arrow_rect = pygame.Rect(screen.get_width() - 100, pages_y_position, 40, 40)
                if current_page < total_pages - 1:
                    pygame.draw.rect(screen, WHITE, right_arrow_rect, 2)
                    arrow_right = guide_small_font.render(">", True, WHITE)
                else:
                    pygame.draw.rect(screen, GRAY, right_arrow_rect, 1)
                    arrow_right = guide_small_font.render(">", True, GRAY)
                arrow_right_rect = arrow_right.get_rect(center=right_arrow_rect.center)
                screen.blit(arrow_right, arrow_right_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    current_page = 0  # Reset page
                    selected_index = (selected_index - 1) % len(guides_data)
                    play_sound("hover", pan=-40, volume=0.5)
                elif event.key == pygame.K_DOWN:
                    current_page = 0  # Reset page
                    selected_index = (selected_index + 1) % len(guides_data)
                    play_sound("hover", pan=-40, volume=0.5)
                elif event.key == pygame.K_LEFT:
                    if current_guide["title"] == "Best Players":
                        # Best Players has pagination support
                        if current_page > 0:
                            current_page -= 1
                        play_sound("turn_page", pan=-40, volume=0.8)
                    elif current_guide["title"] != "Behind the Scenes":
                        # Other guides have pagination support
                        pages, total_pages = get_page_content(current_guide["content"])
                        if current_page > 0:
                            current_page -= 1
                        play_sound("turn_page", pan=-40, volume=0.8)
                elif event.key == pygame.K_RIGHT:
                    if current_guide["title"] == "Best Players":
                        # Best Players has 2 pages
                        if current_page < 1:
                            current_page += 1
                        play_sound("turn_page", pan=40, volume=0.8)
                    elif current_guide["title"] != "Behind the Scenes":
                        # Other guides have pagination support
                        pages, total_pages = get_page_content(current_guide["content"])
                        if current_page < total_pages - 1:
                            current_page += 1
                        play_sound("turn_page", pan=40, volume=0.8)
                elif event.key == pygame.K_RETURN:
                    if current_guide["title"] == "Settings":
                        settings_menu()
                        play_sound("click", pan=0, volume=1.0)
                    elif selected_index == len(guides_data) - 1:
                        return

        update_display()