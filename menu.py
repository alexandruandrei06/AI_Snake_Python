import pygame

# Loading background image
menu_background = pygame.image.load('Background/background.png')

# Create screen
screen = pygame.display.set_mode()

# buttonFont = pygame.font.Font('Font/eater.ttf', 40)

class Checkbox:
    def __init__(self, surface, x, y, idnum, caption, color=(131, 24, 173), outline_color=(255, 255, 255),
                 check_color=(219, 4, 55), font_size=22, font_color=(200, 144, 222), text_offset=(28, 1)):
        self.surface = surface
        self.x = x
        self.y = y
        self.color = color
        self.caption = caption
        self.oc = outline_color
        self.cc = check_color
        self.fs = font_size
        self.fc = font_color
        self.to = text_offset
        self.ft = pygame.font.Font('Font/eater.ttf', 40)
        self.font = None
        self.font_surf = None
        self.font_pos = None
        self.click = None

        # identification for removal and reorginazation
        self.idnum = idnum

        # checkbox object
        self.checkbox_obj = pygame.Rect(self.x, self.y, 12, 12)
        self.checkbox_outline = self.checkbox_obj.copy()

        # variables to test the different states of the checkbox
        self.checked = False

    def draw_button_text(self):
        buttonFont = pygame.font.Font('Font/eater.ttf', 40)
        self.font = buttonFont
        self.font_surf = self.font.render(self.caption, True, self.fc)
        w, h = self.font.size(self.caption)
        self.font_pos = (self.x + self.to[0], self.y + 12 / 2 - h / 2 + self.to[1])
        self.surface.blit(self.font_surf, self.font_pos)

    def render_checkbox(self):
        if self.checked:
            pygame.draw.rect(self.surface, self.color, self.checkbox_obj)
            pygame.draw.rect(self.surface, self.oc, self.checkbox_outline, 1)
            pygame.draw.circle(self.surface, self.cc, (self.x + 6, self.y + 6), 4)

        elif not self.checked:
            pygame.draw.rect(self.surface, self.oc, self.checkbox_obj)
            pygame.draw.rect(self.surface, self.oc, self.checkbox_outline, 1)
        self.draw_button_text()

    def _update(self):
        x, y = pygame.mouse.get_pos()
        px, py, w, h = self.checkbox_obj
        if px < x < px + w and py < y < py + w:
            if self.checked:
                self.checked = False
            else:
                self.checked = True

    def update_checkbox(self, event_object):
        if event_object.type == pygame.MOUSEBUTTONDOWN:
            self.click = True
            self._update()


class Menu:
    pygame.init()

    messageFont = pygame.font.Font('Font/eater.ttf', 40)
    messageX = 120
    messageY = 50
    message = messageFont.render('SELECT GAME MODE', True, (255, 255, 255))

    buttonFont = pygame.font.Font('Font/eater.ttf', 40)

    button_width = 140
    button_height = 40
    button1 = buttonFont.render('MANUAL', True, (255, 0, 0))
    button2 = buttonFont.render('LEARNING', True, (255, 255, 255))
    button3 = buttonFont.render('AUTO', True, (255, 0, 0))
    button1X, button1Y = 50, 500
    button2X, button2Y = 250, 500
    button3X, button3Y = 500, 500

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def update_screen(self, screen, boxes):
        screen.blit(menu_background, (0, 0))
        screen.blit(self.message, (self.messageX, self.messageY))
        screen.blit(self.button1, (self.button1X, self.button1Y))
        screen.blit(self.button2, (self.button2X, self.button2Y))
        screen.blit(self.button3, (self.button3X, self.button3Y))
        for box in boxes:
            box.render_checkbox()

    def create_menu(self):
        screen = pygame.display.set_mode((self.width, self.height))

        boxes = []
        box1 = Checkbox(screen, 140, 430, 1, 'EASY')
        box2 = Checkbox(screen, 420, 430, 2, 'HARD')
        boxes.append(box1)
        boxes.append(box2)

        box_checked = 0

        self.update_screen(screen, boxes)

        running = True
        mode = None
        while running:
            mouse = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.button1X <= mouse[0] <= self.button1X + self.button_width and \
                            self.button1Y <= mouse[1] <= self.button1Y + self.button_height:
                        mode = 'MANUAL'
                        if box_checked:
                            running = False
                    elif self.button2X <= mouse[0] <= self.button2X + self.button_width and \
                            self.button2Y <= mouse[1] <= self.button2Y + self.button_height:
                        mode = 'LEARNING'
                        if box_checked:
                            running = False
                    elif self.button3X <= mouse[0] <= self.button3X + self.button_width and \
                            self.button3Y <= mouse[1] <= self.button3Y + self.button_height:
                        mode = 'AUTO'
                        if box_checked:
                            running = False

                    for box in boxes:
                        box.update_checkbox(event)
                        if box.checked is True:
                            box_checked = 1
                            for b in boxes:
                                if b != box:
                                    b.checked = False

                self.update_screen(screen, boxes)
                pygame.display.update()
        for box in boxes:
            if box.checked:
                return mode, box.idnum
