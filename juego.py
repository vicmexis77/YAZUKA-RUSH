import math
import random
import sys
import pygame

# Inicialización de Pygame y Sonido
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Configuración de la ventana y el mundo
ANCHO, ALTO = 800, 600
ANCHO_MUNDO = 2400
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Test de Juego - Katana vs Horde Zombie")

# Reloj para control de FPS
reloj = pygame.time.Clock()
fuente_hud = pygame.font.SysFont("Arial", 20, bold=True)
fuente_puerta = pygame.font.SysFont("Arial", 24, bold=True)

# --- REPRODUCCIÓN DE MÚSICA EN BUCLE ---
pygame.mixer.music.load("Rain.mp3")
pygame.mixer.music.play(-1)

# --- CARGA DE IMÁGENES DEL MENÚ ---
menu_imagenes = [
    pygame.transform.scale(
        pygame.image.load("MENU 1.jfif").convert(), (ANCHO, ALTO)
    ),
    pygame.transform.scale(
        pygame.image.load("MENU 2.jfif").convert(), (ANCHO, ALTO)
    ),
    pygame.transform.scale(
        pygame.image.load("MENU 3.jfif").convert(), (ANCHO, ALTO)
    ),
]
opcion_menu = 0  # 0: Jugar, 1: Opciones, 2: Salir
estado_juego = "MENU"  # "MENU" o "JUGANDO"

# --- CARGA DE FONDOS POR NIVEL ---
fondo1_on = pygame.transform.scale(
    pygame.image.load("fondo.jpg").convert(), (ANCHO_MUNDO, ALTO)
)
fondo1_off = pygame.transform.scale(
    pygame.image.load("fondo apagado.jpg").convert(), (ANCHO_MUNDO, ALTO)
)

fondo2_on = pygame.transform.scale(
    pygame.image.load("BOSQUE.jfif").convert(), (ANCHO_MUNDO, ALTO)
)
fondo2_off = pygame.transform.scale(
    pygame.image.load("BOSQUE 2.jfif").convert(), (ANCHO_MUNDO, ALTO)
)

fondo_actual = fondo1_on
temporizador_flicker = 0

# --- CARGA DE ANIMACIONES DEL JUGADOR ---
rutas_idle = [f"KATANA FRAME {i}.png" for i in range(1, 6)]
frames_idle = [
    pygame.transform.scale(
        pygame.image.load(r).convert_alpha(), (200, 200)
    )
    for r in rutas_idle
]

rutas_caminar = [f"KATANA CAMINANDO {i}.png" for i in range(1, 5)]
frames_caminar = [
    pygame.transform.scale(
        pygame.image.load(r).convert_alpha(), (200, 200)
    )
    for r in rutas_caminar
]

rutas_arma = [f"KATANA ARMA {i}.png" for i in range(1, 6)]
frames_arma = [
    pygame.transform.scale(
        pygame.image.load(r).convert_alpha(), (200, 200)
    )
    for r in rutas_arma
]

rutas_apuntando = [f"KATANA APUNTANDO {i}.png" for i in range(1, 5)]
frames_apuntando = [
    pygame.transform.scale(
        pygame.image.load(r).convert_alpha(), (200, 200)
    )
    for r in rutas_apuntando
]

rutas_apuncaminando = ["APUNCAMINANDO.png", "APUNCAMINANDO 2.png"]
frames_apuncaminando = [
    pygame.transform.scale(
        pygame.image.load(r).convert_alpha(), (200, 200)
    )
    for r in rutas_apuncaminando
]

frame_disparando = pygame.transform.scale(
    pygame.image.load("KATANA DISPARANDO.png").convert_alpha(), (200, 200)
)
frame_herido = pygame.transform.scale(
    pygame.image.load("KATANA HERIDO.PNG").convert_alpha(), (200, 200)
)

# --- CARGA DE ANIMACIONES DEL ZOMBIE ---
alto_zombie = 200

rutas_zombie_caminar = ["ZOMBIE.png", "zombie 1.png"]
frames_zombie_caminar = []
for ruta in rutas_zombie_caminar:
    img_raw = pygame.image.load(ruta).convert_alpha()
    ancho_proporcional = int(
        img_raw.get_width() * (alto_zombie / img_raw.get_height())
    )
    frames_zombie_caminar.append(
        pygame.transform.scale(img_raw, (ancho_proporcional, alto_zombie))
    )

rutas_zombie_ataque = ["ZOMBIE ATAQUE 1.png", "ZOMBIE ATAQUE 2.png"]
frames_zombie_ataque = []
for ruta in rutas_zombie_ataque:
    img_raw = pygame.image.load(ruta).convert_alpha()
    ancho_proporcional = int(
        img_raw.get_width() * (alto_zombie / img_raw.get_height())
    )
    frames_zombie_ataque.append(
        pygame.transform.scale(img_raw, (ancho_proporcional, alto_zombie))
    )

ancho_zombie = frames_zombie_caminar[0].get_width()

# --- CARGA DE PUERTA (NIVEL) ---
img_puerta_raw = pygame.image.load("PUERTA.PNG").convert_alpha()
img_puerta_abierta_raw = pygame.image.load("PUERTA 2.PNG").convert_alpha()
alto_puerta = 220
ancho_puerta = int(
    img_puerta_raw.get_width() * (alto_puerta / img_puerta_raw.get_height())
)

imagen_puerta_cerrada = pygame.transform.scale(
    img_puerta_raw, (ancho_puerta, alto_puerta)
)
imagen_puerta_abierta = pygame.transform.scale(
    img_puerta_abierta_raw, (ancho_puerta, alto_puerta)
)

pos_puerta_x = ANCHO_MUNDO - 300
pos_puerta_y = ALTO - alto_puerta - 20
puerta_abierta = False
temporizador_transicion = 0
nivel_actual = 1

# --- CARGA DE LA MIRA Y LA BALA ---
imagen_mira = pygame.transform.scale(
    pygame.image.load("mira.png").convert_alpha(), (32, 32)
)
imagen_bala = pygame.transform.scale(
    pygame.image.load("bala.gif").convert_alpha(), (16, 16)
)

# --- VARIABLES DEL PERSONAJE ---
ANCHO_SPRITE = 200
ALTO_SPRITE = 200
suelo_y = ALTO - ALTO_SPRITE - 20
pos_x = 200
pos_y = suelo_y
velocidad_movimiento = 5
vida_jugador = 100

indice_frame = 0.0
velocidad_animacion = 0.15
estado_movimiento = "idle"
mirando_derecha = True

# --- CONTROL DEL ARMA, PROYECTILES Y DAÑO ---
estado_arma = "guardada"
indice_frame_arma = 0.0
indice_frame_apuntando = 0.0
indice_frame_apuncaminando = 0.0
disparando = False
temporizador_disparo = 0
temporizador_herido = 0

balas = []
velocidad_bala = 18

# --- SISTEMA DE ZOMBIES ---
zombie_velocidad = 2.5
zombie_rango_vision = 650
zombie_rango_ataque = 60
velocidad_anim_zombie_caminar = 0.08
velocidad_anim_zombie_ataque = 0.1


def crear_zombies():
    posiciones = [500, 900, 1500, 1900]
    lista = []
    for px in posiciones:
        lista.append(
            {
                "x": px,
                "y": suelo_y,
                "vida": 100,
                "vida_max": 100,
                "activo": True,
                "estado": "idle",
                "mirando_derecha": True,
                "cooldown_ataque": 0,
                "idx_caminar": 0.0,
                "idx_ataque": 0.0,
            }
        )
    return lista


zombies = crear_zombies()

# Bucle principal
ejecutando = True
while ejecutando:
    if estado_juego == "MENU":
        pygame.mouse.set_visible(True)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_DOWN:
                    opcion_menu = (opcion_menu + 1) % 3
                elif evento.key == pygame.K_UP:
                    opcion_menu = (opcion_menu - 1) % 3
                elif evento.key == pygame.K_RETURN:
                    if opcion_menu == 0:
                        estado_juego = "JUGANDO"
                    elif opcion_menu == 1:
                        pass  # Opciones no hace nada
                    elif opcion_menu == 2:
                        ejecutando = False

        pantalla.blit(menu_imagenes[opcion_menu], (0, 0))

    elif estado_juego == "JUGANDO":
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if estado_arma == "desenfundada":
            pygame.mouse.set_visible(False)
        else:
            pygame.mouse.set_visible(True)

        cerca_de_puerta = (
            abs((pos_x + ANCHO_SPRITE // 2) - (pos_puerta_x + ancho_puerta // 2))
            < 120
        )

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_e:
                    if estado_arma == "guardada":
                        estado_arma = "desenfundando"
                        indice_frame_arma = 0.0
                    elif estado_arma == "desenfundada":
                        estado_arma = "enfundando"
                        indice_frame_arma = 4.0

                elif (
                    evento.key == pygame.K_SPACE
                    and cerca_de_puerta
                    and not puerta_abierta
                ):
                    puerta_abierta = True
                    temporizador_transicion = 30

            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    if estado_arma == "desenfundada" and not disparando:
                        objetivo_x = mouse_x + (
                            pos_x + ANCHO_SPRITE // 2 - ANCHO // 2
                        )
                        objetivo_x = max(0, min(objetivo_x, ANCHO_MUNDO))
                        objetivo_y = mouse_y

                        origen_x = pos_x + (140 if mirando_derecha else 60)
                        origen_y = pos_y + 90

                        dx = objetivo_x - origen_x
                        dy = objetivo_y - origen_y

                        permitido_disparar = (mirando_derecha and dx > 0) or (
                            not mirando_derecha and dx < 0
                        )

                        if permitido_disparar:
                            disparando = True
                            temporizador_disparo = 12

                            distancia = math.hypot(dx, dy)
                            if distancia != 0:
                                dir_x = dx / distancia
                                dir_y = dy / distancia

                                balas.append(
                                    {
                                        "x": origen_x,
                                        "y": origen_y,
                                        "vx": dir_x * velocidad_bala,
                                        "vy": dir_y * velocidad_bala,
                                    }
                                )

        # Transición de nivel
        if puerta_abierta:
            temporizador_transicion -= 1
            if temporizador_transicion <= 0:
                nivel_actual += 1
                pos_x = 200
                balas.clear()
                zombies = crear_zombies()
                puerta_abierta = False

        # Fondo según nivel
        f_encendido = fondo1_on if nivel_actual == 1 else fondo2_on
        f_apagado = fondo1_off if nivel_actual == 1 else fondo2_off

        temporizador_flicker += 1
        if temporizador_flicker > 10:
            temporizador_flicker = 0
            if random.random() < 0.15:
                fondo_actual = f_apagado
            else:
                fondo_actual = f_encendido

        # Movimiento del personaje
        teclas = pygame.key.get_pressed()
        nuevo_estado_mov = "idle"

        if teclas[pygame.K_d]:
            pos_x += velocidad_movimiento
            mirando_derecha = True
            nuevo_estado_mov = "caminando"

        elif teclas[pygame.K_a]:
            pos_x -= velocidad_movimiento
            mirando_derecha = False
            nuevo_estado_mov = "caminando"

        pos_x = max(0, min(pos_x, ANCHO_MUNDO - ANCHO_SPRITE))

        if nuevo_estado_mov != estado_movimiento:
            estado_movimiento = nuevo_estado_mov
            indice_frame = 0.0
            indice_frame_apuncaminando = 0.0

        indice_frame += velocidad_animacion
        lista_movimiento = (
            frames_caminar if estado_movimiento == "caminando" else frames_idle
        )
        if indice_frame >= len(lista_movimiento):
            indice_frame = 0.0

        # IA Zombies
        for z in zombies:
            if z["activo"]:
                distancia_al_jugador = pos_x - z["x"]
                distancia_abs = abs(distancia_al_jugador)

                if distancia_abs < zombie_rango_vision:
                    z["mirando_derecha"] = distancia_al_jugador > 0

                    if distancia_abs > zombie_rango_ataque:
                        z["estado"] = "caminando"
                        if z["mirando_derecha"]:
                            z["x"] += zombie_velocidad
                        else:
                            z["x"] -= zombie_velocidad
                    else:
                        z["estado"] = "atacando"
                        if z["cooldown_ataque"] <= 0:
                            vida_jugador -= 15
                            vida_jugador = max(0, vida_jugador)
                            z["cooldown_ataque"] = 60
                            if estado_arma == "desenfundada":
                                temporizador_herido = 15
                else:
                    z["estado"] = "idle"

                if z["cooldown_ataque"] > 0:
                    z["cooldown_ataque"] -= 1

                if z["estado"] == "atacando":
                    z["idx_ataque"] += velocidad_anim_zombie_ataque
                    if z["idx_ataque"] >= len(frames_zombie_ataque):
                        z["idx_ataque"] = 0.0
                elif z["estado"] == "caminando":
                    z["idx_caminar"] += velocidad_anim_zombie_caminar
                    if z["idx_caminar"] >= len(frames_zombie_caminar):
                        z["idx_caminar"] = 0.0
                else:
                    z["idx_caminar"] = 0.0
                    z["idx_ataque"] = 0.0

        # Selección de frame del jugador
        if temporizador_herido > 0 and estado_arma == "desenfundada":
            frame_actual = frame_herido
            temporizador_herido -= 1
            disparando = False

        elif disparando:
            frame_actual = frame_disparando
            temporizador_disparo -= 1
            if temporizador_disparo <= 0:
                disparando = False

        elif estado_arma == "desenfundando":
            indice_frame_arma += velocidad_animacion
            if indice_frame_arma >= 4.9:
                indice_frame_arma = 4.0
                estado_arma = "desenfundada"
                indice_frame_apuntando = 0.0
            frame_actual = frames_arma[int(indice_frame_arma)]

        elif estado_arma == "enfundando":
            indice_frame_arma -= velocidad_animacion
            if indice_frame_arma <= 0:
                indice_frame_arma = 0.0
                estado_arma = "guardada"
                frame_actual = lista_movimiento[int(indice_frame)]
            else:
                frame_actual = frames_arma[int(indice_frame_arma)]

        elif estado_arma == "desenfundada":
            if estado_movimiento == "caminando":
                indice_frame_apuncaminando += velocidad_animacion
                if indice_frame_apuncaminando >= len(frames_apuncaminando):
                    indice_frame_apuncaminando = 0.0
                frame_actual = frames_apuncaminando[
                    int(indice_frame_apuncaminando)
                ]
            else:
                indice_frame_apuntando += velocidad_animacion
                if indice_frame_apuntando >= len(frames_apuntando):
                    indice_frame_apuntando = 0.0
                frame_actual = frames_apuntando[int(indice_frame_apuntando)]

        else:
            frame_actual = lista_movimiento[int(indice_frame)]

        if not mirando_derecha:
            frame_actual = pygame.transform.flip(frame_actual, True, False)

        # Cámara
        camara_x = (pos_x + ANCHO_SPRITE // 2) - (ANCHO // 2)
        camara_x = max(0, min(camara_x, ANCHO_MUNDO - ANCHO))

        # Balas
        for bala in balas[:]:
            bala["x"] += bala["vx"]
            bala["y"] += bala["vy"]
            impacto = False

            for z in zombies:
                if z["activo"]:
                    hitbox_zombie = pygame.Rect(
                        z["x"], z["y"], ancho_zombie, alto_zombie
                    )
                    if hitbox_zombie.collidepoint(bala["x"], bala["y"]):
                        z["vida"] -= 35
                        impacto = True
                        if z["vida"] <= 0:
                            z["activo"] = False
                        break

            if (
                impacto
                or bala["x"] < 0
                or bala["x"] > ANCHO_MUNDO
                or bala["y"] < 0
                or bala["y"] > ALTO
            ):
                if bala in balas:
                    balas.remove(bala)

        # Dibujar
        pantalla.blit(fondo_actual, (0 - camara_x, 0))

        img_puerta_render = (
            imagen_puerta_abierta if puerta_abierta else imagen_puerta_cerrada
        )
        pantalla.blit(img_puerta_render, (pos_puerta_x - camara_x, pos_puerta_y))

        for z in zombies:
            if z["activo"]:
                if z["estado"] == "atacando":
                    frame_z = frames_zombie_ataque[int(z["idx_ataque"])]
                elif z["estado"] == "caminando":
                    frame_z = frames_zombie_caminar[int(z["idx_caminar"])]
                else:
                    frame_z = frames_zombie_caminar[0]

                if not z["mirando_derecha"]:
                    frame_z = pygame.transform.flip(frame_z, True, False)

                pantalla.blit(frame_z, (z["x"] - camara_x, z["y"]))

                ancho_barra = 60
                alto_barra = 7
                zx_pantalla = (
                    z["x"] - camara_x + (ancho_zombie // 2) - (ancho_barra // 2)
                )
                zy_pantalla = z["y"] - 12

                pygame.draw.rect(
                    pantalla,
                    (40, 40, 40),
                    (
                        zx_pantalla - 1,
                        zy_pantalla - 1,
                        ancho_barra + 2,
                        alto_barra + 2,
                    ),
                )
                pygame.draw.rect(
                    pantalla,
                    (180, 0, 0),
                    (zx_pantalla, zy_pantalla, ancho_barra, alto_barra),
                )
                pct_vida = max(0, z["vida"] / z["vida_max"])
                pygame.draw.rect(
                    pantalla,
                    (0, 200, 0),
                    (
                        zx_pantalla,
                        zy_pantalla,
                        int(ancho_barra * pct_vida),
                        alto_barra,
                    ),
                )

        pantalla.blit(frame_actual, (pos_x - camara_x, pos_y))

        for bala in balas:
            pantalla.blit(
                imagen_bala,
                (
                    bala["x"] - camara_x - imagen_bala.get_width() // 2,
                    bala["y"] - imagen_bala.get_height() // 2,
                ),
            )

        if estado_arma == "desenfundada":
            pantalla.blit(
                imagen_mira,
                (
                    mouse_x - imagen_mira.get_width() // 2,
                    mouse_y - imagen_mira.get_height() // 2,
                ),
            )

        # HUD
        pygame.draw.rect(pantalla, (50, 50, 50), (18, 18, 204, 24))
        pygame.draw.rect(pantalla, (180, 0, 0), (20, 20, 200, 20))
        pygame.draw.rect(
            pantalla, (0, 200, 0), (20, 20, max(0, vida_jugador * 2), 20)
        )
        texto_vida = fuente_hud.render(
            f"SALUD: {vida_jugador}%", True, (255, 255, 255)
        )
        texto_nivel = fuente_hud.render(
            f"NIVEL: {nivel_actual}", True, (255, 255, 0)
        )
        pantalla.blit(texto_vida, (25, 21))
        pantalla.blit(texto_nivel, (240, 21))

        if cerca_de_puerta and not puerta_abierta:
            txt_promp = fuente_puerta.render(
                "PRESIONA ESPACIO PARA CONTINUAR", True, (255, 255, 255)
            )
            rect_bg = txt_promp.get_rect(center=(ANCHO // 2, ALTO // 2 - 120))
            pygame.draw.rect(
                pantalla, (0, 0, 0), rect_bg.inflate(20, 10), border_radius=8
            )
            pantalla.blit(txt_promp, rect_bg)

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()
sys.exit()