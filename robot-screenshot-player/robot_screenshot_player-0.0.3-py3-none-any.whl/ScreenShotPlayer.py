from robot.libraries.BuiltIn import BuiltIn
import os
from shutil import copyfile,rmtree


class ScreenShotPlayer(object):
    ROBOT_LISTENER_API_VERSION = 2
    sc_index = 1
    Max_steps_after_which_screen_shot_should_be_captured = 1
    counter = 0
    previous_suite_name = ''
    project_execution_dir = ''
    ScreenShotPlayerReportDir=None

    def __init__(self,whereToSaveReportDir=None):
        if whereToSaveReportDir:
            ScreenShotPlayer.ScreenShotPlayerReportDir=whereToSaveReportDir
     

    @staticmethod
    def start_suite(name, attributes):
        ScreenShotPlayer.sc_index = 1
        ScreenShotPlayer.project_execution_dir = BuiltIn().get_variable_value("${EXECDIR}")
        if ScreenShotPlayer.ScreenShotPlayerReportDir==None:
            ScreenShotPlayer.ScreenShotPlayerReportDir=os.path.join(ScreenShotPlayer.project_execution_dir,'screenShotplayer')

    
    @staticmethod
    def start_keyword(name, attributes):
       
        seleniumlib = BuiltIn().get_library_instance('SeleniumLibrary')
        suite_source = BuiltIn().get_variable_value("${SUITE SOURCE}")
        suite_name = suite_source.rsplit('\\')[-1].replace('.robot', '').strip()
        seleniumlib.capture_page_screenshot('{}/{}/{}-{}.png'.format(ScreenShotPlayer.ScreenShotPlayerReportDir,suite_name, suite_name, ScreenShotPlayer.sc_index))
        # print('{}/{}/{}-{}.png'.format(ScreenShotPlayer.ScreenShotPlayerReportDir,suite_name, suite_name, ScreenShotPlayer.sc_index))
        ScreenShotPlayer.sc_index = ScreenShotPlayer.sc_index+1
      

    @staticmethod
    def end_keyword(name, attributes):
        ScreenShotPlayer.start_keyword(name, attributes)
      
    @staticmethod
    def getHTMLTemplate():
        return """<!DOCTYPE html>

            <html>

            <head>
                <link rel="stylesheet" href="style.css" />
                <title>ScreenShotPlayer</title>
                <script src="data.js"></script>
                <script src="controller.js"></script>
            
            
            </head>

            <body onload="startTimer()">
                <div style='position: absolute;border:2px solid red;width: 100%;height: 100%;'>
                    <div id='sidebar'></div>
                    <div id="imgcontainer">
                        <img id="img" src="" />

                        <div id="progressbar">
                            <div id="myBar"></div>
                        </div>
                        <button id='btn_pause' type="button" onclick="pause()">Pause</button>
                        <button id='btn_resume' type="button" onclick="resume()">Resume</button>
                        <button id='btn_reset' type="button" onclick="reset()">Reset</button>
                        <button id='next_frame' type="button" onclick="showNextFrame()">Next</button>
                        <button id='prev_frame' type="button" onclick="showPrevFrame()">Prev</button>
                        <span>
                            <button id='speed_conroller' type="button" onclick="speedConroller(2)">+</button>
                            <span id='interval_in_ms'>Nil</span>
                            <button id='speed_conroller' type="button" onclick="speedConroller(0.5)">-</button>
                        </span>
                    </div>

                </div>


            </body>

            </html>"""
    

    @staticmethod
    def generateScreenShotPlayerResource(data):
        
        path_of_screen_shot_player= ScreenShotPlayer.ScreenShotPlayerReportDir
        
        
        # if os.path.isdir(path_of_screen_shot_player):
        #     rmtree(path_of_screen_shot_player)
        if  not (os.path.isdir(path_of_screen_shot_player)):
            os.makedirs(path_of_screen_shot_player)
        
        test_str = ScreenShotPlayer.getHTMLTemplate();
        
        #generated html file
        with open(os.path.join(path_of_screen_shot_player,'ScreenShotPlayer.html'), 'w') as f:
            f.write(test_str)
        
        #copy data file from resource data file
        with open(os.path.join(path_of_screen_shot_player,'data.js'), 'w') as f:
            f.write('image_json_container1={}'.format(data))
        

        resource_dir=__file__.replace('ScreenShotPlayer.py','resource')
        copyfile(os.path.join(resource_dir,'style.css'),os.path.join(path_of_screen_shot_player,'style.css'))
        copyfile(os.path.join(resource_dir,'controller.js'),os.path.join(path_of_screen_shot_player,'controller.js'))


        
        #generate controller file
        #generate css file with


    @staticmethod
    def close():
        def custom_sort(a):
                # print(a.replace('.png','').split('-')[-1])
            return int(a.replace('.png', '').split('-')[-1])
        
        image_container = {}
        key = 0

        for root, dirs, files in os.walk(ScreenShotPlayer.ScreenShotPlayerReportDir):
            if(root==ScreenShotPlayer.ScreenShotPlayerReportDir):
                continue
            image_container[str(key)] = [root, files]
            key = key+1

       

        for key, value in image_container.items():
            image_container[key][1] = sorted(
                image_container[key][1], key=custom_sort)
        print(image_container)
        ScreenShotPlayer.generateScreenShotPlayerResource(str(image_container))
        
        print("robot-screenShotplayer completed successfully")


