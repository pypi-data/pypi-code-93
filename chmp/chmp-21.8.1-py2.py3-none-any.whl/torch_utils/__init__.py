"""Helper to construct models with pytorch."""
import functools as ft

import numpy as np
import torch
import torch.nn.functional as F
import torch.utils.data

from chmp.ds import (
    smap,
    transform_args,
    copy_structure,
    default_sequences,
    default_mappings,
    undefined,
)

from ._net import make_net

try:
    import pandas as pd

except ImportError:
    _pd_arrays = ()

else:
    _pd_arrays = (pd.Series, pd.DataFrame)


default_arrays = (np.ndarray, *_pd_arrays)
default_tensors = (torch.Tensor,)

default_batch_size = 32


def register_unknown_kl(type_p, type_q):
    def decorator(func):
        if has_kl(type_p, type_q):
            func.registered = False
            return func

        torch.distributions.kl.register_kl(type_p, type_q)(func)
        func.registered = True
        return func

    return decorator


def has_kl(type_p, type_q):
    return (type_p, type_q) in torch.distributions.kl._KL_REGISTRY


def t2n(
    obj=undefined,
    *,
    dtype=None,
    sequences=default_sequences,
    mappings=default_mappings,
    tensors=default_tensors,
):
    """Torch to numpy."""
    if obj is undefined:
        return ft.partial(
            t2n, dtype=dtype, sequences=sequences, mappings=mappings, tensors=tensors
        )

    if not callable(obj):
        return _t2n_tensors(
            obj, dtype=dtype, sequences=sequences, mappings=mappings, tensors=tensors
        )

    @ft.wraps(obj)
    def wrapper(*args, **kwargs):
        args, kwargs = transform_args(
            obj,
            args,
            kwargs,
            _t2n_tensors,
            dtype=dtype,
            sequences=sequences,
            mappings=mappings,
            tensors=tensors,
        )
        return obj(*args, **kwargs)

    return wrapper


def _t2n_tensors(obj, *, dtype, sequences, mappings, tensors):
    dtype = copy_structure(obj, dtype, sequences=sequences, mappings=mappings)
    return smap(
        ft.partial(_t2n_scalar, tensors=tensors),
        obj,
        dtype,
        sequences=sequences,
        mappings=mappings,
    )


def _t2n_scalar(obj, dtype, tensors):
    if not isinstance(obj, tensors):
        return obj

    return np.asarray(obj.detach().cpu(), dtype=dtype)


def n2t(
    obj=undefined,
    *,
    dtype=None,
    device=None,
    sequences=default_sequences,
    mappings=default_mappings,
    arrays=default_arrays,
):
    """Numpy to torch."""
    if obj is undefined:
        return ft.partial(
            n2t,
            dtype=dtype,
            device=device,
            sequences=sequences,
            mappings=mappings,
            arrays=arrays,
        )

    if not callable(obj):
        return _n2t_tensors(
            obj,
            dtype=dtype,
            device=device,
            sequences=sequences,
            mappings=mappings,
            arrays=arrays,
        )

    @ft.wraps(obj)
    def wrapper(*args, **kwargs):
        args, kwargs = transform_args(
            obj,
            args,
            kwargs,
            _n2t_tensors,
            dtype=dtype,
            device=device,
            sequences=sequences,
            mappings=mappings,
            arrays=arrays,
        )
        return obj(*args, **kwargs)

    return wrapper


def _n2t_tensors(obj, *, dtype, device, sequences, mappings, arrays):
    dtype = copy_structure(obj, dtype, sequences=sequences, mappings=mappings)
    device = copy_structure(obj, device, sequences=sequences, mappings=mappings)

    return smap(
        ft.partial(_n2t_scalar, arrays=arrays),
        obj,
        dtype,
        device,
        sequences=sequences,
        mappings=mappings,
    )


def _n2t_scalar(obj, dtype, device, arrays):
    if not isinstance(obj, arrays):
        return obj

    if isinstance(dtype, str):
        dtype = getattr(torch, dtype)

    if isinstance(device, str):
        device = torch.device(device)

    obj = np.asarray(obj)

    # torch cannot handle negative strides, make a copy to remove striding
    if any(s < 0 for s in obj.strides):
        obj = obj.copy()

    return torch.as_tensor(obj, dtype=dtype, device=device)


def factorized_quadratic(x, weights):
    """A factorized quadratic interaction.

    :param x:
        shape ``(batch_size, in_features)``
    :param weights:
        shape ``(n_factors, in_features, out_features)``
    """
    x = x[None, ...]
    res = (x @ weights) ** 2.0 - (x ** 2.0) @ (weights ** 2.0)
    res = res.sum(dim=0)
    return 0.5 * res


def masked_softmax(logits, mask, axis=-1, eps=1e-9):
    """Compute a masked softmax"""
    keep = 1.0 - mask.type(logits.dtype)
    p = keep * torch.softmax(logits * keep, axis=axis)
    p = p / (eps + p.sum(axis=axis, keepdims=True))
    return p


class DiagonalScaleShift(torch.nn.Module):
    """Scale and shift the inputs along each dimension independently."""

    @classmethod
    def from_data(cls, data):
        return cls(shift=data.mean(), scale=1.0 / (1e-5 + data.std()))

    def __init__(self, shift=None, scale=None):
        super().__init__()
        assert (shift is not None) or (scale is not None)

        if shift is not None:
            shift = torch.as_tensor(shift).clone()

        if scale is not None:
            scale = torch.as_tensor(scale).clone()

        if shift is None:
            shift = torch.zeros_like(scale)

        if scale is None:
            scale = torch.ones_like(shift)

        self.shift = torch.nn.Parameter(shift)
        self.scale = torch.nn.Parameter(scale)

    def forward(self, x):
        return self.scale * (x - self.shift)


class Identity(torch.nn.Module):
    """A module that does not modify its argument"""

    def forward(self, x):
        return x


def format_extra_repr(*kv_pairs):
    return ", ".join("{}={}".format(k, v) for k, v in kv_pairs)


class LocationScale(torch.nn.Module):
    """Split its input into a location / scale part

    The scale part will be positive.
    """

    def __init__(self, activation=None, eps=1e-6):
        super().__init__()

        if activation is None:
            activation = Identity()

        self.eps = eps
        self.activation = activation

    def forward(self, x):
        *_, n = x.shape
        assert (n % 2) == 0, "can only handle even number of features"

        loc = x[..., : (n // 2)]
        scale = x[..., (n // 2) :]

        loc = self.activation(loc)
        scale = self.eps + F.softplus(scale)

        return loc, scale

    def extra_repr(self):
        return f"eps={self.eps},"


class Reshape(torch.nn.Module):
    def __init__(self, shape):
        super().__init__()
        self.shape = tuple(shape)

    def forward(self, x):
        return x.reshape(self.shape)


class SplineBasis(torch.nn.Module):
    """Compute basis splines

    Example::

        basis = SplineBasis(knots, order=3)
        basis = torch.jit.script(basis)

        x = np.linspace(0, 4, 100)
        r = n2n(basis, dtype="float32")(x)

        plt.plot(x, r)
    """

    def __init__(self, knots, order, eps=1e-6):
        super().__init__()

        self.order = order

        knots = torch.as_tensor(knots)
        knots = (
            knots[0, None].repeat(order + 1),
            knots[1:-1],
            knots[-1, None].repeat(order + 1),
        )

        self.knots = torch.cat(knots)

        # NOTE: for torch==1.7.0 jitting requires this combination of tensor / float
        self.eps = torch.tensor(eps)
        self.lower = float(self.knots[0]) + eps
        self.upper = float(self.knots[-1]) - eps

        self.n_splines = len(self.knots) - (1 + order)

    def forward(self, x):
        # adapted from https://en.wikipedia.org/wiki/B-spline
        x = x[..., None]
        knots = self.knots

        res = (knots[:-1] < x).type_as(x) * (x <= knots[1:]).type_as(x)

        for k in range(1, self.order + 1):
            omega = (x - knots[:-k]) / torch.maximum(self.eps, knots[k:] - knots[:-k])
            res = omega[..., :-1] * res[..., :-1] + (1 - omega[..., 1:]) * res[..., 1:]

        return res


class SplineFunction(torch.nn.Module):
    """A function based on splines

    Example::

        func = SplineFunction([0.0, 1.0, 2.0, 3.0, 4.0], order=3)
        func = torch.jit.script(func)

        optim = torch.optim.Adam(func.parameters(), lr=1e-1)

        for _ in range(200):
            optim.zero_grad()
            loss = ((y - func(x)) ** 2.0).mean()
            loss.backward()
            optim.step()

    """

    def __init__(self, knots, order):
        super().__init__()

        self.basis = SplineBasis(knots=knots, order=order)
        self.coeffs = torch.nn.Parameter(torch.randn(self.basis.n_splines))

    def forward(self, x):
        lower = self.basis.lower
        upper = self.basis.upper

        x = torch.clip(x, lower, upper)
        x = self.basis(x)
        return (self.coeffs * x).sum(-1)


class NumpyDataset(torch.utils.data.Dataset):
    """A PyTorch datast composed out of structured numpy array.

    :param data:
        the (structured) data. Nones are returned as is-is.
    :param dtype:
        if given a (structured) dtype to apply to the data
    :param filter:
         an optional boolean mask indicating which items are available
    :param sequences:
        see ``chmp.ds.smap``
    :param mappings:
        see ``chmp.ds.smap``
    """

    def __init__(
        self,
        data,
        dtype=None,
        sequences=default_sequences,
        mappings=default_mappings,
        filter=None,
    ):
        self.data = data
        self.dtype = copy_structure(data, dtype, mappings=mappings, sequences=sequences)
        self.length = self._guess_length()
        self.sequences = sequences
        self.mappings = mappings

        if filter is not None:
            (self.valid_idx,) = np.nonzero(filter)

        else:
            self.valid_idx = np.arange(self.length)

    def filter(self, func):
        """Evaluate a filter on the full data set and set the filter of this dataset"""
        return NumpyDataset(
            self.data,
            dtype=self.dtype,
            sequences=self.sequences,
            mappings=self.mappings,
            filter=func(self),
        )

    def _guess_length(self):
        candidates = set()

        def _add_len(obj):
            if obj is not None:
                candidates.add(len(obj))

        smap(_add_len, self.data)

        if len(candidates) != 1:
            raise ValueError(f"Arrays with different lengths: {candidates}")

        (length,) = candidates
        return length

    def __len__(self):
        return len(self.valid_idx)

    def __getitem__(self, idx):
        def _get(item, dtype):
            if item is None:
                return None

            return np.asarray(item[self.valid_idx[idx]], dtype=dtype)

        return smap(
            _get,
            self.data,
            self.dtype,
            sequences=self.sequences,
            mappings=self.mappings,
        )


@register_unknown_kl(torch.distributions.LogNormal, torch.distributions.Gamma)
def kl_divergence__gamma__log_normal(p, q):
    """Compute the kl divergence with a Gamma prior and LogNormal approximation.

    Taken from C. Louizos, K. Ullrich, M. Welling "Bayesian Compression for Deep Learning"
    https://arxiv.org/abs/1705.08665
    """
    return (
        q.concentration * torch.log(q.rate)
        + torch.lgamma(q.concentration)
        - q.concentration * p.loc
        + torch.exp(p.loc + 0.5 * p.scale ** 2) / q.rate
        - 0.5 * (torch.log(p.scale ** 2.0) + 1 + np.log(2 * np.pi))
    )


class AutoGradient:
    def __init__(self):
        pass

    def __call__(self, compute_loss):
        loss = compute_loss()
        loss.backward()
        return loss, torch.tensor(0.0, device=loss.device)


class ESGradient:
    """Estimate the gradient of a function using Evolution Strategies

    The gradient will be assigned to the ``grad`` property of the parameters.
    This way any PyTorch optimizer can be used. As the tensors are manipulated
    in-place, they must not require gradients. For modules or tensors call
    ``requires_grad_(False)`` before using ``ESGradient``. The return value will
    be the mean and std of the loss.

    Usage::

        grad_fn = ESGradient(model.parameters())
        optimizer = torch.optim.Adam(model.parameters())

        # ...
        optimizer.zero_grad()
        grad_fn(lambda: compute_loss(model))
        optimizer.step()

    :param parameters: the parameters as an iterable :param n_samples: the
        number of samples with which to estimate the gradient :param scale: the
        scale of the perturbation to use. Can be passed as a list with the same
        length as parameters to give different scales for each parameter.
    """

    def __init__(self, parameters, *, n_samples=50, scale=0.1):
        self.parameters = list(parameters)
        self.n_samples = n_samples
        self.scale = scale

    def __call__(self, compute_loss):
        return _add_es_grad(
            self.parameters,
            compute_loss,
            n_samples=self.n_samples,
            scale=self.scale,
        )


def _add_es_grad(params, compute_loss, *, n_samples, scale):
    assert n_samples % 2 == 0

    params = list(params)

    if not isinstance(scale, (list, tuple)):
        scale = [scale] * len(params)

    assert len(params) == len(scale)

    def _step(compute_param):
        for p, c, s in zip(params, centers, scale):
            p.copy_(compute_param(p, c, s))

        loss = compute_loss()

        for p, c, s in zip(params, centers, scale):
            p.grad.add_(loss / (n_samples * s) * (p - c))

        return [torch.as_tensor(loss)]

    with torch.no_grad():
        params = [p for p in params]
        centers = [p.clone() for p in params]

        for p in params:
            if p.grad is None:
                p.grad = torch.zeros_like(p)

        losses = []

        for _ in range(n_samples // 2):
            # compute the positive sample
            losses += _step(lambda _, c, s: c + s * torch.randn(c.shape))

            # compute the negative sample
            losses += _step(lambda p, c, _: c - (p - c))

        for p, c in zip(params, centers):
            p.copy_(c)

        losses = torch.stack(losses)
        return torch.mean(losses), torch.std(losses)


def update_moving_average(alpha, average, value):
    """Update iterables of tensors by an exponentially moving average.

    If ``average`` and ``value`` are passed as module parameters, this function
    can be used to make one module the moving average of the other module::

        target_value_function = copy.copy(value_function)
        target_value_function.requires_grad_(False)

        # ...

        update_moving_average(
            0.9,
            target_value_function.parameters(),
            value_function.parameters(),
        )

    """
    with torch.no_grad():
        for a, v in zip(average, value):
            a.mul_(alpha)
            a.add_((1 - alpha) * v)


class GradientAccumulation:
    """Add gradient accumulation around an another optimizer

    .. note::

        The gradients are simply added. To obtain the same effective learning
        rate, the learning rate of the optimizer should be most likely
        rescaled.

    """

    @classmethod
    def wrap_optional(cls, optimizer, steps=0):
        if steps <= 1:
            return optimizer

        return cls(optimizer, steps)

    def __init__(self, optimizer, steps):
        assert steps > 0

        self.optimizer = optimizer
        self.steps = steps

        self.offset = 0

    def add_param_group(self, param_group):
        self.optimizer.add_param_group(param_group)

    def load_state_dict(self, sd):
        self.offset = sd.pop("GradientAccumulation_offset")
        self.optimizer.load_state_dict(sd)

    def state_dict(self):
        sd = self.optimizer.state_dict()
        assert "GradientAccumulation_offset" not in sd
        sd["GradientAccumulation_offset"] = self.step

        return sd

    def zero_grad(self):
        if self.offset % self.steps == 0:
            self.optimizer.zero_grad()

    def step(self):
        if self.offset % self.steps == (self.steps - 1):
            self.optimizer.step()

        self.offset += 1
