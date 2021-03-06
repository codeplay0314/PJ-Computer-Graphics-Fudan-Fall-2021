import sys
import random
from PIL import Image
from module.AudioAnalyzer import *
from configparser import ConfigParser

config = ConfigParser()
config.read(sys.argv[1], encoding = 'UTF-8')

filename = config["files"]["music_file"]
albumcover = config["files"]["album_cover"]

def avg_rpg():
    im = Image.open(albumcover)
    pix = im.load()
    width = im.size[0]
    height = im.size[1]
    r, b, g = [0, 0, 0]
    for x in range(width):
        for y in range(height):
            p1, p2, p3 = pix[x, y]
            r += p1
            b += p2
            g += p3
    r /= x * y
    b /= x * y
    g /= x * y
    return [r, b, g]

analyzer = AudioAnalyzer()
analyzer.load(filename)

pygame.init()

# Set up window size
infoObject = pygame.display.Info()
screen_w = int(infoObject.current_h)
screen_h = int(infoObject.current_h)

# Set up the drawing window
screen = pygame.display.set_mode([screen_w, screen_h])
t = pygame.time.get_ticks()
getTicksLastFrame = t

cover_l = 200
cover = pygame.image.load(albumcover)
cover = pygame.transform.smoothscale(cover, [cover_l, cover_l])
cover_pos = cover.get_rect()
cover_pos = cover_pos.move((screen_w - cover_pos.width) / 2, (screen_h - cover_pos.height) / 2)

# Set up parameters
timeCount = 0

avg_bass = 0
bass_trigger = -30
bass_trigger_started = 0

min_decibel = -80
max_decibel = 80

circle_color = [255, 255, 255]
polygon_default_color = avg_rpg()
polygon_bass_color = polygon_default_color.copy()
polygon_color_vel = [0, 0, 0]

poly = []
poly_color = polygon_default_color.copy()

circleX = int(screen_w / 2)
circleY = int(screen_h / 2)

min_radius = 200
max_radius = 250
radius = min_radius
radius_vel = 0


bass = {"start": 30, "stop": 150, "count": 12}
heavy_area = {"start": 150, "stop": 500, "count": 40}
low_mids = {"start": 500, "stop": 5000, "count": 50}

freq_groups = [bass, heavy_area, low_mids]

bars = []
tmp_bars = []

length = 0

for group in freq_groups:
    g = []
    s = group["stop"] - group["start"]
    count = group["count"]
    reminder = s % count
    step = int(s / count)
    rng = group["start"]
    for i in range(count):
        arr = None
        if reminder > 0:
            reminder -= 1
            arr = np.arange(start = rng, stop = rng + step + 1)
            rng += step + 1
        else:
            arr = np.arange(start = rng, stop = rng + step)
            rng += step
        g.append(arr)
        length += 1
    tmp_bars.append(g)


angle_dt = 360 / length
ang = 0

w = cover_l * 4 / length
steps = [[w, 0] for i in range(length // 4 + 1)]
steps.extend([[0, w] for i in range(length // 4 + 1)])
steps.extend([[-w, 0] for i in range(length // 4 + 1)])
steps.extend([[0, -w] for i in range (length // 4 + 1)])
x, y = (screen_w - cover_pos.width) / 2, (screen_h - cover_pos.height) / 2
steps[0][0] += x
steps[0][1] += y
for i in range(1, len(steps)):
    steps[i][0] += steps[i - 1][0]
    steps[i][1] += steps[i - 1][1]
random.shuffle(steps)

for g in tmp_bars:
    gr = []
    for c in g:
        gr.append(RotatedAverageAudioBar(0, 0, c, (0, 0, 0), angle = ang, width = 8, max_height = 400))
        ang += angle_dt
    bars.append(gr)


pygame.mixer.music.load(filename)
pygame.mixer.music.play(0)

running = True
while running:
    avg_bass = 0
    poly = []

    # ticks
    t = pygame.time.get_ticks()
    deltaTime = (t - getTicksLastFrame) / 1000.0
    getTicksLastFrame = t

    timeCount += deltaTime

    screen.fill(circle_color)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for b1 in bars:
        for b in b1:
            b.update_all(deltaTime, pygame.mixer.music.get_pos() / 1000.0, analyzer)

    for b in bars[0]:
        avg_bass += b.avg

    avg_bass /= len(bars[0])

    if avg_bass > bass_trigger:
        if bass_trigger_started == 0:
            bass_trigger_started = pygame.time.get_ticks()
        if (pygame.time.get_ticks() - bass_trigger_started) / 1000.0 > 2:
            polygon_bass_color = avg_rpg()
            bass_trigger_started = 0
        if polygon_bass_color is None:
            polygon_bass_color = avg_rpg()
        newr = min_radius + int(avg_bass * ((max_radius - min_radius) / (max_decibel - min_decibel)) + (max_radius - min_radius))
        radius_vel = (newr - radius) / 0.15
        polygon_color_vel = [(polygon_bass_color[x] - poly_color[x]) / 0.15 for x in range(len(poly_color))]

    elif radius > min_radius:
        bass_trigger_started = 0
        polygon_bass_color = None
        radius_vel = (min_radius - radius) / 0.15
        polygon_color_vel = [(polygon_default_color[x] - poly_color[x]) / 0.15 for x in range(len(poly_color))]

    else:
        bass_trigger_started = 0
        poly_color = polygon_default_color.copy()
        polygon_bass_color = None
        polygon_color_vel = [0, 0, 0]

        radius_vel = 0
        radius = min_radius

    radius += radius_vel * deltaTime

    for x in range(len(polygon_color_vel)):
        value = polygon_color_vel[x] * deltaTime + poly_color[x]
        poly_color[x] = value


    i = 0
    for b1 in bars:
        for b in b1:
            b.x, b.y = steps[i]
            i += 1
            b.update_rect()
            poly.append(b.rect.points[3])
            poly.append(b.rect.points[2])

    pygame.draw.polygon(screen, poly_color, poly)
    screen.blit(cover, cover_pos)
    # pygame.draw.circle(screen, circle_color, (circleX, circleY), int(radius))

    pygame.display.flip()

pygame.quit()
