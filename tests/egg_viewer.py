"""
Panda3D view to validate bvh2egg-converter output.
Press S to toggle between converted animation and export from blender using YABEE.
Press Q to toggle free camera.
"""
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from panda3d.core import *


class MyApp(ShowBase):
    
    def __init__(self):
        ShowBase.__init__(self)
        
        self.load_actor()
        # Set background color.
        self.setBackgroundColor(0.0, 0.0, 0.0)

        # Set camera position.
        self.disableMouse()
        self.camera.setPos(10.0, -15.0, 5)
        self.camera.lookAt(0.0, -5.0, 1.6)
        
        dir_light_front = DirectionalLight('directional light')
        # Use a 512x512 resolution shadow map
        dir_light_front.setShadowCaster(True, 512, 512)
        # Enable the shader generator for the receiving nodes
        self.render.setShaderAuto()
        dir_light_front_node_path = self.render.attachNewNode(dir_light_front)
        dir_light_front_node_path.setHpr(0, -60, 45)
        self.render.setLight(dir_light_front_node_path)
        
        dir_light_back = DirectionalLight('directional light')
        dir_light_back.setColor((0.2, 0.2, 0.2, 1))
        # Enable the shader generator for the receiving nodes
        dir_light_back_node_path = self.render.attachNewNode(dir_light_back)
        dir_light_back_node_path.setHpr(120, 0, 0)
        self.render.setLight(dir_light_back_node_path)
        
        self.setup_events()
        
    def load_actor(self):
        self.avatar = Actor('example_files/egg/skeleton_and_mesh.egg',
                            {'ground_truth': 'example_files/egg/walk01_blender_export.egg',
                             'converted': 'example_files/egg/walk01_converted.egg',
                             })
        self.avatar.setScale(0.02, 0.02, 0.02)
        self.avatar.reparentTo(self.render)
        # Loop its animation.
        self.avatar.loop("converted")

    def switch_anim(self):
        if self.avatar.get_current_anim() == 'converted':
            self.avatar.loop('ground_truth')
        else:
            self.avatar.loop('converted')
        
    def setup_events(self):
        self.accept('s', self.switch_anim)
        self.accept('q', self.oobe)
        

if __name__ == "__main__":
    
    app = MyApp()
    app.run()
