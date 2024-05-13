from frame import Frame, MergeType, OffsetType
from StaticLightPlayer import StaticLightsPlayer
from yaml_manager import YamlReader, YamlWritter
import time

if __name__ == "__main__":
    
    f1 = Frame(54) # On instancie une frame vide
    f2 = Frame(54) # On instancie une seconde frame vide
    
    # On remplie la frame 1. Important : on la remplie par timeStamp croissant pour chaque light. 
    # Pour une même light, ne surtout pas faire 2 appends avec un t0 > t1.
    f1.append(48, 12, [1,10,100,0], 0)
    f1.append(48, 50, [2,11,101,0], 1)
    f1.append(48, 120, [3,12,102,0], 0)
    f1.append(48, 150, [4,13,103,0], 0)
    f1.append(48, 190, [5,14,104,0], 1)
    f1.append(48, 250, [6,15,105,0], 0)
    
    #On remplie la frame 2. Même règle
    f2.append(48, 30, [10,100,200,0], 0)
    f2.append(48, 101, [20,110,201,0], 1)
    f2.append(48, 220, [30,120,202,0], 0)
    f2.append(48, 290, [40,130,203,0], 0)
    f2.append(48, 350, [50,140,204,0], 1)
    f2.append(48, 4000, [60,150,205,255], 1)
    

    # On merge la frame 1 et 2 en une seule et même frame. Vous pouvez préciser le type de fusion
    # Ici, on fait la moyenne des couleurs de f1 et f2. On obtient une nouvelle frame f3. f1 et f2
    # restent inchangées
    f3= Frame.merge(f1, f2, MergeType.MEAN)


##################################################
############## AUTRE FONCTIONS ###################
##################################################
# YamlWritter.merge_yamls_in_directory(r"files/yamls", "outputName.yaml", 54, MergeType.MAX)
# Pour merge l'ensemble des yamls d'un répertoire.  Ne fonctionne pas avec notre répertoire yaml car certains yamls sont mal écrits
# 
# YamlWritter.merge_yamls(["yaml1.yaml", "yaml2.yaml", "yaml3.yaml"], "outputYamlName.yaml", 54, MergeType.MIN)
# Merge N fichiers yamls entre eux
##################################################
##################################################
##################################################

    

    # Instanciation du nouveau player statique
    nbLights = 54
    interfaceName = "TkinterDisplayer" # "FT232R",TkinterDisplayer,Dummy
    player = StaticLightsPlayer(54, interfaceName) 
    
    # On charge un yaml sous forme de frame
    yamlFrame = YamlReader.file_to_frame(r"files/yamls/snake.yaml", 54)
    
    # On merge la frame obtenue du yaml avec la frame f3. 
    f4 = Frame.merge(f3, yamlFrame, MergeType.MEAN)
    
    # On donne la frame 4 à jouer au player statique.
    f4.push(player, MergeType.MAX, OffsetType.RELATIVE, 10)
    
    # Lancement du player
    player.start()
    while (player.is_running()):
        time.sleep(1.5) # Toujours laisser un sleep d'au moins 1s
        # Toutes les 3 secondes, on remplie à nouveau le player avec la même frame.
        # OffsetType.RELATIVE et le '10' signifie qu'on charge la frame 10ms dans le futur
        # On peut également choisir OffsetType.ABSOLUTE qui aurait eu pour effet de charger la frame à partir
        # de 10 millisecondes après le lancement du player (donc il ne serait rien passé car ce moment est déjà passé (trop tard))
        yamlFrame.push(player, MergeType.MAX, OffsetType.RELATIVE, 10)
        
    # On quitte le player
    player.quit()