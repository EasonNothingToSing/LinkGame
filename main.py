import os
import sys
import random
import pygame
import copy
import logging


def one_dimen2two_dimen(p):
    return p % GameBase.X_ORIENTATION, p // GameBase.X_ORIENTATION


def two_dimen2one_dimen(ix, iy):
    return int(ix + GameBase.X_ORIENTATION * iy)


def tuple_multiple(tpl0, tpl1):
    return tpl0[0] * tpl1[0], tpl0[1] * tpl1[1]


def tuple_divide(tpl0, tpl1):
    return tpl0[0] // tpl1[0], tpl0[1] // tpl1[1]


def tuple_add(tpl0, tpl1):
    return tpl0[0] + tpl1[0], tpl0[1] + tpl1[1]


class GameBase:
    SCREEN_WIDTH = 500
    SCREEN_HEIGHT = 600

    X_ORIENTATION = 10
    Y_ORIENTATION = 10

    GAME_MAIN_WIDTH = 500
    GAME_MAIN_HEIGHT = 500

    BORDER_LINE_WIDTH = 5

    LINK_LINE_SURVIVE_TIME = 500

    def __init__(self):
        pygame.init()

        self.first_click = {"rect": [], "en": False, "handler": None}
        self.second_click = {"rect": [], "en": False, "handler": None}

        self.ele_stack = {"ele": None, "node": [], "parent": None}
        self.link_line_stack = []

        self.base_surface = pygame.display.set_mode(size=(GameBase.SCREEN_WIDTH, GameBase.SCREEN_HEIGHT))
        self.base_surface.fill((255, 255, 255))
        self.ele_list = []
        self.classify_ele_list = {}
        self.file_list = os.listdir(os.path.join("res"))
        self.scale = (GameBase.GAME_MAIN_WIDTH / GameBase.X_ORIENTATION, GameBase.GAME_MAIN_HEIGHT / GameBase.Y_ORIENTATION)
        # generate a random list
        self.element_gen()

    def order_check(self):
        if self.first_click["en"]:
            return self.second_click
        else:
            return self.first_click

    def recover_click(self):
        self.first_click["en"], self.second_click["en"] = False, False

    def random_order(self):
        for i in range(random.randint(100, 1000)):
            x1, y1 = random.randint(0, GameBase.X_ORIENTATION - 1), random.randint(0, GameBase.Y_ORIENTATION - 1)
            x2, y2 = random.randint(0, GameBase.X_ORIENTATION - 1), random.randint(0, GameBase.Y_ORIENTATION - 1)
            self.ele_list[two_dimen2one_dimen(x1, y1)], self.ele_list[two_dimen2one_dimen(x2, y2)] = self.ele_list[two_dimen2one_dimen(x2, y2)], self.ele_list[two_dimen2one_dimen(x1, y1)]

        for num, i in enumerate(self.ele_list):
            i["position"] = one_dimen2two_dimen(num)

    def ele_classify(self):
        for ele in self.ele_list:
            try:
                self.classify_ele_list[hash(ele["img"])].append(ele)
            except KeyError:
                self.classify_ele_list[hash(ele["img"])] = []
                self.classify_ele_list[hash(ele["img"])].append(ele)

    def element_gen(self):
        for i in range(int(GameBase.X_ORIENTATION * GameBase.Y_ORIENTATION / 2)):
            self.ele_list.append({"img": os.path.join("res", self.file_list[random.randint(0, len(self.file_list) - 1)]), "position": None, "exist": True, "handler": None})
        self.ele_list.extend(copy.deepcopy(self.ele_list))

        self.ele_classify()

        self.random_order()

        while not self.auto_detect():
            self.random_order()

        for num, i in enumerate(self.ele_list):
            i["handler"] = pygame.transform.scale(pygame.image.load(i["img"]).convert_alpha(), self.scale)

    def update(self):
        self.base_surface.fill((255, 255, 255))

        for i in self.ele_list:
            if i["exist"]:
                self.base_surface.blit(i["handler"], tuple_multiple(i["position"], self.scale))

        for col in range(GameBase.X_ORIENTATION + 1):
            pygame.draw.line(self.base_surface, (0, 0, 0), [col*self.scale[0], 0], [col*self.scale[0], GameBase.GAME_MAIN_HEIGHT], GameBase.BORDER_LINE_WIDTH)

        for row in range(GameBase.Y_ORIENTATION + 1):
            pygame.draw.line(self.base_surface, (0, 0, 0), [0, row*self.scale[1]], [GameBase.GAME_MAIN_WIDTH, row*self.scale[1]], GameBase.BORDER_LINE_WIDTH)

        # TODO high light
        self.highlight()

        # TODO link line
        self.link_line()

    def link_line(self):
        tick = pygame.time.get_ticks()
        for item in self.link_line_stack:
            if tick <= item["start"] + GameBase.LINK_LINE_SURVIVE_TIME:
                for num in range(len(item["list"]) - 1):
                    pygame.draw.line(self.base_surface, (0, 255, 0), tuple_add(tuple_multiple(item["list"][num], self.scale), tuple_divide(self.scale, [2, 2])), tuple_add(tuple_multiple(item["list"][num + 1], self.scale), tuple_divide(self.scale, [2, 2])), width=GameBase.BORDER_LINE_WIDTH)
            else:
                self.link_line_stack.remove(item)

    def highlight(self):
        if self.first_click["en"]:
            pygame.draw.rect(self.base_surface, (255, 0, 0), [self.first_click["rect"][0]*self.scale[0], self.first_click["rect"][1]*self.scale[1], self.scale[0], self.scale[1]], GameBase.BORDER_LINE_WIDTH)
        if self.second_click["en"]:
            pygame.draw.rect(self.base_surface, (255, 0, 0), [self.second_click["rect"][0]*self.scale[0], self.second_click["rect"][1]*self.scale[1], self.scale[0], self.scale[1]], GameBase.BORDER_LINE_WIDTH)

    def locate(self, pos):
        inx, iny = tuple_divide(pos, self.scale)
        if inx >= GameBase.X_ORIENTATION or iny >= GameBase.Y_ORIENTATION:
            return None
        else:
            if self.ele_list[two_dimen2one_dimen(inx, iny)]["exist"]:
                return int(inx), int(iny)
            else:
                return None

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
    def get_around_ele(self, pos):
        iix, iiy = pos
        ne_rslt, e_rslt = [], []
        # For top
        ipos = [iix, iiy - 1]
        # Y must be equal or greater than Y:0
        while ipos[1] >= 0:
            # Get the element
            temp = self.ele_list[two_dimen2one_dimen(*ipos)]
            if temp["exist"]:
                # Store into exist result
                e_rslt.append(temp)
                break
            else:
                # Store into non-exist result
                ne_rslt.append(temp)
                # Y- grow
                ipos[1] = ipos[1] - 1

        # For left
        ipos = [iix - 1, iiy]
        # X must be equal or greater than X:0
        while ipos[0] >= 0:
            # Get the element
            temp = self.ele_list[two_dimen2one_dimen(*ipos)]
            if temp["exist"]:
                # Store into exist result
                e_rslt.append(temp)
                break
            else:
                # Store into non-exist result
                ne_rslt.append(temp)
                # X- grow
                ipos[0] = ipos[0] - 1

        # For bottom
        ipos = [iix, iiy + 1]
        # Y must less than Y_ORIENTATION
        while ipos[1] < GameBase.Y_ORIENTATION:
            # Get the element
            temp = self.ele_list[two_dimen2one_dimen(*ipos)]
            if temp["exist"]:
                # Store into exist result
                e_rslt.append(temp)
                break
            else:
                # Store into non-exist result
                ne_rslt.append(temp)
                # Y+ grow
                ipos[1] = ipos[1] + 1

        # For right
        ipos = [iix + 1, iiy]
        # X must less than X_ORIENTATION
        while ipos[0] < GameBase.X_ORIENTATION:
            # Get the element
            temp = self.ele_list[two_dimen2one_dimen(*ipos)]
            if temp["exist"]:
                # Store into exist result
                e_rslt.append(temp)
                break
            else:
                # Store into non-exist result
                ne_rslt.append(temp)
                # X+ grow
                ipos[0] = ipos[0] + 1

        return e_rslt, ne_rslt

    def llg_protocol(self, fc=None, sc=None):
        # # Auto detect the element
        if fc and sc:
            self.first_click["handler"] = fc
            self.first_click["rect"] = fc["position"]
            self.second_click["handler"] = sc
            self.second_click["rect"] = sc["position"]

        if self.first_click["handler"]["img"] == self.second_click["handler"]["img"]:
            fold = 1
            self.ele_stack["ele"], self.ele_stack["node"] = self.first_click["handler"], []
            stack = [[self.ele_stack], [], [], []]
            while fold <= 3:
                logging.debug("loop count: %d" % fold)
                for node in stack[fold-1]:
                    pointer = node
                    e_rslt, ne_rslt = self.get_around_ele(pointer["ele"]["position"])
                    # Every loop check the target element in the search list
                    if self.ele_list[two_dimen2one_dimen(*self.second_click["rect"])] in e_rslt:
                        logging.debug("two element conform the link game protocol, will eliminate fast!!")
                        if fc and sc:
                            return True
                        link_line_list = [self.second_click["handler"]["position"]]
                        while pointer["parent"]:
                            link_line_list.append(pointer["ele"]["position"])
                            pointer = pointer["parent"]
                        link_line_list.append(self.first_click["handler"]["position"])
                        link_line_list.reverse()
                        self.link_line_stack.append({"start": pygame.time.get_ticks(), "list": link_line_list})
                        logging.debug(str(link_line_list))
                        return True
                    # remove ne_rslt element in ancestor
                    if fold < 3:
                        for i in range(fold):
                            for ele in stack[i]:
                                if ele in ne_rslt:
                                    ne_rslt.remove(ele)
                        for ele in ne_rslt:
                            i_node = {"ele": ele, "parent": pointer, "node": []}
                            pointer["node"].append(i_node)
                            stack[fold].append(i_node)
                logging.debug("the length: " + str(len(stack[fold])))
                if not stack[fold]:
                    return False
                fold += 1
            else:
                return False

    def auto_detect(self):
        for ele_list in self.classify_ele_list.values():
            max_len = len(ele_list)
            for num_fc in range(max_len):
                if not ele_list[num_fc]["exist"]:
                    continue
                for num_sc in range(num_fc + 1, max_len):
                    if not ele_list[num_sc]["exist"]:
                        continue
                    if self.llg_protocol(fc=ele_list[num_fc], sc=ele_list[num_sc]):
                        logging.debug("The first:" + str(ele_list[num_fc]) + "The second:" + str(ele_list[num_sc]))
                        return True
        return False

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = self.locate(event.pos)
                    logging.debug(pos)
                    if pos:
                        click = self.order_check()
                        click["rect"], click["en"], click["handler"] = pos, True, self.ele_list[two_dimen2one_dimen(*pos)]
                    if self.second_click["en"]:
                        if self.second_click["handler"] == self.first_click["handler"]:
                            self.recover_click()
                            break
                        # if first click and second click is same picture and conform the link link game protocol, then will eliminate both element, otherwise only highlight the last click image
                        if self.llg_protocol():
                            self.first_click["handler"]["exist"], self.second_click["handler"]["exist"] = False, False
                            self.recover_click()
                            # Auto check again
                            while not self.auto_detect():
                                self.random_order()
                        else:
                            self.recover_click()
                            click = self.order_check()
                            click["rect"], click["en"], click["handler"] = pos, True, self.ele_list[
                                two_dimen2one_dimen(*pos)]

                if event.type == pygame.MOUSEBUTTONUP:
                    pass

            self.update()

            pygame.display.update()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    base = GameBase()
    base.run()
