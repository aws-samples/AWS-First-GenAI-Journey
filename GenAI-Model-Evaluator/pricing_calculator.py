# TODO: Edit model versions available to choose
# TODO: We need to validate the Claude 3 Haiku pricing, it seems to be constantly returning 0
def calculate_input_price(token_number, model_id):
    """
    Calculate the cost for a given number of input tokens based on the model used.

    :param token_number: Number of input tokens (int).
    :param model_id: Identifier of the model (str).
    :return: The cost calculated based on the input tokens and the model used (float).Returns 0 if the model_id is not
    found in the predefined dictionary.
    """
    # Dictionary containing prices per 1000 tokens for different models
    model_input_token_prices = {
        'amazon.titan-embed-text-v1': 0.0001,
        'amazon.titan-embed-text-v2:0': 0.00002,
        'amazon.titan-text-lite-v1': 0.0003,
        'amazon.titan-text-express-v1': 0.0075,
        'ai21.j2-mid-v1': 0.0125,
        'ai21.j2-ultra-v1': 0.0188,
        'anthropic.claude-instant-v1': 0.00080,
        'anthropic.claude-v2': 0.00800,
        'anthropic.claude-v2:1': 0.00800,
        'anthropic.claude-3-sonnet-20240229-v1:0': 0.00300,
        'anthropic.claude-3-haiku-20240307-v1:0': 0.0002500,
        'anthropic.claude-sonnet-4-6': 0.00300,
        'anthropic.claude-haiku-4-5-20251001-v1:0': 0.00100,
        'cohere.command-text-v14': 0.0015,
        'cohere.command-light-text-v14': 0.0003,
        'cohere.embed-english-v3': 0.0001,
        'cohere.embed-multilingual-v3': 0.0001,
        'meta.llama2-13b-chat-v1': 0.00075,
        'meta.llama2-70b-chat-v1': 0.00195,
        'meta.llama3-8b-instruct-v1:0': 0.0004,
        'meta.llama3-70b-instruct-v1:0': 0.00265,
        'mistral.mistral-large-2402-v1:0': 0.008,
        'mistral.mistral-7b-instruct-v0:2': 0.00015,
        'mistral.mixtral-8x7b-instruct-v0:1': 0.00045,
        'gpt-4-0125-preview': 0.01,
        'gpt-4-32k': 0.06
    }

    # Check if the provided model_id exists in our dictionary
    if model_id in model_input_token_prices:
        # Get the price per 1000 input tokens for the given model_id
        price_per_1000_tokens = model_input_token_prices[model_id]
        # Calculate the cost for the given number of input tokens
        cost = (token_number / 1000) * price_per_1000_tokens
        # return the final input token cost, rounded to the 8 decimal place
        return round(cost, 8)
    else:
        # Return 0 if the model_id is not found in the dictionary
        return 0


def calculate_output_price(token_number, model_id):
    """
    Calculate the cost for a given number of output tokens based on the model used.

    :param token_number: Number of output tokens (int).
    :param model_id: Identifier of the model (str).
    :return: The cost calculated based on the output tokens and the model used (float).
             Returns 0 if the model_id is not found in the predefined dictionary.
    """
    # Dictionary containing prices per 1000 output tokens for different models
    model_output_token_prices = {
        'amazon.titan-text-lite-v1': 0.0004,
        'amazon.titan-text-express-v1': 0.0016,
        'ai21.j2-mid-v1': 0.0125,
        'ai21.j2-ultra-v1': 0.0188,
        'anthropic.claude-instant-v1': 0.00240,
        'anthropic.claude-v2': 0.02400,
        'anthropic.claude-v2:1': 0.02400,
        'anthropic.claude-3-sonnet-20240229-v1:0': 0.01500,
        'anthropic.claude-3-haiku-20240307-v1:0': 0.0012500,
        'anthropic.claude-sonnet-4-6': 0.01500,
        'anthropic.claude-haiku-4-5-20251001-v1:0': 0.00500,
        'cohere.command-text-v14': 0.00200,
        'cohere.command-light-text-v14': 0.00060,
        'meta.llama2-13b-chat-v1': 0.00100,
        'meta.llama2-70b-chat-v1': 0.00256,
        'meta.llama3-8b-instruct-v1:0': 0.0006,
        'meta.llama3-70b-instruct-v1:0': 0.0035,
        'mistral.mistral-large-2402-v1:0': 0.024,
        'mistral.mistral-7b-instruct-v0:2': 0.00020,
        'mistral.mixtral-8x7b-instruct-v0:1': 0.00070,
        'gpt-4-0125-preview': 0.03,
        'gpt-4-32k': 0.12
    }
    # Check if the provided model_id exists in our dictionary
    if model_id in model_output_token_prices:
        # Get the price per 1000 output tokens for the given model_id
        price_per_1000_tokens = model_output_token_prices[model_id]
        # Calculate the cost for the given number of output tokens
        cost = (token_number / 1000) * price_per_1000_tokens
        # return the final output token cost, rounded to the 8 decimal place
        return round(cost, 8)
    else:
        # Return 0 if the model_id is not found in the dictionary
        return 0

# TODO: Document this function better
def calculate_total_price(input_tokens, output_tokens, model):
    """
    Calculate the input token cost, output token cost, total cost for one invocation and total cost for 1000 invocations based on
    a given number of input and output tokens and on the specific model used.

    :param input_tokens: Number of input tokens (int).
    :param output_tokens: Number of output tokens (int).
    :param model: Identifier of the model (str).
    :return: The input token cost, output token cost, and total cost, and total cost per 1000 invocations calculated based on
    the input and output tokens and the model used (float).
    """
    # Calculate the input and output token costs
    input_cost = calculate_input_price(input_tokens, model)
    output_cost = calculate_output_price(output_tokens, model)
    # Calculate the total cost
    total_cost = round(input_cost + output_cost, 6)
    total_cost_1000 = round(total_cost * 1000, 6)
    # return the final total cost, rounded to the 8 decimal place
    return input_cost, output_cost, total_cost, total_cost_1000
