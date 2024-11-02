class Player:
    def __init__(self, pos_x, pos_y, texture, render_func, healthpoints, power_ups):
        # position:
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.speed = 0 # speed = pereche de viteza + acceleratie, avem nevoie pt gravitatie
        self.mass = 0

        # graphics/looks
        self.texture = texture
        self.render = render_func

        # player stats
        self.healthpoints = healthpoints # 3 vieti sau cate stabilim
        self.power_ups = power_ups # asta o sa fie vector
    
    # TODO IMPLEMENTATION OF GETTERS/SETTERS/RENDERING
        


