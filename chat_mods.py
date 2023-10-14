import openai
import json
import csv
import os

### Please do not share your API key.
### We recommend you to store your API key as an environment variable. Detailed information: https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety
openai.api_key = os.getenv("OPENAI_API_KEY")
#openai.api_key = "sk-XXXXX"
### Please do not upload the file to any public platform if you have included your API key explicitly here, unless you want other people to use your API key without charge.

def chat(msgs):
    ### model-> Default: "gpt-3.5-turbo-16k". You can select the model you prefer. Detailed information: https://platform.openai.com/docs/models/gpt-4
    ### temperature-> Default: 0. https://platform.openai.com/docs/api-reference/chat/create 
    
    responses = openai.ChatCompletion.create(
      model="gpt-3.5-turbo-16k", 
      messages=msgs,
      temperature=0
    )
    return responses
    
def msg_builder(role, msg):
    return {
        "role": role,
        "content": msg
    }

def get_content(resp):
    return resp.choices[0].message.content

def json_writer(file_name, obj):
    with open(file_name, 'w') as json_f:
        json.dump(obj, json_f, indent=4, ensure_ascii=False)
        
def print_pretty(obj):
    tmp = json.loads(obj)
    tmp = json.dumps(tmp, indent=4)
    print(tmp)

def load_data(free_text):
    text = open(free_text).read()
    text = text.split("\n")
    code_prompt = []
    text_for_machine = ""
    counter = 1
    for i in text:
        txt = f"Response {counter}. {i}"
        tmp = {
                "Q": txt,
                "A": "Let's code the response!"
        }
        code_prompt.append(tmp)
        text_for_machine = text_for_machine + txt + "\n"
        counter += 1
        
    return code_prompt, text_for_machine

def init_code_gen(prompt_exp, prompt_codes):
    msgs = []
    msgs.append(
        {
            "role": "system",
            "content": "You are a researcher to conduct thematic analysis."
        }
    )
    msgs.append(msg_builder("user", prompt_exp))
    content = ""
    for i in prompt_codes:
        content = content + i["Q"]+'\n'+i["A"]+'\n\n'
    
    msgs.append(msg_builder("user", content))
    print("Waiting for the response...")
    resps = chat(msgs)
    print(get_content(resps))
    return resps, msgs, content

def sum_code_gen(resps, msgs):
    msgs.append(msg_builder("assistant", resps.choices[0].message.content))
    prompt_sum ="""Please provide a summary in JSON format.
    The expected output format should follow this structure:
      'number of response':
        'code': 'definition of the code'
    """
    msgs.append(msg_builder("user",prompt_sum))
    print("Waiting for the response...")
    resps = chat(msgs)
    sum_codes = get_content(resps)
    print(sum_codes)
    codes_detail = json.loads(sum_codes)
    codes = []
    for i in list(codes_detail.values()):
        codes.extend(list(i.keys()))
    codes = list(set(codes))
    
    return codes_detail, codes

def codes_to_themes(codes_detail, codes, question):
    prompt_theme = """Please organize the codes into themes in JSON format. Ensure that each code belongs to only one theme. Assign a name to each theme. 
If there are any duplicate codes, please merge them into a single entry in the code book.
The expected output format should follow this structure:
<Name of the theme>: <List of codes and their definition belonging to the theme>
    """
    prompt_theme = f"Here is the question for the responses: {question}" + prompt_theme

    assistant_prompt = """
    codes and their definition: {}
    codes: {}
    """.format(json.dumps(list(codes_detail.values())), "|".join(codes))

    msgs_theme = []
    msgs_theme.append(
        {
            "role": "system",
            "content": "You are a researcher to conduct thematic analysis. The output format should be in JSON."
        })
    msgs_theme.append(msg_builder("assistant", assistant_prompt))
    msgs_theme.append(msg_builder("user", prompt_theme))
    
    print("Waiting for the response...")
    resp_theme = chat(msgs_theme)
    print("Completed!")
    msgs_theme.append(msg_builder("assistant", get_content(resp_theme)))
    resp_theme = json.loads(resp_theme.choices[0].message.content)
    json_writer("revised_theme.json", resp_theme)
    return resp_theme, msgs_theme

def discussion(resp_theme, msgs_theme, action_description):
    with open("revised_theme.json") as json_f:
        revised_theme = json.load(json_f)
    
    discussion_prompt="""
    Here is your version.
    {}
    Here is the revised version.
    {}
    Here are the reasons why I revised the themes.
    {}

    What do you think? Please generate the revised themes.
    Please list the parts with which you agree and disagree and the reason in JSON.
    """.format(resp_theme, revised_theme, action_description)

    msgs_theme.append(msg_builder("user", discussion_prompt))
    print("Waiting for the response...")

    diss_resp = chat(msgs_theme)
    print_pretty(get_content(diss_resp))
    msgs_theme.append(msg_builder("assistant", get_content(diss_resp)))
    
    return msgs_theme

def diss_process(msgs_theme):
    cont_prompt = """
    Please generate the revised version themes in JSON
    Modify the parts that you agree with and retain the part you disagree with."""
    msgs_theme.append(msg_builder("user", cont_prompt))
    print("Waiting for the response...")

    diss_resp = chat(msgs_theme)
    msgs_theme.append(msg_builder("assistant", get_content(diss_resp)))
    resp_theme = json.loads(get_content(diss_resp))
    print_pretty(get_content(diss_resp))
    return resp_theme, msgs_theme

def final_codebook_gen(name, msgs_theme):
    final_code_book_prompt = """
    Please generate the final code book in JSON.
    The code book should include the following structure:
    'theme': 
        'definition': 'definition of the theme'
        'codes': 'list of the codes with the definition' 
    Ensure that the code book reflects this format with the appropriate values and information.
    """
    msgs_theme.append(msg_builder("user", final_code_book_prompt))
    print("Waiting for the response...")
    final_code_book = chat(msgs_theme)
    print_pretty(get_content(final_code_book))
    final_code_book_machine = json.loads(get_content(final_code_book))
    final_code_book = json.loads(get_content(final_code_book))
    counter = 1
    for i in list(final_code_book.keys()):
        tmp = final_code_book[i]["codes"]
        tmp_lst = []
        for j in tmp:
            tmp_lst.append({counter: j})
            counter += 1
        final_code_book[i]["codes"] = tmp_lst
    
    with open(name, 'w') as json_f:
        json.dump(final_code_book, json_f, indent=4)
    print("The code book has been generated! The file name is {}.".format(name))
    return final_code_book_machine
    
def label(final_code_book, content):
    label_prompt = """Using the codes from the code book (not the themes), please proceed to label the responses accordingly.
    {}
    Here are the responses {}.
    The output format should be in JSON.
    "Response": 'list of codes'
    """.format(final_code_book, content)
    print("Waiting for the response...")
    code_result = chat([msg_builder("user", label_prompt)])
    code_result = get_content(code_result)
    code_result = json.loads(code_result)
    json_writer("coded_result.json", code_result)
    return code_result
  