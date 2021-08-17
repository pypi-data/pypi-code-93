import abc

import torch
import torchvision
import clip


class ImageGenerator(metaclass=abc.ABCMeta):
    def __init__(self, ):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"USING {self.device}")

        self.clip_input_img_size = 224

        self.clip_model, _clip_preprocess = clip.load(
            "ViT-B/32",
            device=self.device,
        )
        self.clip_model = self.clip_model.eval()

        self.clip_norm_trans = torchvision.transforms.Normalize(
            (0.48145466, 0.4578275, 0.40821073),
            (0.26862954, 0.26130258, 0.27577711),
        )

        self.aug_transform = torch.nn.Sequential(
            torchvision.transforms.RandomHorizontalFlip(),
            torchvision.transforms.RandomAffine(24, (.1, .1)),
        ).to(self.device)

    def augment(
        self,
        img_batch,
        target_img_width,
        target_img_height,
        num_crops=32,
        crop_scaler=1,
    ):
        x_pad_size = target_img_width // 2
        y_pad_size = target_img_height // 2
        img_batch = torch.nn.functional.pad(
            img_batch,
            (
                x_pad_size,
                x_pad_size,
                y_pad_size,
                y_pad_size,
            ),
            mode='constant',
            value=0,
        )

        img_batch = self.aug_transform(img_batch)

        min_img_size = min(target_img_width, target_img_height)

        augmented_img_list = []
        for crop in range(num_crops):
            crop_size = int(
                torch.normal(
                    1.2,
                    .3,
                    (),
                ).clip(.43, 1.9) * min_img_size)

            if crop > num_crops - 4:
                crop_size = int(min_img_size * 1.4)

            offsetx = torch.randint(
                0,
                int(target_img_width * 2 - crop_size),
                (),
            )
            offsety = torch.randint(
                0,
                int(target_img_height * 2 - crop_size),
                (),
            )
            augmented_img = img_batch[:, :, offsety:offsety + crop_size,
                                      offsetx:offsetx + crop_size, ]
            augmented_img = torch.nn.functional.interpolate(
                augmented_img,
                (int(224 * crop_scaler), int(224 * crop_scaler)),
                mode='bilinear',
                align_corners=True,
            )
            augmented_img_list.append(augmented_img)

        img_batch = torch.cat(augmented_img_list, 0)

        up_noise = 0.11
        img_batch = img_batch + up_noise * torch.rand(
            (img_batch.shape[0], 1, 1, 1)).to(self.device) * torch.randn_like(
                img_batch, requires_grad=False)

        return img_batch

    def get_clip_img_encodings(
        self,
        img_batch: torch.Tensor,
        do_preprocess: bool = True,
    ):
        if do_preprocess:
            img_batch = self.clip_norm_trans(img_batch)
            img_batch = torch.nn.functional.upsample_bilinear(
                img_batch,
                (self.clip_input_img_size, self.clip_input_img_size),
            )

        img_logits = self.clip_model.encode_image(img_batch)
        img_logits = img_logits / img_logits.norm(dim=-1, keepdim=True)

        return img_logits

    def compute_clip_loss(
        self,
        img_batch: torch.Tensor,
        text: str,
    ):
        img_logits = self.get_clip_img_encodings(img_batch)

        tokenized_text = clip.tokenize([text])
        tokenized_text = tokenized_text.to(self.device).detach().clone()
        text_logits = self.clip_model.encode_text(tokenized_text)

        text_logits = text_logits / text_logits.norm(dim=-1, keepdim=True)

        loss = -torch.cosine_similarity(text_logits, img_logits).mean()

        return loss

    @abc.abstractmethod
    def generate_from_prompt(
        self,
        *args,
        **kwargs,
    ):
        raise NotImplementedError(
            '`generate_from_prompt` method must be defined by the user.')