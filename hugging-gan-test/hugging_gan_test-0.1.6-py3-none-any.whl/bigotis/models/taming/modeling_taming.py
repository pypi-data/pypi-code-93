import os
import yaml
import math
import logging
import requests
from typing import *

import torch
import torchvision
from PIL import Image
from omegaconf import OmegaConf
from forks.taming_transformers.taming.models.vqgan import VQModel
from bigotis.modeling_utils import ImageGenerator

logging.basicConfig(format='%(message)s', level=logging.INFO)


class TamingDecoder(ImageGenerator):
    def __init__(
        self,
        target_img_size=256,
        device=None,
    ):
        super().__init__()

        self.target_img_size = target_img_size
        self.embed_size = self.target_img_size // 16

        if device is not None:
            self.device = device

        modeling_dir = os.path.dirname(os.path.abspath(__file__))
        modeling_cache_dir = os.path.join(modeling_dir, ".modeling_cache")
        os.makedirs(modeling_cache_dir, exist_ok=True)

        modeling_ckpt_path = os.path.join(modeling_cache_dir, 'last.ckpt')
        if not os.path.exists(modeling_ckpt_path):
            modeling_ckpt_url = 'https://heibox.uni-heidelberg.de/f/867b05fc8c4841768640/?dl=1'

            logging.info(
                f"Downloading pre-trained weights for VQ-GAN from {modeling_ckpt_url}"
            )
            results = requests.get(modeling_ckpt_url, allow_redirects=True)

            with open(modeling_ckpt_path, "wb") as ckpt_file:
                ckpt_file.write(results.content)

        # TODO: update the url with our own config using the correct paths
        modeling_config_path = os.path.join(modeling_cache_dir, 'model.yaml')
        if not os.path.exists(modeling_config_path):
            modeling_config_url = 'https://raw.githubusercontent.com/vipermu/taming-transformers/master/configs/custom_vqgan.yaml'

            logging.info(
                "Downloading `model.yaml` from vipermu taming-transformers fork"
            )
            results = requests.get(modeling_config_url, allow_redirects=True)

            with open(modeling_config_path, "wb") as yaml_file:
                yaml_file.write(results.content)

        vqgan_config_xl = self.load_config(
            config_path=modeling_config_path,
            display=False,
        )
        self.vqgan_model = self.load_vqgan(
            vqgan_config_xl,
            ckpt_path=modeling_ckpt_path,
        ).to(self.device)

    def vqgan_preprocess(
        self,
        img,
    ):
        img = img.convert("RGB")

        min_img_dim = min(img.size)

        scale_factor = self.target_img_size / min_img_dim
        scaled_img_dim = (round(scale_factor * img.size[0]),
                          round(scale_factor * img.size[1]))
        img = img.resize(scaled_img_dim, Image.LANCZOS)
        img = torchvision.transforms.functional.center_crop(
            img, output_size=2 * [self.target_img_size])
        img_tensor = torch.unsqueeze(torchvision.transforms.ToTensor()(img),
                                     0).to(self.device)

        img_tensor = 2. * img_tensor - 1.

        return img_tensor

    @staticmethod
    def load_config(config_path, display=False):
        config = OmegaConf.load(config_path)

        if display:
            logging.info(yaml.dump(OmegaConf.to_container(config)))

        return config

    @staticmethod
    def load_vqgan(
        config,
        ckpt_path=None,
    ):
        model = VQModel(**config.model.params)

        if ckpt_path is not None:
            # XXX: check wtf is going on here
            sd = torch.load(ckpt_path, map_location="cpu")["state_dict"]
            missing, unexpected = model.load_state_dict(sd, strict=False)

        return model.eval()

    def generate_from_prompt(
        self,
        prompt: str,
        lr: float = 0.5,
        img_save_freq: int = 1,
        num_generations: int = 200,
        num_random_crops: int = 20,
        img_batch=None,
        **kwargs,
    ):
        batch_size = 1

        z_logits = .5 * torch.randn(
            batch_size,
            256,
            self.embed_size,
            self.embed_size,
        ).to(self.device)

        z_logits = torch.nn.Parameter(
            torch.sinh(1.9 * torch.arcsinh(z_logits)), )

        if img_batch is not None:
            clip_img_z_logits = self.get_clip_img_encodings(img_batch)
            clip_img_z_logits = clip_img_z_logits.detach().clone()

            z, _, [_, _, indices] = self.vqgan_model.encode(img_batch)

            z_logits = torch.nn.Parameter(z)
            img_z_logits = z.detach().clone()

        optimizer = torch.optim.AdamW(
            params=[z_logits],
            lr=lr,
            betas=(0.9, 0.999),
            weight_decay=0.1,
        )

        gen_img_list = []
        z_logits_list = []
        for step in range(num_generations):
            loss = 0

            if step % img_save_freq == 0:
                z_logits_list.append(z_logits.detach().clone())

            z = self.vqgan_model.post_quant_conv(z_logits)
            x_rec = self.vqgan_model.decoder(z)
            x_rec = (x_rec.clip(-1, 1) + 1) / 2
            x_rec_stacked = self.augment(
                x_rec,
                num_crops=num_random_crops,
                target_img_width=self.target_img_size,
                target_img_height=self.target_img_size,
            )

            loss += 10 * self.compute_clip_loss(x_rec_stacked, prompt)

            if img_batch is not None:
                loss += -10 * torch.cosine_similarity(z_logits,
                                                      img_z_logits).mean()
            # if img_batch is not None:
            #     loss += -10 * torch.cosine_similarity(
            #         self.get_clip_img_encodings(x_rec), clip_img_z_logits).mean()

            logging.info(f"\nIteration {step} of {num_generations}")
            logging.info(f"Loss {round(float(loss.data), 2)}")

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            if step % img_save_freq == 0:
                x_rec_img = torchvision.transforms.ToPILImage(mode='RGB')(
                    x_rec[0])
                gen_img_list.append(x_rec_img)

            torch.cuda.empty_cache()

        return gen_img_list, z_logits_list

    def interpolate(
        self,
        z_logits_list,
        duration_list,
        **kwargs,
    ):
        gen_img_list = []
        fps = 25

        for idx, (z_logits,
                  duration) in enumerate(zip(z_logits_list, duration_list)):
            num_steps = int(duration * fps)
            z_logits_1 = z_logits
            z_logits_2 = z_logits_list[(idx + 1) % len(z_logits_list)]

            for step in range(num_steps):
                weight = math.sin(1.5708 * step / num_steps)**2
                z_logits = weight * z_logits_2 + (1 - weight) * z_logits_1

                z = self.vqgan_model.post_quant_conv(z_logits)
                x_rec = self.vqgan_model.decoder(z)
                x_rec = (x_rec.clip(-1, 1) + 1) / 2

                x_rec_img = torchvision.transforms.ToPILImage(mode='RGB')(
                    x_rec[0])
                gen_img_list.append(x_rec_img)

                torch.cuda.empty_cache()

        return gen_img_list


if __name__ == '__main__':
    prompt = "Pokemon of type fire"
    lr = 0.5
    img_save_freq = 1
    num_generations = 64
    num_random_crops = 64
    img_batch = None

    taming_decoder = TamingDecoder()
    gen_img_list, z_logits_list = taming_decoder.generate_from_prompt(
        prompt=prompt,
        lr=lr,
        img_save_freq=img_save_freq,
        num_generations=num_generations,
        num_random_crops=num_random_crops,
        img_batch=img_batch,
    )

    _gen_img_list, z_logits_list_ = taming_decoder.generate_from_prompt(
        prompt="Pokemon of type grass",
        lr=lr,
        img_save_freq=img_save_freq,
        num_generations=num_generations,
        num_random_crops=num_random_crops,
        img_batch=img_batch,
    )

    z_logits_interp_list = [z_logits_list[-1], z_logits_list_[-1]]

    duration_list = [0.7] * len(z_logits_interp_list)
    interpolate_img_list = taming_decoder.interpolate(
        z_logits_list=z_logits_interp_list,
        duration_list=duration_list,
    )
