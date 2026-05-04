import os
import boto3
from text_extractor_and_summarizer import (text_extraction, csv_extraction, text_formatter, invoke_anthropic, invoke_mistral, invoke_meta,
                                           invoke_cohere,
                                           invoke_amazon, invoke_AI21)
from orchestration_helper import OrchestrationHelper
from orchestration_rag_helper import OrchestrationRAGHelper
from pricing_calculator import calculate_total_price
from evaluation_steps import evaluate_model_output_orchestrator, evaluate_model_performance, dynamic_grading_criteria, evaluate_rag_output, evaluate_rag_performance
from plotting_and_reporting import write_evaluation_results, plot_model_comparisons, plot_model_performance_comparisons, plot_rag_comparisons, plot_rag_performance_comparisons
import logging
from timeit import default_timer as timer
import pandas as pd
from io import StringIO
from dotenv import load_dotenv
import asyncio
from AnthropicTokenCounter import AnthropicTokenCounter
from langchain_aws import ChatBedrock
from langchain_aws.embeddings import BedrockEmbeddings
from langchain_aws.retrievers.bedrock import AmazonKnowledgeBasesRetriever
from langchain.chains import RetrievalQA
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness, 
    answer_relevancy, 
    context_recall, 
    context_precision, 
    context_entity_recall, 
    answer_similarity, 
    answer_correctness
    )
from ragas.metrics.critique import (
    harmfulness, 
    maliciousness, 
    coherence, 
    correctness, 
    conciseness
    )






# Loading environment variables from a .env file.
load_dotenv()
# logging setup
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# Configuring the default AWS session using the provided profile name from environment variables.
boto3.setup_default_session(profile_name=os.getenv("profile_name"))
# Bedrock Runtime client used to invoke and question the models
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.getenv("region_name")
)


llm_for_text_generation = ChatBedrock(model_id="anthropic.claude-sonnet-4-6", client=bedrock_runtime) ##TODO update to allow user to select the model they want to use
llm_for_evaluation = ChatBedrock(model_id="anthropic.claude-sonnet-4-6", client=bedrock_runtime)

metrics = [
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
        context_entity_recall,
        answer_similarity,
        answer_correctness,
        harmfulness, 
        maliciousness, 
        coherence, 
        correctness, 
        conciseness
    ]


def final_evaluator(pdf_path, models, task_prompt="Summarize this document in 2 sentences.", max_tokens='4096'):
    """
    Evaluate multiple models for summarization and other evaluation metrics.

    :param pdf_path: Path to the PDF file.
    :param models: List of models to evaluate.

    :return: A tuple containing:
        - DataFrame: Evaluation results including model performance metrics and costs.
        - str: Summary of the evaluation results.
        - str: Evaluation of the costs for model selection.
        - DataFrame: Scoring rubric for the evaluated models.
    """
    # Extract the text out of the given PDF
    input_text_data = text_extraction(pdf_path)
    # Calculate the character count of the input text
    character_count = len(input_text_data)
    # Create the prompt for the models to evaluate
    prompt = task_prompt
    # Initialize an empty list to store results for each model
    results_list = []
    # Initialize an empty list to store the scoring rubric for each model
    score_rubric_list = []
    # Initialize an empty string to store the aggregated evaluation results
    evaluation_results = ""
    #create dynamic grading critera for the prompt
    dynamic_evaluation_criteria, dynamic_grading_scale = dynamic_grading_criteria(prompt)
    # for each mode evaluate 
    for model in models:
        if "stability" in model or "embed" in model:
            continue  # skips the current iteration and goes to the next model

        if "anthropic" in model:
            # Start timer
            start = timer()
            # Invoke the specific Anthropic model, and get the generated summary, input tokens and output tokens
            summary_invoke_response, input_token_count, output_token_count = invoke_anthropic(model, prompt,
                                                                                              input_text_data, max_tokens)
            # end timer
            end = timer()
            # calculate total time taken
            time_length = round(end - start, 2)
            # calculate time taken per character
            char_process_time = character_count / time_length
            # calculate costs for the model and the specific inference, specifically the input costs, output cost,
            # total costs and total costs per 1000 invocations
            input_cost, output_cost, total_cost, total_cost_1000 = calculate_total_price(input_token_count,
                                                                                         output_token_count, model)
            # evaluate the models performance against the grading rubric and return the final score, final summary
            # and the scoring rubric
            final_score, final_summary, final_score_rubric = asyncio.run(
                evaluate_model_output_orchestrator(input_text_data, model, summary_invoke_response, prompt,
                                                   dynamic_evaluation_criteria, dynamic_grading_scale))
            #  create a OrchestrationHelper object to store the results of the evaluation
            result = OrchestrationHelper(model, time_length, character_count, char_process_time, input_cost,
                                         output_cost,
                                         total_cost, total_cost_1000, final_score, summary_invoke_response,
                                         final_summary)
            # add the results of the evaluation to the results list
            results_list.append(result.format())
            # add the evaluation results written summary to the evaluation results string
            evaluation_results += result.evaluation_results()
            # add the scoring rubric for the model into the scoring rubric list
            score_rubric_list.append(final_score_rubric)

        if "mistral" in model:
            # Start timer
            start = timer()
            # Invoke the specific Mistral model, and get the generated summary, input tokens and output tokens
            summary_invoke_response, input_token_count, output_token_count = invoke_mistral(model, prompt,
                                                                                              input_text_data, max_tokens)
            # end timer
            end = timer()
            # calculate total time taken
            time_length = round(end - start, 2)
            # calculate time taken per character
            char_process_time = character_count / time_length
            # calculate costs for the model and the specific inference, specifically the input costs, output cost,
            # total costs and total costs per 1000 invocations
            input_cost, output_cost, total_cost, total_cost_1000 = calculate_total_price(input_token_count,
                                                                                         output_token_count, model)
            # evaluate the models performance against the grading rubric and return the final score, final summary
            # and the scoring rubric
            final_score, final_summary, final_score_rubric = asyncio.run(
                evaluate_model_output_orchestrator(input_text_data, model, summary_invoke_response, prompt,
                                                   dynamic_evaluation_criteria, dynamic_grading_scale))
            #  create a OrchestrationHelper object to store the results of the evaluation
            result = OrchestrationHelper(model, time_length, character_count, char_process_time, input_cost,
                                         output_cost,
                                         total_cost, total_cost_1000, final_score, summary_invoke_response,
                                         final_summary)
            # add the results of the evaluation to the results list
            results_list.append(result.format())
            # add the evaluation results written summary to the evaluation results string
            evaluation_results += result.evaluation_results()
            # add the scoring rubric for the model into the scoring rubric list
            score_rubric_list.append(final_score_rubric)

        if "meta" in model:
            # Start timer
            start = timer()
            # Invoke the specific Meta model, and get the generated summary, input tokens and output tokens
            summary_invoke_response, input_token_count, output_token_count = invoke_meta(model, prompt,
                                                                                              input_text_data, max_tokens)
            # end timer
            end = timer()
            # calculate total time taken
            time_length = round(end - start, 2)
            # calculate time taken per character
            char_process_time = character_count / time_length
            # calculate costs for the model and the specific inference, specifically the input costs, output cost,
            # total costs and total costs per 1000 invocations
            input_cost, output_cost, total_cost, total_cost_1000 = calculate_total_price(input_token_count,
                                                                                         output_token_count, model)
            # evaluate the models performance against the grading rubric and return the final score, final summary
            # and the scoring rubric
            final_score, final_summary, final_score_rubric = asyncio.run(
                evaluate_model_output_orchestrator(input_text_data, model, summary_invoke_response, prompt,
                                                   dynamic_evaluation_criteria, dynamic_grading_scale))
            #  create a OrchestrationHelper object to store the results of the evaluation
            result = OrchestrationHelper(model, time_length, character_count, char_process_time, input_cost,
                                         output_cost,
                                         total_cost, total_cost_1000, final_score, summary_invoke_response,
                                         final_summary)
            # add the results of the evaluation to the results list
            results_list.append(result.format())
            # add the evaluation results written summary to the evaluation results string
            evaluation_results += result.evaluation_results()
            # add the scoring rubric for the model into the scoring rubric list
            score_rubric_list.append(final_score_rubric)

        if "cohere" in model:
            # Start timer
            start = timer()
            # Invoke the specific Cohere model, and get the generated summary, input tokens and output tokens
            summary_invoke_response, input_token_count, output_token_count = invoke_cohere(model, prompt,
                                                                                              input_text_data,max_tokens)
            # end timer
            end = timer()
            # calculate total time taken
            time_length = round(end - start, 2)
            # calculate time taken per character
            char_process_time = character_count / time_length
            # calculate costs for the model and the specific inference, specifically the input costs, output cost,
            # total costs and total costs per 1000 invocations
            input_cost, output_cost, total_cost, total_cost_1000 = calculate_total_price(input_token_count,
                                                                                         output_token_count, model)
            # evaluate the models performance against the grading rubric and return the final score, final summary
            # and the scoring rubric
            final_score, final_summary, final_score_rubric = asyncio.run(
                evaluate_model_output_orchestrator(input_text_data, model, summary_invoke_response, prompt,
                                                   dynamic_evaluation_criteria, dynamic_grading_scale))
            #  create a OrchestrationHelper object to store the results of the evaluation
            result = OrchestrationHelper(model, time_length, character_count, char_process_time, input_cost,
                                         output_cost,
                                         total_cost, total_cost_1000, final_score, summary_invoke_response,
                                         final_summary)
            # add the results of the evaluation to the results list
            results_list.append(result.format())
            # add the evaluation results written summary to the evaluation results string
            evaluation_results += result.evaluation_results()
            # add the scoring rubric for the model into the scoring rubric list
            score_rubric_list.append(final_score_rubric)

        if "amazon" in model:
            # Start timer
            start = timer()
            # Invoke the specific Amazon model, and get the generated summary, input tokens and output tokens
            summary_invoke_response, input_token_count, output_token_count = invoke_amazon(model, prompt,
                                                                                              input_text_data,max_tokens)
            # end timer
            end = timer()
            # calculate total time taken
            time_length = round(end - start, 2)
            # calculate time taken per character
            char_process_time = character_count / time_length
            # calculate costs for the model and the specific inference, specifically the input costs, output cost,
            # total costs and total costs per 1000 invocations
            input_cost, output_cost, total_cost, total_cost_1000 = calculate_total_price(input_token_count,
                                                                                         output_token_count, model)
            # evaluate the models performance against the grading rubric and return the final score, final summary
            # and the scoring rubric
            final_score, final_summary, final_score_rubric = asyncio.run(
                evaluate_model_output_orchestrator(input_text_data, model, summary_invoke_response, prompt,
                                                   dynamic_evaluation_criteria, dynamic_grading_scale))
            #  create a OrchestrationHelper object to store the results of the evaluation
            result = OrchestrationHelper(model, time_length, character_count, char_process_time, input_cost,
                                         output_cost,
                                         total_cost, total_cost_1000, final_score, summary_invoke_response,
                                         final_summary)
            # add the results of the evaluation to the results list
            results_list.append(result.format())
            # add the evaluation results written summary to the evaluation results string
            evaluation_results += result.evaluation_results()
            # add the scoring rubric for the model into the scoring rubric list
            score_rubric_list.append(final_score_rubric)

        if "ai21" in model:
            # Start timer
            start = timer()
            # Invoke the specific AI21 model, and get the generated summary, input tokens and output tokens
            summary_invoke_response, input_token_count, output_token_count = invoke_AI21(model, prompt,
                                                                                              input_text_data, max_tokens)
            # end timer
            end = timer()
            # calculate total time taken
            time_length = round(end - start, 2)
            # calculate time taken per character
            char_process_time = character_count / time_length
            # calculate costs for the model and the specific inference, specifically the input costs, output cost,
            # total costs and total costs per 1000 invocations
            input_cost, output_cost, total_cost, total_cost_1000 = calculate_total_price(input_token_count,
                                                                                         output_token_count, model)
            # evaluate the models performance against the grading rubric and return the final score, final summary
            # and the scoring rubric
            final_score, final_summary, final_score_rubric = asyncio.run(
                evaluate_model_output_orchestrator(input_text_data, model, summary_invoke_response, prompt,
                                                   dynamic_evaluation_criteria, dynamic_grading_scale))
            #  create a OrchestrationHelper object to store the results of the evaluation
            result = OrchestrationHelper(model, time_length, character_count, char_process_time, input_cost,
                                         output_cost,
                                         total_cost, total_cost_1000, final_score, summary_invoke_response,
                                         final_summary)
            # add the results of the evaluation to the results list
            results_list.append(result.format())
            # add the evaluation results written summary to the evaluation results string
            evaluation_results += result.evaluation_results()
            # add the scoring rubric for the model into the scoring rubric list
            score_rubric_list.append(final_score_rubric)
    # Setting the display to max column width
    pd.set_option('display.max_colwidth', None)
    # Convert scoring rubric list into a DataFrame
    score_rubric_df = pd.DataFrame(score_rubric_list)
    # Display DataFrame  for scoring rubric
    print(score_rubric_df)
    # Convert performance and cost results list into a DataFrame
    results_df = pd.DataFrame(results_list)
    # Display DataFrame for results
    print(results_df[['Model', 'Time Length', 'Total Cost', 'Summary Score']])
    # Multiply Total Cost values by 1000 invocations
    results_df['Total Cost'] *= 1000
    # Save this dataframe as a CSV file      
    file_path = os.path.join('reports', 'model_performance_comparison.csv')
    # Save DataFrame to CSV file
    results_df.to_csv(file_path, index=False)
    # Convert DataFrame to CSV format string to send to Bedrock for eval
    csv_data = StringIO()
    # Save DataFrame to CSV file
    results_df.to_csv(csv_data, index=False)
    # Move to start of StringIO object to read its content
    csv_data.seek(0)
    # Read CSV data from StringIO object (as a string)
    csv_string = csv_data.getvalue()
    # ask the model which is the best model to use for cost and performance
    invoke_costs_eval_response = evaluate_model_performance(csv_string, "anthropic.claude-sonnet-4-6")
    # chart out the performance and cost results
    plot_model_comparisons(results_df)
    # plot the performance rubric scores 
    plot_model_performance_comparisons(score_rubric_df)
    # Save the reports to a file
    write_evaluation_results(evaluation_results, eval_name="summary")
    write_evaluation_results(invoke_costs_eval_response, eval_name="cost")
    #  return the results dataframe, evaluation results, invoke costs eval response and score rubric dataframe
    return results_df, evaluation_results, invoke_costs_eval_response, score_rubric_df




def final_rag_evaluator(csv_path_1, csv_path_2, knowledge_bases):
    """
    Evaluate multiple knowledge bases for accuracy and other evaluation metrics.

    :param csv_path_1: Path to the question CSV file.
    :param csv_path_2: Path to the answer CSV file.
    :param knowledge_bases: List of knowledge bases to evaluate.

    :return: A tuple containing:
        - DataFrame: Evaluation results including knowledge base performance metrics and costs.
        - str: Summary of the evaluation results.
        - str: Evaluation of the costs for model selection.
        - DataFrame: Scoring rubric for the evaluated models.
    """
    # Extract the questions out of the given CSV
    questions = csv_extraction(csv_path_1)
    # Extract the answers out of the given CSV
    ground_truths = csv_extraction(csv_path_2)

    # Calculate the character count of the input text
    embedding_character_count = len(text_formatter(questions))

    # Initialize an empty list to store results for each knowledge base
    results_list = []
    # Initialize an empty list to store the scoring rubric for each model
    score_rubric_list = []
    # Initialize an empty string to store the aggregated evaluation results
    evaluation_results = ""
    # for each mode evaluate 
    for knowledge_base in knowledge_bases:

        embedding_model_name = knowledge_base['embedding_model_arn'].split('/')[1]

        bedrock_embeddings = BedrockEmbeddings(model_id=embedding_model_name, client=bedrock_runtime)
        retriever = AmazonKnowledgeBasesRetriever(
            knowledge_base_id=knowledge_base['id'],
            retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 4}}
        )

        input_embedding_token_count = len(text_formatter(questions))/6 ## TODO FIX ME!!!

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm_for_text_generation, retriever=retriever, return_source_documents=True
        )

        answers = []
        contexts = []
        token_counter = AnthropicTokenCounter(llm_for_text_generation)
        input_llm_token_count = 0
        output_llm_token_count = 0

        start = timer()
        for question in questions:
            answers.append(qa_chain.invoke(question, config={"callbacks": [token_counter]})["result"])
            input_llm_token_count += token_counter.input_tokens
            output_llm_token_count += token_counter.output_tokens
            contexts.append([docs.page_content for docs in retriever.get_relevant_documents(question)])
        # end timer
        end = timer()
        # calculate total time taken
        time_length = round(end - start, 2)
        # calculate time taken per character
        char_process_time = embedding_character_count / time_length
        # calculate llm_character_count
        llm_character_count = embedding_character_count + len(" ".join(item[0] for item in contexts))

        # To dict
        data = {
            "question": questions,
            "answer": answers,
            "contexts": contexts,
            "ground_truth": ground_truths
        }
        # Convert dict to dataset
        dataset = Dataset.from_dict(data)
        # Run RAGAS on dataset
        result = evaluate(
            dataset = dataset, 
            metrics=metrics,
            llm=llm_for_evaluation,
            embeddings=bedrock_embeddings,
        )

        input_embedding_cost, output_embedding_cost, embedding_total_cost, embedding_total_cost_1000 = calculate_total_price(input_embedding_token_count, 0, embedding_model_name)
        input_llm_cost, output_llm_cost, llm_total_cost, llm_total_cost_1000 = calculate_total_price(input_llm_token_count, output_llm_token_count, llm_for_text_generation.model_id)

        # evaluate the models performance against the grading rubric and return the final score, final summary
        # and the scoring rubric
        final_score, final_summary, final_score_rubric = evaluate_rag_output(result, knowledge_base, contexts)
    
        #  create a OrchestrationHelper object to store the results of the evaluation
        result = OrchestrationRAGHelper(knowledge_base['name'], time_length, embedding_character_count, llm_character_count, char_process_time, input_embedding_cost, 
                                     output_embedding_cost, embedding_total_cost, embedding_total_cost_1000, input_llm_cost, 
                                     output_llm_cost, llm_total_cost, llm_total_cost_1000,
                                     final_score, text_formatter(answers), final_summary)
        # add the results of the evaluation to the results list
        results_list.append(result.format())
        # add the evaluation results written summary to the evaluation results string
        evaluation_results += result.evaluation_results()            
        # add the scoring rubric for the model into the scoring rubric list
        score_rubric_list.append(final_score_rubric)

    # Setting the display to max column width
    pd.set_option('display.max_colwidth', None)
    # Convert scoring rubric list into a DataFrame
    score_rubric_df = pd.DataFrame(score_rubric_list)
    # Convert performance and cost results list into a DataFrame
    results_df = pd.DataFrame(results_list)
    # Save this dataframe as a CSV file      
    file_path = os.path.join('reports', 'model_performance_comparison.csv')
    # Save DataFrame to CSV file
    results_df.to_csv(file_path, index=False)
    # Convert DataFrame to CSV format string to send to Bedrock for eval
    csv_data = StringIO()
    # Save DataFrame to CSV file
    results_df.to_csv(csv_data, index=False)
    # Move to start of StringIO object to read its content
    csv_data.seek(0)
    # Read CSV data from StringIO object (as a string)
    csv_string = csv_data.getvalue()
    # ask the model which is the best model to use for cost and performance
    invoke_costs_eval_response = evaluate_rag_performance(csv_string, "anthropic.claude-sonnet-4-6")
    # chart out the performance and cost results
    plot_rag_comparisons(results_df)
    # plot the performance rubric scores 
    plot_rag_performance_comparisons(score_rubric_df)
    # Save the reports to a file
    write_evaluation_results(evaluation_results, eval_name="summary")
    write_evaluation_results(invoke_costs_eval_response, eval_name="cost")
    #  return the results dataframe, evaluation results, invoke costs eval response and score rubric dataframe
    return results_df, evaluation_results, invoke_costs_eval_response, score_rubric_df
