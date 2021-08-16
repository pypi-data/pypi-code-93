import torch


def load_optimizer(optimizer_type,
                   model,
                   learning_rate,
                   **kwargs):
    """
    Returns the optimizer for model training.
    :param optimizer_type: Returns the
    :param model: The model to be trained.
    :param learning_rate: Initial learning rate.
    :param kwargs:
    :return: Optimizer for model training.
    """
    if optimizer_type.lower() == "adadelta":
        return torch.optim.Adadelta(model.parameters(),
                                    lr=learning_rate,
                                    rho=kwargs.get("rho", 0.9),
                                    weight_decay=kwargs.get("weight_decay", 0.0))
    elif optimizer_type.lower() == "adagrad":
        return torch.optim.Adagrad(model.parameters(),
                                   lr=learning_rate,
                                   lr_decay=kwargs.get("lr_decay", 0),
                                   weight_decay=kwargs.get("weight_decay", 0))
    elif optimizer_type.lower() == "adam":
        return torch.optim.Adam(model.parameters(),
                                lr=learning_rate)
    elif optimizer_type.lower() == "adamw":
        return torch.optim.AdamW(model.parameters(),
                                 lr=learning_rate,
                                 weight_decay=kwargs.get("weight_decay", 4e-5))
    elif optimizer_type.lower() == "adamax":
        return torch.optim.Adamax(model.parameters(),
                                  lr=learning_rate,
                                  weight_decay=kwargs.get("weight_decay", 0))
    elif optimizer_type.lower() == "rmsprop":
        return torch.optim.RMSprop(model.parameters(),
                                   lr=learning_rate,
                                   momentum=kwargs.get("momentum", 0.9))
    elif optimizer_type.lower() == "rprop":
        return torch.optim.Rprop(model.parameters(),
                                 lr=learning_rate)
    elif optimizer_type.lower() == "sgd":
        return torch.optim.SGD(model.parameters(),
                               lr=learning_rate,
                               momentum=kwargs.get("momentum", 0.9))
