from x_transformers.x_transformers import *
from x_transformers import Decoder
from torch.nn import CrossEntropyLoss

class LucidLM2HF(nn.Module):
    def __init__(self, config, addl_decoder_config={}):
        r'''
        '''
        super().__init__()
        self.config = config # Before we turn int into a dict, save it
        config = config.to_dict() # Make nicer if possible (currently done so that we have `get`)

        attn_layers = Decoder(dim=config['n_embd'], depth=config['n_layer'], heads=config['n_head'], **addl_decoder_config)

        self.token_emb = nn.Embedding(config['vocab_size'], config['n_embd'])
        self.pos_emb = AbsolutePositionalEmbedding(config['n_embd'], config['n_positions']) if (config.get('use_pos_emb', True) \
                                                   and not attn_layers.has_pos_emb) else always(0)
        self.emb_dropout = nn.Dropout(config.get('emb_dropout', 0.))

        #self.project_emb = nn.Linear(config['n_embd'], config['n_embd']) if config['n_embd'] != config.get('n_embd_proj', config['n_embd']) \
        #                    else nn.Identity()
        self.project_emb = nn.Identity()

        self.attn_layers = attn_layers
        self.norm = nn.LayerNorm(config['n_embd'])

        self.init_()

        self.to_logits = nn.Linear(config['n_embd'], config['vocab_size']) if not config.get('tie_embedding', False) \
                                   else lambda t: t @ self.token_emb.weight.t()

        # memory tokens (like [cls]) from Memory Transformers paper
        num_memory_tokens = config.get('num_memory_tokens', 0)
        self.num_memory_tokens = num_memory_tokens
        if num_memory_tokens > 0:
            self.memory_tokens = nn.Parameter(torch.randn(num_memory_tokens, config['n_embd']))

            # let funnel encoder know number of memory tokens, if specified
            # TODO: think of a cleaner solution
            if hasattr(attn_layers, 'num_memory_tokens'):
                attn_layers.num_memory_tokens = num_memory_tokens

        # Use this to pass old mems to a new run
        self.mems = None


    def init_(self):
        nn.init.normal_(self.token_emb.weight, std = 0.02)


    def forward(self, input_ids=None, attention_mask=None, labels=None, **kwargs):
        r''' Runs the forward pass.

        Args:
            input_ids
            attention_mask
            labels
        '''
        config = self.config.to_dict()
        output = {} # Return a dictionary, easier than to find positions at which something has to be
        x = input_ids # Lazy
        b, n, device, num_mem = *x.shape, x.device, self.num_memory_tokens

        x = self.token_emb(x)
        x += self.pos_emb(x)
        x = self.emb_dropout(x)


        x = self.project_emb(x)

        if num_mem > 0:
            mem = repeat(self.memory_tokens, 'n d -> b n d', b = b)
            x = torch.cat((mem, x), dim = 1)

            # auto-handle masking after appending memory tokens
            if attention_mask is not None:
                attention_mask = F.pad(attention_mask, (num_mem, 0), value = True)


        x, intermediates = self.attn_layers(x, mask=attention_mask, mems=self.mems, return_hiddens=True, **kwargs)
        x = self.norm(x)

        mem, x = x[:, :num_mem], x[:, num_mem:]

        lm_logits = self.to_logits(x)
        output['logits'] = lm_logits

        if labels is not None:
            # Shift labels/ids to deal with ids==labels
            shift_logits = lm_logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            # Flatten the tokens
            loss_fct = CrossEntropyLoss()
            loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))
            output['loss'] = loss
        if config.get('return_mems', False):
            hiddens = intermediates.hiddens
            new_mems = list(map(lambda pair: torch.cat(pair, dim = -2), zip(self.mems, hiddens))) if exists(self.mems) else hiddens
            new_mems = list(map(lambda t: t[..., -config.get('max_mem_len', 0.):, :].detach(), new_mems))
            output['new_mems'] = new_mems
            self.mems = new_mems # If I understood correctly how this works
        if config.get('return_attn', False):
            attn_maps = list(map(lambda t: t.post_softmax_attn, intermediates.attn_intermediates))
            output['attn_maps'] = attn_maps

        return output

