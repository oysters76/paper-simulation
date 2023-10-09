import pygame  
import random
import copy
import math 

width  = 1000; 
height = 1000; 
bgColor = "white"; 
ROCK    = 0; 
PAPER   = 1; 
SCISSOR = 2; 
images = []; # contains images for rock/paper/scissior - emojis
pathnames = ["rock.png", "paper.png", "scissor.png"]; 
img_rect_size = 30
img_size = (img_rect_size,img_rect_size) 
objects = [] 
margin = 50

rock_count = 25 
scissor_count = 25 
paper_count = 25
sim_speed = 1

#rock smash scissor
#paper cover rock
#scissor cut paper
rules = [SCISSOR, ROCK, PAPER]

#Position of indexes in a single object array
X_POS    = 0 
Y_POS    = 1 
SURFACE  = 2 
I_TYPE   = 3 

# holds all currently available particle systems 
particle_systems = [] 

#sounds 
collide_sound = None;

# Particle system that emits particles when two objects collide with different types
class ParticleSystem:

    P_POS = 0 #position index
    P_RAD = 1 #radius index
    P_DIR = 2 #direction index

    def __init__(self, p_surface, p_color, p_shrink_rate, p_max_radius, p_origin, p_size):
        self.particles = [] 
        self.surface = p_surface 
        self.color = p_color 
        self.shrinkrate = p_shrink_rate 
        self.mradius = p_max_radius
        self.origin = p_origin
        self.size = p_size # amount of particles to be generated 

        for i in range(self.size):
            self.create() 
    
    # creates particles to be emitted with random x,y & other properties (radius) 
    def create(self):
        x_pos, y_pos = self.origin
        radius = random.randint(5, self.mradius) 
        dir_x = random.randint(-3, 3) 
        dir_y = random.randint(-3, 3) 

        particle = [(x_pos, y_pos), radius, (dir_x, dir_y)]
        self.particles.append(particle) 

    
    # emits created particles on to screen
    def emit(self):
        self.delete() #deletes particles first before drawing them 
        for p in self.particles:
            x, y = p[ParticleSystem.P_POS]
            dx, dy = p[ParticleSystem.P_DIR] 
            x += dx 
            y += dy 
            p[ParticleSystem.P_POS] = (x,y) 
            p[ParticleSystem.P_RAD] -= self.shrinkrate
            
            pygame.draw.circle(self.surface, self.color, p[ParticleSystem.P_POS], p[ParticleSystem.P_RAD], 0)

    def delete(self):
        self.particles = [p for p in self.particles if p[ParticleSystem.P_RAD] > 0] # deletes all particles if their radius reaches zero 
    
    def can_delete(self):
        return len(self.particles) == 0 

# Adds a particle system to the display
def add_psystem(p_surface, p_color, p_shrink_rate, p_max_radius, p_origin, p_size):
    p = ParticleSystem(p_surface, p_color, p_shrink_rate, p_max_radius, p_origin, p_size) 
    particle_systems.append(p)

def emit_psystems(psystems):
    for ps in psystems:
        ps.emit()

def clean_psystems(psystems):
    return [ps for ps in psystems if not ps.can_delete()] # delete particle systems if not in use, if particle list is empty 

#Gets a list of all the objects with their inital position 
def init_objects_pos(rocksize, ssize, papersize, images, width,height):
    objects = [] 
    total_objects = rocksize + ssize + papersize; 
    item = [] 
    for i in range(total_objects): 
        item = [random.randint(margin, width-margin), random.randint(margin, height-margin)] 
        item_index = -1 
        if ((i - rocksize) >= 0):
            if ((i - (rocksize+ssize)) >= 0):
                item_index = PAPER 
            else:
                item_index = SCISSOR 
        else:
            item_index = ROCK 
        
        item.append(images[item_index].copy()) 
        item.append(item_index) 
        objects.append(item) 
    
    return objects

# draws bounding rects (red rects) around objects for visualizing collision 
def draw_bounding_rects(scrn, objects, rect_color):
    for i, obj in enumerate(objects):
        left,top = obj[X_POS], obj[Y_POS]; 
        rect = pygame.Rect(left, top, img_rect_size, img_rect_size);
        pygame.draw.rect(scrn, rect_color, rect, 1);

def init_sounds():
    pygame.mixer.init();
    global collide_sound
    collide_sound = pygame.mixer.Sound("collide.wav") 

def init_images():
    for path in pathnames:
        _img = pygame.image.load(path);
        _img = pygame.transform.scale(_img, img_size);
        images.append(_img); 

def init_window():
    init_images();
    init_sounds()
    return init_objects_pos(rock_count, scissor_count, paper_count, images, width, height); 
     

def draw_objects(scrn, objects):
    for i, obj in enumerate(objects):
       scrn.blit(obj[2], (obj[0], obj[1])) 

def is_equal(obj, other_obj):
    return obj[0] == other_obj[0] and obj[1] == other_obj[1] 

def is_point_inside(tx, ty, p):

    return (p >= tx and p <= (tx+img_rect_size)) or (p >= ty and p <= (ty+img_rect_size))  


X  = 0 
XW = 1 
Y  = 2 
YW = 3
def get_points(tx, ty, w):
    return [tx, tx+w, ty, ty+w] 

def is_collide(target, obj):
    tx, ty = target[X_POS], target[Y_POS] 
    ox, oy = obj[X_POS], obj[Y_POS] 

    rect1 = get_points(ox,oy,img_rect_size);  
    rect2 = get_points(tx,ty,img_rect_size);
        
    return rect1[X] < rect2[XW] and rect1[XW] > rect2[X] and rect1[Y] < rect2[YW] and rect1[YW] > rect2[Y]   

# returns index positions of objects that collide with target object
def check_collision(target, objects):
    collisions = [] 
    for i, obj in enumerate(objects):
        if is_equal(target, obj):
            continue
        if (is_collide(target, obj)):
            collisions.append(i);  

    return collisions 
        
def get_distance(o1, o2):
    o1_x, o1_y = o1[X_POS], o1[Y_POS] 
    o2_x, o2_y = o2[X_POS], o2[Y_POS] 

    return math.dist((o1_x, o1_y), (o2_x, o2_y)) 

# finds the closest object which has the opposite type to the passed 'obj', if not found returns -1
def find_closest_opp_type(obj, objects):
    opp_type = rules[obj[I_TYPE]] 
    i_min = -1 
    min_dist = math.inf  
    for i, o in enumerate(objects):
        if is_equal(obj, o):
            continue 
        if opp_type != o[I_TYPE]:
            continue 
        d = get_distance(o, obj) 
        if (d < min_dist):
            i_min = i 
            min_dist = d 
    return i_min 

# gets the direction vector from obj to the closest opposite type object 
def get_dir_vector_from(obj, c_obj):
    o_x, o_y     = obj[X_POS], obj[Y_POS] 
    opp_x, opp_y = c_obj[X_POS], c_obj[Y_POS] 
    dir_x = opp_x - o_x
    dir_y = opp_y - o_y

    return [dir_x, dir_y] 

def get_unit_vec(vec):
    total = 0
    for v in vec:
        total += (v ** 2) 
    mod = math.sqrt(total) + 0.005 
    return [vec[X_POS]/mod, vec[Y_POS]/mod]  


# moves the obj in the direction of the opposite type object
def move_in_dir(obj, d_vect, speed):
    unit_vec = get_unit_vec(d_vect) 
    o_x, o_y = obj[X_POS], obj[Y_POS] 
    o_x += (speed*unit_vec[X_POS])
    o_y += (speed*unit_vec[Y_POS]) 

    return [o_x, o_y] 

# moves the object some direction or the object stays still
def move_in_direction(obj, objects):
    closest_opp_ind = find_closest_opp_type(obj, objects) 
    if closest_opp_ind == -1:
        return create_new_obj(obj)

    closest_opp_type = objects[closest_opp_ind]
    
    d_vect = get_dir_vector_from(obj,closest_opp_type)
    n_vect = move_in_dir(obj, d_vect, sim_speed);  
    new_obj = create_new_obj(obj) 
    new_obj[X_POS] = n_vect[X_POS] 
    new_obj[Y_POS] = n_vect[Y_POS] 

    return new_obj 

def make_obj(obj, obj_type):
    return [obj[X_POS], obj[Y_POS], images[obj_type].copy(), obj_type]; 


'''
Logging functions
'''
def get_type_str(o):
    t = o[I_TYPE] 
    if t == ROCK:
        return "Rock"
    if t == SCISSOR:
        return "Scissor" 
    if t == PAPER:
        return "Paper" 
    return ""

def log_collision(obj, collision, objects):
    o = objects[obj] 
    c = objects[collision]
    print(get_type_str(o), "is colliding with ", get_type_str(c)) 

'''
obj, and collision ind, and objects array

returns: whether obj won, the changed obj, whether it is a draw
'''
def change_type(obj, collision, objects):
    collide_obj = objects[collision] 
    collide_obj_type = collide_obj[I_TYPE] 
    obj_type = obj[I_TYPE] 

    does_obj_win = rules[obj_type] == collide_obj_type 
    does_coll_win = rules[collide_obj_type] == obj_type 

    if (does_obj_win):
        return (True, make_obj(collide_obj, obj_type), False) 
    if (does_coll_win):
        return (False, make_obj(obj, collide_obj_type), False)

    # if draw then (same types) 
    return (False,create_new_obj(obj),True)

def create_new_obj(obj):
    return [obj[X_POS], obj[Y_POS], obj[SURFACE].copy(), obj[I_TYPE]]  


def is_same_type(obj, target, objects):
    return objects[obj][I_TYPE] == objects[target][I_TYPE] 

def get_collision_origin(obj, collision,w, objects):
    o, c = objects[obj], objects[collision] 
    ox, oy = o[X_POS], o[Y_POS] 
    cx, cy = c[X_POS], c[Y_POS] 

    middle = [ox+cx, oy+cy] 
    return (middle[0]/2, middle[1]/2)

def get_rand_color():
    return (random.randint(0,255), random.randint(0,255), random.randint(0,255)) 

'''
 Loop through each object from the list 
 for each object in the list do 
    1. check collision, if collision check type, if type is in the 
       rules, the object that is in collision should change type to the 
       current object's type 
    2. move in direction of nearest object with opposite type 
        e.g. rock move in direction of scissor by a constant amount delta 
 once positions,images & types are updated return object array with updated values for rendering to scrn

'''
def simulate(dsp, objects):
    changes = objects; 
    did_change = [False] * len(objects)  
    
    did_collid = False 
    if (collide_sound):
        collide_sound.stop() 

    for i, obj in enumerate(objects):
              
        changes[i] = move_in_direction(obj, objects) 
        
        if did_collid:
            continue
        
        for j, collision in enumerate(check_collision(obj, objects)):
            obj_won, changed_obj, is_draw = change_type(obj, collision, objects)
            if (is_draw):
                continue 
            if obj_won:
                changes[collision] = changed_obj 
            if not obj_won:
                changes[i] = changed_obj
            did_collid = True
            add_psystem(dsp,get_rand_color(), 1, random.randint(10,20), get_collision_origin(i,collision,img_rect_size,objects),
                    random.randint(50,100));
            collide_sound.play(); 

    return changes

def draw(scrn):
    draw_objects(scrn, objects); 
    return simulate(scrn,objects)
    
def print_obj_types(objects):
    tarray = [] 
    for obj in objects:
        if (len(obj) < I_TYPE):
            tarray.append(-1) 
            continue 
        tarray.append(obj[I_TYPE]) 
    print(tarray)

# if all objects are of a same type then the simulation has stopped
def has_simulation_stop(objects):
    t = objects[0][I_TYPE] 
    for obj in objects:
        if t != obj[I_TYPE]:
            return False 
    return True 

pygame.init();
objects = init_window();
screen = pygame.display.set_mode((width, height)); 
clock = pygame.time.Clock(); 

pygame.font.init() 
header_font = pygame.font.Font("customfont.ttf", size=70) 
sub_font = pygame.font.Font("customfont.ttf", size=50) 

player1, player2 = -1, -1 

def draw_option(surface, opt, coords):
    x, y = coords
    img = pygame.image.load(pathnames[opt]) 
    img = pygame.transform.scale(img, (150,150)); 
    screen.blit(img, (x,y))
    return pygame.Rect(x, y, 150, 150)

def draw_selection_boxes(surface, possible_options, gap=(150+50)):
    sel_rects = [] 
    for i, opt in enumerate(possible_options):
        sel_rects.append([draw_option(surface, opt, (200+(i*gap), 400)), opt]);
    return sel_rects

def intro_screen():
    pygame.display.set_caption("Choose!") 
    player1, player2 = -1,-1
    running = True 
    game_text = header_font.render("ROCK - PAPER - SCISSORS!", False, (0,0,0), None) 
    player1_text = sub_font.render("Player 1 Choose!", False, (0,0,0), None) 
    player2_text = sub_font.render("Player 2 Choose!", False, (0,0,0), None) 
    
    player1_done = False 
    possible_options = [ROCK, PAPER, SCISSOR] 
    sel_rects = [] 

    while running:

        if player1 != -1 and player2 != -1:
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False 
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x,y = pygame.mouse.get_pos() 
                sel_opt = -1
                for rect in sel_rects:
                    if (rect[0].collidepoint(x,y)):
                        sel_opt = rect[1]
                        break; 
                if (sel_opt != -1):
                    if (not player1_done):
                        player1 = sel_opt 
                        player1_done = True 
                    else:
                        player2 = sel_opt 



            
        screen.fill(bgColor)
        screen.blit(game_text, (100, 100))
        
        text = None
        if (not player1_done):
            text = player1_text 
        else:
            possible_options = [opt for opt in possible_options if opt != player1];
            text = player2_text 
        
        screen.blit(text, (width/2-200, 200))
        sel_rects = draw_selection_boxes(screen, possible_options); 
        pygame.display.flip()   
        clock.tick(60)

    return player1, player2


def game_loop(objects,pl1, pl2):
    pygame.display.set_caption("The simulation!")
    running = True
    did_player1_won, did_player2_won, is_draw = False, False, False 
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False 
    
        screen.fill(bgColor) 
        clean_psystems(particle_systems)  
        objects = draw(screen);
        emit_psystems(particle_systems)

        if has_simulation_stop(objects):
            win_type = objects[0][I_TYPE] 
            did_player1_won = pl1 == win_type 
            did_player2_won = pl2 == win_type 

            is_draw = (not did_player1_won) and (not did_player2_won) 

            running = False 

        pygame.display.flip(); 
        clock.tick(60);
    return did_player1_won, did_player2_won, is_draw

def end_screen(player1, player2, is_draw): 
    pygame.display.set_caption("Game Over!")
    text = ""
    if (player1 or player2):
        if (player1):
            text = "Player 1" 
        else:
            text = "Player 2" 
        text = text + " Won! :)"
    else:
        text = "Its but a draw! :(" 
    
    result_text = header_font.render(text, False, (0,0,0), None) 
    
    play_again_text = sub_font.render("Play Again?", False, (0,0,0), None)
    play_again_width, play_again_height = play_again_text.get_width(), play_again_text.get_height()
    play_again_rect = pygame.Rect(150, 300, play_again_width, play_again_height) 
    
    quit_text = sub_font.render("Quit?", False, (0,0,0), None) 
    quit_text_width, quit_text_height = quit_text.get_width(), quit_text.get_height() 
    quit_text_rect = pygame.Rect(450, 300, quit_text_width, quit_text_height)

    running = True 
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                x,y = pygame.mouse.get_pos() 
                if play_again_rect.collidepoint(x,y):
                    running = False 
                    return True 
                if quit_text_rect.collidepoint(x,y):
                    running = False 
                    return False 
        
        screen.fill(bgColor)
        screen.blit(result_text, (100, 100)) 
        screen.blit(play_again_text, (150, 300))
        screen.blit(quit_text, (450, 300)) 
        pygame.display.flip() 
        clock.tick(60);
    return False 

can_run = True
while can_run:
    objects = init_objects_pos(rock_count, scissor_count, paper_count, images, width, height)
    player1, player2 = intro_screen()
    is_player1, is_player2, is_draw = game_loop(objects,player1, player2)
    can_run = end_screen(is_player1, is_player2, is_draw); 

pygame.font.quit() 
pygame.quit(); 




