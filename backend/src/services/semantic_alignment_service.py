"""Semantic Alignment Service for NET-EST System
Implements paragraph alignment using BERTimbau embeddings
"""

import asyncio
import hashlib
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import numpy as np


# ML Libraries
try:
    import torch
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances

    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

from ..models.semantic_alignment import (
    AlignedPair,
    AlignmentConfiguration,
    AlignmentMatrix,
    AlignmentMethod,
    AlignmentRequest,
    AlignmentResponse,
    AlignmentResult,
    EmbeddingRequest,
    EmbeddingResponse,
    UnalignedParagraph,
)


logger = logging.getLogger(__name__)


class EmbeddingCache:
    """Simple in-memory cache for embeddings"""

    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.max_size = max_size
        self.access_order = []

    def _get_cache_key(self, text: str, model_name: str) -> str:
        """Generate cache key for text and model"""
        content = f"{model_name}:{text}"
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, text: str, model_name: str) -> list[float] | None:
        """Get embedding from cache"""
        key = self._get_cache_key(text, model_name)
        if key in self.cache:
            # Update access order
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None

    def set(self, text: str, model_name: str, embedding: list[float]):
        """Store embedding in cache"""
        key = self._get_cache_key(text, model_name)

        # Evict oldest if cache is full
        if len(self.cache) >= self.max_size and key not in self.cache:
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]

        self.cache[key] = embedding
        if key not in self.access_order:
            self.access_order.append(key)


class SemanticAlignmentService:
    """Service for semantic alignment of paragraphs"""

    def __init__(self, config: AlignmentConfiguration | None = None):
        # Use provided config or a sensible default configuration.
        # The default model for semantic alignment should be the lightweight
        # paraphrase-multilingual-MiniLM-L12-v2 (miniLM) as the primary operational default.
        self.config = config or AlignmentConfiguration(
            bertimbau_model="paraphrase-multilingual-MiniLM-L12-v2",
            similarity_threshold=0.7,
            max_sequence_length=512,
            batch_size=8,
            device="cpu",
            cache_embeddings=True,
        )
        self.model = None
        self.embedding_cache = EmbeddingCache()
        self.executor = ThreadPoolExecutor(max_workers=2)
        # Lazy sentence alignment service (initialized on first use)
        self.sentence_alignment_service = None

        if not ML_AVAILABLE:
            logger.warning(
                "ML libraries not available. Semantic alignment will use fallback methods."
            )

        logger.info(
            f"SemanticAlignmentService initialized with model: {self.config.bertimbau_model}"
        )

    async def _load_model(self):
        """Load BERTimbau model lazily"""
        if self.model is None and ML_AVAILABLE:
            try:
                logger.info(f"Loading model: {self.config.bertimbau_model}")
                # Run model loading in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                self.model = await loop.run_in_executor(self.executor, self._load_model_sync)
                logger.info("Model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load model {self.config.bertimbau_model}: {str(e)}")
                raise RuntimeError(f"Model loading failed: {str(e)}")

    def _load_model_sync(self) -> SentenceTransformer:
        """Synchronous model loading"""
        return SentenceTransformer(self.config.bertimbau_model, device=self.config.device)

    async def generate_embeddings(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate embeddings for texts"""
        start_time = time.time()

        if not ML_AVAILABLE:
            # Fallback: return random embeddings for testing
            logger.warning("Using fallback random embeddings")
            embeddings = [[np.random.random() for _ in range(768)] for _ in request.texts]
            return EmbeddingResponse(
                embeddings=embeddings,
                model_used="fallback_random",
                embedding_dim=768,
                processing_time=time.time() - start_time,
            )

        await self._load_model()

        # Check cache first
        cached_embeddings = []
        texts_to_process = []
        indices_to_process = []

        for i, text in enumerate(request.texts):
            cached = self.embedding_cache.get(text, request.model_name)
            if cached is not None:
                cached_embeddings.append((i, cached))
            else:
                texts_to_process.append(text)
                indices_to_process.append(i)

        # Generate embeddings for uncached texts
        new_embeddings = []
        if texts_to_process:
            try:
                loop = asyncio.get_event_loop()
                embeddings_array = await loop.run_in_executor(
                    self.executor,
                    self._generate_embeddings_sync,
                    texts_to_process,
                    request.normalize,
                )
                new_embeddings = embeddings_array.tolist()

                # Cache new embeddings
                for text, embedding in zip(texts_to_process, new_embeddings, strict=False):
                    self.embedding_cache.set(text, request.model_name, embedding)

            except Exception as e:
                logger.error(f"Error generating embeddings: {str(e)}")
                raise RuntimeError(f"Embedding generation failed: {str(e)}")

        # Combine cached and new embeddings
        all_embeddings: list[list[float]] = [[] for _ in range(len(request.texts))]

        # Fill cached embeddings
        for i, embedding in cached_embeddings:
            all_embeddings[i] = embedding

        # Fill new embeddings
        for i, idx in enumerate(indices_to_process):
            all_embeddings[idx] = new_embeddings[i]

        processing_time = time.time() - start_time

        return EmbeddingResponse(
            embeddings=all_embeddings,
            model_used=request.model_name,
            embedding_dim=len(all_embeddings[0]) if all_embeddings and all_embeddings[0] else 0,
            processing_time=processing_time,
        )

    def _generate_embeddings_sync(self, texts: list[str], normalize: bool = True) -> np.ndarray:
        """Synchronous embedding generation"""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        embeddings = self.model.encode(
            texts,
            batch_size=self.config.batch_size,
            normalize_embeddings=normalize,
            show_progress_bar=False,
        )
        return embeddings

    def _compute_similarity_matrix(
        self,
        source_embeddings: list[list[float]],
        target_embeddings: list[list[float]],
        method: AlignmentMethod,
    ) -> np.ndarray:
        """Compute similarity matrix between source and target embeddings"""
        source_array = np.array(source_embeddings)
        target_array = np.array(target_embeddings)

        if method == AlignmentMethod.COSINE_SIMILARITY:
            # Compute cosine similarity
            similarity_matrix = cosine_similarity(source_array, target_array)
        elif method == AlignmentMethod.EUCLIDEAN_DISTANCE:
            # Compute euclidean distances and convert to similarities
            distances = euclidean_distances(source_array, target_array)
            # Convert distances to similarities (0 = most similar, higher = less similar)
            max_distance = np.max(distances)
            similarity_matrix = (
                1 - (distances / max_distance) if max_distance > 0 else np.ones_like(distances)
            )
        elif method == AlignmentMethod.DOT_PRODUCT:
            # Compute dot product similarities
            similarity_matrix = np.dot(source_array, target_array.T)
        else:
            raise ValueError(f"Unknown alignment method: {method}")

        return similarity_matrix

    def _determine_confidence(self, similarity_score: float) -> str:
        """Determine confidence level based on similarity score"""
        if similarity_score >= self.config.confidence_thresholds["high"]:
            return "high"
        elif similarity_score >= self.config.confidence_thresholds["medium"]:
            return "medium"
        elif similarity_score >= self.config.confidence_thresholds["low"]:
            return "low"
        else:
            return "very_low"

    def _find_alignments(
        self,
        similarity_matrix: np.ndarray,
        source_paragraphs: list[str],
        target_paragraphs: list[str],
        threshold: float,
        max_alignments_per_source: int,
        method: AlignmentMethod,
    ) -> tuple[list[AlignedPair], list[int], list[int]]:
        """Find paragraph alignments based on similarity matrix"""
        aligned_pairs = []
        aligned_target_indices = set()
        unaligned_source_indices = []

        for source_idx in range(len(source_paragraphs)):
            # Get similarities for this source paragraph
            similarities = similarity_matrix[source_idx]

            # Find indices of targets above threshold, sorted by similarity
            candidate_indices = [
                (target_idx, sim_score)
                for target_idx, sim_score in enumerate(similarities)
                if sim_score >= threshold and target_idx not in aligned_target_indices
            ]

            # Sort by similarity score (descending)
            candidate_indices.sort(key=lambda x: x[1], reverse=True)

            # Take top candidates up to max_alignments_per_source
            selected_candidates = candidate_indices[:max_alignments_per_source]

            if selected_candidates:
                for target_idx, sim_score in selected_candidates:
                    aligned_pair = AlignedPair(
                        source_index=source_idx,
                        target_index=target_idx,
                        source_text=source_paragraphs[source_idx],
                        target_text=target_paragraphs[target_idx],
                        similarity_score=float(sim_score),
                        confidence=self._determine_confidence(sim_score),
                        alignment_method=method.value,
                    )
                    aligned_pairs.append(aligned_pair)
                    aligned_target_indices.add(target_idx)
            else:
                unaligned_source_indices.append(source_idx)

        # Find unaligned target indices
        unaligned_target_indices = [
            idx for idx in range(len(target_paragraphs)) if idx not in aligned_target_indices
        ]

        return aligned_pairs, unaligned_source_indices, unaligned_target_indices

    def _create_unaligned_details(
        self,
        unaligned_indices: list[int],
        paragraphs: list[str],
        similarity_matrix: np.ndarray,
        is_source: bool,
    ) -> list[UnalignedParagraph]:
        """Create detailed information for unaligned paragraphs"""
        unaligned_details = []

        for idx in unaligned_indices:
            if is_source:
                similarities = similarity_matrix[idx]
            else:
                similarities = similarity_matrix[:, idx]

            max_similarity = float(np.max(similarities)) if len(similarities) > 0 else 0.0

            reason = "No alignment found above threshold"
            if max_similarity > 0:
                reason = f"Best similarity ({max_similarity:.3f}) below threshold"

            unaligned_details.append(
                UnalignedParagraph(
                    index=idx,
                    text=paragraphs[idx],
                    reason=reason,
                    nearest_similarity=max_similarity,
                )
            )

        return unaligned_details

    async def align_paragraphs(self, request: AlignmentRequest) -> AlignmentResponse:
        """Perform semantic alignment of paragraphs"""
        try:
            start_time = time.time()
            warnings = []

            # Validate input
            if not request.source_paragraphs or not request.target_paragraphs:
                return AlignmentResponse(
                    success=False, errors=["Both source and target paragraphs are required"]
                )

            # Log alignment request
            logger.info(
                f"Starting alignment: {len(request.source_paragraphs)} source -> {len(request.target_paragraphs)} target"
            )

            # Generate embeddings
            embedding_request = EmbeddingRequest(
                texts=request.source_paragraphs + request.target_paragraphs,
                model_name=self.config.bertimbau_model,
                normalize=True,
            )

            embedding_response = await self.generate_embeddings(embedding_request)

            # Split embeddings
            source_count = len(request.source_paragraphs)
            source_embeddings = embedding_response.embeddings[:source_count]
            target_embeddings = embedding_response.embeddings[source_count:]

            # Compute similarity matrix
            similarity_matrix = self._compute_similarity_matrix(
                source_embeddings, target_embeddings, request.alignment_method
            )

            # Find alignments
            aligned_pairs, unaligned_source_indices, unaligned_target_indices = (
                self._find_alignments(
                    similarity_matrix,
                    request.source_paragraphs,
                    request.target_paragraphs,
                    request.similarity_threshold,
                    request.max_alignments_per_source,
                    request.alignment_method,
                )
            )
            
            # --- Step 2 integration:
            # Lazily instantiate the sentence alignment service and compute
            # sentence-level alignments for each aligned paragraph pair.
            # We run the (synchronous) sentence alignment in the executor to avoid blocking.
            sentence_alignments = []
            try:
                # Read user-configured options (if any)
                user_cfg = request.user_config or {}
                enable_sentence_alignment = bool(user_cfg.get("enable_sentence_alignment", False))
                sentence_threshold = float(user_cfg.get("sentence_similarity_threshold", 0.5))

                if enable_sentence_alignment and aligned_pairs:
                    # Lazy import to avoid circular imports at module load time
                    if self.sentence_alignment_service is None:
                        from .sentence_alignment_service import SentenceAlignmentService

                        self.sentence_alignment_service = SentenceAlignmentService()

                    # Prepare tasks for executor
                    loop = asyncio.get_event_loop()
                    tasks = []
                    for pair in aligned_pairs:
                        src_para = pair.source_text
                        tgt_para = pair.target_text
                        # Run the lightweight sync aligner in threadpool
                        tasks.append(
                            loop.run_in_executor(
                                self.executor,
                                self.sentence_alignment_service.align,
                                [src_para],
                                [tgt_para],
                                sentence_threshold,
                            )
                        )

                    if tasks:
                        sentence_results = await asyncio.gather(*tasks, return_exceptions=True)
                        for res in sentence_results:
                            if isinstance(res, Exception):
                                logger.debug(f"Sentence alignment task failed: {res}")
                                sentence_alignments.append(None)
                            else:
                                # Convert dataclass result to serializable dict
                                sentence_alignments.append(
                                    {
                                        "aligned": res.aligned,
                                        "unmatched_source": res.unmatched_source,
                                        "unmatched_target": res.unmatched_target,
                                        "similarity_matrix": res.similarity_matrix,
                                    }
                                )
                else:
                    # Sentence-level disabled or no aligned pairs; leave empty
                    sentence_alignments = []
            except Exception as e:
                # Do not fail the paragraph alignment due to sentence-level failures;
                # log and continue.
                logger.debug(f"Sentence-level alignment integration failed: {e}")
                sentence_alignments = []

            # Create unaligned details
            unaligned_source_details = self._create_unaligned_details(
                unaligned_source_indices,
                request.source_paragraphs,
                similarity_matrix,
                is_source=True,
            )

            unaligned_target_details = self._create_unaligned_details(
                unaligned_target_indices,
                request.target_paragraphs,
                similarity_matrix,
                is_source=False,
            )

            # Create alignment matrix model
            alignment_matrix = AlignmentMatrix(
                source_count=len(request.source_paragraphs),
                target_count=len(request.target_paragraphs),
                matrix=similarity_matrix.tolist(),
                method=request.alignment_method.value,
            )

            # Calculate statistics
            processing_time = time.time() - start_time
            alignment_stats = {
                "total_source_paragraphs": len(request.source_paragraphs),
                "total_target_paragraphs": len(request.target_paragraphs),
                "aligned_pairs_count": len(aligned_pairs),
                "unaligned_source_count": len(unaligned_source_indices),
                "unaligned_target_count": len(unaligned_target_indices),
                "alignment_rate_source": (
                    len(aligned_pairs) / len(request.source_paragraphs)
                    if request.source_paragraphs
                    else 0
                ),
                "alignment_rate_target": (
                    len(set(pair.target_index for pair in aligned_pairs))
                    / len(request.target_paragraphs)
                    if request.target_paragraphs
                    else 0
                ),
                "average_similarity": (
                    float(np.mean([pair.similarity_score for pair in aligned_pairs]))
                    if aligned_pairs
                    else 0.0
                ),
                "max_similarity": (
                    float(np.max([pair.similarity_score for pair in aligned_pairs]))
                    if aligned_pairs
                    else 0.0
                ),
                "min_similarity": (
                    float(np.min([pair.similarity_score for pair in aligned_pairs]))
                    if aligned_pairs
                    else 0.0
                ),
                "processing_time_seconds": processing_time,
                "embedding_time_seconds": embedding_response.processing_time,
                "model_used": embedding_response.model_used,
            }

            # Add warnings for low alignment rates
            if alignment_stats["alignment_rate_source"] < 0.5:
                warnings.append(
                    f"Low source alignment rate: {alignment_stats['alignment_rate_source']:.1%}"
                )

            if alignment_stats["alignment_rate_target"] < 0.5:
                warnings.append(
                    f"Low target alignment rate: {alignment_stats['alignment_rate_target']:.1%}"
                )

            # Create result
            alignment_result = AlignmentResult(
                aligned_pairs=aligned_pairs,
                unaligned_source_indices=unaligned_source_indices,
                unaligned_target_indices=unaligned_target_indices,
                unaligned_source_details=unaligned_source_details,
                unaligned_target_details=unaligned_target_details,
                similarity_matrix=alignment_matrix,
                alignment_stats=alignment_stats,
            )

            return AlignmentResponse(
                success=True,
                alignment_result=alignment_result,
                warnings=warnings,
                processing_metadata={
                    "processing_time": processing_time,
                    "similarity_threshold": request.similarity_threshold,
                    "alignment_method": request.alignment_method.value,
                    "max_alignments_per_source": request.max_alignments_per_source,
                },
            )

        except Exception as e:
            logger.error(f"Error in semantic alignment: {str(e)}")
            return AlignmentResponse(
                success=False, errors=[f"Alignment processing failed: {str(e)}"]
            )

    async def get_health_status(self) -> dict[str, Any]:
        """Get health status of the alignment service"""
        status = {
            "service": "semantic_alignment",
            "ml_libraries_available": ML_AVAILABLE,
            "model_loaded": self.model is not None,
            "cache_size": len(self.embedding_cache.cache),
            "config": {
                "model": self.config.bertimbau_model,
                "device": self.config.device,
                "similarity_threshold": self.config.similarity_threshold,
                "batch_size": self.config.batch_size,
            },
        }

        if ML_AVAILABLE:
            try:
                await self._load_model()
                status["model_status"] = "loaded"
            except Exception as e:
                status["model_status"] = f"error: {str(e)}"
        else:
            status["model_status"] = "ml_libraries_not_available"

        return status
