import sys
import random
import pygame
import copy

# 5*6 link game
X_ORIENTATION = 5
Y_ORIENTATION = 6

class_color_list = [(0, 0, 205), (205, 0, 0), (0, 205, 0), (205, 0, 205), (205, 205, 0), (0, 205, 205), (205, 205, 205)]
ele_list = []


# ------------------------>  x+
# |
# |
# |           T
# |         L P R
# |           B
# |
# |
# |
# V
# Y+


def one_dimen2two_dimen(p):
    return p % X_ORIENTATION, p // X_ORIENTATION


def two_dimen2one_dimen(ix, iy):
    return ix + X_ORIENTATION * iy


def element_gen():
    for i in range(int(X_ORIENTATION * Y_ORIENTATION / 2)):
        ele_list.append({"color": class_color_list[random.randint(0, len(class_color_list) - 1)], "position": None,
                         "exist": True, "handler": None})
    ele_list.extend(copy.deepcopy(ele_list))
    for i in range(random.randint(100, 1000)):
        x1, y1 = random.randint(0, X_ORIENTATION - 1), random.randint(0, Y_ORIENTATION - 1)
        x2, y2 = random.randint(0, X_ORIENTATION - 1), random.randint(0, Y_ORIENTATION - 1)
        ele_list[two_dimen2one_dimen(x1, y1)], ele_list[two_dimen2one_dimen(x2, y2)] = \
            ele_list[two_dimen2one_dimen(x2, y2)], ele_list[two_dimen2one_dimen(x1, y1)]

    for num, i in enumerate(ele_list):
        i["position"] = one_dimen2two_dimen(num)


def get_around_ele(ix, iy):
    ne_rslt, e_rslt = [], []
    temp = None

    # For top
    pos = [ix, iy - 1]
    # Y must be equal or greater than Y:0
    while pos[1] >= 0:
        # Get the element
        temp = ele_list[two_dimen2one_dimen(*pos)]
        if temp["exist"]:
            # Store into exist result
            e_rslt.append(temp)
            break
        else:
            # Store into non-exist result
            ne_rslt.append(temp)
            # Y- grow
            pos[1] = pos[1] - 1

    # For left
    pos = [ix - 1, iy]
    # X must be equal or greater than X:0
    while pos[0] >= 0:
        # Get the element
        temp = ele_list[two_dimen2one_dimen(*pos)]
        if temp["exist"]:
            # Store into exist result
            e_rslt.append(temp)
            break
        else:
            # Store into non-exist result
            ne_rslt.append(temp)
            # X- grow
            pos[0] = pos[0] - 1

    # For bottom
    pos = [ix, iy + 1]
    # Y must less than Y_ORIENTATION
    while pos[1] < Y_ORIENTATION:
        # Get the element
        temp = ele_list[two_dimen2one_dimen(*pos)]
        if temp["exist"]:
            # Store into exist result
            e_rslt.append(temp)
            break
        else:
            # Store into non-exist result
            ne_rslt.append(temp)
            # Y+ grow
            pos[1] = pos[1] + 1

    # For right
    pos = [ix + 1, iy]
    # X must less than X_ORIENTATION
    while pos[0] < X_ORIENTATION:
        # Get the element
        temp = ele_list[two_dimen2one_dimen(*pos)]
        if temp["exist"]:
            # Store into exist result
            e_rslt.append(temp)
            break
        else:
            # Store into non-exist result
            ne_rslt.append(temp)
            # X+ grow
            pos[0] = pos[0] + 1

    return e_rslt, ne_rslt


first_input, second_input = None, None
stage = "waiting"


def clear_stage_mechine(item):
    global first_input, second_input, stage

    if stage == "waiting":
        first_input = item
        # TODO open a timer
        stage = "pending"
    elif stage == "pending":
        if item:
            second_input = item
            # TODO handle the Match function to check the two item is match

            stage = "waiting"
        else:
            # Time out
            pass


def highlight_rect(item):
    pygame.draw.rect(item["handler"], (255, 255, 255), (item["position"][0] * 100, item["position"][1] * 100, 100, 100), 5)


def get_match_res(items):
    for item in items:
        get_around_ele(*item["position"])


if __name__ == "__main__":
    element_gen()

    pygame.init()

    base_surface = pygame.display.set_mode(size=(500, 600))

    while True:
        base_surface.fill((0, 0, 0))

        # Render the link link game picture
        for x in range(0, X_ORIENTATION):
            for y in range(0, Y_ORIENTATION):
                if ele_list[two_dimen2one_dimen(x, y)]["exist"]:
                    ele_list[two_dimen2one_dimen(x, y)]["handler"] = \
                        pygame.draw.rect(base_surface, ele_list[two_dimen2one_dimen(x, y)]["color"],
                                         (x * 100, y * 100, 100, 100))

        # Capture the event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                in_x, in_y = event.pos[0] // 100, event.pos[1] // 100
                print("Click x: %d, y: %d" % (in_x, in_y))


                def highlight_rect(item):
                    pygame.draw.rect(base_surface, (255, 255, 255),
                                     (item["position"][0] * 100, item["position"][1] * 100, 100, 100), 5)

                highlight_rect(ele_list[two_dimen2one_dimen(in_x, in_y)])
                # clear_stage_mechine(ele_list[two_dimen2one_dimen(in_x, in_y)])

        pygame.display.flip()
