class Player:
    def __init__(self, x, y, is_fire):
        self.x = float(x)
        self.y = float(y)
        self.is_fire = is_fire

        self.hp = 100
        self.display_hp = 100
        self.speed = 5

        self.charging = False
        self.charge_time = 0
        self.charge_threshold = 45

        self.animation_time = random.random() * 10
        self.hit_flash = 0

        # Direction toward the opponent
        self.direction = 1 if is_fire else -1

        # Attack animation
        self.attack_timer = 0
        self.attack_duration = 18

        # Humanoid dimensions
        self.body_width = 28
        self.body_height = 44
        self.head_radius = 13

        self.color = FIRE_MAIN if is_fire else WATER_MAIN

        self.rect = pygame.Rect(
            int(x - 20),
            int(y - 45),
            40,
            75,
        )

    def move(self, up_key, down_key, keys):
        if keys[up_key]:
            self.y -= self.speed

        if keys[down_key]:
            self.y += self.speed

        self.y = max(
            125,
            min(GROUND_Y - 45, self.y),
        )

        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)

    def update(self, particles):
        self.animation_time += 0.12

        self.display_hp += (
            self.hp - self.display_hp
        ) * 0.12

        if abs(self.hp - self.display_hp) < 0.1:
            self.display_hp = self.hp

        if self.hit_flash > 0:
            self.hit_flash -= 1

        if self.attack_timer > 0:
            self.attack_timer -= 1

        # Charge particles gather around the hands and body.
        if self.charging:
            self.charge_time += 1

            colors = (
                FIRE_COLORS if self.is_fire
                else WATER_COLORS
            )

            angle = random.uniform(0, math.tau)

            radius = random.randint(
                20,
                min(65, 25 + self.charge_time),
            )

            px = self.x + math.cos(angle) * radius
            py = self.y + math.sin(angle) * radius

            particles.append(
                Particle(
                    px,
                    py,
                    random.choice(colors),
                    random.randint(3, 7),
                    18,
                    (self.x - px) * 0.08,
                    (self.y - py) * 0.08,
                )
            )

    def take_damage(self, damage):
        self.hp = max(0, self.hp - damage)
        self.hit_flash = 8

    def get_hand_position(self):
        """
        Calculate the current attacking hand position.
        Used by both the character animation and attacks.
        """

        direction = self.direction

        shoulder_x = self.x + direction * 12
        shoulder_y = self.y - 8

        if self.charging:
            # Pull the arm backward while gathering energy.
            progress = min(
                1,
                self.charge_time / self.charge_threshold,
            )

            hand_x = shoulder_x - direction * (
                18 + progress * 15
            )

            hand_y = shoulder_y + 15

        elif self.attack_timer > 0:
            # Extend the arm during the attack.
            progress = self.attack_timer / self.attack_duration

            extension = 30 * (1 - progress)

            hand_x = shoulder_x + direction * (
                24 + extension
            )

            hand_y = shoulder_y - 4

        else:
            # Relaxed fighting stance.
            hand_x = shoulder_x + direction * 18

            hand_y = shoulder_y + 14 + math.sin(
                self.animation_time * 2
            ) * 2

        return hand_x, hand_y

    def release_attack(self):
        charged = (
            self.charge_time >= self.charge_threshold
        )

        self.charging = False
        self.charge_time = 0

        # Start the arm extension animation.
        self.attack_timer = self.attack_duration

        if charged:
            return Beam(self)

        hand_x, hand_y = self.get_hand_position()

        return Projectile(
            hand_x,
            hand_y,
            self.direction,
            self.is_fire,
            False,
        )

    def draw(self, surface, target_x):
        # Always face the opponent.
        self.direction = (
            1 if target_x > self.x else -1
        )

        direction = self.direction

        colors = (
            FIRE_COLORS if self.is_fire
            else WATER_COLORS
        )

        main_color = (
            FIRE_MAIN if self.is_fire
            else WATER_MAIN
        )

        highlight = colors[-1]

        t = self.animation_time

        # Subtle breathing animation.
        breathe = math.sin(t * 2) * 2

        # Running / idle leg movement.
        leg_swing = math.sin(t * 3) * 5

        # Humanoid body coordinates.
        head_y = self.y - 43 + breathe * 0.3

        shoulder_y = self.y - 14
        hip_y = self.y + 19

        head_x = self.x

        body_rect = pygame.Rect(
            int(self.x - 14),
            int(self.y - 27 + breathe * 0.3),
            28,
            44,
        )

        # -------------------------------------------------
        # CHARACTER GLOW
        # -------------------------------------------------

        draw_glow(
            surface,
            self.x,
            self.y - 10,
            38,
            main_color,
            80,
        )

        # -------------------------------------------------
        # LEGS
        # -------------------------------------------------

        left_hip = (self.x - 7, hip_y)
        right_hip = (self.x + 7, hip_y)

        left_foot = (
            self.x - 13 + leg_swing,
            self.y + 43,
        )

        right_foot = (
            self.x + 13 - leg_swing,
            self.y + 43,
        )

        # Upper legs
        pygame.draw.line(
            surface,
            main_color,
            left_hip,
            (
                self.x - 11 + leg_swing * 0.3,
                self.y + 28,
            ),
            9,
        )

        pygame.draw.line(
            surface,
            main_color,
            right_hip,
            (
                self.x + 11 - leg_swing * 0.3,
                self.y + 28,
            ),
            9,
        )

        # Lower legs
        pygame.draw.line(
            surface,
            highlight,
            (
                self.x - 11 + leg_swing * 0.3,
                self.y + 28,
            ),
            left_foot,
            7,
        )

        pygame.draw.line(
            surface,
            highlight,
            (
                self.x + 11 - leg_swing * 0.3,
                self.y + 28,
            ),
            right_foot,
            7,
        )

        # Feet
        pygame.draw.ellipse(
            surface,
            main_color,
            (
                int(left_foot[0] - 8),
                int(left_foot[1] - 3),
                16,
                8,
            ),
        )

        pygame.draw.ellipse(
            surface,
            main_color,
            (
                int(right_foot[0] - 8),
                int(right_foot[1] - 3),
                16,
                8,
            ),
        )

        # -------------------------------------------------
        # BACK ARM
        # -------------------------------------------------

        back_shoulder = (
            self.x - direction * 12,
            shoulder_y,
        )

        back_elbow = (
            self.x - direction * 22,
            self.y + 1 + math.sin(t * 2) * 2,
        )

        back_hand = (
            self.x - direction * 24,
            self.y + 13,
        )

        pygame.draw.line(
            surface,
            main_color,
            back_shoulder,
            back_elbow,
            10,
        )

        pygame.draw.line(
            surface,
            highlight,
            back_elbow,
            back_hand,
            8,
        )

        pygame.draw.circle(
            surface,
            highlight,
            (int(back_hand[0]), int(back_hand[1])),
            6,
        )

        # -------------------------------------------------
        # TORSO
        # -------------------------------------------------

        pygame.draw.rect(
            surface,
            main_color,
            body_rect,
            border_radius=10,
        )

        # Chest highlight
        pygame.draw.line(
            surface,
            highlight,
            (
                int(self.x),
                int(self.y - 22),
            ),
            (
                int(self.x),
                int(self.y + 5),
            ),
            4,
        )

        # Shoulder armor
        pygame.draw.circle(
            surface,
            highlight,
            (
                int(self.x - 13),
                int(shoulder_y),
            ),
            7,
        )

        pygame.draw.circle(
            surface,
            highlight,
            (
                int(self.x + 13),
                int(shoulder_y),
            ),
            7,
        )

        # -------------------------------------------------
        # HEAD
        # -------------------------------------------------

        pygame.draw.circle(
            surface,
            main_color,
            (
                int(head_x),
                int(head_y),
            ),
            self.head_radius,
        )

        pygame.draw.circle(
            surface,
            highlight,
            (
                int(head_x),
                int(head_y - 2),
            ),
            self.head_radius - 5,
        )

        # Eyes face the opponent.
        eye_x = head_x + direction * 5

        pygame.draw.circle(
            surface,
            BLACK,
            (
                int(eye_x),
                int(head_y - 1),
            ),
            3,
        )

        # -------------------------------------------------
        # ATTACKING ARM
        # -------------------------------------------------

        shoulder = (
            self.x + direction * 12,
            shoulder_y,
        )

        hand_x, hand_y = self.get_hand_position()

        if self.charging:
            # Elbow bends backward as energy accumulates.
            elbow = (
                self.x - direction * 3,
                self.y + 1,
            )

        elif self.attack_timer > 0:
            # Arm straightens during the attack.
            elbow = (
                shoulder[0] + direction * 17,
                shoulder[1] - 3,
            )

        else:
            # Bent arm in the neutral stance.
            elbow = (
                self.x + direction * 19,
                self.y + 1,
            )

        # Upper arm
        pygame.draw.line(
            surface,
            main_color,
            shoulder,
            elbow,
            11,
        )

        # Forearm
        pygame.draw.line(
            surface,
            highlight,
            elbow,
            (
                int(hand_x),
                int(hand_y),
            ),
            8,
        )

        # -------------------------------------------------
        # HAND AND ENERGY
        # -------------------------------------------------

        draw_glow(
            surface,
            hand_x,
            hand_y,
            13 if self.charging else 9,
            highlight,
            120,
        )

        pygame.draw.circle(
            surface,
            highlight,
            (
                int(hand_x),
                int(hand_y),
            ),
            7,
        )

        pygame.draw.circle(
            surface,
            WHITE,
            (
                int(hand_x),
                int(hand_y),
            ),
            3,
        )

        # Charging energy grows over time.
        if self.charging:
            progress = min(
                1,
                self.charge_time / self.charge_threshold,
            )

            radius = int(12 + progress * 15)

            pygame.draw.circle(
                surface,
                highlight,
                (
                    int(hand_x),
                    int(hand_y),
                ),
                radius,
                2,
            )

            if progress >= 1:
                pygame.draw.circle(
                    surface,
                    WHITE,
                    (
                        int(hand_x),
                        int(hand_y),
                    ),
                    radius + 5,
                    2,
                )
