from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

#ChatPromptTemplate.from_template is used when we have only one input generally which is user input
#PromptTemplate is used when we have one user input and other inputs like variable input etc.
 
# -----------------------------
# Schema
# -----------------------------

class ClassificationOutput(BaseModel):
    call_type: str = Field(description="Type of customer call")
    confidence: float = Field(description="Confidence score between 0 and 1")


# -----------------------------
# Chain Builder
# -----------------------------

def get_classification_chain(llm, config):
    """
    Creates and returns the classification chain.
    """
    parser = PydanticOutputParser(pydantic_object=ClassificationOutput)

    prompt = PromptTemplate(
        template="""
You are a call classification assistant.

Classify the following customer support transcript into one of these categories:
{labels}

Transcript:
{transcript}

{format_instructions}
""",
        input_variables=["transcript"],
        partial_variables = {
            "format_instructions": parser.get_format_instructions(),
            "labels": config["classification"]["labels"]
        }
    )
    
    classification_chain = prompt | llm | parser
    return classification_chain

#partial_variables -> we pass it mostly once