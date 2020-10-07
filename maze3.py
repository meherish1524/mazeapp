
from enum import Enum
import random
import pygame as pg
from tkinter import *
import tkinter.messagebox as tkMessageBox
import sqlite3
# Global Settings
SHOW_DRAW = True# Show the maze being created
SHOW_FPS = False  # Show frames per second in caption
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 480
# Maze Size: 30 X 30 is max size for screen of 1200 X 1024
MAZE_WIDTH = 30   # in cells
MAZE_HEIGHT = 20  # in cells
CELL_COUNT = MAZE_WIDTH * MAZE_HEIGHT
BLOCK_SIZE = 5 # Pixel size/Wall thickness
PATH_WIDTH = 3 # Width of pathway in blocks
CELL_SIZE = BLOCK_SIZE * PATH_WIDTH + BLOCK_SIZE   # extra BLOCK_SIZE to include wall to east and south of cell
MAZE_WIDTH_PX = CELL_SIZE * MAZE_WIDTH + BLOCK_SIZE  # extra BLOCK_SIZE to include left edge wall
MAZE_HEIGHT_PX = CELL_SIZE * MAZE_HEIGHT + BLOCK_SIZE   # extra BLOCK_SIZE to include top edge wall
MAZE_TOP_LEFT_CORNER = (SCREEN_WIDTH // 2 - MAZE_WIDTH_PX // 2, SCREEN_HEIGHT // 2 - MAZE_HEIGHT_PX // 2)
# Define the colors we'll need
BACK_COLOR = (0,0,0)
WALL_COLOR = (0,255,0)
DRAW_COLOR= (18,98,32)
#18,98,32
MAZE_COLOR = (255, 255, 255)
UNVISITED_COLOR = (0, 0, 0)
PLAYER1_COLOR = (255, 0, 0)
PLAYER2_COLOR = (0, 0, 255)
MESSAGE_COLOR = (0, 255, 0)




name1=input("enter player1 name :: ")
name2=input("enter player2 name :: ")



class CellProp(Enum):
    Path_N = 1
    Path_E = 2
    Path_S = 4
    Path_W = 8
    Visited = 16


class Direction(Enum):
    North = (0, -1)
    East = (1, 0)
    South = (0, 1)
    West = (-1, 0)


class Player(pg.sprite.Sprite):
    def __init__(self, color, x, y, radius):
	# Call the parent class (Sprite) constructor
        super().__init__()
	# Save the start position
        self.start_x = x
        self.start_y = y
	# Create the rectangular image, fill and set background to transparent
        self.image = pg.Surface([radius * 2, radius * 2])
        self.image.fill(MAZE_COLOR)
        self.image.set_colorkey(MAZE_COLOR)
	# Draw our player onto the transparent rectangle

        pg.draw.circle(self.image, color, (radius, radius), radius)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def reset(self):
        self.rect.x = self.start_x
        self.rect.y = self.start_y


class MazeGenerator:


    direction_to_flag = {
        Direction.North: CellProp.Path_N,
        Direction.East: CellProp.Path_E,
        Direction.South: CellProp.Path_S,
        Direction.West: CellProp.Path_W
    }

    opposite_direction = {
        Direction.North: Direction.South,
        Direction.East: Direction.West,
        Direction.South: Direction.North,
        Direction.West: Direction.East
    }

    def __init__(self):
	# Need to initialize pygame before using it
        pg.init()
	# Create a display surface to draw our game on
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
 	# Set the title on the window

        pg.display.set_caption('MY MAZE GAME')
	# Use a single list to store 2D array

        self.maze = []

        random.seed()
 	# Store maze as image after we create it so that we just have to redraw the image on update

        self.maze_image = None

        # Create players
        self.player1 = Player(PLAYER1_COLOR, MAZE_TOP_LEFT_CORNER[0] + BLOCK_SIZE,
                              MAZE_TOP_LEFT_CORNER[1] + BLOCK_SIZE, (BLOCK_SIZE * 3) // 2)
        self.player1_sprite = None

        self.player2 = Player(PLAYER2_COLOR,
                              MAZE_TOP_LEFT_CORNER[0] + MAZE_WIDTH_PX - CELL_SIZE,
                              MAZE_TOP_LEFT_CORNER[1] + MAZE_HEIGHT_PX - CELL_SIZE,
                              (BLOCK_SIZE * 3) // 2)
        self.player2_sprite = None

        self.player1_score = 0
        self.player2_score = 0

        self.round = 1

        self.win1_flag = False
        self.win2_flag = False

            
    def get_cell_index(self, position):
	# Initialize maze with zero values
        x, y = position
        return y * MAZE_WIDTH + x

    def generate_maze(self):
        self.maze = [0] * CELL_COUNT
        visited_count = 0
	# Start at alternating corners to be more fair

        process_stack = [(0, 0)]
        if self.round % 2 == 0:
            process_stack = [(MAZE_WIDTH - 1, MAZE_HEIGHT - 1)]
            self.maze[CELL_COUNT - 1] |= CellProp.Visited.value
        else:
            process_stack = [(0, 0)]
            self.maze[0] |= CellProp.Visited.value

        visited_count += 1
        while visited_count < CELL_COUNT:
            # Step 1 - Create a list of the unvisited neighbor
            x, y = process_stack[-1] 
            current_cell_index = self.get_cell_index((x, y))
            # Find all unvisited neighbors
            neighbors = []
            for direction in Direction:
                dir = direction.value
                new_x, new_y = (x + dir[0], y + dir[1])
                if 0 <= new_x < MAZE_WIDTH and 0 <= new_y < MAZE_HEIGHT:
                    index = self.get_cell_index((new_x, new_y))
                    if not self.maze[index] & CellProp.Visited.value:
                        # Cell was not already visited so add to neighbors list with the direction
                        neighbors.append((new_x, new_y, direction))

            if len(neighbors) > 0:
                # Choose a random neighboring cell
                cell = neighbors[random.randrange(len(neighbors))]
                cell_x, cell_y, cell_direction = cell
                cell_position = (cell_x, cell_y)
                cell_index = self.get_cell_index(cell_position)
                flag_to = MazeGenerator.direction_to_flag[cell_direction]
                flag_from = MazeGenerator.direction_to_flag[MazeGenerator.opposite_direction[cell_direction]]
                # Create a path between the neighbor and the current cell by setting the direction property flag
                self.maze[current_cell_index] |= flag_to.value
                self.maze[cell_index] |= flag_from.value | CellProp.Visited.value

                process_stack.append(cell_position)
                visited_count += 1
            else:
		# Backtrack since there were no unvisited neighbors
                process_stack.pop()

            if SHOW_DRAW:
                self.draw_maze()
                pg.display.update()
                pg.time.wait(1)
                pg.event.pump()
	# save image of completed maze
        self.draw_maze()
        pg.display.update()
        self.maze_image = self.screen.copy()

    def draw_maze(self):
        self.screen.fill(BACK_COLOR)
        pg.draw.rect(self.screen, WALL_COLOR, (MAZE_TOP_LEFT_CORNER[0], MAZE_TOP_LEFT_CORNER[1],
                                               MAZE_WIDTH_PX, MAZE_HEIGHT_PX))

        for x in range(MAZE_WIDTH):
            for y in range(MAZE_HEIGHT):
                for py in range(PATH_WIDTH):
                    for px in range(PATH_WIDTH):
                        cell_index = self.get_cell_index((x, y))
                        if self.maze[cell_index] & CellProp.Visited.value:
                            self.draw(MAZE_COLOR, x * (PATH_WIDTH + 1) + px, y * (PATH_WIDTH + 1) + py)
                        else:
                            self.draw(UNVISITED_COLOR, x * (PATH_WIDTH + 1) + px, y * (PATH_WIDTH + 1) + py)

                for p in range(PATH_WIDTH):
                    if self.maze[y * MAZE_WIDTH + x] & CellProp.Path_S.value:
                        self.draw(MAZE_COLOR, x * (PATH_WIDTH + 1) + p, y * (PATH_WIDTH + 1) + PATH_WIDTH)

                    if self.maze[y * MAZE_WIDTH + x] & CellProp.Path_E.value:
                        self.draw(MAZE_COLOR, x * (PATH_WIDTH + 1) + PATH_WIDTH, y * (PATH_WIDTH + 1) + p)
	# Color the player exits
        pg.draw.rect(self.screen, PLAYER2_COLOR, (MAZE_TOP_LEFT_CORNER[0],
                     MAZE_TOP_LEFT_CORNER[1] + BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE * 3))

        pg.draw.rect(self.screen, PLAYER1_COLOR,
                     (MAZE_TOP_LEFT_CORNER[0] + MAZE_WIDTH_PX - BLOCK_SIZE,
                      MAZE_TOP_LEFT_CORNER[1] + MAZE_HEIGHT_PX - BLOCK_SIZE * 4,
                      BLOCK_SIZE, BLOCK_SIZE * 3))

    def draw(self, color, x, y):
        x_offset = MAZE_TOP_LEFT_CORNER[0] + BLOCK_SIZE
        y_offset = MAZE_TOP_LEFT_CORNER[1] + BLOCK_SIZE
        pg.draw.rect(self.screen, color, (x * BLOCK_SIZE + x_offset,
                                          y * BLOCK_SIZE + y_offset,
                                          BLOCK_SIZE, BLOCK_SIZE))

    def draw_screen(self):
        self.screen.blit(self.maze_image, (0, 0))
        self.player1_sprite.draw(self.screen)
        self.player2_sprite.draw(self.screen)
	# Display Scores
        font = pg.font.SysFont('Arial', 18, True)
        p3_msg=name1
        p4_msg=name2
        p1_msg = f'PLAYER 1: {self.player1_score}'
        p2_msg = f'PLAYER 2: {self.player2_score}'
        p1_size = font.size(p1_msg)
        p2_size = font.size(p2_msg)
        p3_size = font.size(p3_msg)
        p4_size = font.size(p4_msg)
        p1 = font.render(p1_msg, True, PLAYER1_COLOR)
        p2 = font.render(p2_msg, True, PLAYER2_COLOR)
        p3 = font.render(p3_msg, True, PLAYER1_COLOR)
        p4 = font.render(p4_msg, True, PLAYER2_COLOR)
        self.screen.blit(p1, (MAZE_TOP_LEFT_CORNER[0], MAZE_TOP_LEFT_CORNER[1] - p1_size[1] ))
        self.screen.blit(p2, (MAZE_TOP_LEFT_CORNER[0] + MAZE_WIDTH_PX - p2_size[0] -p4_size[1],
                              MAZE_TOP_LEFT_CORNER[1] - p1_size[1] ))
        
        
	# Display instructions
        p1_msg = 'a w s d to move'
        p2_msg = '← ↑ ↓ → to move'
        p2_size = font.size(p2_msg)
        p1 = font.render(p1_msg, True, PLAYER1_COLOR)
        p2 = font.render(p2_msg, True, PLAYER2_COLOR)
        self.screen.blit(p1, (MAZE_TOP_LEFT_CORNER[0], MAZE_TOP_LEFT_CORNER[1] + MAZE_HEIGHT_PX + 2))
        self.screen.blit(p2, (MAZE_TOP_LEFT_CORNER[0] + MAZE_WIDTH_PX - p2_size[0],
                              MAZE_TOP_LEFT_CORNER[1] + MAZE_HEIGHT_PX + 2))

        pg.display.update()

    def display_win(self):
        msg = name1+' Wins!!!' if self.win1_flag else name2+' Wins!!!'

        self.round += 1
        if self.win1_flag:
            self.player1_score += 1
        else:
            self.player2_score += 1

        font = pg.font.SysFont('Arial', 72, True)
        size = font.size(msg)
        s = font.render(msg, True, MESSAGE_COLOR, (0, 0, 0))
        self.screen.blit(s, (SCREEN_WIDTH // 2 - size[0] // 2, SCREEN_HEIGHT // 2 - size[1] // 2))
        pg.display.update()
        pg.time.wait(1000)

    def can_move(self, direction, player):
	# Top left corner of first cell
        corner_offset_x = MAZE_TOP_LEFT_CORNER[0] + BLOCK_SIZE
        corner_offset_y = MAZE_TOP_LEFT_CORNER[1] + BLOCK_SIZE
	# Calculate which cells the player occupies
        square = BLOCK_SIZE * 4
        p1 = (player.rect.x - corner_offset_x, player.rect.y - corner_offset_y)
        p2 = (p1[0] + square - 1, p1[1] + square - 1)
        player_pos1 = (p1[0] // square, p1[1] // square)
        player_pos2 = (p2[0] // square, p2[1] // square)
        cell_index1 = self.get_cell_index((player_pos1[0], player_pos1[1]))
        cell_index2 = self.get_cell_index((player_pos2[0], player_pos2[1]))

        functions = {
            Direction.North: self.can_move_up,
            Direction.East: self.can_move_right,
            Direction.South: self.can_move_down,
            Direction.West: self.can_move_left
        }
	# Check for maze exit/win
        # Check if player is at opposing player's start x,y
        if self.player1.rect.x == self.player2.start_x and self.player1.rect.y == self.player2.start_y:
            self.win1_flag = True
        elif self.player2.rect.x == self.player1.start_x and self.player2.rect.y == self.player1.start_y:
            self.win2_flag = True

        return functions[direction](cell_index1, cell_index2)

    def can_move_up(self, index1, index2):
        if index1 == index2:
            return self.maze[index1] & CellProp.Path_N.value
        else:
            return index2 == index1 + MAZE_WIDTH

    def can_move_right(self, index1, index2):
        if index1 == index2:
            return self.maze[index1] & CellProp.Path_E.value
        else:
            return index2 == index1 + 1

    def can_move_down(self, index1, index2):
        if index1 == index2:
            return self.maze[index1] & CellProp.Path_S.value
        else:
            return index2 == index1 + MAZE_WIDTH

    def can_move_left(self, index1, index2):
        if index1 == index2:
            return self.maze[index1] & CellProp.Path_W.value
        else:
            return index2 == index1 + 1

    def move_up(self, player):
        if self.can_move(Direction.North, player):
            player.rect.y -= 1

    def move_right(self, player):
        if self.can_move(Direction.East, player):
            player.rect.x += 1

    def move_down(self, player):
        if self.can_move(Direction.South, player):
            player.rect.y += 1

    def move_left(self, player):
        if self.can_move(Direction.West, player):
            player.rect.x -= 1

    def initialize(self):
        self.player1_sprite = None
        self.player1.reset()
        self.player2_sprite = None
        self.player2.reset()

        self.generate_maze()
        self.player1_sprite = pg.sprite.RenderPlain(self.player1)
        self.player2_sprite = pg.sprite.RenderPlain(self.player2)

    def run_game(self):
        clock = pg.time.Clock()
        self.initialize()
        run = True
        while run:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    run = False
		# Main game loop

            if not self.win1_flag and not self.win2_flag:
                keys = pg.key.get_pressed()
                if keys[pg.K_LEFT]:
                    self.move_left(self.player2)
                if keys[pg.K_RIGHT]:
                    self.move_right(self.player2)
                if keys[pg.K_UP]:
                    self.move_up(self.player2)
                if keys[pg.K_DOWN]:
                    self.move_down(self.player2)
                if keys[pg.K_a]:
                    self.move_left(self.player1)
                if keys[pg.K_d]:
                    self.move_right(self.player1)
                if keys[pg.K_w]:
                    self.move_up(self.player1)
                if keys[pg.K_s]:
                    self.move_down(self.player1)

                if self.win1_flag or self.win2_flag:
                    self.display_win()
                    self.initialize()
                    self.win1_flag = self.win2_flag = False

                self.draw_screen()

                if SHOW_FPS:
                    pg.display.set_caption(f'PyMaze ({str(int(clock.get_fps()))} FPS)')
                    clock.tick()

        pg.quit()



root = Tk()
root.title("login for mymaze")
 
width = 640
height = 480
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width/2) - (width/2)
y = (screen_height/2) - (height/2)
root.geometry("%dx%d+%d+%d" % (width, height, x, y))
root.resizable(0, 0)


#=======================================VARIABLES=====================================
USERNAME = StringVar()
PASSWORD = StringVar()
FIRSTNAME = StringVar()
LASTNAME = StringVar()


def Database():
    global conn, cursor
    conn = sqlite3.connect("db_member.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS `member` (mem_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT, password TEXT, firstname TEXT, lastname TEXT)")


def Exit():
    result = tkMessageBox.askquestion('System', 'Are you sure you want to exit?', icon="warning")
    if result == 'yes':
        root.destroy()
        exit()
def LoginForm():
    global LoginFrame, lbl_result1
    LoginFrame = Frame(root)
    LoginFrame.pack(side=TOP, pady=80)
    lbl_username = Label(LoginFrame, text="Username:", font=('arial', 25), bd=18)
    lbl_username.grid(row=1)
    lbl_password = Label(LoginFrame, text="Password:", font=('arial', 25), bd=18)
    lbl_password.grid(row=2)
    lbl_result1 = Label(LoginFrame, text="", font=('arial', 18))
    lbl_result1.grid(row=3, columnspan=2)
    username = Entry(LoginFrame, font=('arial', 20), textvariable=USERNAME, width=15)
    username.grid(row=1, column=1)
    password = Entry(LoginFrame, font=('arial', 20), textvariable=PASSWORD, width=15, show="*")
    password.grid(row=2, column=1)
    btn_login = Button(LoginFrame, text="Login", font=('arial', 18), width=35, command=Login)
    btn_login.grid(row=4, columnspan=2, pady=20)
    lbl_register = Label(LoginFrame, text="Register", fg="Blue", font=('arial', 12))
    lbl_register.grid(row=0, sticky=W)
    lbl_register.bind('<Button-1>', ToggleToRegister)

def RegisterForm():
    global RegisterFrame, lbl_result2
    RegisterFrame = Frame(root)
    RegisterFrame.pack(side=TOP, pady=40)
    lbl_username = Label(RegisterFrame, text="Username:", font=('arial', 18), bd=18)
    lbl_username.grid(row=1)
    lbl_password = Label(RegisterFrame, text="Password:", font=('arial', 18), bd=18)
    lbl_password.grid(row=2)
    lbl_firstname = Label(RegisterFrame, text="Firstname:", font=('arial', 18), bd=18)
    lbl_firstname.grid(row=3)
    lbl_lastname = Label(RegisterFrame, text="Lastname:", font=('arial', 18), bd=18)
    lbl_lastname.grid(row=4)
    lbl_result2 = Label(RegisterFrame, text="", font=('arial', 18))
    lbl_result2.grid(row=5, columnspan=2)
    username = Entry(RegisterFrame, font=('arial', 20), textvariable=USERNAME, width=15)
    username.grid(row=1, column=1)
    password = Entry(RegisterFrame, font=('arial', 20), textvariable=PASSWORD, width=15, show="*")
    password.grid(row=2, column=1)
    firstname = Entry(RegisterFrame, font=('arial', 20), textvariable=FIRSTNAME, width=15)
    firstname.grid(row=3, column=1)
    lastname = Entry(RegisterFrame, font=('arial', 20), textvariable=LASTNAME, width=15)
    lastname.grid(row=4, column=1)
    btn_login = Button(RegisterFrame, text="Register", font=('arial', 18), width=35, command=Register)
    btn_login.grid(row=6, columnspan=2, pady=20)
    lbl_login = Label(RegisterFrame, text="Login", fg="Blue", font=('arial', 12))
    lbl_login.grid(row=0, sticky=W)
    lbl_login.bind('<Button-1>', ToggleToLogin)

def ToggleToLogin(event=None):
    RegisterFrame.destroy()
    LoginForm()

def ToggleToRegister(event=None):
    LoginFrame.destroy()
    RegisterForm()

def Register():
    Database()
    if USERNAME.get == "" or PASSWORD.get() == "" or FIRSTNAME.get() == "" or LASTNAME.get == "":
        lbl_result2.config(text="Please complete the required field!", fg="orange")
    else:
        cursor.execute("SELECT * FROM `member` WHERE `username` = ?", (USERNAME.get(),))
        if cursor.fetchone() is not None:
            lbl_result2.config(text="Username is already taken", fg="red")
        else:
            cursor.execute("INSERT INTO `member` (username, password, firstname, lastname) VALUES(?, ?, ?, ?)", (str(USERNAME.get()), str(PASSWORD.get()), str(FIRSTNAME.get()), str(LASTNAME.get())))
            conn.commit()
            USERNAME.set("")
            PASSWORD.set("")
            FIRSTNAME.set("")
            LASTNAME.set("")
            lbl_result2.config(text="Successfully Created!", fg="black")
        cursor.close()
        conn.close()
def Login():
    Database()
    if USERNAME.get == "" or PASSWORD.get() == "":
        lbl_result1.config(text="Please complete the required field!", fg="orange")
    else:
        cursor.execute("SELECT * FROM `member` WHERE `username` = ? and `password` = ?", (USERNAME.get(), PASSWORD.get()))
        if cursor.fetchone() is not None:
            lbl_result1.config(text="You Successfully Login", fg="blue")
            root.destroy()
            r=random.randint(1,5)
            pg.init()
            if(r==1):
                pg.mixer.music.load('maze1.mp3')
                pg.mixer.music.play(-1)
            if(r==2):
                pg.mixer.music.load('maze2.mp3')
                pg.mixer.music.play(-1)
            if(r==3):
                pg.mixer.music.load('maze3.mp3')
                pg.mixer.music.play(-1)
            if(r==4):
                pg.mixer.music.load('maze4.mp3')
                pg.mixer.music.play(-1)
            if(r==5):
                pg.mixer.music.load('maze5.mp3')
                pg.mixer.music.play(-1)
            mg = MazeGenerator()
            mg.run_game()
        else:
            lbl_result1.config(text="Invalid Username or password", fg="red")
LoginForm()


menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Exit", command=Exit)
menubar.add_cascade(label="File", menu=filemenu)
root.config(menu=menubar)


if __name__ == '__main__':
    root.mainloop()
   








