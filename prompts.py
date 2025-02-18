def make_prompt(prompt, slide_count, additional_info):
    """
    Create a structured prompt for generating a presentation.

    Args:
        prompt (str): The topic of the presentation.
        slide_count (int): The number of slides required.
        additional_info (str): Additional instructions or details for the presentation.

    Returns:
        str: The formatted prompt.
    """
    if slide_count:
        slide_count_text = f" EXACTLY {slide_count} slides"
    else:
        slide_count_text = "At least 8 slides/contents."

    additional_info_text = f"Also consider this for the presentation:\n{additional_info}" if additional_info else ""

    main_prompt = f"""
Write a presentation text about "{prompt}". You must follow these instructions:
- The presentation have {slide_count_text}(Count starts from 1).
- Each slide has text no longer than 1000 characters.
- Include Atleast 5 points per Slide.
- Use very short and concise titles.
- The presentation must be easy to understand.
- Include a table of contents that matches the slide count.
- Include a summary slide at the end.
- From beginning to the end the number of slides should not exceed the slide count.
- Do not include links or images.
- Do not repeat the information in slides.
- you can include information remotely similar to the topic "{prompt}" ONLY if you cannot add anymore information.
{additional_info_text}

Example format - Stick to this formatting exactly:

Title: TITLE OF THE PRESENTATION

Slide: 1
Header: TABLE OF CONTENT
Content: 1. CONTENT OF THIS POWERPOINT
2. CONTENT OF THIS POWERPOINT
3. CONTENT OF THIS POWERPOINT
...

Slide: 2
Header: TITLE OF SLIDE
Content: CONTENT OF THE SLIDE

Slide: 3
Header: TITLE OF SLIDE
Content: CONTENT OF THE SLIDE

...

Slide: X
Header: SUMMARY
Content: CONTENT OF THE SUMMARY


"""
    return main_prompt


