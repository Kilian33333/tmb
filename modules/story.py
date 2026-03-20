import pygame
import sys
from pathlib import Path


class CutsceneManager:
    """Manages all cutscene display without parameter passing"""
    
    # Pygame globals initialized once
    screen = None
    clock = None
    font = None
    
    # Cutscene definitions: each cutscene has parts with image and text
    # Each part can have:
    #   - "image": path to image (optional)
    #   - "text": dialogue/text to display (optional)
    CUTSCENES = {
        1: [  # Opening cutscene
            {
                "image": None,
                "text": "Knight of the North"
            },
            {
                "image": None,
                "text": "Press ENTER to begin your journey..."
            }
        ],
        2: [  # Game Over
            {
                "image": None,
                "text": "You have fallen...\n\nGame Over"
            }
        ],
        3: [  # Pre-fight 6 cutscene
            {
                "image": None,
                "text": "A new challenger approaches..."
            },
            {
                "image": None,
                "text": "Prepare for battle!"
            }
        ],
        4: [  # Pre-fight 11 cutscene
            {
                "image": None,
                "text": "The battle intensifies..."
            },
            {
                "image": None,
                "text": "Your skills are being tested!"
            }
        ],
        5: [  # Pre-fight 16 cutscene (final)
            {
                "image": None,
                "text": "The final enemy stands before you..."
            },
            {
                "image": None,
                "text": "This is your ultimate test!"
            }
        ],
        6: [  # Victory cutscene
            {
                "image": None,
                "text": "You have triumphed!"
            },
            {
                "image": None,
                "text": "The kingdom is safe.\n\nYou are a true Knight.\n\nThe End"
            }
        ]
    }

    @classmethod
    def init(cls, screen, clock, font):
        """Initialize the cutscene manager with pygame objects. Call once in main()"""
        cls.screen = screen
        cls.clock = clock
        cls.font = font

    @classmethod
    def show(cls, cutscene_id):
        """Show a cutscene by ID. Simple one-liner to replace show_cutscene() calls"""
        if cutscene_id not in cls.CUTSCENES:
            print(f"Warning: Cutscene {cutscene_id} not found")
            return

        for part in cls.CUTSCENES[cutscene_id]:
            cls._show_part(part)

    @classmethod
    def _show_part(cls, part):
        """Display a single cutscene part, skippable with ENTER"""
        image = None
        if "image" in part and part["image"]:
            try:
                image = pygame.image.load(part["image"]).convert()
                image = pygame.transform.scale(image, (cls.screen.get_width(), cls.screen.get_height()))
            except Exception as e:
                print(f"Warning: Could not load cutscene image: {e}")

        text = part.get("text", "")
        cls._show_with_input_wait(image, text)

    @classmethod
    def _show_with_input_wait(cls, image, text):
        """Show part until ENTER is pressed"""
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    waiting = False

            cls._draw_part(image, text)
            cls.clock.tick(60)



    @classmethod
    def _draw_part(cls, image, text):
        """Render image and/or text to screen"""
        if image:
            cls.screen.blit(image, (0, 0))
        else:
            cls.screen.fill((10, 10, 20))

        if text:
            lines = text.split("\n")
            y_offset = (cls.screen.get_height() - len(lines) * 40) // 2

            for i, line in enumerate(lines):
                surf = cls.font.render(line, True, (255, 255, 255))
                rect = surf.get_rect(center=(cls.screen.get_width() // 2, y_offset + i * 40))
                cls.screen.blit(surf, rect)

        pygame.display.update()


