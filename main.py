from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.vector import Vector
import random
import math

# Set window size for development (will be full screen on mobile)
Window.size = (400, 600)

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15
        self.velocity_y = 0
        self.velocity_x = 0
        self.gravity = 0.4
        self.jump_strength = -12  # Stronger for touch controls
        self.move_speed = 6
        self.color = (1, 0, 0, 1)  # Red in RGBA format for Kivy
        self.invisible = False
        self.invisible_timer = 0

    def update(self, dt, slowmo=False):
        # Apply gravity
        gravity_effect = self.gravity * (0.3 if slowmo else 1.0)
        self.velocity_y += gravity_effect

        # Apply velocities
        velocity_multiplier = 0.3 if slowmo else 1.0
        self.y += self.velocity_y * velocity_multiplier
        self.x += self.velocity_x * velocity_multiplier

        # Apply friction to horizontal movement
        self.velocity_x *= 0.85

        # Update power-up timers
        if self.invisible_timer > 0:
            self.invisible_timer -= 60 * dt  # Convert to frames
            if self.invisible_timer <= 0:
                self.invisible = False

        # Keep ball on screen horizontally
        if self.x < self.radius:
            self.x = self.radius
            self.velocity_x = 0
        elif self.x > 400 - self.radius:  # Screen width
            self.x = 400 - self.radius
            self.velocity_x = 0

        # Keep ball from going above screen
        if self.y > 600 - self.radius:  # Screen height (inverted Y in Kivy)
            self.y = 600 - self.radius
            self.velocity_y = min(0, self.velocity_y)

    def jump(self):
        self.velocity_y = self.jump_strength

    def move_left(self):
        self.velocity_x = -self.move_speed

    def move_right(self):
        self.velocity_x = self.move_speed

    def move_down(self):
        self.velocity_y = self.move_speed

    def change_color(self):
        colors = [(1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1), (1, 1, 0, 1), 
                  (1, 0, 1, 1), (1, 0.5, 0, 1), (0, 1, 1, 1)]
        self.color = random.choice(colors)

    def make_invisible(self, duration=300):
        self.invisible = True
        self.invisible_timer = duration

class Brick:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 20
        self.speed = speed
        self.color = (0.55, 0.27, 0.07, 1)  # Brown in RGBA

    def update(self, dt, slowmo=False):
        speed_multiplier = 0.3 if slowmo else 1.0
        self.y -= self.speed * speed_multiplier * 60 * dt  # Convert to frame rate

    def collides_with(self, ball):
        if ball.invisible:
            return False
        return (self.x < ball.x + ball.radius and 
                self.x + self.width > ball.x - ball.radius and
                self.y < ball.y + ball.radius and 
                self.y + self.height > ball.y - ball.radius)

class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.speed = 2
        self.type = random.choice(['invisible', 'slowmo'])
        self.color = (0.5, 0, 0.5, 1) if self.type == 'invisible' else (0, 1, 1, 1)

    def update(self, dt, slowmo=False):
        speed_multiplier = 0.3 if slowmo else 1.0
        self.y -= self.speed * speed_multiplier * 60 * dt

    def collides_with(self, ball):
        distance = math.sqrt((self.x - ball.x)**2 + (self.y - ball.y)**2)
        return distance < self.radius + ball.radius

class GameWidget(Widget):
    def __init__(self, **kwargs):
        super(GameWidget, self).__init__(**kwargs)
        self.reset_game()
        self.game_state = "start"  # "start", "playing", "game_over"
        self.background_colors = [(0.53, 0.81, 0.92, 1), (1, 0.71, 0.76, 1), 
                                  (0.6, 0.98, 0.6, 1), (1, 0.85, 0.73, 1), (0.87, 0.63, 0.87, 1)]
        self.background_color = self.background_colors[0]

        # Touch control areas (invisible buttons)
        self.bind(size=self.update_graphics)

    def reset_game(self):
        self.ball = Ball(200, 300)  # Center of 400x600 screen
        self.bricks = []
        self.powerups = []
        self.score = 0
        self.brick_spawn_timer = 0
        self.powerup_spawn_timer = 0
        self.slowmo_timer = 0
        self.difficulty_level = 1

    def spawn_brick(self):
        x = random.randint(0, 340)  # 400 - 60 (brick width)
        speed = 2 + (self.score // 100) * 0.5
        if self.score >= 200:
            speed *= 1.5
        self.bricks.append(Brick(x, 620, speed))  # Start above screen

    def spawn_powerup(self):
        if random.random() < 0.3:
            x = random.randint(20, 380)
            self.powerups.append(PowerUp(x, 620))

    def update_difficulty(self):
        old_level = self.difficulty_level
        self.difficulty_level = 1 + (self.score // 100)

        if self.difficulty_level > old_level:
            self.ball.change_color()
            self.background_color = random.choice(self.background_colors)

    def handle_collisions(self):
        # Check brick collisions
        for brick in self.bricks[:]:
            if brick.collides_with(self.ball):
                if not self.ball.invisible:
                    self.game_state = "game_over"
                    return

        # Check powerup collisions
        for powerup in self.powerups[:]:
            if powerup.collides_with(self.ball):
                if powerup.type == 'invisible':
                    self.ball.make_invisible(300)
                elif powerup.type == 'slowmo':
                    self.slowmo_timer = 300
                self.powerups.remove(powerup)

        # Check boundary collisions
        if (self.ball.x - self.ball.radius <= 0 or 
            self.ball.x + self.ball.radius >= 400 or 
            self.ball.y - self.ball.radius <= 0):  # Bottom in Kivy coords
            self.game_state = "game_over"

    def update_game(self, dt):
        if self.game_state == "playing":
            # Update ball
            slowmo = self.slowmo_timer > 0
            self.ball.update(dt, slowmo)

            # Update slowmo timer
            if self.slowmo_timer > 0:
                self.slowmo_timer -= 60 * dt

            # Spawn bricks
            spawn_rate = 1.0 - (self.score // 50) * 0.1  # Faster spawning
            if self.score >= 200:
                spawn_rate = max(spawn_rate / 2, 0.2)

            self.brick_spawn_timer += dt
            if self.brick_spawn_timer >= spawn_rate:
                self.spawn_brick()
                self.brick_spawn_timer = 0

            # Spawn powerups
            self.powerup_spawn_timer += dt
            if self.powerup_spawn_timer >= 5.0:  # Every 5 seconds
                self.spawn_powerup()
                self.powerup_spawn_timer = 0

            # Update bricks
            for brick in self.bricks[:]:
                brick.update(dt, slowmo)
                if brick.y < -50:  # Off screen
                    self.bricks.remove(brick)
                    self.score += 10

            # Update powerups
            for powerup in self.powerups[:]:
                powerup.update(dt, slowmo)
                if powerup.y < -50:
                    self.powerups.remove(powerup)

            # Update difficulty
            self.update_difficulty()

            # Handle collisions
            self.handle_collisions()

        # Always update graphics
        self.update_graphics()

    def update_graphics(self, *args):
        self.canvas.clear()

        with self.canvas:
            # Background
            Color(*self.background_color)
            Rectangle(pos=(0, 0), size=(400, 600))

            if self.game_state == "playing":
                # Draw borders
                Color(1, 0, 0, 1)  # Red
                Line(rectangle=(0, 0, 400, 600), width=5)

                # Draw ball
                alpha = 0.3 if self.ball.invisible else 1.0
                Color(*self.ball.color[:3], alpha)
                Ellipse(pos=(self.ball.x - self.ball.radius, self.ball.y - self.ball.radius), 
                       size=(self.ball.radius * 2, self.ball.radius * 2))

                # Draw white center dot
                Color(1, 1, 1, alpha)
                center_radius = self.ball.radius // 3
                Ellipse(pos=(self.ball.x - center_radius, self.ball.y - center_radius),
                       size=(center_radius * 2, center_radius * 2))

                # Draw bricks
                Color(*self.bricks[0].color if self.bricks else (0.55, 0.27, 0.07, 1))
                for brick in self.bricks:
                    Rectangle(pos=(brick.x, brick.y), size=(brick.width, brick.height))

                # Draw powerups
                for powerup in self.powerups:
                    Color(*powerup.color)
                    Ellipse(pos=(powerup.x - powerup.radius, powerup.y - powerup.radius),
                           size=(powerup.radius * 2, powerup.radius * 2))

    def on_touch_down(self, touch):
        if self.game_state == "playing":
            # Touch anywhere to jump
            self.ball.jump()

            # Touch zones for movement
            if touch.x < 100:  # Left side - move left
                self.ball.move_left()
            elif touch.x > 300:  # Right side - move right  
                self.ball.move_right()
            elif touch.y < 150:  # Bottom area - move down
                self.ball.move_down()

        return True

class StartScreen(BoxLayout):
    def __init__(self, app, **kwargs):
        super(StartScreen, self).__init__(**kwargs)
        self.app = app
        self.orientation = 'vertical'
        self.spacing = 20
        self.padding = [20, 50, 20, 50]

        # Title
        title = Label(text='TAP BALL GAME', font_size='32sp', 
                     size_hint=(1, 0.2), color=(0, 0, 0, 1))
        self.add_widget(title)

        # Instructions
        instructions = Label(
            text='📱 TOUCH CONTROLS:\n\n'
                 '• Tap anywhere to JUMP\n'
                 '• Tap LEFT side to move left\n'
                 '• Tap RIGHT side to move right\n'
                 '• Tap BOTTOM to move down\n\n'
                 '🎯 AVOID falling bricks\n'
                 '⚡ COLLECT power-ups\n'
                 '🏆 SCORE increases with survival',
            font_size='14sp', text_size=(350, None), halign='center',
            size_hint=(1, 0.6), color=(0, 0, 0, 1)
        )
        self.add_widget(instructions)

        # Start button
        start_btn = Button(text='START GAME', size_hint=(0.6, 0.2), 
                          pos_hint={'center_x': 0.5})
        start_btn.bind(on_press=self.start_game)
        self.add_widget(start_btn)

    def start_game(self, instance):
        self.app.start_game()

class GameOverScreen(BoxLayout):
    def __init__(self, app, **kwargs):
        super(GameOverScreen, self).__init__(**kwargs)
        self.app = app
        self.orientation = 'vertical'
        self.spacing = 20
        self.padding = [20, 100, 20, 100]

        # Game Over title
        title = Label(text='GAME OVER', font_size='36sp',
                     size_hint=(1, 0.2), color=(1, 0, 0, 1))
        self.add_widget(title)

        # Score display
        self.score_label = Label(text='Score: 0', font_size='24sp',
                               size_hint=(1, 0.2), color=(1, 1, 1, 1))
        self.add_widget(self.score_label)

        # Buttons
        button_layout = BoxLayout(size_hint=(1, 0.4), spacing=20)

        restart_btn = Button(text='RESTART', size_hint=(0.5, 1))
        restart_btn.bind(on_press=self.restart_game)
        button_layout.add_widget(restart_btn)

        back_btn = Button(text='BACK', size_hint=(0.5, 1))
        back_btn.bind(on_press=self.back_to_start)
        button_layout.add_widget(back_btn)

        self.add_widget(button_layout)

    def update_score(self, score):
        self.score_label.text = f'Score: {score}'

    def restart_game(self, instance):
        self.app.restart_game()

    def back_to_start(self, instance):
        self.app.show_start_screen()

class TapBallApp(App):
    def build(self):
        self.title = 'Tap Ball Game'

        # Main layout
        self.root_layout = FloatLayout()

        # Create screens
        self.start_screen = StartScreen(self)
        self.game_widget = GameWidget()
        self.game_over_screen = GameOverScreen(self)

        # UI Labels for game screen
        self.score_label = Label(text='Score: 0', font_size='18sp',
                               pos_hint={'x': 0, 'top': 1}, size_hint=(0.4, 0.1),
                               color=(0, 0, 0, 1))

        self.level_label = Label(text='Level: 1', font_size='16sp',
                               pos_hint={'x': 0, 'top': 0.9}, size_hint=(0.4, 0.08),
                               color=(0, 0, 0, 1))

        self.status_label = Label(text='', font_size='14sp',
                                pos_hint={'x': 0, 'top': 0.82}, size_hint=(1, 0.08),
                                color=(0.5, 0, 0.5, 1))

        # Show start screen initially
        self.show_start_screen()

        return self.root_layout

    def show_start_screen(self):
        self.root_layout.clear_widgets()
        self.root_layout.add_widget(self.start_screen)

    def start_game(self):
        self.root_layout.clear_widgets()
        self.game_widget.reset_game()
        self.game_widget.game_state = "playing"

        # Add game widget and UI
        self.root_layout.add_widget(self.game_widget)
        self.root_layout.add_widget(self.score_label)
        self.root_layout.add_widget(self.level_label)
        self.root_layout.add_widget(self.status_label)

        # Start game loop
        Clock.schedule_interval(self.update_game, 1/60.0)  # 60 FPS

    def update_game(self, dt):
        if self.game_widget.game_state == "playing":
            self.game_widget.update_game(dt)

            # Update UI
            self.score_label.text = f'Score: {self.game_widget.score}'
            self.level_label.text = f'Level: {self.game_widget.difficulty_level}'

            # Update status
            status = ""
            if self.game_widget.ball.invisible:
                status += "INVISIBLE! "
            if self.game_widget.slowmo_timer > 0:
                status += "SLOW MOTION! "
            self.status_label.text = status

        elif self.game_widget.game_state == "game_over":
            Clock.unschedule(self.update_game)
            self.show_game_over()

    def show_game_over(self):
        self.root_layout.clear_widgets()
        self.game_over_screen.update_score(self.game_widget.score)
        self.root_layout.add_widget(self.game_over_screen)

    def restart_game(self):
        self.start_game()

if __name__ == '__main__':
    TapBallApp().run()
