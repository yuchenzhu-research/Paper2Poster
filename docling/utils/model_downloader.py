import logging
from pathlib import Path
from typing import Optional

from docling.datamodel.pipeline_options import smolvlm_picture_description
from docling.datamodel.settings import settings

_log = logging.getLogger(__name__)


def download_models(
    output_dir: Optional[Path] = None,
    *,
    force: bool = False,
    progress: bool = False,
    with_layout: bool = True,
    with_tableformer: bool = True,
    with_code_formula: bool = True,
    with_picture_classifier: bool = True,
    with_smolvlm: bool = True,
    with_easyocr: bool = True,
):
    if output_dir is None:
        output_dir = settings.cache_dir / "models"

    # Make sure the folder exists
    output_dir.mkdir(exist_ok=True, parents=True)

    if with_layout:
        from docling.models.layout_model import LayoutModel

        _log.info(f"Downloading layout model...")
        LayoutModel.download_models(
            local_dir=output_dir / LayoutModel._model_repo_folder,
            force=force,
            progress=progress,
        )

    if with_tableformer:
        from docling.models.table_structure_model import TableStructureModel

        _log.info(f"Downloading tableformer model...")
        TableStructureModel.download_models(
            local_dir=output_dir / TableStructureModel._model_repo_folder,
            force=force,
            progress=progress,
        )

    if with_picture_classifier:
        from docling.models.document_picture_classifier import (
            DocumentPictureClassifier,
        )

        _log.info(f"Downloading picture classifier model...")
        DocumentPictureClassifier.download_models(
            local_dir=output_dir / DocumentPictureClassifier._model_repo_folder,
            force=force,
            progress=progress,
        )

    if with_code_formula:
        from docling.models.code_formula_model import CodeFormulaModel

        _log.info(f"Downloading code formula model...")
        CodeFormulaModel.download_models(
            local_dir=output_dir / CodeFormulaModel._model_repo_folder,
            force=force,
            progress=progress,
        )

    if with_smolvlm:
        from docling.models.picture_description_vlm_model import (
            PictureDescriptionVlmModel,
        )

        _log.info(f"Downloading SmolVlm model...")
        PictureDescriptionVlmModel.download_models(
            repo_id=smolvlm_picture_description.repo_id,
            local_dir=output_dir / smolvlm_picture_description.repo_cache_folder,
            force=force,
            progress=progress,
        )

    if with_easyocr:
        from docling.models.easyocr_model import EasyOcrModel

        _log.info(f"Downloading easyocr models...")
        EasyOcrModel.download_models(
            local_dir=output_dir / EasyOcrModel._model_repo_folder,
            force=force,
            progress=progress,
        )

    return output_dir
