from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from customattack.commands import CustomAttackCommand
from customattack import Attacker, CommandLineAttackArgs, DatasetArgs, ModelArgs

class AttackCommand(CustomAttackCommand):
    """The TextAttack attack module:
    A commands line parser to run an attack from user specifications.
    """

    def run(self, args):
        print("start running")
        print("args:", args)
        attack_args = CommandLineAttackArgs(**vars(args))
        print(attack_args)
        dataset = DatasetArgs._create_dataset_from_args(attack_args)
        print("dataset module:", dataset)
        if attack_args.interactive:
            model_wrapper = ModelArgs._create_model_from_args(attack_args)
            attack = CommandLineAttackArgs._create_attack_from_args(
                attack_args, model_wrapper
            )
            Attacker.attack_interactive(attack)
        else:
            model_wrapper = ModelArgs._create_model_from_args(attack_args)
            attack = CommandLineAttackArgs._create_attack_from_args(
                attack_args, model_wrapper
            )
            attacker = Attacker(attack, dataset, attack_args)
            attacker.attack_dataset()
        print("end running")

    @staticmethod
    def register_subcommand(main_parser: ArgumentParser):
        parser = main_parser.add_parser(
            "attack",
            help="run an attack on an NLP model",
            formatter_class=ArgumentDefaultsHelpFormatter,
        )
        parser = CommandLineAttackArgs._add_parser_args(parser)
        parser.set_defaults(func=AttackCommand())