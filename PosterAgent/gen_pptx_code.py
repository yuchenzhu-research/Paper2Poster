import re
import json

def sanitize_for_var(name):
    # Convert any character that is not alphanumeric or underscore into underscore.
    return re.sub(r'[^0-9a-zA-Z_]+', '_', name)

def initialize_poster_code(width, height, slide_object_name, presentation_object_name, utils_functions):
    code = utils_functions
    code += fr'''
# Poster: {presentation_object_name}
{presentation_object_name} = create_poster(width_inch={width}, height_inch={height})

# Slide: {slide_object_name}
{slide_object_name} = add_blank_slide({presentation_object_name})
'''

    return code

def save_poster_code(output_file, utils_functions, presentation_object_name):
    code = utils_functions
    code = fr'''
# Save the presentation
save_presentation({presentation_object_name}, file_name="{output_file}")
'''
    return code

def generate_panel_code(panel_dict, utils_functions, slide_object_name, visible=False, theme=None):
    code = utils_functions
    raw_name = panel_dict["panel_name"]
    var_name = 'var_' + sanitize_for_var(raw_name)

    code += fr'''
# Panel: {raw_name}
{var_name} = add_textbox(
    {slide_object_name}, 
    '{var_name}', 
    {panel_dict['x']}, 
    {panel_dict['y']}, 
    {panel_dict['width']}, 
    {panel_dict['height']}, 
    text="", 
    word_wrap=True,
    font_size=40,
    bold=False,
    italic=False,
    alignment="left",
    fill_color=None,
    font_name="Arial"
)
'''

    if visible:
        if theme is None:
            code += fr'''
# Make border visible
style_shape_border({var_name}, color=(0, 0, 0), thickness=5, line_style="solid")
'''
        else:
            code += fr'''
# Make border visible
style_shape_border({var_name}, color={theme['color']}, thickness={theme['thickness']}, line_style="{theme['line_style']}")
'''
    
    return code

def generate_textbox_code(
    text_dict,
    utils_functions,
    slide_object_name,
    visible=False,
    content=None,
    theme=None,
    tmp_dir='tmp',
    is_title=False,
):
    code = utils_functions
    raw_name = text_dict["textbox_name"]
    var_name = sanitize_for_var(raw_name)

    code += fr'''
# Textbox: {raw_name}
{var_name} = add_textbox(
    {slide_object_name},
    '{var_name}',
    {text_dict['x']},
    {text_dict['y']},
    {text_dict['width']},
    {text_dict['height']},
    text="",
    word_wrap=True,
    font_size=40,
    bold=False,
    italic=False,
    alignment="left",
    fill_color=None,
    font_name="Arial"
)
'''
    if visible:
        # Extract textbox_theme from full theme if needed
        textbox_border_theme = None
        if theme is not None and isinstance(theme, dict):
            textbox_border_theme = theme.get('textbox_theme')

        if textbox_border_theme is None:
            code += fr'''
# Make border visible
style_shape_border({var_name}, color=(255, 0, 0), thickness=5, line_style="solid")
'''
        else:
            code += fr'''
# Make border visible
style_shape_border({var_name}, color={textbox_border_theme['color']}, thickness={textbox_border_theme['thickness']}, line_style="{textbox_border_theme['line_style']}")
'''

    if content is not None:
        tmp_name = f'{tmp_dir}/{var_name}_content.json'
        json.dump(content, open(tmp_name, 'w'), indent=4)

        # Determine vertical alignment
        vertical_anchor = None
        if is_title and theme is not None and 'section_title_vertical_align' in theme:
            vertical_anchor = theme['section_title_vertical_align']

        if vertical_anchor:
            code += fr'''
fill_textframe({var_name}, json.load(open('{tmp_name}', 'r')), vertical_anchor="{vertical_anchor}")
'''
        else:
            code += fr'''
fill_textframe({var_name}, json.load(open('{tmp_name}', 'r')))
'''

    return code

def generate_figure_code(figure_dict, utils_functions, slide_object_name, img_path, visible=False, theme=None):
    code = utils_functions
    raw_name = figure_dict["figure_name"]
    var_name = sanitize_for_var(raw_name)

    code += fr'''
# Figure: {raw_name}
{var_name} = add_image(
    {slide_object_name}, 
    '{var_name}', 
    {figure_dict['x']}, 
    {figure_dict['y']}, 
    {figure_dict['width']}, 
    {figure_dict['height']}, 
    image_path="{img_path}"
)
'''

    if visible:
        if theme is None:
            code += fr'''
# Make border visible
style_shape_border({var_name}, color=(0, 0, 255), thickness=5, line_style="long_dash_dot")
'''
        else:
            code += fr'''
# Make border visible
style_shape_border({var_name}, color={theme['color']}, thickness={theme['thickness']}, line_style="{theme['line_style']}")
'''
    
    return code

def generate_poster_code(
    panel_arrangement_list,
    text_arrangement_list,
    figure_arrangement_list,
    presentation_object_name,
    slide_object_name,
    utils_functions,
    slide_width,
    slide_height,
    img_path,
    save_path,
    visible=False,
    content=None,
    check_overflow=False,
    theme=None,
    tmp_dir='tmp',
):
    code = ''
    code += initialize_poster_code(slide_width, slide_height, slide_object_name, presentation_object_name, utils_functions)

    def _clone_paragraph_spec_with_text(paragraphs_spec, text):
        if isinstance(paragraphs_spec, list) and paragraphs_spec:
            paragraph = json.loads(json.dumps(paragraphs_spec[0]))
        else:
            paragraph = {
                "alignment": "center",
                "bullet": False,
                "level": 0,
                "font_size": 40,
                "runs": [{"text": ""}],
            }

        runs = paragraph.get("runs", [])
        if not runs:
            runs = [{"text": ""}]

        first_run = json.loads(json.dumps(runs[0]))
        first_run["text"] = text
        paragraph["runs"] = [first_run]
        return [paragraph]

    def _extract_plain_text(paragraphs_spec):
        if isinstance(paragraphs_spec, str):
            return paragraphs_spec
        if not isinstance(paragraphs_spec, list):
            return "" if paragraphs_spec is None else str(paragraphs_spec)

        texts = []
        for paragraph in paragraphs_spec:
            for run in paragraph.get("runs", []):
                run_text = run.get("text", "")
                if run_text:
                    texts.append(run_text)
        return " ".join(texts).strip()

    def _split_rich_text_for_boxes(paragraphs_spec, count):
        if count <= 1:
            return [paragraphs_spec]

        plain_text = _extract_plain_text(paragraphs_spec)
        if not plain_text:
            return [_clone_paragraph_spec_with_text(paragraphs_spec, "") for _ in range(count)]

        words = plain_text.split()
        if len(words) <= count:
            parts = words + [""] * (count - len(words))
        else:
            parts = []
            start = 0
            for i in range(count):
                remaining_words = len(words) - start
                remaining_parts = count - i
                take = max(1, round(remaining_words / remaining_parts))
                end = min(len(words), start + take)
                parts.append(" ".join(words[start:end]))
                start = end
            if start < len(words):
                parts[-1] = (parts[-1] + " " + " ".join(words[start:])).strip()

        return [_clone_paragraph_spec_with_text(paragraphs_spec, part) for part in parts]

    if theme is None:
        panel_visible = visible
        textbox_visible = visible
        figure_visible = visible

        panel_theme, textbox_theme, figure_theme = None, None, None
    else:
        panel_visible = theme['panel_visible']
        textbox_visible = theme['textbox_visible']
        figure_visible = theme['figure_visible']
        panel_theme = theme['panel_theme']
        textbox_theme = theme['textbox_theme']
        figure_theme = theme['figure_theme']

    for p in panel_arrangement_list:
        code += generate_panel_code(p, '', slide_object_name, panel_visible, panel_theme)

    if check_overflow:
        t = text_arrangement_list[0]
        # Pass full theme for consistency
        code += generate_textbox_code(t, '', slide_object_name, textbox_visible, content, theme, tmp_dir, is_title=False)
    else:
        aligned_content = []
        aligned_title_flags = []
        if content is not None:
            boxes_by_panel = {}
            for textbox in text_arrangement_list:
                boxes_by_panel.setdefault(textbox["panel_id"], []).append(textbox)

            for panel_id, section_content in enumerate(content):
                panel_boxes = boxes_by_panel.get(panel_id, [])
                title_boxes = [box for box in panel_boxes if box["textbox_id"] == 0]
                title_parts = _split_rich_text_for_boxes(
                    section_content.get("title", []), len(title_boxes)
                )
                title_part_idx = 0

                for textbox in panel_boxes:
                    textbox_id = textbox["textbox_id"]
                    if textbox_id == 0:
                        textbox_content = title_parts[title_part_idx]
                        title_part_idx += 1
                        is_title = True
                    else:
                        textbox_content = section_content.get(f"textbox{textbox_id}", "")
                        is_title = False
                    aligned_content.append(textbox_content)
                    aligned_title_flags.append(is_title)

        for i in range(len(text_arrangement_list)):
            t = text_arrangement_list[i]
            if content is not None:
                textbox_content = aligned_content[i]
                is_title = aligned_title_flags[i]
            else:
                textbox_content = None
                is_title = False
            # Pass full theme (not textbox_theme) so vertical alignment config is available
            code += generate_textbox_code(t, '', slide_object_name, textbox_visible, textbox_content, theme, tmp_dir, is_title=is_title)

    for f in figure_arrangement_list:
        if img_path is None:
            code += generate_figure_code(f, '', slide_object_name, f['figure_path'], figure_visible, figure_theme)
        else:
            code += generate_figure_code(f, '', slide_object_name, img_path, figure_visible, figure_theme)

    code += save_poster_code(save_path, '', presentation_object_name)

    return code
