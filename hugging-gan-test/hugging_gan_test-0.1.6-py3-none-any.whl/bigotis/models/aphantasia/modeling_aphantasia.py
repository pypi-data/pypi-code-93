import os
import math
import logging
from typing import *

import torch
import numpy as np
import clip
from PIL import Image
from bigotis.modeling_utils import ImageGenerator

logging.basicConfig(format='%(message)s', level=logging.INFO)

NUM_IMG_CHANNELS = 3
NUM_IMAGINARY_CHANNELS = 2


class Aphantasia(ImageGenerator):
    def __init__(
        self,
        device=None,
    ):
        super().__init__()

        if device is not None:
            self.device = device

        modeling_dir = os.path.dirname(os.path.abspath(__file__))
        modeling_cache_dir = os.path.join(modeling_dir, ".modeling_cache")
        os.makedirs(modeling_cache_dir, exist_ok=True)

    # From https://github.com/tensorflow/lucid/blob/master/lucid/optvis/param/spatial.py
    @staticmethod
    def compute_2d_img_freqs(
        height: int,
        width: int,
    ):
        y_freqs = np.fft.fftfreq(height)[:, None]

        # NOTE: when we have an odd input dimension we need to keep one
        # additional frequency and later cut off 1 pixel
        width_even_idx = (width + 1) // 2 if width % 2 == 1 else width // 2 + 1

        x_freqs = np.fft.fftfreq(width)[:width_even_idx]

        img_freqs = np.sqrt(x_freqs * x_freqs + y_freqs * y_freqs)

        return img_freqs

    @staticmethod
    def get_scale_from_img_freqs(
        img_freqs,
        decay_power,
    ):
        height, width = img_freqs.shape
        clamped_img_freqs = np.maximum(img_freqs, 1.0 / max(width, height))

        scale = 1.0 / clamped_img_freqs**decay_power
        scale *= np.sqrt(width * height)
        scale = torch.tensor(scale).float()[None, None, ..., None]

        return scale

    def fft_to_rgb(
        self,
        fft_img,
        scale,
        height,
        width,
        shift=None,
        contrast=1.,
        decorrelate=True,
    ):
        scaled_fft_img = scale * fft_img
        if shift is not None:
            scaled_fft_img += scale * shift

        img_size = (height, width)

        image = torch.irfft(
            scaled_fft_img,
            NUM_IMAGINARY_CHANNELS,
            normalized=True,
            signal_sizes=img_size,
        )
        image = image * contrast / image.std()  # keep contrast, empirical

        if decorrelate:
            colors = 1
            color_correlation_svd_sqrt = np.asarray([
                [0.26, 0.09, 0.02],
                [0.27, 0.00, -0.05],
                [0.27, -0.09, 0.03],
            ]).astype("float32")
            color_correlation_svd_sqrt /= np.asarray([
                colors,
                1.,
                1.,
            ])  # saturate, empirical

            max_norm_svd_sqrt = np.max(
                np.linalg.norm(color_correlation_svd_sqrt, axis=0))

            color_correlation_normalized = color_correlation_svd_sqrt / max_norm_svd_sqrt

            image_permute = image.permute(0, 2, 3, 1)
            image_permute = torch.matmul(
                image_permute,
                torch.tensor(color_correlation_normalized.T).to(self.device))

            image = image_permute.permute(0, 3, 1, 2)

        image = torch.sigmoid(image)

        return image

    def get_fft_img(
        self,
        height: int,
        width: int,
        batch_size: int = 1,
        std: float = 0.01,
        return_img_freqs=False,
    ):
        #NOTE: generata all possible freqs for the input image size
        img_freqs = self.compute_2d_img_freqs(
            height=height,
            width=width,
        )

        spectrum_shape = [
            batch_size,
            NUM_IMG_CHANNELS,
            *img_freqs.shape,
            NUM_IMAGINARY_CHANNELS,
        ]

        fft_img = (torch.randn(*spectrum_shape) * std)

        if return_img_freqs:
            return fft_img, img_freqs
        else:
            return fft_img

    def generate_from_prompt(
        self,
        prompt: str,
        lr: float = 3e-1,
        img_save_freq: int = 1,
        num_generations: int = 200,
        num_random_crops: int = 20,
        height: int = 256,
        width: int = 256,
    ):
        tokenized_text = clip.tokenize([prompt]).to(self.device).detach()
        text_logits = self.clip_model.encode_text(tokenized_text)

        fft_img, img_freqs = self.get_fft_img(
            height,
            width,
            batch_size=1,
            std=0.01,
            return_img_freqs=True,
        )

        fft_img = fft_img.to(self.device)
        fft_img.requires_grad = True

        scale = self.get_scale_from_img_freqs(
            img_freqs=img_freqs,
            decay_power=1,
        ).to(self.device)

        shift = None
        # if noise > 0:
        #     img_size = img_freqs.shape
        #     noise_size = (1, 1, *img_size, 1)
        #     shift = self.noise * torch.randn(noise_size, ).to(self.device)

        optimizer = torch.optim.Adam(
            [fft_img],
            lr,
        )

        # NOTE: with SGD the results are less complex but still good
        # optimizer = torch.optim.SGD(
        #     [fft_img],
        #     lr,
        # )

        gen_img_list = []
        gen_fft_list = []
        for step in range(num_generations):
            loss = 0

            initial_img = self.fft_to_rgb(
                fft_img=fft_img,
                scale=scale,
                height=height,
                width=width,
                shift=shift,
                contrast=1.0,
                decorrelate=True,
            )

            x_rec_stacked = self.augment(
                img_batch=initial_img,
                num_crops=num_random_crops,
                target_img_height=height,
                target_img_width=width,
            )
            loss += 10 * self.compute_clip_loss(x_rec_stacked, prompt)

            logging.info(f"\nIteration {step} of {num_generations}")
            logging.info(f"Loss {round(float(loss.data), 2)}")

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            if step % img_save_freq == 0:
                with torch.no_grad():
                    img = self.fft_to_rgb(
                        fft_img=fft_img,
                        scale=scale,
                        height=height,
                        width=width,
                        shift=shift,
                        contrast=1.0,
                        decorrelate=True,
                    )

                    img = img.detach().cpu().numpy()[0]
                    img = np.transpose(np.array(img)[:, :, :], (1, 2, 0))
                    img = np.clip(img * 255, 0, 255).astype(np.uint8)

                    pil_img = Image.fromarray(img)

                    gen_img_list.append(pil_img)
                    gen_fft_list.append(fft_img)

            torch.cuda.empty_cache()

        return gen_img_list, gen_fft_list

    def interpolate(
        self,
        fft_img_list,
        duration_list,
        height,
        width,
        **kwargs,
    ):
        fft_img, img_freqs = self.get_fft_img(
            height,
            width,
            batch_size=1,
            std=0.01,
            return_img_freqs=True,
        )

        scale = self.get_scale_from_img_freqs(
            img_freqs=img_freqs,
            decay_power=1,
        )
        scale = scale.to(self.device)

        gen_img_list = []
        fps = 25

        for idx, (fft_img,
                  duration) in enumerate(zip(fft_img_list, duration_list)):
            num_steps = int(duration * fps)
            fft_img_1 = fft_img
            fft_img_2 = fft_img_list[(idx + 1) % len(fft_img_list)]

            for step in range(num_steps):
                weight = math.sin(1.5708 * step / num_steps)**2
                fft_img_interp = weight * fft_img_2 + (1 - weight) * fft_img_1
                img = self.fft_to_rgb(
                    fft_img=fft_img_interp,
                    scale=scale,
                    height=height,
                    width=width,
                    shift=None,
                    contrast=1.0,
                    decorrelate=True,
                )
                img = img.detach().cpu().numpy()[0]
                img = np.transpose(np.array(img)[:, :, :], (1, 2, 0))
                img = np.clip(img * 255, 0, 255).astype(np.uint8)
                pil_img = Image.fromarray(img)

                gen_img_list.append(pil_img)

        return gen_img_list


if __name__ == '__main__':
    prompt = "'Tempus Fugit' by Salvador Dali"
    lr = 0.5
    img_save_freq = 1
    num_generations = 64
    num_random_crops = 32
    height = 256
    width = 512

    aphantasia = Aphantasia()
    gen_img_list, fft_logits_list = aphantasia.generate_from_prompt(
        prompt=prompt,
        lr=lr,
        img_save_freq=img_save_freq,
        num_generations=num_generations,
        num_random_crops=num_random_crops,
        height=height,
        width=width,
    )

    _gen_img_list, fft_logits_list_ = aphantasia.generate_from_prompt(
        prompt="'Tempus Fugit', by Escher",
        lr=lr,
        img_save_freq=img_save_freq,
        num_generations=num_generations,
        num_random_crops=num_random_crops,
        height=height,
        width=width,
    )

    fft_logits_interp_list = [fft_logits_list[-1], fft_logits_list_[-1]]

    duration_list = [0.7] * len(fft_logits_interp_list)
    interpolate_img_list = aphantasia.interpolate(
        fft_logits_list=fft_logits_interp_list,
        duration_list=duration_list,
        height=height,
        width=width,
    )
