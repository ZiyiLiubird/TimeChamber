# Copyright (c) 2018-2022, NVIDIA Corporation
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from timechamber.ase.utils import amp_models

class ModelASEContinuous(amp_models.ModelAMPContinuous):
    def __init__(self, network):
        super().__init__(network)
        return

    def build(self, config):
        net = self.network_builder.build('ase', **config)
        for name, _ in net.named_parameters():
            print(name)
        # print(f"ASE config: {config}")
        obs_shape = config['input_shape']
        normalize_value = config.get('normalize_value', False)
        normalize_input = config.get('normalize_input', False)
        value_size = config.get('value_size', 1)
        return ModelASEContinuous.Network(net,obs_shape=obs_shape, normalize_value=normalize_value,
                                          normalize_input=normalize_input, value_size=value_size)


    class Network(amp_models.ModelAMPContinuous.Network):
        def __init__(self, a2c_network, obs_shape, normalize_value, normalize_input, value_size):
            super().__init__(a2c_network,
                             obs_shape=obs_shape, 
                             normalize_value=normalize_value,
                             normalize_input=normalize_input, 
                             value_size=value_size)
            return

        def forward(self, input_dict):
            is_train = input_dict.get('is_train', True)
            result = super().forward(input_dict)

            if (is_train):
                amp_obs = input_dict['amp_obs']
                enc_pred = self.a2c_network.eval_enc(amp_obs)
                result["enc_pred"] = enc_pred

            return result

        def eval_actor(self, obs, ase_latents, use_hidden_latents=False):
            processed_obs = self.norm_obs(obs)
            mu, sigma = self.a2c_network.eval_actor(obs=processed_obs, ase_latents=ase_latents)
            return mu, sigma

        def eval_critic(self, obs, ase_latents, use_hidden_latents=False):
            processed_obs = self.norm_obs(obs)
            value = self.a2c_network.eval_critic(processed_obs, ase_latents, use_hidden_latents)
            return value