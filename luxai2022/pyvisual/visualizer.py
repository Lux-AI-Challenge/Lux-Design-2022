import pygame
from luxai2022.map.board import Board
from luxai2022.state import State
from luxai2022.unit import UnitType

color_to_rgb = dict(yellow=[236, 238, 126], green=[173, 214, 113], blue=[154, 210, 203], red=[164, 74, 63])


class Visualizer:
    def __init__(self, state: State) -> None:
        # self.screen = pygame.display.set_mode((3*N*game_map.width, N*game_map.height))
        self.screen_size = (1000, 1000)
        self.board = state.board
        self.tile_width = min(self.screen_size[0] // self.board.width, self.screen_size[1] // self.board.height)
        self.screen = pygame.display.set_mode((self.tile_width * self.board.width, self.tile_width * self.board.height))
        self.state = state
        pygame.font.init() # you have to call this at the start, 

    def update_scene(self, state: State):
        self.state = state
        for x in range(self.board.width):
            for y in range(self.board.height):
                rubble_color = [255 - self.state.board.rubble[y][x] * 255 / 100] * 3
                # ice_color = [0, 0, self.board.ice[y][x]*255/100]
                # ore_color = [self.board.ore[y][x]*255/100, 0, 0]
                self.screen.fill(
                    rubble_color, (self.tile_width * x, self.tile_width * y, self.tile_width, self.tile_width)
                )
                if self.state.board.ice[y, x] > 0:
                    pygame.draw.rect(
                        self.screen,
                        [10 + self.state.board.ice[y, x] * 5, 130, 250],
                        pygame.Rect(self.tile_width * x, self.tile_width * y, self.tile_width, self.tile_width),
                    )
                if self.state.board.ore[y, x] > 0:
                    pygame.draw.rect(
                        self.screen,
                        [250, self.state.board.ice[y, x] * 5, 100],
                        pygame.Rect(self.tile_width * x, self.tile_width * y, self.tile_width, self.tile_width),
                    )
                # screen.fill(ice_color, (N*x+N*game_map.width, N*y, N, N))
                # screen.fill(ore_color, (N*x+2*N*game_map.width, N*y, N, N))
        if len(state.teams) > 0:
            for agent in state.factories:
                team = state.teams[agent]
                for factory in state.factories[agent].values():
                    x = factory.pos.x
                    y = factory.pos.y
                    pygame.draw.rect(
                        self.screen,
                        color_to_rgb[team.faction.value.color],
                        pygame.Rect(
                            self.tile_width * (x - 1),
                            self.tile_width * (y - 1),
                            self.tile_width * 3,
                            self.tile_width * 3,
                        ),
                        border_radius=int(self.tile_width / 2)
                    )
                    self.sans_font = pygame.font.SysFont('Open Sans', 30)
                    self.screen.blit(self.sans_font.render('F', False, [51,56,68]), (self.tile_width * x, self.tile_width * y))
            for agent in state.units:
                team = state.teams[agent]
                for unit in state.units[agent].values():
                    x = unit.pos.x
                    y = unit.pos.y
                    h=1
                    pygame.draw.rect(
                        self.screen,
                        [51,56,68],
                        
                        pygame.Rect(
                            self.tile_width * (x),
                            self.tile_width * (y),
                            self.tile_width * 1,
                            self.tile_width * 1,
                        ),
                    )
                    pygame.draw.rect(
                        self.screen,
                        color_to_rgb[team.faction.value.color],
                        pygame.Rect(
                            self.tile_width * (x)+h,
                            self.tile_width * (y)+ h,
                            (self.tile_width) * 1 - h * 2,
                            (self.tile_width) * 1 - h * 2,
                        ),
                    )
                    
                    label = "H"
                    if unit.unit_type == UnitType.LIGHT:
                        label = "L"
                    self.sans_font = pygame.font.SysFont('Open Sans', 20)
                    self.screen.blit(self.sans_font.render(label, False, [51,56,68]), (self.tile_width * x+2, self.tile_width * y+2))
    def render(self):
        pygame.display.update()
