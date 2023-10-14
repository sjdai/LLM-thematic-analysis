# LLM-thematic-analysis
This repository contains code for the paper on 2023 EMNLP Findings: "LLM-in-the-loop: Leveraging Large Language Model for Thematic Analysis"

We propose a human–LLM collaboration framework (i.e., LLM-in-the-loop) to conduct thematic analysis (TA) with in-context learning (ICL). This framework provides the prompt to frame discussions with LLM to generate the final codebook for TA. We demonstrate the utility of this framework using survey datasets on the aspects of the music listening experience and the usage of a password manager. The results and a case study show that the proposed framework yields similar coding quality to that of human coders but reduces TA’s labor and time demands.

![](https://hackmd.io/_uploads/rJe-diD-6.png)

The two datasets we used in this work can be found here:
* Music Shuffle: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7004375/
* Password Manager: https://www.usenix.org/conference/usenixsecurity22/presentation/mayer

## Requirements
* Python >= 3.8
* jupyter notebook
* OpenAI API Key
*If you want to use ChatGPT (a GUI interface for using GPT), you can find the prompts we used in the paper.*
## Quick Start
### Step 1. Installation
```
pip install openai
```
### Step 2. Have your free-text response ready
Put all your free-text responses in a `.txt` file.
Example:
```
I am a response.
I am a response as well.
Maybe I am a response.
...
```
### Step 3. Setup your API key, model, temperature in `chat_mods.py`
```
# We recommend you to store your API key as an environment variable.
# Detailed information: https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety
openai.api_key = os.getenv("OPENAI_API_KEY")
```
```
# model-> Default: "gpt-3.5-turbo-16k". You can select the model you prefer. Detailed information: https://platform.openai.com/docs/models/gpt-4
# temperature-> Default: 0. https://platform.openai.com/docs/api-reference/chat/create 
    
    responses = openai.ChatCompletion.create(
      model="gpt-3.5-turbo-16k", 
      messages=msgs,
      temperature=0
    )
```

### Step 4. Conducting thematic analysis with LLM!
1. Open `thematic_analysis.ipynb` with `jupyter notebook`
2. Start the task!

## Citation
Coming Soon!
