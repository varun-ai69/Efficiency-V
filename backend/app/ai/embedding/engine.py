import os
import yaml
import faiss
import numpy as np
import logging
from sentence_transformers import SentenceTransformer
import glob

logger = logging.getLogger("efficiency_v.ai.embedding")

class EmbeddingEngine:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        logger.info(f"Loading SentenceTransformer model: {model_name}")
        self.model = SentenceTransformer(model_name)
        
        self.templates = {}
        self.index = None
        self.utterance_map = {}  # index -> template_id
        
        self._load_templates()
        self._build_index()

    def _load_templates(self):
        # Path to datasets/templates
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "datasets", "templates"))
        logger.info(f"Scanning for templates in: {base_dir}")
        
        # Recursively find all YAML files
        search_pattern = os.path.join(base_dir, "**", "*.yaml")
        yaml_files = glob.glob(search_pattern, recursive=True)
        
        for file_path in yaml_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    template_data = yaml.safe_load(f)
                    
                    if not template_data or "id" not in template_data:
                        continue
                        
                    template_id = template_data["id"]
                    self.templates[template_id] = template_data
            except Exception as e:
                logger.error(f"Failed to load template {file_path}: {e}")
                
        logger.info(f"Loaded {len(self.templates)} YAML templates.")

    def _build_index(self):
        if not self.templates:
            logger.warning("No templates to build FAISS index.")
            return

        utterances = []
        for template_id, template in self.templates.items():
            # Generate utterances from display name, category, and ID
            # e.g. "Chest Pain / Tightness cardiovascular chest_pain"
            base_text = f"{template.get('display_name', '')} {template.get('category', '')} {template_id}".strip()
            
            # We add a few variations to help the embedding engine
            variations = [
                base_text,
                template.get('display_name', ''),
                template_id.replace("_", " ")
            ]
            
            for text in variations:
                if text:
                    self.utterance_map[len(utterances)] = template_id
                    utterances.append(text.lower())

        if not utterances:
            return

        logger.info(f"Encoding {len(utterances)} utterances for FAISS index...")
        embeddings = self.model.encode(utterances, convert_to_numpy=True)
        
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)
        logger.info("FAISS index built successfully.")

    def match_complaint(self, text: str, top_k: int = 1):
        if self.index is None:
            return None, 0.0

        query_embedding = self.model.encode([text.lower()], convert_to_numpy=True)
        distances, indices = self.index.search(query_embedding, top_k)
        
        best_idx = indices[0][0]
        distance = distances[0][0]
        
        if best_idx != -1 and best_idx in self.utterance_map:
            template_id = self.utterance_map[best_idx]
            # Convert L2 distance to a mock confidence score
            confidence = max(0.0, 1.0 - (distance / 2.0))
            return template_id, confidence
            
        return None, 0.0

    def get_template(self, template_id: str):
        return self.templates.get(template_id)

# Singleton instance
embedding_engine = EmbeddingEngine()
