from robot.libraries.BuiltIn import BuiltIn
import os
from shutil import copyfile,rmtree
from pkg_resources import resource_string

class ScreenShotPlayer(object):
    ROBOT_LISTENER_API_VERSION = 2
    sc_index = 1
    Max_steps_after_which_screen_shot_should_be_captured = 1
    counter = 0
    previous_suite_name = ''
    project_execution_dir = ''
    ScreenShotPlayerReportDir=None
    whereToSaveReportDirRelativePath=None

    def __init__(self,whereToSaveReportDir=None):
        if whereToSaveReportDir:
            ScreenShotPlayer.whereToSaveReportDirRelativePath=whereToSaveReportDir
           

    @staticmethod
    def start_suite(name, attributes):
        ScreenShotPlayer.sc_index = 1
        ScreenShotPlayer.project_execution_dir = BuiltIn().get_variable_value("${EXECDIR}")
        if ScreenShotPlayer.whereToSaveReportDirRelativePath==None:
            ScreenShotPlayer.ScreenShotPlayerReportDir=os.path.join(ScreenShotPlayer.project_execution_dir,'screenShotplayer')
        else:
             ScreenShotPlayer.ScreenShotPlayerReportDir=os.path.join(ScreenShotPlayer.project_execution_dir,ScreenShotPlayer.whereToSaveReportDirRelativePath,'screenShotplayer')


    @staticmethod
    def start_keyword(name, attributes):
        # print(attributes)
        if 'alert' in name.lower():return

        try:
            seleniumlib = BuiltIn().get_library_instance('SeleniumLibrary')
            suite_source = BuiltIn().get_variable_value("${SUITE SOURCE}")
            suite_name = suite_source.rsplit('\\')[-1].replace('.robot', '').strip()
            seleniumlib.capture_page_screenshot('{}/{}/{}-{}.png'.format(ScreenShotPlayer.ScreenShotPlayerReportDir,suite_name, suite_name, ScreenShotPlayer.sc_index))
            # print('{}/{}/{}-{}.png'.format(ScreenShotPlayer.ScreenShotPlayerReportDir,suite_name, suite_name, ScreenShotPlayer.sc_index))
            ScreenShotPlayer.sc_index = ScreenShotPlayer.sc_index+1
        except Exception as e:
            print(e)
         
      

    @staticmethod
    def end_keyword(name, attributes):
        pass
        # print(attributes['status'])
        # pass
        # ScreenShotPlayer.start_keyword(name, attributes)
      
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
    <div class='grid'>
        <div id='sidebar'></div>
        <div id="imgcontainer">
            <img id="img" src="" />

            <div id="progressbar">
                <div id="myBar"></div>
            </div>
            <div  class='controller_btn'>
            <button id='btn_pause' class='btn' type="button" onclick="pause()">Pause</button>
            <button id='btn_resume' class='btn' type="button" onclick="resume()">Resume</button>
            <button id='btn_reset'   class='btn' type="button" onclick="reset()">Reset</button>
            <button id='next_frame' class='btn'  type="button" onclick="showNextFrame()">Next</button>
            <button id='prev_frame'  class='btn'  type="button" onclick="showPrevFrame()">Prev</button>
            <span class='speed_conroller_grp'>
                <button id='speed_conroller' type="button" onclick="speedConroller(2)">+</button>
                <span id='interval_in_ms'>100</span>
                <button id='speed_conroller' type="button" onclick="speedConroller(0.5)">-</button>
            </span>
            </div>
        </div>

    </div>


</body>

</html>"""

    @staticmethod
    def getCssCode():
        return  '''    *{
                    margin:0;
                    padding:0;
                    box-sizing: border-box;
                }
                html{
                    width:100%;
                    height:100%;
                }
                body{
                    width:100%;
                    height:100%;
                }
                .grid{
                    display:grid;
                    grid-template-columns: 2fr 6fr 2fr;
                    width:100%;
                    height:100%;
                }
                        

            a{
                display: block;
                overflow: hidden;
            }

            #imgcontainer {
                width:100%;
                height:75%;
                border:2px solid black;
                margin-top: 8%;
                position: relative;
            }
            img {
                width: 100%;
                height: 100%;
                object-fit: contain;
                /* margin-left: 10%; */
            }
            #progressbar{
                position: relative;
                bottom:0%;
                width: 100%;
                background-color: grey;
                height: 8px;
            
            }
            #myBar {
                    position: absolute;
                    width: 0%;
                    height: 100%;
                    background-color: green;
                    
            }
            #btn_pause{
                position: relative;
            }

            .controller_btn{
                display: flex;
                align-items: center;
                justify-content: center;
            
            }
            .btn{
                margin:5px;
            }
            .speed_conroller_grp{
                background-color:lightblue
            }
            #speed_conroller{
                min-width: 40px;
            }

            #sidebar{
                border:1px solid black;
                padding-left:2%
            }'''
    

    @staticmethod
    def getJavascriptCode():
        return  """
            var current_imageworkflow_path=''
            var id_of_anchor_link=-1
            var interval
            var current_image_index=0
            var period_for_image_update=1000
            var  image_json_container=typeof image_json_container1 === 'undefined'?{}:image_json_container1


            function displayNextImage() {
            if(image_json_container[id_of_anchor_link][1].length<=current_image_index) {
                    current_image_index=0
                    clearInterval(interval)
                    interval=null
                    console.log("end of the image")
                    return
            }
            let image_src=`${current_imageworkflow_path}${image_json_container[id_of_anchor_link][1][current_image_index]}`
            document.getElementById("img").src = image_src
            document.getElementById("myBar").style.width=(current_image_index/image_json_container[id_of_anchor_link][1].length)*100+'%'
            // console.log(image_src)
            current_image_index++


            }
            function update_time(text){
            document.getElementById("interval_in_ms").textContent=text+'ms'
            }

            function populate_sideBar_for_various_workflow(){
            let sidebar=document.getElementById("sidebar")
            for(let item in image_json_container){
                link=document.createElement("a")
                link.text = image_json_container[item][0].split("\\\\").reverse()[0]
                link.href='#'
                link.id=item
                link.onclick= function(event) {
                    if(interval){
                        clearInterval(interval)
                        interval=null
                    }
                    current_image_index=0
                    id_of_anchor_link=event.target.id
                    current_imageworkflow_path=`${image_json_container[event.target.id][0]}/`
                    interval=setInterval(displayNextImage, period_for_image_update);
                    console.log(id_of_anchor_link)
                }
            
            
                sidebar.appendChild(link)
                
            }
            }
            function startTimer() {

            populate_sideBar_for_various_workflow()
            update_time(period_for_image_update)


            }

            function pause(){
            if(interval){
                clearInterval(interval);
                interval=null
            }
            }

            function resume(){
            console.log(!interval)
            console.log(current_image_index+"----- in resume")
            if (!interval)
            {
                interval=setInterval(displayNextImage, period_for_image_update);
            }
            }
            /**
            * clearing setinterval  and setting  the frame to zero 
            * */
            function reset(){
            if(interval!=null){
                clearInterval(interval);
                interval=null
                current_image_index=0
                document.getElementById("myBar").style.width=0
                document.getElementById("img").src = ''
                
            }

            }

            function showNextFrame(){
            //only in pause state
            if(interval==null && id_of_anchor_link!=-1){
                displayNextImage()
            }
            }

            function showPrevFrame(){
            //only in pause state
            if(interval==null && id_of_anchor_link!=-1){
                current_image_index=current_image_index-2;
                displayNextImage()
            }
            }

            function speedConroller(speeding_factor){
            period_for_image_update=period_for_image_update/speeding_factor
            console.log(`Time lagging for two consecutive image is :`,period_for_image_update)
            update_time(period_for_image_update)
            if(interval!=null){
                clearInterval(interval)
                interval=setInterval(displayNextImage,period_for_image_update)
            }
            }






                    """

    @staticmethod
    def generateScreenShotPlayerResource(data):
        
        path_of_screen_shot_player= ScreenShotPlayer.ScreenShotPlayerReportDir
        
        
        # if os.path.isdir(path_of_screen_shot_player):
        #     rmtree(path_of_screen_shot_player)
        if  not (os.path.isdir(path_of_screen_shot_player)):
            os.makedirs(path_of_screen_shot_player)
        
        test_str = ScreenShotPlayer.getHTMLTemplate()
        
        #generated html file
        with open(os.path.join(path_of_screen_shot_player,'ScreenShotPlayer.html'), 'w') as f:
            f.write(test_str)
        
        #copy data file from resource data file
        with open(os.path.join(path_of_screen_shot_player,'data.js'), 'w') as f:
            f.write('image_json_container1={}'.format(data))
        
        #copy data file from resource data file
        with open(os.path.join(path_of_screen_shot_player,'controller.js'), 'w') as f:
            f.write(ScreenShotPlayer.getJavascriptCode())
        
        with open(os.path.join(path_of_screen_shot_player,'style.css'), 'w') as f:
            f.write(ScreenShotPlayer.getCssCode())
        
       
        # resource_dir=__file__.replace('ScreenShotPlayer.py','resource')
        # ScreenShotPlayer.createResourceCopy('style.css',path_of_screen_shot_player)
        # ScreenShotPlayer.createResourceCopy('controller.js',path_of_screen_shot_player)
        # copyfile(os.path.join(resource_dir,'style.css'),os.path.join(path_of_screen_shot_player,'style.css'))
        # copyfile(os.path.join(resource_dir,'controller.js'),os.path.join(path_of_screen_shot_player,'controller.js'))


        
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
            image_container[str(key)] = [os.path.relpath(root,ScreenShotPlayer.ScreenShotPlayerReportDir), files]
            key = key+1

       

        for key, value in image_container.items():
            image_container[key][1] = sorted(
                image_container[key][1], key=custom_sort)
        # print(image_container)
        ScreenShotPlayer.generateScreenShotPlayerResource(str(image_container))
        
        print("[robot-screenshot-player]:report saved at location:\t{}/{}".format(ScreenShotPlayer.ScreenShotPlayerReportDir,'ScreenShotPlayer.html'))
    
    @staticmethod
    def createResourceCopy(resource_name,path_where_to_create):
        with open(os.path.join(path_where_to_create,resource_name),'w') as f:
            f.write(str(resource_string("resource",resource_name).decode()))
       


