import sys
from .robot import Robot
from .commandparser import Command, CommandParser

robot = Robot()
robot.load_state("pbtoyrobot/robot_state.yaml")
command = Command(robot.commands_desc)
command_parser = CommandParser(command_separator=" ", argument_separator=",")

def main():
    args = " ".join(sys.argv[1:])
    (commands, output_file) = command_parser.read(args, command)
    robot.execute(commands, output_file)

if __name__ == '__main__':
    main()
