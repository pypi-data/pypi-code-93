from pathlib import Path

from openpecha.cli import download_pecha

from pedurma.utils import from_yaml, to_yaml


def get_text_info(text_id, index):
    texts = index["annotations"]
    for uuid, text in texts.items():
        if text["work_id"] == text_id:
            return (uuid, text)
    return ("", "")


def get_page_num(page_ann):
    pg_num = int(page_ann[:-1]) * 2
    pg_face = page_ann[-1]
    if pg_face == "a":
        pg_num -= 1
    return pg_num


def get_start_page(pagination, start):
    pages = pagination["annotations"]
    for uuid, page in pages.items():
        if page["span"]["end"] > start:
            return get_page_num(page["page_index"])
    return ""


def get_pg_index(pg_num):
    pg_idx = ""
    base_pg_num = int(pg_num / 2)
    if pg_num % 2 == 0:
        pg_idx = f"{base_pg_num}b"
    else:
        pg_idx = f"{base_pg_num+1}a"
    return pg_idx


def get_pg_offset(first_pg_ref, span, pagination_layer):
    start = span["start"]
    start_page = get_start_page(pagination_layer, start)
    return start_page - first_pg_ref


def update_pagination_annotation(durchen_pg_ref_uuid, pg_idx, paginations):
    for uuid, pagination in paginations.items():
        if pagination["page_index"] == pg_idx:
            paginations[uuid]["note_ref"] = durchen_pg_ref_uuid
            return paginations
    return paginations


def get_page_uuid(pg_num, paginations):
    pg_idx = get_pg_index(pg_num)
    for uuid, pagination in paginations.items():
        if pagination["page_index"] == pg_idx:
            return uuid
    return ""


def add_note_pg_ref(page_to_edit, pagination_layer):
    try:
        start_pg = int(page_to_edit.ref_start_page_no)
        end_pg = int(page_to_edit.ref_end_page_no)
    except Exception:
        return pagination_layer
    durchen_image_num = page_to_edit.image_no
    offset = durchen_image_num - int(page_to_edit.page_no)
    paginations = pagination_layer["annotations"]
    durchen_pg_ref_uuid = get_page_uuid(durchen_image_num, paginations)
    if start_pg != 0 and end_pg != 0:
        for pg in range(start_pg, end_pg + 1):
            pg_num = pg + offset
            pg_idx = get_pg_index(pg_num)
            paginations = update_pagination_annotation(
                durchen_pg_ref_uuid, pg_idx, paginations
            )
    pagination_layer["annotations"] = paginations
    return pagination_layer

def is_valid_page_to_edit(prev_pg_to_edit, pg_to_edit):
    try:
        prev_pg_ref_end = int(prev_pg_to_edit.ref_end_page_no)
        cur_pg_ref_start = int(pg_to_edit.ref_start_page_no)
        cur_pg_ref_end = int(pg_to_edit.ref_end_page_no)
    except:
        return False
    if prev_pg_to_edit == pg_to_edit:
        if cur_pg_ref_end >= cur_pg_ref_start:
            return True
        else:
            return False
    elif prev_pg_to_edit.vol != pg_to_edit.vol and cur_pg_ref_start <= cur_pg_ref_end:
        return True
    elif cur_pg_ref_start <= cur_pg_ref_end and prev_pg_ref_end <= cur_pg_ref_start:
        return True
    else:
        return False

def update_pg_ref(vol, pages_to_edit, pagination_layer):
    prev_pg_edit = pages_to_edit[0]
    for page_to_edit in pages_to_edit:
        if vol == page_to_edit.vol:
            if is_valid_page_to_edit(prev_pg_edit, page_to_edit):
                pagination_layer = add_note_pg_ref(page_to_edit, pagination_layer)
        prev_pg_edit = page_to_edit
    return pagination_layer


def update_pagination(pecha_id, text_id, pedurma_edit_notes, index, pecha_path):
    text_uuid, text_info = get_text_info(text_id, index)
    for span in text_info["span"]:
        vol = span["vol"]
        pagination_layer = from_yaml(
            Path(f"{pecha_path}/{pecha_id}.opf/layers/v{int(vol):03}/Pagination.yml")
        )
        pagination_layer = update_pg_ref(vol, pedurma_edit_notes, pagination_layer)
        yield vol, pagination_layer


def update_text_pagination(pecha_id, text_id, pedurma_edit_notes):
    pecha_path = download_pecha(pecha_id, needs_update=False)
    index = from_yaml(Path(f"{pecha_path}/{pecha_id}.opf/index.yml"))
    for vol, new_pagination in update_pagination(
        pecha_id, text_id, pedurma_edit_notes, index, pecha_path
    ):
        new_pagination_yml = to_yaml(new_pagination)
        Path(
            f"{pecha_path}/P000792.opf/layers/v{int(vol):03}/Pagination.yml"
        ).write_text(new_pagination_yml, encoding="utf-8")
