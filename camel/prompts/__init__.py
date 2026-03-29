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

from .base import CodePrompt, TextPrompt, TextPromptDict

_LAZY_EXPORTS = {
    "AISocietyPromptTemplateDict": (".ai_society", "AISocietyPromptTemplateDict"),
    "CodePromptTemplateDict": (".code", "CodePromptTemplateDict"),
    "EvaluationPromptTemplateDict": (".evaluation", "EvaluationPromptTemplateDict"),
    "GenerateTextEmbeddingDataPromptTemplateDict": (
        ".generate_text_embedding_data",
        "GenerateTextEmbeddingDataPromptTemplateDict",
    ),
    "ImageCraftPromptTemplateDict": (".image_craft", "ImageCraftPromptTemplateDict"),
    "MisalignmentPromptTemplateDict": (".misalignment", "MisalignmentPromptTemplateDict"),
    "MultiConditionImageCraftPromptTemplateDict": (
        ".multi_condition_image_craft",
        "MultiConditionImageCraftPromptTemplateDict",
    ),
    "ObjectRecognitionPromptTemplateDict": (
        ".object_recognition",
        "ObjectRecognitionPromptTemplateDict",
    ),
    "PersonaHubPrompt": (".persona_hub", "PersonaHubPrompt"),
    "PromptTemplateGenerator": (".prompt_templates", "PromptTemplateGenerator"),
    "RoleDescriptionPromptTemplateDict": (
        ".role_description_prompt_template",
        "RoleDescriptionPromptTemplateDict",
    ),
    "SolutionExtractionPromptTemplateDict": (
        ".solution_extraction",
        "SolutionExtractionPromptTemplateDict",
    ),
    "TaskPromptTemplateDict": (".task_prompt_template", "TaskPromptTemplateDict"),
    "TranslationPromptTemplateDict": (".translation", "TranslationPromptTemplateDict"),
    "VideoDescriptionPromptTemplateDict": (
        ".video_description_prompt",
        "VideoDescriptionPromptTemplateDict",
    ),
}

__all__ = [
    "TextPrompt",
    "CodePrompt",
    "TextPromptDict",
    "AISocietyPromptTemplateDict",
    "CodePromptTemplateDict",
    "MisalignmentPromptTemplateDict",
    "TranslationPromptTemplateDict",
    "EvaluationPromptTemplateDict",
    "RoleDescriptionPromptTemplateDict",
    "TaskPromptTemplateDict",
    "PromptTemplateGenerator",
    "PersonaHubPrompt",
    "SolutionExtractionPromptTemplateDict",
    "GenerateTextEmbeddingDataPromptTemplateDict",
    "ObjectRecognitionPromptTemplateDict",
    "ImageCraftPromptTemplateDict",
    "MultiConditionImageCraftPromptTemplateDict",
    "VideoDescriptionPromptTemplateDict",
]


def __getattr__(name):
    if name not in _LAZY_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module_name, attr_name = _LAZY_EXPORTS[name]
    module = importlib.import_module(module_name, __name__)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value
