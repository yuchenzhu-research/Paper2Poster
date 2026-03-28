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

from .base import BaseAgent

_LAZY_EXPORTS = {
    "ChatAgent": (".chat_agent", "ChatAgent"),
    "CriticAgent": (".critic_agent", "CriticAgent"),
    "EmbodiedAgent": (".embodied_agent", "EmbodiedAgent"),
    "KnowledgeGraphAgent": (".knowledge_graph_agent", "KnowledgeGraphAgent"),
    "RoleAssignmentAgent": (".role_assignment_agent", "RoleAssignmentAgent"),
    "SearchAgent": (".search_agent", "SearchAgent"),
    "TaskCreationAgent": (".task_agent", "TaskCreationAgent"),
    "TaskPlannerAgent": (".task_agent", "TaskPlannerAgent"),
    "TaskPrioritizationAgent": (".task_agent", "TaskPrioritizationAgent"),
    "TaskSpecifyAgent": (".task_agent", "TaskSpecifyAgent"),
    "BaseToolAgent": (".tool_agents.base", "BaseToolAgent"),
    "HuggingFaceToolAgent": (
        ".tool_agents.hugging_face_tool_agent",
        "HuggingFaceToolAgent",
    ),
}

__all__ = [
    "BaseAgent",
    "ChatAgent",
    "TaskSpecifyAgent",
    "TaskPlannerAgent",
    "TaskCreationAgent",
    "TaskPrioritizationAgent",
    "CriticAgent",
    "BaseToolAgent",
    "HuggingFaceToolAgent",
    "EmbodiedAgent",
    "RoleAssignmentAgent",
    "SearchAgent",
    "KnowledgeGraphAgent",
]


def __getattr__(name):
    if name not in _LAZY_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module_name, attr_name = _LAZY_EXPORTS[name]
    module = importlib.import_module(module_name, __name__)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value
