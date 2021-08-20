import PySimpleGUI as sg
from . import polymer_chains as pc
from . import GUI_tools as GUI

def main():
    # ------------------------------- PySimpleGUI CODE
    # define chain options for dropdown
    chain_options = GUI.chain_options

    # get help_text
    help_text = GUI.get_helptext()

    layout = [
        [GUI.main_options_frame, GUI.output_frame],
        [GUI.chain_options_frame, GUI.plotting_frame]]

    output_multiline=GUI.output_multiline
    canvas_size = GUI.canvas_size
    chain_objects = GUI.chain_objects
    window = sg.Window('Polymer Plotting', layout, resizable=True)

    # Event loop for main window
    while True:
        event, values = window.read()
        print(event)
        # close loop if window closed or exit button pressed
        if event in (sg.WIN_CLOSED, 'Exit'):  # always,  always give a way out!
            break
        # plot chains if plot button is pressed
        if event == 'Plot':
            fig = pc.plot_chains(chain_objects)
            DPI = fig.get_dpi()
            fig.set_size_inches(canvas_size[0] / float(DPI), canvas_size[1] / float(DPI))
            GUI.draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas)
        # prevent input values being anything but integers
        if event[-8:] == "_length-" and values[event] and values[event][-1] not in ('0123456789'):
            window[event].update(values[event][:-1])
        # RC (Right Click): calculate coords and other chain values for chain object once it is confirmed
        if event[-9:] == "_confirm-":
            chain_index = GUI.get_chain_index(event)
            GUI.confirm_chain(chain_objects, chain_index, values)
        # RC: print the coords of the chain to the output box
        if event[-13:] == "print_coords-":
            chain_index = GUI.get_chain_index(event)
            sg.cprint("\n")
            sg.cprint(chain_objects[chain_index].coords)
        # confirm all the chains at once
        if event == "-confirm_all_chains-":
            for chain_index in range(len(chain_objects)):
                GUI.confirm_chain(chain_objects, chain_index, values)
        # clear all the chains at once
        if event == "-clear_all_chains-":##############################################################################################################
            sg.cprint("The button works!")
        # create a help window
        if event == "-help-":
            GUI.open_text_window(help_text,"-help_window-", title="Help Text", size=(150,30))
        # create a popout window version of the output box
        if event == "-output_popout-":
            GUI.open_text_window(GUI.output_multiline.get(), "Expanded Output Textbox", title="Expanded Output Textbox")
        # clear the output box
        if event == "-output_clear-":
            output_multiline.update(value="")
        # print the selected properties of all the chains to the output box
        if event == "-calculate_chain_properties-":
            GUI.calculate_chain_properties(chain_objects, values)
        # save the current properties to a .csv file
        if event == "-save_chain_properties-":
            GUI.save_chain_properties(chain_objects, values)
    window.close()
