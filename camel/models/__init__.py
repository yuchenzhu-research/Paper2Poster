# ========= Copyright 2023-2024 @ CAMEL-AI.org. All Rights Reserved. =========
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ========= Copyright 2023-2024 @ CAMEL-AI.org. All Rights Reserved. =========
import importlib

from .base_model import BaseModelBackend
from .model_factory import ModelFactory
from .model_manager import ModelManager, ModelProcessingError

_LAZY_EXPORTS = {
    "AnthropicModel": (".anthropic_model", "AnthropicModel"),
    "AzureOpenAIModel": (".azure_openai_model", "AzureOpenAIModel"),
    "CohereModel": (".cohere_model", "CohereModel"),
    "DeepSeekModel": (".deepseek_model", "DeepSeekModel"),
    "FishAudioModel": (".fish_audio_model", "FishAudioModel"),
    "GeminiModel": (".gemini_model", "GeminiModel"),
    "DeepInfraGeminiModel": (".gemini_model", "DeepInfraGeminiModel"),
    "GroqModel": (".groq_model", "GroqModel"),
    "InternLMModel": (".internlm_model", "InternLMModel"),
    "LiteLLMModel": (".litellm_model", "LiteLLMModel"),
    "MistralModel": (".mistral_model", "MistralModel"),
    "NemotronModel": (".nemotron_model", "NemotronModel"),
    "NvidiaModel": (".nvidia_model", "NvidiaModel"),
    "OllamaModel": (".ollama_model", "OllamaModel"),
    "OpenAIAudioModels": (".openai_audio_models", "OpenAIAudioModels"),
    "OpenAICompatibleModel": (".openai_compatible_model", "OpenAICompatibleModel"),
    "OpenAICompatibleModelV2": (
        ".openai_compatible_model_v2",
        "OpenAICompatibleModelV2",
    ),
    "OpenAIModel": (".openai_model", "OpenAIModel"),
    "OpenRouterModel": (".openrouter_model", "OpenRouterModel"),
    "QwenModel": (".qwen_model", "QwenModel"),
    "DeepInfraPhi4Model": (".qwen_model", "DeepInfraPhi4Model"),
    "RekaModel": (".reka_model", "RekaModel"),
    "SambaModel": (".samba_model", "SambaModel"),
    "SGLangModel": (".sglang_model", "SGLangModel"),
    "StubModel": (".stub_model", "StubModel"),
    "TogetherAIModel": (".togetherai_model", "TogetherAIModel"),
    "VLLMModel": (".vllm_model", "VLLMModel"),
    "YiModel": (".yi_model", "YiModel"),
    "ZhipuAIModel": (".zhipuai_model", "ZhipuAIModel"),
}

__all__ = [
    "BaseModelBackend",
    "OpenAIModel",
    "AzureOpenAIModel",
    "AnthropicModel",
    "MistralModel",
    "GroqModel",
    "StubModel",
    "ZhipuAIModel",
    "CohereModel",
    "ModelFactory",
    "ModelManager",
    "LiteLLMModel",
    "OpenAIAudioModels",
    "NemotronModel",
    "NvidiaModel",
    "OllamaModel",
    "VLLMModel",
    "SGLangModel",
    "GeminiModel",
    "OpenAICompatibleModel",
    "OpenAICompatibleModelV2",
    "RekaModel",
    "SambaModel",
    "TogetherAIModel",
    "YiModel",
    "QwenModel",
    "ModelProcessingError",
    "DeepSeekModel",
    "FishAudioModel",
    "InternLMModel",
    "OpenRouterModel",
    "DeepInfraPhi4Model",
    "DeepInfraGeminiModel",
]


def __getattr__(name):
    if name not in _LAZY_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module_name, attr_name = _LAZY_EXPORTS[name]
    module = importlib.import_module(module_name, __name__)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value
