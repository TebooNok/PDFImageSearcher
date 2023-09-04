def get_adjacent_lines(blocks, block_index):
    """
    Returns two lists: the lines of text before and after the block at block_index.
    Each list contains lines in order from closest to furthest from the block.
    """
    def is_same_line(origin1, origin2):
        # Adjust this threshold if needed
        THRESHOLD = 10
        return abs(origin1[1] - origin2[1]) < THRESHOLD

    def extract_spans_from_blocks(target_blocks):
        spans = []
        for block in target_blocks:
            if 'lines' in block:
                for line in block['lines']:
                    for span in line['spans']:
                        spans.append(span)
        return spans

    def merge_spans_to_lines(spans):
        if not spans:
            return []

        lines = []
        current_line = spans[0]['text']
        current_origin = spans[0]['origin']

        for span in spans[1:]:
            if is_same_line(span['origin'], current_origin):
                current_line += " " + span['text']
            else:
                lines.append(current_line.strip())
                current_line = span['text']
                current_origin = span['origin']

        lines.append(current_line.strip())
        return lines

    spans_before = extract_spans_from_blocks(blocks[:block_index])
    spans_after = extract_spans_from_blocks(blocks[block_index + 1:])

    lines_before = merge_spans_to_lines(spans_before)
    lines_after = merge_spans_to_lines(spans_after)

    return lines_before, lines_after


def get_text_around_image(blocks, image_index,  lang='CN', word_count=50):
    before_lines, after_lines = get_adjacent_lines(blocks, image_index)

    # print(before_lines)
    # print(after_lines)
    text_content = ""
    counter = word_count

    # Process lines before the image
    for line in reversed(before_lines):
        text_content = line + '\n' + text_content
        if lang == 'CN':
            counter -= len(line)
        else:
            counter -= len(line.split(' '))
        if counter <= 0:
            break

    # Reset the word counter for lines after the image
    counter = word_count

    # Process lines after the image
    for line in after_lines:
        text_content += line + '\n'
        if lang == 'CN':
            counter -= len(line)
        else:
            counter -= len(line.split(' '))
        if counter <= 0:
            break

    return text_content.strip()


def get_title_of_image(blocks, image_index, lang='CN'):
    before_lines, after_lines = get_adjacent_lines(blocks, image_index)

    # Search for a title in the lines before the image
    title = None
    for line in reversed(before_lines):
        if lang == 'CN' and '图' in line:
            title = f"title: {line}"
            break
        elif 'figure' in line.lower():
            title = f"title: {line}"
            break

    # Search for a title in the lines after the image
    for line in after_lines:
        if lang == 'CN' and '图 ' in line:
            return f"title: {line}"
        elif 'figure' in line.lower():
            return f"title: {line}"

    return title if title else "title: Not Found"
