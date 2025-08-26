# ui3d.py
from ursina import Entity, Text, camera, color

class HUD:
    def __init__(self):
        self.root = Entity(parent=camera.ui)
        self.score_text = Text(parent=self.root, text="Score: 0", origin=(-.5,.5), position=(-.87,.45), scale=1, color=color.white)
        self.level_text = Text(parent=self.root, text="Level: 1", origin=(-.5,.5), position=(-.87,.40), scale=1, color=color.white)
        # stamina bar
        self.bar_bg = Entity(parent=self.root, model='quad', color=color.rgba(0.2,0.2,0.2,0.9),
                             position=(-.65, .34), scale=(.34, .03))
        self.bar_fg = Entity(parent=self.root, model='quad', color=color.rgba(1,0.6,0.2,0.95),
                             position=(-.82, .34), scale=(.001, .02), origin=(-.5,0))

    def update(self, score, level, stamina):
        self.score_text.text = f"Score: {int(score)}"
        self.level_text.text = f"Level: {level}"
        # stamina 0..100
        pct = max(0.0, min(1.0, stamina/100.0))
        self.bar_fg.scale_x = .32 * pct

def show_lore(lines, continue_hint="Press any key to continue..."):
    from ursina import Text, invoke, destroy, held_keys, time
    # overlay
    texts = []
    y = 0.2
    for ln in lines:
        t = Text(text=ln, origin=(0,0), position=(0, y), scale=1.4, color=color.white)
        texts.append(t)
        y -= 0.12
    hint = Text(text=continue_hint, origin=(0,0), position=(0, -0.35), scale=0.9, color=color.rgba(1,1,1,0.7))
    # wait until any key pressed
    def waiter():
        if any(held_keys.values()):
            for t in texts: destroy(t)
            destroy(hint)
            return
        invoke(waiter, delay=0.02)
    invoke(waiter, delay=0.02)
