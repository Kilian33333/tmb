import pygame

from modules.screenSet import screen, screen_type

tick = 0
loading_complete = False
fade_started = False

splash_image = pygame.image.load("src/splash.png").convert_alpha()

scaled_width = int(
    splash_image.get_width()
    * (screen.get_height() / splash_image.get_height())
)

if screen_type == 2:
    splash_image_scaled = pygame.transform.scale(
        splash_image,
        (int(scaled_width / 1.4), int(screen.get_height() / 1.4))
    )
else:
    splash_image_scaled = pygame.transform.scale(
        splash_image,
        (scaled_width, screen.get_height())
    )

background_draw_x = (
    screen.get_width() - splash_image_scaled.get_width()
) // 2

background_draw_y = (
    screen.get_height() - splash_image_scaled.get_height()
) // 2

fade_duration = 45

loading_font = pygame.font.Font("src/Jacquard24-Regular.ttf", 30)
prompt_font = pygame.font.Font("src/Jacquard24-Regular.ttf", 25)

bar_width = 300
bar_height = 20
bar_x = (screen.get_width() - bar_width) // 2
bar_y = screen.get_height() // 2 + 200

credits = [
    ["Main-Development:", "Kilian D."],
    ["Programming:", "Kilian D.", "Co.Programming:", "Jannis S."],
    ["Music by:", "Kilian D.", "Mixing:", "Alen K."],
    ["Main-Artwork:", "Kilian D.", "Background and Character Art:", "Jannis S.", "Kilian D.", "Moritz G."],
    ["Special Thanks:", "Alen K.", "Moritz G."]
]

credit_display_duration = 330
credit_fade_duration = 30
credit_cycle_tick = 0


def collect_files():
    return [
        "load Pictures",
        "Adjusting Gravity",
        "Forge armor",
        "Recruiting Knights",
        "Draw Menu and Starting..."
    ]


loading_files = collect_files()
frames_per_file = 35


def get_loading_info(current_tick):
    if not loading_files:
        return "Loading...", 0.0

    file_index = min(
        current_tick // frames_per_file,
        len(loading_files) - 1
    )

    progress = min(
        (current_tick / frames_per_file) / len(loading_files),
        1.0
    )

    return loading_files[file_index], progress


def get_current_credit_alpha(cycle_tick, total_duration, fade_duration):
    if cycle_tick < fade_duration:
        return int(255 * (cycle_tick / fade_duration))

    if cycle_tick < total_duration - fade_duration:
        return 255

    fade_out_progress = (
        cycle_tick - (total_duration - fade_duration)
    ) / fade_duration

    return int(255 * (1 - fade_out_progress))


def draw_credits():
    global credit_cycle_tick

    total_cycle_duration = (
        credit_display_duration + credit_fade_duration
    )

    credit_index = (
        credit_cycle_tick // total_cycle_duration
    ) % len(credits)

    cycle_position = credit_cycle_tick % total_cycle_duration
    current_credit = credits[credit_index]

    alpha = get_current_credit_alpha(
        cycle_position,
        credit_display_duration,
        credit_fade_duration
    )

    credit_x = screen.get_width() - 370
    credit_y = screen.get_height() // 2 - 50

    title_surface = prompt_font.render(
        current_credit[0],
        True,
        (255, 255, 255)
    )

    title_surface.set_alpha(alpha)
    screen.blit(title_surface, (credit_x, credit_y))

    for i, name in enumerate(current_credit[1:], 1):
        name_surface = prompt_font.render(
            name,
            True,
            (200, 200, 200)
        )

        name_surface.set_alpha(alpha)

        screen.blit(
            name_surface,
            (credit_x, credit_y + 30 * i)
        )

    credit_cycle_tick += 1


def splash():
    global tick
    global loading_complete
    global fade_started

    loading_duration = len(loading_files) * frames_per_file

    if loading_complete and not fade_started:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                fade_started = True
                tick = 0

    if fade_started:
        if tick < fade_duration:
            screen.blit(
                splash_image_scaled,
                (background_draw_x, background_draw_y)
            )

            fade_progress = tick / fade_duration
            alpha = int(255 * (1 - fade_progress))

            fade_surface = pygame.Surface(
                (screen.get_width(), screen.get_height())
            )

            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(255 - alpha)

            screen.blit(fade_surface, (0, 0))

            pygame.display.flip()

            tick += 1
            return True

        return False

    screen.fill((0, 0, 0))

    screen.blit(
        splash_image_scaled,
        (background_draw_x, background_draw_y)
    )

    draw_credits()

    loading_text, progress = get_loading_info(tick)

    pygame.draw.rect(
        screen,
        (50, 50, 50),
        (bar_x, bar_y, bar_width, bar_height)
    )

    fill_width = int(bar_width * progress)

    pygame.draw.rect(
        screen,
        (200, 200, 200),
        (bar_x, bar_y, fill_width, bar_height)
    )

    pygame.draw.rect(
        screen,
        (255, 255, 255),
        (bar_x, bar_y, bar_width, bar_height),
        2
    )

    text_surface = loading_font.render(
        loading_text,
        True,
        (255, 255, 255)
    )

    text_rect = text_surface.get_rect(
        center=(
            screen.get_width() // 2,
            bar_y + bar_height + 25
        )
    )

    screen.blit(text_surface, text_rect)

    if tick >= loading_duration:
        loading_complete = True

        prompt_text = prompt_font.render(
            "Press any key to continue",
            True,
            (255, 255, 255)
        )

        prompt_rect = prompt_text.get_rect(
            center=(
                screen.get_width() // 2,
                screen.get_height() - 60
            )
        )

        screen.blit(prompt_text, prompt_rect)

    pygame.display.flip()

    tick += 1

    return True