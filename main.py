import sys
import random
import pygame

# 5*6 link game
X_ORIENTATION = 5
Y_ORIENTATION = 6

class_color_list = [(0, 0, 205), (205, 0, 0), (0, 205, 0), (205, 0, 205), (205, 205, 0), (0, 205, 205), (205, 205, 205)]
ele_list = []


def element_gen():
    for i in range(int(X_ORIENTATION * Y_ORIENTATION / 2)):
        ele_list.append({"color": class_color_list[random.randint(0, len(class_color_list) - 1)], "position": None,
                         "exist": True})
    ele_list.extend(ele_list)
    for i in range(random.randint(100, 1000)):
        x1, y1 = random.randint(0, X_ORIENTATION-1), random.randint(0, Y_ORIENTATION-1)
        x2, y2 = random.randint(0, X_ORIENTATION-1), random.randint(0, Y_ORIENTATION-1)
        ele_list[x1 + y1 * X_ORIENTATION], ele_list[x2 + y2 * X_ORIENTATION] = ele_list[x2 + y2 * X_ORIENTATION], \
                                                                               ele_list[x1 + y1 * X_ORIENTATION]


if __name__ == "__main__":
    element_gen()

    pygame.init()
    base_surface = pygame.display.set_mode(size=(500, 600))

    while True:
        for event in pygame.event.get():
            if event:
                print(event)

        for x in range(0, X_ORIENTATION):
            for y in range(0, Y_ORIENTATION):
                if ele_list[x+y*X_ORIENTATION]["exist"]:
                    pygame.draw.rect(base_surface, ele_list[x+y*X_ORIENTATION]["color"], (x*100, y*100, 100, 100))
        pygame.display.flip()
