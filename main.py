import pygame
from game.game_engine import GameEngine

WIDTH, HEIGHT = 540, 360
FPS = 60

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Math Flashcards - Pygame Edition")
    clock = pygame.time.Clock()

    engine = GameEngine(WIDTH, HEIGHT)

    running = True
    dt = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            engine.handle_event(event)

        engine.update(dt)
        engine.render(screen)

        pygame.display.flip()
        # ms -> seconds, clamped so dragging the window can't instantly expire a card
        dt = min(clock.tick(FPS) / 1000, 0.1)

    pygame.quit()


if __name__ == "__main__":
    main()