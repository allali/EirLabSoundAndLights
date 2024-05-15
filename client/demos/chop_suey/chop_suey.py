import time
from os import path
import sys
MAIN_FOLDER = path.abspath(path.dirname(path.dirname(path.dirname(__file__))))
sys.path.append(MAIN_FOLDER)
import light
if __name__ == "__main__":


    # Instanciation du nouveau player statique
    nbLights = 54
    interfaceName = "TkinterDisplayer" # "FT232R",TkinterDisplayer,Dummy
    player = light.StaticLightsPlayer(54, interfaceName) 

    yamlFrame = light.YamlReader.file_to_frame(r"files/yamls/chop_suey.yaml", 54)

    yamlFrame.push(player, light.MergeType.MAX, light.OffsetType.RELATIVE, 0)

    player.start()

    while (player.is_running()):
        time.sleep(1.5)

    player.quit()
    