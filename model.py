from huggingface_hub import InferenceClient
from transformers import AutoTokenizer
from prompts import make_prompt
client = InferenceClient(api_key="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")

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-Coder-32B-Instruct")

# local_model = AutoModelForCausalLM.from_pretrained(r"D:\SRM\4th_Year\Internship\Research\model\Qwen\qwen_2")

DEFAULT_PROMPT = "Refine the following content based on the question: {}\n\nContent:\n{}"
def generate_response(query, retrieved_content, slide_count=None, additional_info=None, use_api=True):
    """
    Generate a response using either the local fine-tuned Qwen model or the Hugging Face API.

    Args:
        query (str): The user query.
        retrieved_content (str): The content retrieved from Qdrant.
        slide_count (int, optional): The number of slides required.
        additional_info (str, optional): Additional instructions for the presentation.
        use_api (bool): Whether to use the Hugging Face API for inference or local model.

    Returns:
        str: The generated response.
    """
    print("executed this")
    if slide_count or additional_info:
        prompt = make_prompt(query, slide_count, additional_info)
        # print("inside prompt")
        # print("prompt is",prompt)

    else:
        prompt = DEFAULT_PROMPT.format(query, retrieved_content)

    return refine_content_via_api(prompt,slide_count)


def refine_content_via_api(prompt,slide_count):
    """
    Refine the content using the Hugging Face Inference API.

    Args:
        prompt (str): The formatted prompt for the model.

    Returns:
        str: The refined response from the model.
    """
    base_tokens = 500
    tokens_per_slide = 100
    max_tokens = base_tokens + (tokens_per_slide * slide_count)
    max_tokens = min(max_tokens, 4000)
    print(max_tokens)

    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]

    stream = client.chat.completions.create(
        model="Qwen/Qwen2.5-Coder-32B-Instruct",
        messages=messages,
        max_tokens=1000,
        stream=True
    )

    refined_response = ""
    for chunk in stream:
        refined_response += chunk.choices[0].delta.content

    return refined_response


# def refine_content_locally(prompt):
#     inputs = tokenizer(prompt, return_tensors="pt")
#     with torch.no_grad():
#         outputs = local_model.generate(inputs["input_ids"], max_length=2000)
#         print(outputs)
#     refined_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # return refined_response

