import boto3
import json
from typing import Dict, List, Optional, Union
import base64
from pathlib import Path
import time
import logging
import dicttoxml
import requests
class BedrockLanguageModels:
    """Utility class for interacting with AWS Bedrock foundation models.
    Modified from: https://github.com/RenaissancePlace/prlsi-ai-pocs/blob/main/np_flocab_alt_text/np_flocab_alt_text/language_models.py
    """
    
    def __init__(self, region_name: str, profile_name: str = 'ai-poc'):
        """Initialize the language model client.
        
        Args:
            region_name (str): AWS region name
        """
        self.profile_name = profile_name
        session = boto3.Session(profile_name=self.profile_name)
        
        self.region_name = region_name
        self.bedrock = session.client(
            service_name='bedrock-runtime',
            region_name=region_name
        )
        self.pricing = boto3.client('pricing', region_name='us-east-1')  # Pricing API is only available in us-east-1
        self._last_processing_time = 0.0
        self._last_cost = 0.0
        self._last_token_count = 0
        self.logger = logging.getLogger(__name__)
        
        # Available foundation models and their IDs
        self.models = {
            "claude": "anthropic.claude-v2",
            "claude-3": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
            "claude-instant": "anthropic.claude-instant-v1",
            "titan": "amazon.titan-text-express-v1",
            "jurassic": "ai21.j2-ultra-v1",
            "claude-3-5-v2": "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        }
        
        # Models that support image analysis
        self.image_capable_models = {
            "claude-3": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
            "claude-3-5-v2": "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        }

    def get_available_models(self) -> List[str]:
        """Get list of available foundation model identifiers.
        
        Returns:
            List[str]: List of model identifiers
        """
        return list(self.models.keys())

    def list_bedrock_models(self) -> List[Dict]:
        """List all available foundation models in AWS Bedrock.
        
        Returns:
            List[Dict]: List of model information dictionaries containing
                       modelId, modelName, provider, and other metadata
        """
        try:
            # Create a bedrock client (not runtime) to access model listing
            session = boto3.Session(profile_name=self.profile_name)
            bedrock = session.client('bedrock', region_name=self.bedrock.meta.region_name)
            response = bedrock.list_foundation_models()
            return response['modelSummaries']
        except Exception as e:
            raise Exception(f"Error listing Bedrock models: {str(e)}")

    def select_model(self, 
                    task: str = "text-generation",
                    provider: Optional[str] = None,
                    min_tokens: Optional[int] = None) -> str:
        """Select an appropriate model based on specified criteria.
        
        Args:
            task (str): The intended task (e.g., 'text-generation', 'embedding')
            provider (str, optional): Preferred provider (e.g., 'anthropic', 'amazon')
            min_tokens (int, optional): Minimum context window size needed
            
        Returns:
            str: Selected model ID
            
        Raises:
            ValueError: If no suitable model is found matching criteria
        """
        try:
            models = self.list_bedrock_models()
            suitable_models = []
            
            for model in models:
                model_id = model['modelId']
                
                # Check if model matches task
                if task.lower() in model.get('inferenceTypesSupported', []):
                    # Check provider if specified
                    if provider and provider.lower() not in model_id.lower():
                        continue
                        
                    # Check minimum tokens if specified
                    if min_tokens:
                        model_tokens = model.get('inputTokenLimit', 0)
                        if model_tokens < min_tokens:
                            continue
                            
                    suitable_models.append(model)
            
            if not suitable_models:
                raise ValueError(f"No models found matching criteria: task={task}, provider={provider}, min_tokens={min_tokens}")
            
            # Sort by input token limit (descending) as a simple heuristic
            suitable_models.sort(key=lambda x: x.get('inputTokenLimit', 0), reverse=True)
            
            # Return the first suitable model ID
            return suitable_models[0]['modelId']
            
        except Exception as e:
            raise Exception(f"Error selecting model: {str(e)}")

    def _get_model_pricing(self, model_id: str) -> tuple[float, float]:
        """Get current pricing for a model from AWS Pricing API.
        
        Args:
            model_id (str): The model identifier
            
        Returns:
            tuple[float, float]: Input and output token prices per 1K tokens
        """
        try:
            response = self.pricing.get_products(
                ServiceCode='AmazonBedrock',
                Filters=[
                    {'Type': 'TERM_MATCH', 'Field': 'modelId', 'Value': model_id},
                    {'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': self.region_name}
                ]
            )
            
            # Parse pricing information from response
            price_list = response.get('PriceList', [])
            if not price_list:
                # Fallback to default pricing if not found
                return (0.00025, 0.00125)  # Default Claude 3 pricing
            
            # Extract pricing from the first matching product
            product = json.loads(price_list[0])
            terms = product.get('terms', {})
            
            # Get input and output token prices
            input_price = float(terms.get('OnDemand', {}).get('inputTokenPrice', 0.00025))
            output_price = float(terms.get('OnDemand', {}).get('outputTokenPrice', 0.00125))
            
            return (input_price, output_price)
            
        except Exception as e:
            self.logger.warning(f"Failed to get pricing from AWS API: {str(e)}")
            return (0.00025, 0.00125)  # Fallback to default pricing
        
    def _encode_image(self, image_path: str) -> str:
        """Encode an image to a base64 string.
        
        Args:            
        Returns:
        """
        if isinstance(image_path, str) and image_path.startswith(('http://', 'https://')):
            # Handle URL
            response = requests.get(image_path)
            return response.content
        else:
            # Handle local file
            image_path = Path(image_path)
            if image_path.exists():
                with open(image_path, "rb") as image_file:
                    return image_file.read()
            else:
                raise ValueError(f"Image file does not exist: {image_path}")

    def analyze_image(self, image_path: str, prompt: str, model: str = "claude-3", temperature: float = 0.1) -> str:
        """Analyze an image and generate alt text.
        
        Args:
            image_path (Union[Path, str]): Path to the image file or URL
            prompt (str): Prompt to use for generation
            model (str): Model to use for analysis
            
        Returns:
            str: Generated alt text
        """
        if model not in self.image_capable_models:
            raise ValueError(f"Model {model} does not support image analysis")
            
        # Load image data
        try:
            image_data = self._encode_image(image_path)
        except Exception as e:
            raise ValueError(f"Failed to load image: {str(e)}")
            
        # Prepare request body
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "temperature": temperature,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": base64.b64encode(image_data).decode('utf-8')
                            }
                        }
                    ]
                }
            ]
        }
        
        # Send request to Bedrock
        try:
            start_time = time.time()
            response = self.bedrock.invoke_model(
                modelId=self.image_capable_models[model],
                body=json.dumps(request_body)
            )
            self._last_processing_time = time.time() - start_time
            
            # Parse response
            response_body = json.loads(response.get('body').read())
            
            # Extract usage information
            usage = response_body.get('usage', {})
            input_tokens = usage.get('input_tokens', 0)
            output_tokens = usage.get('output_tokens', 0)
            self._last_token_count = input_tokens + output_tokens
            
            # # Get current pricing
            # input_price, output_price = self._get_model_pricing(self.image_capable_models[model])
            
            # # Calculate cost using current pricing
            # self._last_cost = (input_tokens * input_price + output_tokens * output_price) / 1000
            
            return response_body['content'][0]['text']
            
        except Exception as e:
            raise RuntimeError(f"Failed to analyze image: {str(e)}")
        
    def _convert_json_object_to_xml(self, json_object: dict, root_name: str = "math_question") -> str:
        """Convert a JSON object to an XML string.
        
        Args:
            json_object (dict): The JSON object to convert
            
        """
        # Convert dict to XML
        xml_data = dicttoxml.dicttoxml(json_object, custom_root=root_name, attr_type=False)
        # Convert XML to string
        xml_string = xml_data.decode('utf-8')
        return xml_string
        
    def invoke_model_with_multi_modal_input_1(self, 
                                              json_object: dict,
                                              response_json_schema: str,
                                              prompt_2_system: str, 
                                              prompt_2_user_1: str, 
                                              prompt_2_guides: str,
                                              image_path: str,
                                              prefill: str = "",
                                              model: str = "claude-3", 
                                              temperature: float = 0.1, 
                                              max_tokens = 1000) -> str:
        """Invoke a model multi-modal, text and image, input.
        
        Args:
            json_object (dict): JSON object to use for analysis
            response_json_schema (str): JSON schema to use for output generation
            model (str): Model to use for analysis
        """
        # first, check if the model is supported
        if model not in self.image_capable_models:
            raise ValueError(f"Model {model} does not support image analysis")
        
        # Load image data
        try:
            image_data = self._encode_image(image_path)
        except Exception as e:
            raise ValueError(f"Failed to load image: {str(e)}")
        
        # then, generate the messages
        _messages = [
            {
                "role": "user",
                "content": self._convert_json_object_to_xml(json_object)
            },
            {
                "role": "user",
                "content":
                    [
                        {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": base64.b64encode(image_data).decode('utf-8')
                        }
                    }
                ]
            },
            {
                "role": "user",
                "content": prompt_2_user_1
            },
            {
                "role": "user",
                "content": prompt_2_guides.format(response_json_schema)
            },
            {
                "role": "assistant",
                "content": prefill
            }
        ]
        # then generate request body
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": _messages,
            "system": prompt_2_system
        }

         # Send request to Bedrock
        try:
            start_time = time.time()
            response = self.bedrock.invoke_model(
                modelId=self.image_capable_models[model],
                body=json.dumps(request_body)
            )
            self._last_processing_time = time.time() - start_time
            
            # Parse response
            response_body = json.loads(response.get('body').read())
            
            # Extract usage information
            usage = response_body.get('usage', {})
            input_tokens = usage.get('input_tokens', 0)
            output_tokens = usage.get('output_tokens', 0)
            self._last_token_count = input_tokens + output_tokens
            
            # # Get current pricing
            # input_price, output_price = self._get_model_pricing(self.image_capable_models[model])
            
            # # Calculate cost using current pricing
            # self._last_cost = (input_tokens * input_price + output_tokens * output_price) / 1000
            
            # if there is prefill, concat it with the response and return
            if prefill:
                return prefill + response_body['content'][0]['text']
            else:
                return response_body['content'][0]['text']
            
        except Exception as e:
            raise RuntimeError(f"Failed to analyze image: {str(e)}")
        
    def get_last_processing_time(self) -> float:
        """Get the processing time of the last image analysis.
        
        Returns:
            float: Processing time in seconds
        """
        return self._last_processing_time

    def get_last_cost(self) -> float:
        """Get the cost of the last API call.
        
        Returns:
            float: Cost in USD
        """
        return self._last_cost

    def get_last_token_count(self) -> int:
        """Get the token count from the last API call.
        
        Returns:
            int: Total number of tokens used
        """
        return self._last_token_count

    def get_image_capable_models(self) -> List[str]:
        """Get list of models that support image analysis.
        
        Returns:
            List[str]: List of model identifiers supporting image analysis
        """
        return list(self.image_capable_models.keys())
    
    def simple_call(self, 
                    messages: list, 
                    system_prompt: str = '',
                    max_tokens: int = 1000,
                    temperature: float = 0.1,
                    model: str = "claude-3"):
        """A simple model invocation that just returns the prompt as the response"""
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
            "system": system_prompt
        }
        response = self.bedrock.invoke_model(
            modelId=self.image_capable_models[model],
            body=json.dumps(request_body)
        )
        return json.loads(response.get('body').read())['content'][0]['text']