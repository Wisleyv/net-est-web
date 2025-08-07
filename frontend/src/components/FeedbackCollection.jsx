/**
 * FeedbackCollection.jsx - Phase 4 Human-in-the-Loop Implementation
 * Feedback collection component for user corrections and ML improvement
 */

import React, { useState } from 'react';
import { Star, Send, MessageCircle, AlertCircle, CheckCircle } from 'lucide-react';
import { analyticsAPI } from '../services/api';

const FeedbackCollection = ({ 
  analysisId, 
  sessionId,
  expectedResult = null,
  actualResult = null,
  onFeedbackSubmitted = () => {},
  className = ""
}) => {
  const [rating, setRating] = useState(0);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [comment, setComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [error, setError] = useState(null);

  const handleRatingClick = (value) => {
    setRating(value);
    setError(null);
  };

  const handleSubmit = async () => {
    if (rating === 0) {
      setError('Por favor, selecione uma avaliação (1-5 estrelas)');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const feedbackData = {
        session_id: sessionId,
        analysis_id: analysisId,
        feedback_type: 'rating',
        rating: rating,
        comment: comment.trim() || null,
        expected_result: expectedResult,
        actual_result: actualResult,
        is_helpful: rating >= 3 // Consider 3+ stars as helpful
      };

      await analyticsAPI.submitFeedback(feedbackData);
      
      setIsSubmitted(true);
      onFeedbackSubmitted({
        rating,
        comment,
        analysisId
      });

    } catch (err) {
      console.error('Failed to submit feedback:', err);
      setError('Erro ao enviar feedback. Tente novamente.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getRatingText = (ratingValue) => {
    switch (ratingValue) {
      case 1: return 'Muito ruim';
      case 2: return 'Ruim';
      case 3: return 'Regular';
      case 4: return 'Bom';
      case 5: return 'Excelente';
      default: return 'Selecione uma avaliação';
    }
  };

  if (isSubmitted) {
    return (
      <div className={`bg-green-50 border border-green-200 rounded-lg p-4 ${className}`}>
        <div className="flex items-center gap-2 text-green-700">
          <CheckCircle className="w-5 h-5" />
          <span className="font-medium">Feedback enviado com sucesso!</span>
        </div>
        <p className="text-sm text-green-600 mt-1">
          Obrigado por ajudar a melhorar o sistema.
        </p>
      </div>
    );
  }

  return (
    <div className={`bg-white border border-gray-200 rounded-lg p-4 space-y-4 ${className}`}>
      <div className="flex items-center gap-2">
        <MessageCircle className="w-5 h-5 text-blue-600" />
        <h3 className="font-medium text-gray-900">Avalie este resultado</h3>
      </div>

      {/* Star Rating */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">
          Qual a qualidade da análise?
        </label>
        <div className="flex items-center gap-1">
          {[1, 2, 3, 4, 5].map((value) => (
            <button
              key={value}
              type="button"
              onClick={() => handleRatingClick(value)}
              onMouseEnter={() => setHoveredRating(value)}
              onMouseLeave={() => setHoveredRating(0)}
              className="p-1 rounded transition-colors"
              aria-label={`${value} estrela${value > 1 ? 's' : ''}`}
            >
              <Star
                className={`w-6 h-6 transition-colors ${
                  value <= (hoveredRating || rating)
                    ? 'text-yellow-400 fill-yellow-400'
                    : 'text-gray-300'
                }`}
              />
            </button>
          ))}
          <span className="ml-2 text-sm text-gray-600">
            {getRatingText(hoveredRating || rating)}
          </span>
        </div>
      </div>

      {/* Comment */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">
          Comentários (opcional)
        </label>
        <textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Deixe seus comentários sobre o resultado da análise..."
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm
                     focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                     resize-none"
          rows={3}
          maxLength={500}
        />
        <div className="text-xs text-gray-500 text-right">
          {comment.length}/500 caracteres
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="flex items-center gap-2 text-red-600 text-sm">
          <AlertCircle className="w-4 h-4" />
          <span>{error}</span>
        </div>
      )}

      {/* Submit Button */}
      <button
        onClick={handleSubmit}
        disabled={isSubmitting || rating === 0}
        className={`w-full flex items-center justify-center gap-2 px-4 py-2 rounded-md text-sm font-medium
                   transition-colors ${
                     isSubmitting || rating === 0
                       ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                       : 'bg-blue-600 text-white hover:bg-blue-700'
                   }`}
      >
        {isSubmitting ? (
          <>
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            Enviando...
          </>
        ) : (
          <>
            <Send className="w-4 h-4" />
            Enviar Feedback
          </>
        )}
      </button>

      <p className="text-xs text-gray-500 text-center">
        Seu feedback nos ajuda a melhorar a qualidade das análises
      </p>
    </div>
  );
};

export default FeedbackCollection;

/*
Contains AI-generated code.
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ
Projeto: NET-EST - Sistema de Análise de Estratégias de Simplificação Textual em Tradução Intralingual
Phase 4: Human-in-the-Loop Interaction - Feedback Collection System
*/
