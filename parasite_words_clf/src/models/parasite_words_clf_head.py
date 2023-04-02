import torch.nn as nn


class ParasiteWordsClfHead(nn.Module):
    def __init__(self, in_size, out_size):
        super(ParasiteWordsClfHead, self).__init__()
        self.layers = nn.Sequential(
            nn.Linear(in_size, out_size),
            nn.Sigmoid(),
        )

    def forward(self, x):
        x = self.layers(x)
        return x
