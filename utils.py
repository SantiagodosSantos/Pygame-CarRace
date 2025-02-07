import pygame

def blit_rotate_center(win, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(center = top_left).center)
    win.blit(rotated_image, new_rect.topleft)
    return rotated_image

def blit_text_center(win, font, text):
    render = font.render(text, 1, "magenta")
    win.blit(render, (win.get_width()/2 - render.get_width()/2, win.get_height()/2 - render.get_height()/2))
    