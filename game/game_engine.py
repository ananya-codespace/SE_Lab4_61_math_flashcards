import random
import pygame
from game.text_box import TextBox


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.score = 0
        self.total_attempts = 0
        self.feedback_msg = "Solve the card and press Enter!"
        self.feedback_color = (200, 205, 215)

        self.num_a = 0
        self.num_b = 0
        self.operator = "+"

        box_w, box_h = 130, 44
        self.input_box = TextBox(width // 2 - 110, 230, box_w, box_h)
        self.submit_btn = pygame.Rect(width // 2 + 30, 230, 90, box_h)

        self.font_title = pygame.font.SysFont(None, 38)
        self.font_hud = pygame.font.SysFont(None, 26)
        self.font_card = pygame.font.SysFont(None, 56)
        self.font_btn = pygame.font.SysFont(None, 24)

        self.time_limit = 10.0          # seconds per card
        self.time_left = self.time_limit

        self.streak = 0
        self.correct_count = 0   # correct answers, separate from points

        self.generate_new_card()

    def generate_new_card(self):
        self.num_a = random.randint(3, 15)
        self.num_b = random.randint(2, 12)
        self.operator = random.choice(["+", "-", "*"])
        if self.operator == "-" and self.num_a < self.num_b:
            self.num_a, self.num_b = self.num_b, self.num_a

        self.input_box.clear()
        self.time_left = self.time_limit   # new card = fresh timer

    def compute_expected_answer(self):
        if self.operator == "+":
            return self.num_a + self.num_b
        if self.operator == "-":
            return self.num_a - self.num_b
        if self.operator == "*":
            return self.num_a * self.num_b
        raise ValueError(f"Unknown operator: {self.operator}")

    def get_multiplier(self):
        if self.streak >= 5:
            return 3
        if self.streak >= 3:
            return 2
        return 1
    # streak 1,2 -> 1x | 3,4 -> 2x | 5+ -> 3x

    def register_miss(self):
        """Single place for 'the player failed this card' (wrong answer or timeout)."""
        self.total_attempts += 1
        self.streak = 0

    def submit_answer(self):
        val_str = self.input_box.text.strip()
        if not val_str or val_str == "-":
            self.feedback_msg = "Type an answer first!"
            self.feedback_color = (240, 175, 40)
            return

        user_answer = int(val_str)
        expected = self.compute_expected_answer()

        if user_answer == expected:
            self.total_attempts += 1
            self.correct_count += 1
            self.streak += 1                 # increment FIRST...
            mult = self.get_multiplier()     # ...so the 3rd correct answer already gets 2x
            self.score += mult
            self.feedback_msg = f"CORRECT! {self.num_a} {self.operator} {self.num_b} = {expected}  (+{mult})"
            self.feedback_color = (80, 230, 110)
            self.generate_new_card()
        else:
            self.register_miss()
            self.feedback_msg = f"WRONG! Expected {expected}. Streak lost."
            self.feedback_color = (240, 75, 75)
            self.input_box.clear()

    def handle_event(self, event):
        self.input_box.handle_event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.submit_answer()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.submit_btn.collidepoint(event.pos):
                self.submit_answer()

    def update(self, dt):
        self.time_left -= dt
        if self.time_left <= 0:
            self.handle_timeout()

    def handle_timeout(self):
        expected = self.compute_expected_answer()   # before the card changes
        self.register_miss()
        self.feedback_msg = f"TIME'S UP! Answer was {expected}."
        self.feedback_color = (240, 75, 75)
        self.generate_new_card()
        
    def render(self, screen):
        screen.fill((25, 29, 37))

        title_surf = self.font_title.render("Math Flashcards Arena", True, (245, 245, 245))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 18))

        score_surf = self.font_hud.render(
            f"Score: {self.score}   Correct: {self.correct_count}/{self.total_attempts}",
            True, (255, 220, 80))
        screen.blit(score_surf, (self.width // 2 - score_surf.get_width() // 2, 58))

        card_rect = pygame.Rect(self.width // 2 - 130, 95, 260, 110)
        pygame.draw.rect(screen, (240, 242, 245), card_rect, border_radius=12)
        pygame.draw.rect(screen, (85, 120, 175), card_rect, width=3, border_radius=12)

        card_str = f"{self.num_a}  {self.operator}  {self.num_b}"
        card_surf = self.font_card.render(card_str, True, (25, 30, 42))
        screen.blit(card_surf, (card_rect.centerx - card_surf.get_width() // 2, card_rect.centery - card_surf.get_height() // 2))

        # --- timer bar ---
        bar_rect = pygame.Rect(card_rect.x, 212, card_rect.width, 8)
        ratio = max(self.time_left / self.time_limit, 0)

        if ratio < 0.3:
            bar_color = (240, 75, 75)      # red
        elif ratio < 0.6:
            bar_color = (240, 175, 40)     # amber
        else:
            bar_color = (80, 230, 110)     # green

        pygame.draw.rect(screen, (60, 66, 80), bar_rect, border_radius=4)   # track
        fill_w = int(bar_rect.width * ratio)
        if fill_w > 0:
            fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, fill_w, bar_rect.height)
            pygame.draw.rect(screen, bar_color, fill_rect, border_radius=4)

        self.input_box.render(screen)

        pygame.draw.rect(screen, (45, 140, 80), self.submit_btn, border_radius=6)
        pygame.draw.rect(screen, (215, 225, 220), self.submit_btn, width=2, border_radius=6)
        btn_txt = self.font_btn.render("SUBMIT", True, (255, 255, 255))
        screen.blit(btn_txt, (self.submit_btn.centerx - btn_txt.get_width() // 2, self.submit_btn.centery - btn_txt.get_height() // 2))

        msg_surf = self.font_hud.render(self.feedback_msg, True, self.feedback_color)
        screen.blit(msg_surf, (self.width // 2 - msg_surf.get_width() // 2, 295))

        mult = self.get_multiplier()
        streak_color = (80, 230, 110) if mult > 1 else (200, 205, 215)
        streak_surf = self.font_hud.render(f"Streak: {self.streak}  (x{mult})", True, streak_color)
        screen.blit(streak_surf, (self.width // 2 - streak_surf.get_width() // 2, 325))