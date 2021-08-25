from cryoloBM import helper,boxmanager_view,boxmanager_controller,boxmanager_model,helper_GUI
from sys import argv as sys_argv




def start_boxmanager(image_dir:str, box_dir:str, wildcard:str, is_tomo:bool)->None:
    app = helper_GUI.QtG.QApplication(sys_argv)
    view = boxmanager_view.Boxmanager_view(font=app.font())
    model = boxmanager_model.Boxmanager_model(image_dir=image_dir, box_dir=box_dir, wildcard=wildcard, is_tomo=is_tomo)
    c = boxmanager_controller.Boxmanager_controller(view=view, model=model, app=app)
    c.run()


def run()->None:
    # collect args from cli
    args = helper.create_parser().parse_args()

    start_boxmanager(args.image_dir, args.box_dir, args.wildcard, is_tomo=args.is_tomo)



if __name__ == "__main__":
    run()
