from frame import Frame, MergeType, OffsetType
from StaticLightPlayer import StaticLightsPlayer
from yaml_manager import YamlReader, YamlWritter
import time

if __name__ == "__main__":


    # Instanciation du nouveau player statique
    nbLights = 54
    interfaceName = "TkinterDisplayer" # "FT232R",TkinterDisplayer,Dummy
    player = StaticLightsPlayer(54, interfaceName) 

    yamlFrame = YamlReader.file_to_frame(r"files/yamls/chop_suey.yaml", 54)

    yamlFrame.push(player, MergeType.MAX, OffsetType.RELATIVE, 0)

    player.start()

    while (player.is_running()):
        time.sleep(1.5)

    player.quit()
    