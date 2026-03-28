import argparse
import json
import os
import random
import re
from pathlib import Path

import PIL
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import ImageRefMode, PictureItem, TableItem
from dotenv import load_dotenv
from jinja2 import Template
from tenacity import retry, stop_after_attempt

from camel.agents import ChatAgent
from camel.models import ModelFactory
from utils.src.utils import get_json_from_response
from utils.wei_utils import account_token, get_agent_config

load_dotenv()
IMAGE_RESOLUTION_SCALE = 5.0

pipeline_options = PdfPipelineOptions()
pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
pipeline_options.generate_page_images = True
pipeline_options.generate_picture_images = True

doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)


def _build_marker_fallback():
    try:
        import torch
        from marker.models import create_model_dict

        from utils.src.model_utils import parse_pdf
    except ImportError as exc:
        raise RuntimeError(
            "Docling parsing produced too little text and the optional marker "
            "fallback is unavailable. Install marker/torch extras or use a PDF "
            "that docling can parse on its own."
        ) from exc

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32
    return create_model_dict, parse_pdf, device, dtype


@retry(stop=stop_after_attempt(5))
def parse_raw(args, actor_config, version=1):
    raw_source = args.poster_path
    markdown_clean_pattern = re.compile(r"<!--[\s\S]*?-->")

    raw_result = doc_converter.convert(raw_source)

    raw_markdown = raw_result.document.export_to_markdown()
    text_content = markdown_clean_pattern.sub("", raw_markdown)

    if len(text_content) < 500:
        create_model_dict, parse_pdf, device, dtype = _build_marker_fallback()
        print(f"\nParsing with docling was insufficient, using marker on {device}\n")
        parser_model = create_model_dict(device=device, dtype=dtype)
        text_content, _rendered = parse_pdf(
            raw_source, model_lst=parser_model, save_file=False
        )

    if version == 1:
        template = Template(open("utils/prompts/gen_poster_raw_content.txt").read())
    elif version == 2:
        template = Template(open("utils/prompts/gen_poster_raw_content_v2.txt").read())
    else:
        raise ValueError(f"Unsupported parse_raw version: {version}")

    if args.model_name_t.startswith("vllm_qwen"):
        actor_model = ModelFactory.create(
            model_platform=actor_config["model_platform"],
            model_type=actor_config["model_type"],
            model_config_dict=actor_config["model_config"],
            url=actor_config["url"],
        )
    else:
        actor_model = ModelFactory.create(
            model_platform=actor_config["model_platform"],
            model_type=actor_config["model_type"],
            model_config_dict=actor_config["model_config"],
        )

    actor_sys_msg = (
        "You are the author of the paper, and you will create a poster for the paper."
    )

    actor_agent = ChatAgent(
        system_message=actor_sys_msg,
        model=actor_model,
        message_window_size=10,
        token_limit=actor_config.get("token_limit", None),
    )

    while True:
        prompt = template.render(markdown_document=text_content)
        actor_agent.reset()
        response = actor_agent.step(prompt)
        input_token, output_token = account_token(response)

        content_json = get_json_from_response(response.msgs[0].content)

        if len(content_json) > 0:
            break
        print("Error: Empty response, retrying...")
        if args.model_name_t.startswith("vllm_qwen"):
            text_content = text_content[:80000]

    if len(content_json["sections"]) > 9:
        selected_sections = (
            content_json["sections"][:2]
            + random.sample(content_json["sections"][2:-2], 5)
            + content_json["sections"][-2:]
        )
        content_json["sections"] = selected_sections

    has_title = False

    for section in content_json["sections"]:
        if (
            type(section) != dict
            or "title" not in section
            or "content" not in section
        ):
            print("Ouch! The response is invalid, the LLM is not following the format :(")
            print("Trying again...")
            raise RuntimeError("Invalid poster section format returned by model")
        if "title" in section["title"].lower():
            has_title = True

    if not has_title:
        print("Ouch! The response is invalid, the LLM is not following the format :(")
        raise RuntimeError("Poster outline did not include a title section")

    os.makedirs("contents", exist_ok=True)
    json.dump(
        content_json,
        open(
            f"contents/<{args.model_name_t}_{args.model_name_v}>_{args.poster_name}_raw_content.json",
            "w",
        ),
        indent=4,
    )
    return input_token, output_token, raw_result


def gen_image_and_table(args, conv_res):
    input_token, output_token = 0, 0

    output_dir = Path(f"<{args.model_name_t}_{args.model_name_v}>_images_and_tables/{args.poster_name}")
    output_dir.mkdir(parents=True, exist_ok=True)
    doc_filename = args.poster_name

    for page_no, page in conv_res.document.pages.items():
        page_no = page.page_no
        page_image_filename = output_dir / f"{doc_filename}-{page_no}.png"
        with page_image_filename.open("wb") as fp:
            page.image.pil_image.save(fp, format="PNG")

    table_counter = 0
    picture_counter = 0
    for element, _level in conv_res.document.iterate_items():
        if isinstance(element, TableItem):
            table_counter += 1
            element_image_filename = output_dir / f"{doc_filename}-table-{table_counter}.png"
            with element_image_filename.open("wb") as fp:
                element.get_image(conv_res.document).save(fp, "PNG")

        if isinstance(element, PictureItem):
            picture_counter += 1
            element_image_filename = (
                output_dir / f"{doc_filename}-picture-{picture_counter}.png"
            )
            with element_image_filename.open("wb") as fp:
                element.get_image(conv_res.document).save(fp, "PNG")

    md_filename = output_dir / f"{doc_filename}-with-images.md"
    conv_res.document.save_as_markdown(md_filename, image_mode=ImageRefMode.EMBEDDED)

    md_filename = output_dir / f"{doc_filename}-with-image-refs.md"
    conv_res.document.save_as_markdown(md_filename, image_mode=ImageRefMode.REFERENCED)

    html_filename = output_dir / f"{doc_filename}-with-image-refs.html"
    conv_res.document.save_as_html(html_filename, image_mode=ImageRefMode.REFERENCED)

    tables = {}

    table_index = 1
    for table in conv_res.document.tables:
        caption = table.caption_text(conv_res.document)
        if len(caption) > 0:
            table_img_path = (
                f"<{args.model_name_t}_{args.model_name_v}>_images_and_tables/"
                f"{args.poster_name}/{args.poster_name}-table-{table_index}.png"
            )
            table_img = PIL.Image.open(table_img_path)
            tables[str(table_index)] = {
                "caption": caption,
                "table_path": table_img_path,
                "width": table_img.width,
                "height": table_img.height,
                "figure_size": table_img.width * table_img.height,
                "figure_aspect": table_img.width / table_img.height,
            }

        table_index += 1

    images = {}
    image_index = 1
    for image in conv_res.document.pictures:
        caption = image.caption_text(conv_res.document)
        if len(caption) > 0:
            image_img_path = (
                f"<{args.model_name_t}_{args.model_name_v}>_images_and_tables/"
                f"{args.poster_name}/{args.poster_name}-picture-{image_index}.png"
            )
            image_img = PIL.Image.open(image_img_path)
            images[str(image_index)] = {
                "caption": caption,
                "image_path": image_img_path,
                "width": image_img.width,
                "height": image_img.height,
                "figure_size": image_img.width * image_img.height,
                "figure_aspect": image_img.width / image_img.height,
            }
        image_index += 1

    json.dump(
        images,
        open(
            f"<{args.model_name_t}_{args.model_name_v}>_images_and_tables/{args.poster_name}_images.json",
            "w",
        ),
        indent=4,
    )
    json.dump(
        tables,
        open(
            f"<{args.model_name_t}_{args.model_name_v}>_images_and_tables/{args.poster_name}_tables.json",
            "w",
        ),
        indent=4,
    )

    return input_token, output_token, images, tables


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--poster_name", type=str, default=None)
    parser.add_argument("--model_name", type=str, default="4o")
    parser.add_argument("--poster_path", type=str, required=True)
    parser.add_argument("--index", type=int, default=0)
    args = parser.parse_args()

    agent_config = get_agent_config(args.model_name)

    if args.poster_name is None:
        args.poster_name = (
            args.poster_path.split("/")[-1].replace(".pdf", "").replace(" ", "_")
        )

    input_token, output_token, raw_result = parse_raw(args, agent_config)
    gen_image_and_table(args, raw_result)

    print(f"Token consumption: {input_token} -> {output_token}")
