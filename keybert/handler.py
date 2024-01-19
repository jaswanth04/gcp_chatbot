import os
import json
import torch
from transformers import AutoModel, AutoTokenizer, pipeline
from ts.torch_handler.base_handler import BaseHandler
from keybert import KeyBERT

# logger = logging.getLogger(__name__)



class TransformersClassifierHandler(BaseHandler):
    """
    The handler takes an input string and returns the classification text 
    based on the serialized transformers checkpoint.
    """
    def __init__(self):
        super(TransformersClassifierHandler, self).__init__()
        self.initialized = False

    def initialize(self, ctx):
        """ Loads the model.pt file and initialized the model object.
        Instantiates Tokenizer for preprocessor to use
        Loads labels to name mapping file for post-processing inference response
        """
        self.manifest = ctx.manifest

        properties = ctx.system_properties
        model_dir = properties.get("model_dir")
        print(model_dir)
        self.device = torch.device("cuda:" + str(properties.get("gpu_id")) if torch.cuda.is_available() else "cpu")

        # Read model serialize/pt file
        serialized_file = self.manifest["model"]["serializedFile"]
        model_pt_path = os.path.join(model_dir, serialized_file)
        if not os.path.isfile(model_pt_path):
            raise RuntimeError("Missing the model.pt or pytorch_model.bin file")
        
        # Load model
        model = AutoModel.from_pretrained(model_dir)
        model.to(self.device)
        model.eval()
        print('Transformer model from path {0} loaded successfully'.format(model_dir))
        
        # Ensure to use the same tokenizer used during training
        tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-mpnet-base-v2")
        hf_model = pipeline("feature-extraction", model=model, tokenizer=tokenizer)
        self.kw_model = KeyBERT(model=hf_model)

        self.initialized = True

    def preprocess(self, data):
        """ Preprocessing input request by tokenizing
            Extend with your own preprocessing steps as needed
        """
        print(data)

        if "body" in data[0]:
            data = data[0]['body']
            if "instances" in data:
                data = data['instances']

        sentences = [d.get("data") for d in data]
        # if text is None:
        #     text = data[0].get("body")
        # sentences = text.decode('utf-8')
        print("Received text: '%s'", sentences)

        return [sentences]

    def inference(self, inputs):
        """ Predict the class of a text using a trained transformer model.
        """
        result = self.kw_model.extract_keywords(
            inputs[0],
            keyphrase_ngram_range=(2, 2),
            stop_words='english',
            use_mmr=True,
            diversity=0.25,
            highlight=False,
            top_n=4,
            threshold=0.5 
        )
        print(result)
        
        return [result]
        

    def postprocess(self, inference_output):

        return inference_output(.pqenv) 
