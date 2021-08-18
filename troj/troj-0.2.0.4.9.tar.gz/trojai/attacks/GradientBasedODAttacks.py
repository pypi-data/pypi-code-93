import torch


def OD_FGSM_linf(
    model, X, y, epsilon, alpha, num_iter, return_examples=True, return_losses=True
):
    # TODO make a class for consistency.
    """
    Construct adversarial examples using the FGSM algorithm on the example X, where X is a list containing a single image.
    """
    losses = {}
    init_loss = model.compute_loss(X, y, grad=False, reduce=True)
    losses["initial_loss"] = init_loss.item()
    delta = torch.nn.init.normal_(
        torch.zeros_like(X[0], requires_grad=True), mean=0, std=0.001
    )
    for t in range(num_iter):
        loss = model.compute_loss([X[0] + delta], y, grad=True, reduce=True)
        loss.backward()
        delta.data = (delta + X[0].shape[0] * alpha * delta.grad.data).clamp(
            -epsilon, epsilon
        )
        delta.grad.zero_()
    losses["final_loss"] = loss.item()
    if return_examples:
        model.train()
        return (X[0] + delta.detach(), losses)
    else:
        model.train()
        return (delta.detach(), losses)
