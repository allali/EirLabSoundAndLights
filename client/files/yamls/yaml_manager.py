import sys
import yaml
import random
from pathlib import Path

class yaml_writer:
    def __init__(self,name):
        self.name = name
        base_path = Path(__file__).parent
        folder_path = base_path
        folder_path.mkdir(parents=True, exist_ok=True)
        
        self.file_path = folder_path / f"{name}.yaml"
        
        if not self.file_path.exists():
            self.fileOpened = True
            # self.file = open(file_path, 'w')
            # for i in range(54):
            #     yaml.dump([{"id": i, "times": []}], self.file, default_flow_style=False)
            # self.file.close()
            self.fileOpened = False
            self.data = [{"id": i, "times": []} for i in range(54)]
            
        else:
            print(f"The file '{name}' already exists.")
            sys.exit(1)



    def add(self, id, time, red, green, blue, white, Tr):
        
        if id < 0 or id > 53:
            print(f"The id '{id}' doesn't exists.")
            sys.exit(1)

        if time < 0:
            print(f"time can't be negative ({time}).")
            sys.exit(1)

        if not(0 <= red <= 255) or not(0 <= green <= 255) or not(0 <= blue <= 255) or not(0 <= white <= 255):
            print(f"Invalid colors ({red},{green},{blue},{white}).")
            sys.exit(1)

        if Tr != 0 and Tr != 1:
            print(f"Wrong Tr ({Tr}).")
            sys.exit(1)

        base_path = Path(__file__).parent
        folder_path = base_path / 'yamls'
        folder_path.mkdir(parents=True, exist_ok=True)
        
        file_path = folder_path / f"{self.name}.yaml"
        
        # if not file_path.exists():
        #     print(f"The file '{self.name}' doesn't exists.")
        #     sys.exit(1)
        

        self.data[id]['times'].append({
            'time': int(time),
            'red': int(red),
            'green': int(green),
            'blue': int(blue),
            'white': int(white),
            'Tr': int(Tr)
        })

    
    def write(self):
        if self.fileOpened:
            yaml.dump(self.data, self.file, default_flow_style=False)
        else:
            self.isOpened = True
            with open(self.file_path , 'w') as file:
                yaml.dump(self.data, file, default_flow_style=True)
            self.isOpened = False
        #print(self.data)
            

    #Change all the lights with given parameters
    def full_change(self, time, red, green, blue, white, Tr):
        for i in range(54):
            self.add(i,time,red,green,blue,white,Tr)


    def column(self, number, time, red, green, blue, white, Tr):
        if number > 6 or number < 1:
            print(f"Wrong number ({number})")
            sys.exit(1)
        if number == 1:
            self.add(0,time,red,green,blue,white,Tr)
        for i in range(number-1, 54, 6):
            self.add(i, time, red, green, blue, white, Tr)

    
    #Wave effect following the column
    def wave_column(self, time, duration, red_wave, green_wave, blue_wave, white_wave, red, green, blue, white):
        pause = duration / 6
        for i in range(1, 7):
            if i != 1:
                yw.column(i-1, time+(i*pause), red, green, blue, white, 1)
            yw.column(i, time+(i*pause), red_wave, green_wave, blue_wave, white_wave, 1)
            if i == 6:
                yw.column(i, time+(i+1)*pause,red,green,blue,white,1)
        

    def line(self, number, time, red, green, blue, white, Tr):
        if number > 9 or number < 1:
            print(f"Wrong number ({number})")
            sys.exit(1)
        for i in range((number-1)*6 ,number*6):
            self.add(i, time, red, green, blue, white, Tr)
    
    #Wave effect following the line
    #Is it better to have the duration or the start time and end time ?
    def line_column(self, time, duration, red_wave, green_wave, blue_wave, white_wave, red, green, blue, white):
        pause = duration / 9
        for i in range(1,10):
            if i != 1:
                self.line(i-1, time+((i+2)*pause), red, green, blue, white, 1)
            self.line(i, time+(i*pause), red_wave, green_wave, blue_wave, white_wave, 1)
            if i == 9:
                self.line(i, (time + (i+3)*pause), red, green, blue, white,1)

    #Cross (weird because its an odd by even grid)
    def cross(self, time, red, green, blue, white, Tr):
        for i in range(24,30):
            self.add(i,time,red,green,blue,white,Tr)
        for i in range(2,51,6):
            self.add(i,time,red,green,blue,white,Tr)
            self.add(i+1,time,red,green,blue,white,Tr)

    #Basically a small wave on a single line
    def passing_line(self, number, time, duration, red_wave, green_wave, blue_wave, white_wave, red, green, blue, white):
        pause = duration / 6
        for i in range((number-1)*6,number*6):
            if i != (number-1)*6:
                self.add(i-1, time+((i%6)+2)*pause,red,green,blue,white,1)
            self.add(i, time+(i%6)*pause,red_wave,green_wave,blue_wave,white_wave,1)
            if i == number*6-1:
                self.add(i, time+((i%6)+3)*pause, red, green, blue, white, 1)

    #Same but for column
    def passing_column(self, number, time, duration, red_wave, green_wave, blue_wave, white_wave, red, green, blue, white):
        pause = duration / 9
        if number == 1:
            self.add(0,time,red_wave,green_wave,blue_wave,white_wave,1)
            self.add(0,time+(12*pause),red, green, blue, white, 1)
        for i in range(number-1, 54, 6):
            if i != number-1:
                self.add(i-6, time+(i%9)*pause,red,green,blue,white,1)
            self.add(i, time)


    def full_random(self,time, Tr):
        for i in range(54):
            self.add(i,time,random.randrange(256), random.randrange(256), random.randrange(256), random.randrange(256), Tr)
        
    def expanding_point(self, number, time, duration, red, green, blue, white, Tr):
            pass


    def round(self,time,duration,new_red,new_green,new_blue,new_white):
        pause = duration/30
        incr = 0
        for i in range(6):
            self.add(i,time+incr,new_red,new_green,new_blue,new_white,0)
            incr+=pause
            #self.add(i,time+incr,red,green,blue,white,0)
        for i in range(5,54,6):
            self.add(i,time+incr,new_red,new_green,new_blue,new_white,0)
            incr+=pause
            #self.add(i,time+incr,red,green,blue,white,0)
        for i in range(53,48,-1):
            self.add(i,time+incr,new_red,new_green,new_blue,new_white,0)
            incr+=pause
            #self.add(i,time+incr,red,green,blue,white,0)
        for i in range(48,0,-6):
            self.add(i,time+incr,new_red,new_green,new_blue,new_white,0)
            incr+=pause
            #self.add(i,time+incr,red,green,blue,white,0)

    def round_cst_1_row(self,time,n_red,n_green,n_blue,n_white):
        for k in range(9):
            self.add(6* k,time,n_red,n_green,n_blue,n_white,0)
            self.add(6*k + 5,time,n_red,n_green,n_blue,n_white,0)
        for k in range(6):
            self.add(k,time,n_red,n_green,n_blue,n_white,0)
            self.add(k+48,time,n_red,n_green,n_blue,n_white,0)

    def round_cst_2_row(self,time,n_red,n_green,n_blue,n_white):
        for k in range(1,8):
            self.add(6* k + 1,time,n_red,n_green,n_blue,n_white,0)
            self.add(6*k + 4,time,n_red,n_green,n_blue,n_white,0)
        for k in range(1,5):
            self.add(k + 6,time,n_red,n_green,n_blue,n_white,0)
            self.add(k + 43,time,n_red,n_green,n_blue,n_white,0)

    def spiral(self,time,duration,new_red,new_green,new_blue,new_white):
        pause = duration/54
        incr = 0
        for i in range(6):
            self.add(i,time+incr,new_red,new_green,new_blue,new_white,0)
            incr+=pause
            #self.add(i,time+incr,red,green,blue,white,0)
        for i in range(5,54,6):
            self.add(i,time+incr,new_red,new_green,new_blue,new_white,0)
            incr+=pause
            #self.add(i,time+incr,red,green,blue,white,0)
        for i in range(53,48,-1):
            self.add(i,time+incr,new_red,new_green,new_blue,new_white,0)
            incr+=pause
            #self.add(i,time+incr,red,green,blue,white,0)
        for i in range(48,0,-6):
            self.add(i,time+incr,new_red,new_green,new_blue,new_white,0)
            incr+=pause
        for i in range(7,11):
            self.add(i,time+incr,new_red,new_green,new_blue,new_white,0)
            incr+=pause
        for i in range(10,47,6):
            self.add(i,time+incr,new_red,new_green,new_blue,new_white,0)
            incr+=pause
        for i in range(46,43,-1):
            self.add(i,time+incr,new_red,new_green,new_blue,new_white,0)
            incr+=pause
        for i in range(43,7,-6):
            self.add(i,time+incr,new_red,new_green,new_blue,new_white,0)
            incr+=pause
        for i in range(14,16):
            self.add(i,time+incr,new_red,new_green,new_blue,new_white,0)
            incr+=pause
        for i in range(15,40,6):
            self.add(i,time+incr,new_red,new_green,new_blue,new_white,0)
            incr+=pause
        for i in range(39,38,-1):
            self.add(i,time+incr,new_red,new_green,new_blue,new_white,0)
            incr+=pause
        for i in range(38,14,-6):
            self.add(i,time+incr,new_red,new_green,new_blue,new_white,0)
            incr+=pause

if __name__ == "__main__":
    yw = yaml_writer("test")
    #yw.cross(250,255,0,0,0,1)
    yw.full_change(1,255,0,0,100,1)
    yw.round(500,3000,0,0,255,100,0,255,0,100)
    yw.write()
