def get_text_around_image(blocks, image_index, lang='CN', word_count=50):
    # print(len(blocks))
    # print(image_index)
    # Initialize text accumulator and word counter
    text_content = ''
    counter = word_count

    # Process blocks before the image
    for block in reversed(blocks[:image_index]):
        if 'lines' in block:  # Check if it's a text block
            for line in reversed(block['lines']):
                for span in reversed(line['spans']):
                    text = span['text']
                    # print(text)
                    text_content = text + '\n' + text_content
                    if lang == 'CN':
                        counter -= len(text)
                    else:
                        words = text.split(' ')
                        counter -= len(words)
                    if counter <= 0:
                        break
                if counter <= 0:
                    break
            if counter <= 0:
                break
    # print(text_content)
    counter = word_count  # Reset the word counter for blocks after the image

    # Process blocks after the image
    for block in blocks[image_index+1:]:
        if 'lines' in block:  # Check if it's a text block
            for line in block['lines']:
                for span in line['spans']:
                    text = span['text']
                    text_content += text + '\n'
                    if lang == 'CN':
                        counter -= len(text)
                    else:
                        words = text.split(' ')
                        counter -= len(words)
                    if counter <= 0:
                        break
                if counter <= 0:
                    break
            if counter <= 0:
                break
    # print(text_content)
    return text_content


# search the closest line above and below，check whether it contains 'figure'.
# Set this line as title of image if it does. Line below has higher priority.
def get_title_of_image(blocks, image_index, lang='CN'):
    # Initialize caption holder
    caption = None

    # Process blocks before the image to find a potential caption
    for block in reversed(blocks[:image_index]):
        if 'lines' in block:  # Check if it's a text block
            for line in reversed(block['lines']):
                for span in reversed(line['spans']):
                    text = span['text']
                    # If the text contains "图", assume it's a caption
                    if '图' in text or 'figure' in text.lower():
                        caption = text
                        break  # stop when found the first line that contains "图"
                if caption is not None:
                    break  # stop when found the first line that contains "图"
            if caption is not None:
                break  # stop when found the first line that contains "图"

    # Process blocks after the image to update the caption (if any)
    for block in blocks[image_index+1:]:
        if 'lines' in block:  # Check if it's a text block
            for line in block['lines']:
                for span in line['spans']:
                    text = span['text']
                    # If the text contains "图", assume it's a caption
                    if '图' in text or 'figure' in text.lower():
                        caption = text
                        break  # stop when found the first line that contains "图"
                if caption is not None:
                    break  # stop when found the first line that contains "图"
            if caption is not None:
                break  # stop when found the first line that contains "图"

    return f"title: {caption}" if caption else "title: Not Found"