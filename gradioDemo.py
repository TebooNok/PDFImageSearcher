import gradio as gr
from pdfImage import *


done = False
engine = None
tmp_dir = None


def main_interface(file, dpi, skip_page_front, skip_page_back, skip_block, lang, query):
    global done, engine, tmp_dir
    if not done:
        # Load PDF, Convert to Image, Description, and Index
        tmp_dir = load_pdf(file.name, dpi, skip_page_front, skip_page_back, skip_block, lang)
        ix, _ = build_index(file.name, tmp_dir, lang)
        engine = ix
        done = True
    results_list = search(engine, query, lang)
    return return_image(file.name, results_list, tmp_dir)

    # Ensure that the image save directory and index directory are deleted
    # base_name = os.path.basename(file).split('.')[0]
    # path_name = f'images{base_name}'
    # index_path = f'{base_name}_index_dir'
    # if os.path.exists(path_name):
    #     shutil.rmtree(path_name)
    # if os.path.exists(index_path):
    #     shutil.rmtree(index_path)
    # return titles, images


def display_images(*images):
    return images


iface = gr.Interface(
    fn=main_interface,
    inputs=[
        gr.inputs.File(label="Upload PDF"),
        gr.inputs.Number(default=300, label="DPI"),
        gr.inputs.Number(default=0, label="Skip Front Page"),
        gr.inputs.Number(default=1, label="Skip Back Page"),
        gr.inputs.Number(default=5, label="Skip Block"),
        gr.inputs.Dropdown(choices=["CN", "EN"], default="CN", label="Language"),
        gr.inputs.Textbox(label="Search Query")
    ],
    outputs=[
        gr.outputs.Textbox(label="Title"),
        gr.outputs.Image(type="pil", label="Image")
    ],
    live=False
)

iface.launch()
